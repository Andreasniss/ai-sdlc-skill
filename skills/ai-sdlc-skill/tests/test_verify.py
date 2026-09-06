"""Behavior tests use isolated repositories and no credentials or network."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify.py"


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.DEVNULL)

    def prepare(self, checks):
        (self.root / "checks.json").write_text(json.dumps({"checks": checks}))
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")

    def check(self, code, name="fixture", **kw):
        return {"name": name, "argv": [sys.executable, "-c", code], **kw}

    def run_report(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.root), "--config", "checks.json"], capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)

    def test_success_records_exact_revision_without_output(self):
        self.prepare([self.check("print('private child output')")])
        code, report = self.run_report()
        self.assertEqual(code, 0)
        self.assertEqual(report["revision"], self.git("rev-parse", "HEAD").decode().strip())
        self.assertNotIn("private child output", json.dumps(report))

    def test_failure_stops_later_checks(self):
        self.prepare([self.check("raise SystemExit(7)"), self.check("pass", "later")])
        code, report = self.run_report()
        self.assertEqual(code, 1)
        self.assertEqual(len(report["checks"]), 1)
        self.assertEqual(report["checks"][0]["returncode"], 7)

    def test_missing_executable_fails(self):
        self.prepare([{"name": "missing", "argv": ["/nonexistent-ai-sdlc-skill-fixture"]}])
        code, report = self.run_report()
        self.assertEqual(code, 1)
        self.assertEqual(report["checks"][0]["status"], "unavailable")

    def test_timeout_fails(self):
        self.prepare([self.check("import time; time.sleep(10)", timeout_seconds=1)])
        code, report = self.run_report()
        self.assertEqual(code, 1)
        self.assertEqual(report["checks"][0]["status"], "timeout")

    def test_empty_suite_rejected(self):
        self.prepare([])
        self.assertEqual(self.run_report()[0], 2)

    def test_invalid_timeout_rejected(self):
        self.prepare([self.check("pass", timeout_seconds=True)])
        self.assertEqual(self.run_report()[0], 2)

    def test_duplicate_names_rejected(self):
        self.prepare([self.check("pass"), self.check("pass")])
        self.assertEqual(self.run_report()[0], 2)

    def test_dirty_candidate_rejected(self):
        self.prepare([self.check("pass")])
        (self.root / "extra").write_text("uncommitted")
        self.assertEqual(self.run_report()[0], 2)

    def test_check_cannot_mutate_candidate_silently(self):
        self.prepare([self.check("from pathlib import Path; Path('new').write_text('changed')")])
        code, report = self.run_report()
        self.assertEqual(code, 1)
        self.assertFalse(report["candidate_unchanged"])

    def test_new_commit_invalidates_run(self):
        self.prepare([self.check("import subprocess; subprocess.run(['git','commit','--allow-empty','-qm','changed'],check=True)")])
        code, report = self.run_report()
        self.assertEqual(code, 1)
        self.assertFalse(report["candidate_unchanged"])

    def test_no_shell_interpolation(self):
        self.prepare([{"name": "literal", "argv": [sys.executable, "-c", "import sys; assert sys.argv[1] == '$(touch injected)'", "$(touch injected)"]}])
        self.assertEqual(self.run_report()[0], 0)
        self.assertFalse((self.root / "injected").exists())

    def test_symlink_config_rejected(self):
        self.prepare([self.check("pass")])
        (self.root / "real.json").write_bytes((self.root / "checks.json").read_bytes())
        (self.root / "checks.json").unlink()
        (self.root / "checks.json").symlink_to("real.json")
        self.git("add", ".")
        self.git("commit", "-qm", "symlink fixture")
        self.assertEqual(self.run_report()[0], 2)


if __name__ == "__main__":
    unittest.main()
