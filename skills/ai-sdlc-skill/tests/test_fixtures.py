# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Every evaluation case that needs a repository must start from the same bytes."""
import json
from pathlib import Path
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

    def test_a_state_is_reproducible_byte_for_byte(self):
        _, _, first = self.build("documented", "first")
        _, _, second = self.build("documented", "second")
        for name in ("app.js", "index.html", "README.md", "test/tasks.test.js"):
            self.assertEqual((first / name).read_text(), (second / name).read_text(),
                             f"{name} differs between builds of the same state")

    def test_the_bug_state_hides_a_live_defect_behind_a_green_suite(self):
        _, _, target = self.build("bug")
        checks = subprocess.run(["node", "--test", "test/tasks.test.js"], cwd=target,
                                capture_output=True, text=True)
        if checks.returncode == 127 or "not found" in checks.stderr:
            self.skipTest("node is unavailable in this environment")
        self.assertEqual(checks.returncode, 0, "the bug state must ship a passing suite")
        observed = subprocess.run(
            ["node", "-e", "const {add,complete}=require('./app-under-test.js');"
                           "const t=add(add([],'write'),'write');"
                           "process.exit(complete(t,t[0].id)[1].done ? 0 : 1);"],
            cwd=target, capture_output=True, text=True)
        self.assertEqual(observed.returncode, 0, "the duplicate-title defect is not present")

    def test_review_and_resume_states_carry_their_branches(self):
        for state, branch in (("branch", "export-filtered"), ("interrupted", "filter-tasks")):
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

    def test_readable_cases_are_the_rendering_of_the_case_set(self):
        completed = subprocess.run([sys.executable, str(RENDER), "--check"], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout)


if __name__ == "__main__":
    unittest.main()
