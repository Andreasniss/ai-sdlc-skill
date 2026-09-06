# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""The bundle must stay internally consistent when copied on its own."""
import re
from pathlib import Path
import unittest

BUNDLE = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
VERSION = re.compile(r"[Vv]ersion (\d+\.\d+\.\d+)")


def documents():
    return sorted(BUNDLE.glob("*.md")) + sorted(BUNDLE.glob("references/*.md")) + sorted(BUNDLE.glob("evals/*.md"))


class BundleConsistencyTests(unittest.TestCase):
    def setUp(self):
        declared = re.search(r"^\s*version:\s*(\S+)\s*$", (BUNDLE / "SKILL.md").read_text(), re.M)
        self.assertIsNotNone(declared, "SKILL.md must declare metadata.version")
        self.version = declared.group(1)

    def test_documented_version_matches_skill_metadata(self):
        for name in ("README.md", "references/adoption.md"):
            text = (BUNDLE / name).read_text()
            found = set(VERSION.findall(text))
            self.assertTrue(found, f"{name} states no version")
            self.assertEqual(found, {self.version}, f"{name} disagrees with SKILL.md")

    def test_relative_links_resolve(self):
        for document in documents():
            for target in LINK.findall(document.read_text()):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                path = (document.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(path.exists(), f"{document.name} links to missing {target}")

    def test_skill_routes_to_every_reference(self):
        text = (BUNDLE / "SKILL.md").read_text()
        for reference in sorted(BUNDLE.glob("references/*.md")):
            self.assertIn(f"references/{reference.name}", text,
                          f"SKILL.md never routes to {reference.name}")

    def test_evaluation_cases_are_reachable_from_the_instructions(self):
        reachable = (BUNDLE / "references" / "evaluation.md").read_text()
        self.assertIn("evals/cases.md", reachable)
        self.assertTrue((BUNDLE / "evals" / "cases.json").is_file())

    def test_frontmatter_is_well_formed_and_names_the_bundle(self):
        text = (BUNDLE / "SKILL.md").read_text()
        self.assertTrue(text.startswith("---\n"), "SKILL.md must open with frontmatter")
        block = text.split("---\n", 2)[1]
        keys = dict(re.findall(r"^([a-z_]+):\s*(.*)$", block, re.M))
        self.assertEqual(keys.get("name"), BUNDLE.name, "the declared name must match the bundle directory")
        self.assertTrue(keys.get("description", "").strip(), "SKILL.md must carry a description for discovery")
        self.assertLessEqual(len(keys["description"]), 1024, "description is too long for reliable discovery")
        self.assertIn("version:", block, "SKILL.md must declare metadata.version")

    def test_licensing_notices_are_present(self):
        self.assertTrue((BUNDLE / "NOTICE").is_file())
        self.assertIn("SPDX-License-Identifier", (BUNDLE / "SKILL.md").read_text())
        for script in sorted(BUNDLE.glob("scripts/*.py")) + sorted(BUNDLE.glob("tests/*.py")):
            head = script.read_text()[:400]
            self.assertIn("SPDX-FileCopyrightText", head, f"{script.name} lacks an SPDX copyright header")
            self.assertIn("SPDX-License-Identifier", head, f"{script.name} lacks an SPDX license header")


if __name__ == "__main__":
    unittest.main()
