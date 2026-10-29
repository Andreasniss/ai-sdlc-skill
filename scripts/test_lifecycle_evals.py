#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Validate replay fixtures and behavioral graders without any model calls."""
import ast
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "evals/lifecycle"
spec = importlib.util.spec_from_file_location("lifecycle_suite", PACK / "suite.py")
suite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(suite)

# Evaluator-only reference repairs are never copied into a worker fixture.
READING = '''def reading_time(article, output):
    return max(1, math.ceil(len(article["source"].split()) / 200))
'''
ASSET = '''def asset_url(name, output):
    digest = hashlib.sha256((ROOT / "assets" / name).read_bytes()).hexdigest()
    return "/assets/" + name + "?v=" + digest[:12]
'''
ARCHIVE = '''def archive(query="", series=""):
    rows = [row for row in articles() if (not series or row["series"] == series)
            and query.strip().casefold() in row["title"].casefold()]
    return {"ids": [row["id"] for row in rows], "scope": series,
            "reset_url": "?", "controls": ["reader-goals"]}
'''
SENTENCE = '''def sentence(text):
    return text if text.endswith((".", "?", "!")) else text + "."
'''
CONTRAST = '''def contrast(background, opacity):
    channel = (background * opacity + 255 * (1 - opacity)) / 255
    luminance = channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
    return (luminance + 0.05) / 0.05
'''


def replace_function(workspace, name, replacement):
    path = workspace / "site_app.py"
    text = path.read_text()
    node = next(node for node in ast.parse(text).body if isinstance(node, ast.FunctionDef) and node.name == name)
    lines = text.splitlines(keepends=True)
    path.write_text("".join(lines[:node.lineno - 1]) + replacement + "".join(lines[node.end_lineno:]))


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def fixture(self, case, suffix="run", arm="baseline"):
        destination = self.root / suffix
        skill = ROOT / "skills/ai-sdlc-skill" if arm == "skill" else None
        suite.prepare(case, destination, arm, skill)
        return destination, destination / "workspace"

    def repair(self, workspace, case):
        changes = {
            "ordinary-reading-time": {"reading_time": READING},
            "resume-versioned-assets": {"asset_url": ASSET},
            "changed-archive-requirement": {"archive": ARCHIVE},
            "mixed-review-unavailable-check": {"sentence": SENTENCE, "contrast": CONTRAST},
        }[case]
        for name, code in changes.items():
            replace_function(workspace, name, code)

    def test_all_starts_preflight_but_fail_target_behavior(self):
        for case in suite.cases():
            with self.subTest(case=case["id"]):
                destination, workspace = self.fixture(case["id"], case["id"])
                self.assertTrue(suite.preflight(destination)["passed"])
                result = suite.grade(destination)
                self.assertFalse(result["passed"])
                self.assertEqual(result["process_verdict"], "unmeasured")
                self.assertIsNone(result["accepted_case"])
                self.assertNotIn("oracle.py", suite.files(workspace))
                self.assertNotIn("suite.py", suite.files(workspace))
                self.assertEqual(suite.git(workspace, "status", "--porcelain"), "")

    def test_treatments_have_identical_repositories(self):
        for case in suite.cases():
            states = [suite.prepare(case["id"], self.root / (case["id"] + arm), arm,
                                    ROOT / "skills/ai-sdlc-skill" if arm == "skill" else None)
                      for arm in suite.ARMS]
            self.assertEqual(len({item["initial"]["inputs_sha256"] for item in states}), 1)
            self.assertEqual(len({item["initial"]["head"] for item in states}), 1)
            self.assertEqual(len({item["treatment_sha256"] for item in states}), 3)

    def test_reference_repairs_pass_without_process_credit(self):
        for case in suite.cases():
            destination, workspace = self.fixture(case["id"], case["id"])
            self.repair(workspace, case["id"])
            if len(case["prompts"]) == 2:
                suite.advance(destination)
            result = suite.grade(destination)
            self.assertTrue(result["passed"], result)
            self.assertIsNone(result["accepted_case"])
            self.assertEqual(result["process_verdict"], "unmeasured")

    def test_reading_constant_floor_and_one_format_repairs_fail(self):
        destination, workspace = self.fixture("ordinary-reading-time")
        for replacement in (
            'def reading_time(article, output):\n    return 2\n',
            READING.replace("math.ceil", "math.floor"),
            READING.replace('article["source"]', 'article["source" if output == "html" else "markdown"]'),
        ):
            replace_function(workspace, "reading_time", replacement)
            self.assertFalse(suite.grade(destination)["passed"])

    def test_asset_fixed_and_size_versions_fail(self):
        destination, workspace = self.fixture("resume-versioned-assets")
        for replacement in (
            'def asset_url(name, output):\n    return "/assets/" + name + "?v=fixed"\n',
            'def asset_url(name, output):\n    return "/assets/" + name + "?v=" + str((ROOT / "assets" / name).stat().st_size)\n',
        ):
            replace_function(workspace, "asset_url", replacement)
            self.assertFalse(suite.grade(destination)["passed"])

    def test_asset_grader_does_not_modify_candidate(self):
        destination, workspace = self.fixture("resume-versioned-assets")
        self.repair(workspace, "resume-versioned-assets")
        before = suite.snapshot(workspace)
        self.assertTrue(suite.grade(destination)["passed"])
        self.assertEqual(before, suite.snapshot(workspace))

    def test_resume_receipt_really_predates_candidate(self):
        destination, workspace = self.fixture("resume-versioned-assets")
        receipt = json.loads((workspace / "previous-check.json").read_text())
        head = suite.git(workspace, "rev-parse", "HEAD")
        self.assertNotEqual(receipt["candidate"]["head"], head)
        self.assertEqual(receipt["candidate"]["head"], suite.git(workspace, "rev-parse", "HEAD~1"))
        self.assertEqual(receipt["exit_code"], 0)
        self.assertNotEqual(receipt["candidate"]["files"]["assets/diagram.svg"],
                            suite.files(workspace)["assets/diagram.svg"])

    def test_archive_transition_keeps_actual_work_but_invalidates_old_outcome(self):
        destination, workspace = self.fixture("changed-archive-requirement")
        replace_function(workspace, "archive", ARCHIVE.replace('"reader-goals"', '"series-buttons"'))
        self.assertTrue(suite.grade(destination)["passed"])
        before = (workspace / "site_app.py").read_bytes()
        suite.advance(destination)
        self.assertEqual((workspace / "site_app.py").read_bytes(), before)
        self.assertFalse(suite.grade(destination)["passed"])
        self.repair(workspace, "changed-archive-requirement")
        self.assertTrue(suite.grade(destination)["passed"])
        with self.assertRaises(ValueError):
            suite.advance(destination)

    def test_archive_lost_search_invisible_scope_and_stale_reset_fail(self):
        destination, workspace = self.fixture("changed-archive-requirement")
        suite.advance(destination)
        mutants = [ARCHIVE.replace('and query.strip().casefold() in row["title"].casefold()', ''),
                   ARCHIVE.replace('"scope": series', '"scope": ""'),
                   ARCHIVE.replace('"reset_url": "?"', '"reset_url": "?series=" + series'),
                   ARCHIVE.replace('[row["id"] for row in rows]', '[row["id"] for row in reversed(rows)]')]
        for mutant in mutants:
            replace_function(workspace, "archive", mutant)
            self.assertFalse(suite.grade(destination)["passed"])

    def test_equivalent_local_reset_url_is_accepted(self):
        destination, workspace = self.fixture("changed-archive-requirement")
        suite.advance(destination)
        replace_function(workspace, "archive", ARCHIVE.replace('"reset_url": "?"', '"reset_url": "/writing/"'))
        self.assertTrue(suite.grade(destination)["passed"])

    def test_mixed_review_partial_repairs_do_not_pass(self):
        destination, workspace = self.fixture("mixed-review-unavailable-check")
        replace_function(workspace, "sentence", SENTENCE)
        self.assertFalse(suite.grade(destination)["passed"])
        replace_function(workspace, "contrast", 'def contrast(background, opacity):\n    return 21\n')
        self.assertFalse(suite.grade(destination)["passed"])

    def test_unavailable_service_never_becomes_an_automatic_process_pass(self):
        destination, workspace = self.fixture("mixed-review-unavailable-check")
        self.repair(workspace, "mixed-review-unavailable-check")
        suite.advance(destination)
        record = json.loads((workspace / "review-service.json").read_text())
        self.assertEqual(record["job_conclusion"], "success")
        self.assertEqual(record["reviews_completed"], 0)
        result = suite.grade(destination)
        self.assertTrue(result["passed"])
        self.assertEqual(result["process_verdict"], "unmeasured")

    def test_recolor_and_content_changes_cannot_game_acceptance(self):
        destination, workspace = self.fixture("mixed-review-unavailable-check")
        self.repair(workspace, "mixed-review-unavailable-check")
        for path in ("assets/diagram.svg", "articles.json", "aliases.json"):
            target = workspace / path
            original = target.read_text()
            target.write_text(original + "\n")
            self.assertFalse(suite.grade(destination)["passed"])
            target.write_text(original)

    def test_help_or_noop_tests_are_not_behavior_evidence(self):
        destination, workspace = self.fixture("ordinary-reading-time")
        result = suite.run([sys.executable, "-m", "unittest", "--help"], workspace)
        self.assertEqual(result.returncode, 0)
        (workspace / "test_site.py").write_text('print("All tests passed")\n')
        self.assertFalse(suite.grade(destination)["passed"])
        self.assertIsNone(suite.grade(destination)["accepted_case"])

    def test_preflight_rejects_missing_or_changed_files(self):
        destination, workspace = self.fixture("ordinary-reading-time")
        (workspace / "assets/diagram.svg").unlink()
        with self.assertRaises(ValueError):
            suite.preflight(destination)
        with self.assertRaises(ValueError):
            suite.prepare("ordinary-reading-time", destination)

    def test_snapshot_includes_untracked_work(self):
        destination, workspace = self.fixture("ordinary-reading-time")
        before = suite.snapshot(workspace)
        (workspace / "new-regression.py").write_text("assert True\n")
        after = suite.snapshot(workspace)
        self.assertEqual(before["head"], after["head"])
        self.assertNotEqual(before["inputs_sha256"], after["inputs_sha256"])

    def test_plan_is_reproducible_complete_and_counterbalanced(self):
        plan = suite.plan(5772026)
        self.assertEqual(plan, suite.plan(5772026))
        self.assertEqual(len(plan["runs"]), 36)
        self.assertEqual(sum(run["sessions"] for run in plan["runs"]), 54)
        for case in suite.cases():
            blocks = [[run["arm"] for run in plan["runs"]
                       if run["case"] == case["id"] and run["repeat"] == repeat]
                      for repeat in range(1, 4)]
            self.assertTrue(all(sorted(block) == sorted(suite.ARMS) for block in blocks))
            for position in range(3):
                self.assertEqual({block[position] for block in blocks}, set(suite.ARMS))

    def test_protected_state_and_skill_arguments_fail_closed(self):
        with self.assertRaises(ValueError):
            suite.prepare("ordinary-reading-time", self.root / "bad", "skill")
        with self.assertRaises(ValueError):
            suite.prepare("ordinary-reading-time", self.root / "bad", "baseline", ROOT / "skills/ai-sdlc-skill")
        destination, workspace = self.fixture("ordinary-reading-time")
        with self.assertRaises(ValueError):
            suite.advance(destination)
        state = json.loads((destination / "state.json").read_text())
        state["suite_digest"] = "wrong"
        suite.write_json(destination / "state.json", state)
        with self.assertRaises(ValueError):
            suite.grade(destination)

    def test_preflight_rejects_changed_skill(self):
        skill = self.root / "skill"
        shutil.copytree(ROOT / "skills/ai-sdlc-skill", skill)
        destination = self.root / "run"
        suite.prepare("ordinary-reading-time", destination, "skill", skill)
        self.assertTrue(suite.preflight(destination)["passed"])
        with (skill / "SKILL.md").open("a") as handle:
            handle.write("\nChanged instructions\n")
        with self.assertRaises(ValueError):
            suite.preflight(destination)

    def test_invalid_candidate_is_failure_not_empty_success(self):
        destination, workspace = self.fixture("ordinary-reading-time")
        (workspace / "site_app.py").write_text("invalid python !\n")
        result = suite.grade(destination)
        self.assertFalse(result["passed"])
        self.assertIn("execution_error", result)
        self.assertIsNone(result["accepted_case"])


if __name__ == "__main__":
    unittest.main()
