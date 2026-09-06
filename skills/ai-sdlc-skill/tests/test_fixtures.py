# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Every evaluation case that needs a repository must start from the same bytes."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

BUNDLE = Path(__file__).resolve().parents[1]
BUILDER = BUNDLE / "scripts" / "make_fixture.py"
RENDER = BUNDLE / "scripts" / "render_cases.py"
CASES = BUNDLE / "evals" / "cases.json"


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def build(self, state, name=None):
        target = self.root / (name or state)
        completed = subprocess.run([sys.executable, str(BUILDER), "--state", state, "--into", str(target)],
                                   capture_output=True, text=True)
        return completed.returncode, json.loads(completed.stdout), target

    def test_every_declared_state_builds_a_clean_repository(self):
        for state in sorted(json.loads(CASES.read_text())["fixtures"]):
            code, report, target = self.build(state)
            self.assertEqual(code, 0, f"{state} did not build")
            self.assertEqual(report["state"], state)
            self.assertEqual(len(report["revision"]), 40)
            dirty = subprocess.check_output(["git", "-C", str(target), "status", "--porcelain"], text=True)
            self.assertEqual(dirty, "", f"{state} does not start clean")

    def test_the_init_state_genuinely_has_no_checks_to_find(self):
        _, _, target = self.build("undocumented")
        self.assertFalse((target / "test").exists(),
                         "the init case cannot observe an absent test suite if one is shipped")
        self.assertFalse((target / "README.md").exists())

    def test_the_resume_record_counts_the_checks_that_file_declares(self):
        _, _, target = self.build("interrupted")
        settled = subprocess.check_output(
            ["git", "-C", str(target), "show", "main:test/tasks.test.js"], text=True)
        recorded = (target / "docs" / "check-results.md").read_text()
        self.assertIn(f"passed, {settled.count(chr(10) + 'test(')} checks", recorded,
                      "the handoff must not record a check count the suite never ran")

    def test_the_export_control_is_connected_in_export_bearing_states(self):
        for state in ("branch", "duplication"):
            _, _, target = self.build(state, name=f"wired-{state}")
            page, application = (target / "index.html").read_text(), (target / "app.js").read_text()
            self.assertIn('id="export"', page)
            self.assertIn('getElementById("export").addEventListener', application,
                          f"{state} shows an export control the page never wires up")
            self.assertIn("exportTasks(filterTasks(", application,
                          f"{state} must export what the list is showing, or the branch change is invisible")

    def test_identifiers_survive_removing_tasks(self):
        if shutil.which("node") is None:
            self.skipTest("node is unavailable in this environment")
        _, _, target = self.build("interrupted")
        # The resume case's own work removes tasks; ids must not then collide for a later add.
        observed = subprocess.run(
            ["node", "-e",
             "const {add}=require('./app-under-test.js');"
             "let t=add(add([],'a'),'b');"
             "t=t.filter(task=>task.id!==t[0].id);"
             "t=add(t,'c');"
             "process.exit(new Set(t.map(x=>x.id)).size===t.length ? 0 : 1);"],
            cwd=target, capture_output=True, text=True)
        self.assertEqual(observed.returncode, 0,
                         "adding after a removal reuses an id, so the case would hide an unrelated defect")

    def test_a_state_is_reproducible_byte_for_byte(self):
        _, _, first = self.build("documented", "first")
        _, _, second = self.build("documented", "second")
        for name in ("app.js", "index.html", "README.md", "test/tasks.test.js"):
            self.assertEqual((first / name).read_text(), (second / name).read_text(),
                             f"{name} differs between builds of the same state")

    def test_the_bug_state_hides_a_live_defect_behind_a_green_suite(self):
        # A missing executable raises rather than returning a code, so check before running.
        if shutil.which("node") is None:
            self.skipTest("node is unavailable in this environment")
        _, _, target = self.build("bug")
        checks = subprocess.run(["node", "--test", "test/tasks.test.js"], cwd=target,
                                capture_output=True, text=True)
        self.assertEqual(checks.returncode, 0, "the bug state must ship a passing suite")
        observed = subprocess.run(
            ["node", "-e", "const {add,complete}=require('./app-under-test.js');"
                           "const t=add(add([],'write'),'write');"
                           "process.exit(complete(t,t[0].id)[1].done ? 0 : 1);"],
            cwd=target, capture_output=True, text=True)
        self.assertEqual(observed.returncode, 0, "the duplicate-title defect is not present")

    def test_review_and_resume_states_carry_their_branches(self):
        for state, branch in (("branch", "export-filtered"), ("interrupted", "clear-completed")):
            _, _, target = self.build(state)
            head = subprocess.check_output(["git", "-C", str(target), "branch", "--show-current"], text=True)
            self.assertEqual(head.strip(), branch, f"{state} is not on {branch}")

    def test_a_non_empty_destination_is_refused(self):
        target = self.root / "occupied"
        target.mkdir()
        (target / "keep.txt").write_text("existing work")
        code, report, _ = self.build("documented", "occupied")
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue((target / "keep.txt").is_file(), "the builder must not disturb existing files")

    def test_the_feature_case_starts_before_the_behavior_it_asks_for(self):
        _, _, target = self.build("documented")
        application = (target / "app.js").read_text()
        self.assertNotIn("exportTasks", application,
                         "the feature case must not start with CSV export already written")
        self.assertNotIn("Export CSV", (target / "index.html").read_text(),
                         "the page must not advertise an export the state does not have")
        # The prompt says "the currently filtered tasks", so filtering and a UI must already exist.
        for required in ("function render", "function filterTasks", "addEventListener"):
            self.assertIn(required, application,
                          f"the feature case assumes working behavior; {required} is missing")
        _, _, with_export = self.build("branch")
        self.assertIn("exportTasks", (with_export / "app.js").read_text(),
                      "the review case needs the export its branch changes")

    def test_the_review_state_supplies_the_requirement_its_diff_is_judged_against(self):
        _, _, target = self.build("branch")
        requirement = (target / "ISSUE.md").read_text()
        self.assertIn("currently showing", requirement,
                      "the review case needs a stated requirement, not a bare diff")
        diff = subprocess.check_output(["git", "-C", str(target), "diff", "main..HEAD"], text=True)
        self.assertIn("task => !task.done", diff,
                      "the branch must actually depart from the requirement, or there is nothing to find")

    def test_the_resume_note_claims_only_what_the_branch_contains(self):
        _, _, target = self.build("interrupted")
        page, application = (target / "index.html").read_text(), (target / "app.js").read_text()
        self.assertIn('id="clear-completed"', page, "the note claims a control that is not on the page")
        self.assertIn('clear-completed").addEventListener', application,
                      "the note claims a handler that is not attached")
        self.assertIn("TODO", application, "the handler must still be unfinished")
        self.assertNotIn("clearCompleted", (target / "app-under-test.js").read_text(),
                         "the removal is the remaining work and must not be implemented")

    def test_the_resume_state_supplies_the_inputs_its_case_reads(self):
        _, _, target = self.build("interrupted")
        for name in ("ISSUE.md", "docs/decisions.md", "docs/check-results.md", "NOTES.md"):
            self.assertTrue((target / name).is_file(), f"the resume case cannot read a missing {name}")
        recorded = (target / "docs" / "check-results.md").read_text()
        settled = subprocess.check_output(["git", "-C", str(target), "rev-parse", "main"], text=True).strip()
        head = subprocess.check_output(["git", "-C", str(target), "rev-parse", "HEAD"], text=True).strip()
        self.assertIn(settled, recorded, "the check record must name a real revision")
        self.assertNotIn(head, recorded,
                         "the record must predate the branch work, or the case cannot test stale evidence")

    def test_fixture_descriptions_match_the_case_set(self):
        declared = json.loads(CASES.read_text())["fixtures"]
        states = json.loads(subprocess.check_output(
            [sys.executable, "-c",
             "import json,importlib.util;"
             "spec=importlib.util.spec_from_file_location('f', r'%s');"
             "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
             "print(json.dumps(m.STATES))" % BUILDER], text=True))
        self.assertEqual(declared, states, "cases.json and make_fixture.py describe the states differently")

    def test_readable_cases_are_the_rendering_of_the_case_set(self):
        completed = subprocess.run([sys.executable, str(RENDER), "--check"], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout)


if __name__ == "__main__":
    unittest.main()
