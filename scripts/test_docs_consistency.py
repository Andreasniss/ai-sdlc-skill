#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Repository documentation must agree with the bundle it describes."""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "skills" / "ai-sdlc-skill"
VERSION = re.compile(r"version (\d+\.\d+\.\d+)", re.I)
COUNT = re.compile(r"(\d+) (?:bundle|helper) tests pass")
SNAPSHOT = re.compile(r"(\d+) passing deterministic tests")
REFERENCED = re.compile(r"(?:skills|scripts|\.github|\.githooks)/[A-Za-z0-9_./-]+\.(?:py|json|md|yml|yaml)")


def declared_version():
    match = re.search(r"^\s*version:\s*(\S+)\s*$", (BUNDLE / "SKILL.md").read_text(), re.M)
    assert match, "SKILL.md must declare metadata.version"
    return match.group(1)


def collected_tests():
    listing = subprocess.check_output(
        [sys.executable, "-m", "unittest", "discover", "-s", str(BUNDLE / "tests"), "-v"],
        cwd=ROOT, stderr=subprocess.STDOUT, text=True, timeout=300)
    match = re.search(r"^Ran (\d+) tests", listing, re.M)
    assert match, "could not read the bundle test count"
    return int(match.group(1))


class DocumentationConsistencyTests(unittest.TestCase):
    def test_root_documents_state_the_bundle_version(self):
        version = declared_version()
        stated = set(VERSION.findall((ROOT / "README.md").read_text()))
        self.assertTrue(stated, "README.md states no version")
        self.assertEqual(stated, {version}, "README.md disagrees with SKILL.md")

    def test_stated_test_counts_match_the_suite(self):
        actual = collected_tests()
        for name, pattern in (("INSTALLATION.md", COUNT), ("README.md", SNAPSHOT)):
            claimed = pattern.findall((ROOT / name).read_text())
            self.assertTrue(claimed, f"{name} makes no test-count claim to check")
            for value in claimed:
                self.assertEqual(int(value), actual, f"{name} claims {value} tests; the suite runs {actual}")

    def test_python_files_carry_spdx_headers(self):
        for script in sorted(ROOT.glob("scripts/*.py")) + sorted(BUNDLE.glob("scripts/*.py")) + sorted(BUNDLE.glob("tests/*.py")):
            head = script.read_text()[:400]
            self.assertIn("SPDX-FileCopyrightText", head, f"{script} lacks an SPDX copyright header")
            self.assertIn("SPDX-License-Identifier: Apache-2.0", head, f"{script} lacks an SPDX license header")

    def test_notices_agree(self):
        self.assertEqual((ROOT / "NOTICE").read_text(), (BUNDLE / "NOTICE").read_text(),
                         "the bundle NOTICE has drifted from the repository NOTICE")

    def test_documented_paths_exist(self):
        # Extract the paths each document actually names, so a typo fails instead of being skipped.
        for name in ("README.md", "INSTALLATION.md", "CONTRIBUTING.md", "AGENTS.md", "PRIVACY.md", "SECURITY.md"):
            text = (ROOT / name).read_text()
            found = set(REFERENCED.findall(text))
            for path in sorted(found):
                self.assertTrue((ROOT / path).is_file(), f"{name} names missing {path}")
        commands = (ROOT / "CONTRIBUTING.md").read_text()
        for required in ("scripts/test_docs_consistency.py", "skills/ai-sdlc-skill/scripts/eval_report.py"):
            self.assertIn(required, commands, f"CONTRIBUTING.md no longer documents {required}")


if __name__ == "__main__":
    unittest.main()
