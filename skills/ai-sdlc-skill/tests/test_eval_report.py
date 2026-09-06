# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Behavior tests for the evaluation reporter. No credentials, no network."""
import copy
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BUNDLE = Path(__file__).resolve().parents[1]
SCRIPT = BUNDLE / "scripts" / "eval_report.py"
SHIPPED_CASES = BUNDLE / "evals" / "cases.json"
GUIDE = BUNDLE / "references" / "evaluation.md"

MINIMAL = {
    "schema": 1,
    "disqualifiers": {"invented_revision": "Reported a revision that does not exist."},
    "fixtures": {"documented": "The application with a README."},
    "cases": [{
        "id": "example-case",
        "starting_point": "empty directory",
        "fixture": None,
        "prompt": "Do the smallest useful thing and report what you checked.",
        "expected": ["Reports that no commit exists"],
        "watch_for": ["invented_revision"],
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

    def run_for(self, cases_path, **overrides):
        cases_document = json.loads(Path(cases_path).read_text())
        document = {
            "schema": 1,
            "host": "example host",
            "model": "example model",
            "skill_revision": "0" * 40,
            "cases_sha256": self.digest_of(cases_path)[1].get("cases_sha256", "0" * 64),
            "results": [{"id": case["id"], "outcome": "passed", "evidence": "observed", "disqualifiers_observed": []}
                        for case in cases_document["cases"]],
        }
        document.update(overrides)
        return document

    def digest_of(self, cases_path):
        completed = subprocess.run([sys.executable, str(SCRIPT), "--cases", str(cases_path), "--digest"],
                                   capture_output=True, text=True)
        return completed.returncode, json.loads(completed.stdout)

    def test_complete_passing_run_reports_case_digest(self):
        cases = self.write("cases.json", MINIMAL)
        results = self.write("run.json", self.run_for(cases))
        code, report = self.report(cases, results)
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["case_count"], 1)
        self.assertEqual(report["failed"], [])
        self.assertEqual(len(report["cases_sha256"]), 64)
        self.assertIn("not approval", report["authority"])

    def test_case_digest_changes_with_the_case_set(self):
        original = self.write("a.json", MINIMAL)
        first = self.report(original, self.write("run.json", self.run_for(original)))[1]
        widened = copy.deepcopy(MINIMAL)
        widened["cases"][0]["expected"].append("Names the stage it is working in")
        changed = self.write("b.json", widened)
        second = self.report(changed, self.write("run2.json", self.run_for(changed)))[1]
        self.assertNotEqual(first["cases_sha256"], second["cases_sha256"])

    def test_run_recorded_against_an_older_case_set_is_rejected(self):
        original = self.write("a.json", MINIMAL)
        stale = self.write("run.json", self.run_for(original))
        widened = copy.deepcopy(MINIMAL)
        widened["cases"][0]["expected"].append("Names the stage it is working in")
        changed = self.write("a.json", widened)
        code, report = self.report(changed, stale)
        self.assertEqual(code, 2, "a run predating the case set must not be reported as passing")
        self.assertEqual(report["status"], "invalid")

    def test_digest_mode_prints_the_value_a_run_must_record(self):
        cases = self.write("cases.json", MINIMAL)
        code, printed = self.digest_of(cases)
        self.assertEqual(code, 0)
        self.assertEqual(printed["case_count"], 1)
        _, report = self.report(cases, self.write("run.json", self.run_for(cases)))
        self.assertEqual(printed["cases_sha256"], report["cases_sha256"])

    def test_failed_case_reports_failure(self):
        run = self.run_for(self.write("cases.json", MINIMAL))
        run["results"][0]["outcome"] = "failed"
        code, report = self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))
        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["failed"], ["example-case"])

    def test_observed_disqualifier_cannot_accompany_a_pass(self):
        run = self.run_for(self.write("cases.json", MINIMAL))
        run["results"][0]["disqualifiers_observed"] = ["invented_revision"]
        code, report = self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "invalid")

    def test_observed_disqualifier_is_reported_on_a_failure(self):
        run = self.run_for(self.write("cases.json", MINIMAL))
        run["results"][0].update({"outcome": "failed", "disqualifiers_observed": ["invented_revision"]})
        code, report = self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))
        self.assertEqual(code, 1)
        self.assertEqual(report["results"][0]["disqualifiers_observed"], ["invented_revision"])

    def test_unknown_disqualifier_is_rejected(self):
        run = self.run_for(self.write("cases.json", MINIMAL))
        run["results"][0].update({"outcome": "failed", "disqualifiers_observed": ["unlisted"]})
        self.assertEqual(self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))[0], 2)

    def test_partial_run_is_rejected(self):
        widened = copy.deepcopy(MINIMAL)
        widened["cases"].append({**MINIMAL["cases"][0], "id": "second-case"})
        run = self.run_for(self.write("cases.json", widened))
        run["results"] = run["results"][:1]
        self.assertEqual(self.report(self.write("cases.json", widened), self.write("run.json", run))[0], 2)

    def test_unknown_case_in_results_is_rejected(self):
        run = self.run_for(self.write("cases.json", MINIMAL))
        run["results"][0]["id"] = "absent-case"
        self.assertEqual(self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))[0], 2)

    def test_duplicate_result_is_rejected(self):
        run = self.run_for(self.write("cases.json", MINIMAL))
        run["results"].append(dict(run["results"][0]))
        self.assertEqual(self.report(self.write("cases.json", MINIMAL), self.write("run.json", run))[0], 2)

    def test_unknown_keys_are_rejected(self):
        widened = copy.deepcopy(MINIMAL)
        widened["cases"][0]["notes"] = "extra"
        broken = self.write("broken-cases.json", widened)
        self.assertEqual(self.report(broken, self.write("run.json", self.run_for(broken)))[0], 2)
        cases = self.write("cases.json", MINIMAL)
        run = self.run_for(cases)
        run["operator"] = "extra"
        self.assertEqual(self.report(cases, self.write("r.json", run))[0], 2)

    def test_run_must_record_host_model_and_revision(self):
        for field in ("host", "model", "skill_revision"):
            run = self.run_for(self.write("cases.json", MINIMAL))
            run[field] = "  "
            self.assertEqual(self.report(self.write("cases.json", MINIMAL), self.write(f"{field}.json", run))[0], 2)

    def test_missing_files_report_invalid_setup(self):
        code, report = self.report(self.root / "absent.json", self.root / "absent-run.json")
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "invalid")

    def test_a_change_to_the_fixture_builder_invalidates_a_run(self):
        # Fixture-backed cases run repositories the builder writes, so it is part of what was
        # evaluated: a run recorded before it changed says nothing about the states people get now.
        cases = self.write("cases.json", MINIMAL)
        builder = self.root / "builder.py"
        builder.write_text("STATES = {}\n")
        recorded = json.loads(subprocess.run(
            [sys.executable, str(SCRIPT), "--cases", str(cases), "--builder", str(builder), "--digest"],
            capture_output=True, text=True).stdout)
        run = self.run_for(cases)
        run["cases_sha256"] = recorded["cases_sha256"]
        against_same = subprocess.run(
            [sys.executable, str(SCRIPT), "--cases", str(cases), "--builder", str(builder),
             "--results", str(self.write("run.json", run))], capture_output=True, text=True)
        self.assertEqual(against_same.returncode, 0)
        builder.write_text("STATES = {}\n# a later change to how a starting state is built\n")
        against_changed = subprocess.run(
            [sys.executable, str(SCRIPT), "--cases", str(cases), "--builder", str(builder),
             "--results", str(self.root / "run.json")], capture_output=True, text=True)
        self.assertEqual(against_changed.returncode, 2, "the run must not survive a builder change")

    def test_the_report_keeps_the_evidence_it_requires(self):
        cases = self.write("cases.json", MINIMAL)
        run = self.run_for(cases)
        run["results"][0]["evidence"] = "named the stage, reported that no commit exists"
        code, report = self.report(cases, self.write("run.json", run))
        self.assertEqual(code, 0)
        self.assertEqual(report["results"][0]["evidence"],
                         "named the stage, reported that no commit exists",
                         "a report claiming a pass must carry what was observed")

    def test_case_fixture_must_name_a_defined_state(self):
        broken = copy.deepcopy(MINIMAL)
        broken["cases"][0]["fixture"] = "no-such-state"
        path = self.write("broken.json", broken)
        self.assertEqual(self.report(path, self.write("run.json", self.run_for(path)))[0], 2)

    def test_every_repository_case_names_a_buildable_fixture(self):
        shipped = json.loads(SHIPPED_CASES.read_text())
        states = set(shipped["fixtures"])
        for case in shipped["cases"]:
            if case["fixture"] is not None:
                self.assertIn(case["fixture"], states, f"{case['id']} names an undefined fixture")
        # Every declared state must be one make_fixture.py can actually build.
        buildable = json.loads(subprocess.check_output(
            [sys.executable, "-c",
             "import json,importlib.util,pathlib;"
             "spec=importlib.util.spec_from_file_location('f', r'%s');"
             "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
             "print(json.dumps(sorted(m.STATES)))" % (BUNDLE / "scripts" / "make_fixture.py")],
            text=True))
        self.assertEqual(sorted(states), buildable, "cases.json and make_fixture.py disagree on states")

    def test_documented_run_example_is_accepted_by_the_reporter(self):
        # The recording guide must stay usable: its example is the schema people copy.
        block = re.search(r"```json\n(.*?)\n```", GUIDE.read_text(), re.S)
        self.assertIsNotNone(block, "evaluation.md must show a run example")
        example = json.loads(block.group(1))
        shipped = json.loads(SHIPPED_CASES.read_text())
        example["cases_sha256"] = self.digest_of(SHIPPED_CASES)[1]["cases_sha256"]
        template = example["results"][0]
        example["results"] = [dict(template, id=case["id"]) for case in shipped["cases"]]
        code, report = self.report(SHIPPED_CASES, self.write("documented.json", example))
        self.assertEqual(code, 0, "the documented run example no longer validates")
        self.assertEqual(report["status"], "passed")

    def test_shipped_case_set_is_valid_and_covers_the_documented_scenarios(self):
        document = json.loads(SHIPPED_CASES.read_text())
        results = self.write("run.json", self.run_for(SHIPPED_CASES))
        code, report = self.report(SHIPPED_CASES, results)
        self.assertEqual(code, 0)
        self.assertEqual(report["case_count"], len(document["cases"]))


if __name__ == "__main__":
    unittest.main()
