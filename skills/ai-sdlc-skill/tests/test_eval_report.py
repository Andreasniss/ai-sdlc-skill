# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Behavior tests for the evaluation reporter. No credentials, no network."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BUNDLE = Path(__file__).resolve().parents[1]
SCRIPT = BUNDLE / "scripts" / "eval_report.py"
SHIPPED_CASES = BUNDLE / "evals" / "cases.json"

MINIMAL = {
    "schema": 1,
    "disqualifiers": {"invented_revision": "Reported a revision that does not exist."},
    "cases": [{
        "id": "example-case",
        "starting_point": "empty directory",
        "prompt": "Do the smallest useful thing and report what you checked.",
        "expected": ["Reports that no commit exists"],
        "disqualifiers": ["invented_revision"],
    }],
}


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, name, document):
        path = self.root / name
        path.write_text(json.dumps(document))
        return path

    def report(self, cases, results):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--cases", str(cases), "--results", str(results)],
            capture_output=True, text=True)
        return completed.returncode, json.loads(completed.stdout)

    def run_for(self, cases_document, **overrides):
        document = {
            "schema": 1,
            "host": "example host",
            "model": "example model",
            "skill_revision": "0" * 40,
            "results": [{"id": case["id"], "outcome": "passed", "evidence": "observed", "disqualifiers_observed": []}
                        for case in cases_document["cases"]],
        }
        document.update(overrides)
        return document

    def test_complete_passing_run_reports_case_digest(self):
        cases = self.write("cases.json", MINIMAL)
        results = self.write("run.json", self.run_for(MINIMAL))
        code, report = self.report(cases, results)
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["case_count"], 1)
        self.assertEqual(report["failed"], [])
        self.assertEqual(len(report["cases_sha256"]), 64)
        self.assertIn("not approval", report["authority"])

    def test_case_digest_changes_with_the_case_set(self):
        first = self.report(self.write("a.json", MINIMAL), self.write("run.json", self.run_for(MINIMAL)))[1]
        widened = copy.deepcopy(MINIMAL)
        widened["cases"][0]["expected"].append("Names the stage it is working in")
        second = self.report(self.write("b.json", widened), self.write("run2.json", self.run_for(widened)))[1]
        self.assertNotEqual(first["cases_sha256"], second["cases_sha256"])

    def test_failed_case_reports_failure(self):
        run = self.run_for(MINIMAL)
        run["results"][0]["outcome"] = "failed"
        code, report = self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))
        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["failed"], ["example-case"])

    def test_observed_disqualifier_cannot_accompany_a_pass(self):
        run = self.run_for(MINIMAL)
        run["results"][0]["disqualifiers_observed"] = ["invented_revision"]
        code, report = self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "invalid")

    def test_observed_disqualifier_is_reported_on_a_failure(self):
        run = self.run_for(MINIMAL)
        run["results"][0].update({"outcome": "failed", "disqualifiers_observed": ["invented_revision"]})
        code, report = self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))
        self.assertEqual(code, 1)
        self.assertEqual(report["results"][0]["disqualifiers_observed"], ["invented_revision"])

    def test_unknown_disqualifier_is_rejected(self):
        run = self.run_for(MINIMAL)
        run["results"][0].update({"outcome": "failed", "disqualifiers_observed": ["unlisted"]})
        self.assertEqual(self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))[0], 2)

    def test_partial_run_is_rejected(self):
        widened = copy.deepcopy(MINIMAL)
        widened["cases"].append({**MINIMAL["cases"][0], "id": "second-case"})
        run = self.run_for(widened)
        run["results"] = run["results"][:1]
        self.assertEqual(self.report(self.write("cases.json", widened), self.write("run.json", run))[0], 2)

    def test_unknown_case_in_results_is_rejected(self):
        run = self.run_for(MINIMAL)
        run["results"][0]["id"] = "absent-case"
        self.assertEqual(self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))[0], 2)

    def test_duplicate_result_is_rejected(self):
        run = self.run_for(MINIMAL)
        run["results"].append(dict(run["results"][0]))
        self.assertEqual(self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))[0], 2)

    def test_unknown_keys_are_rejected(self):
        widened = copy.deepcopy(MINIMAL)
        widened["cases"][0]["notes"] = "extra"
        self.assertEqual(self.report(self.write("cases.json", widened), self.write("run.json", self.run_for(MINIMAL)))[0], 2)
        run = self.run_for(MINIMAL)
        run["operator"] = "extra"
        self.assertEqual(self.report(self.write("c.json", MINIMAL), self.write("r.json", run))[0], 2)

    def test_run_must_record_host_model_and_revision(self):
        for field in ("host", "model", "skill_revision"):
            run = self.run_for(MINIMAL)
            run[field] = "  "
            self.assertEqual(self.report(self.write("cases.json", MINIMAL), self.write(f"{field}.json", run))[0], 2)

    def test_missing_files_report_invalid_setup(self):
        code, report = self.report(self.root / "absent.json", self.root / "absent-run.json")
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "invalid")

    def test_shipped_case_set_is_valid_and_covers_the_documented_scenarios(self):
        document = json.loads(SHIPPED_CASES.read_text())
        results = self.write("run.json", self.run_for(document))
        code, report = self.report(SHIPPED_CASES, results)
        self.assertEqual(code, 0)
        self.assertEqual(report["case_count"], len(document["cases"]))


if __name__ == "__main__":
    unittest.main()
