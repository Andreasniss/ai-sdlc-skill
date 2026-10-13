#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Static packaging and synthetic payload checks, not host compatibility tests."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "scripts/fixtures/plugin-hooks"


def read_json(path):
    return json.loads((ROOT / path).read_text())


class PluginPackagingTests(unittest.TestCase):
    def test_manifest_identities_match_canonical_version(self):
        portable = read_json("plugin.json")
        codex = read_json(".codex-plugin/plugin.json")
        claude = read_json(".claude-plugin/plugin.json")
        version = re.search(r"^  version: (.+)$", (ROOT / "skills/ai-sdlc-skill/SKILL.md").read_text(), re.M).group(1)
        self.assertEqual(portable["version"], version)
        self.assertEqual(portable["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        for key in ("name", "version", "description", "author", "repository", "license"):
            self.assertEqual(codex[key], portable[key])
            self.assertEqual(claude[key], portable[key])
        self.assertEqual(portable["name"], "ai-sdlc")
        self.assertEqual(portable["license"], "Apache-2.0")

    def test_all_layouts_resolve_one_canonical_skill(self):
        # Portable and Claude use fixed default directories. Claude custom paths
        # are additive, so do not re-declare its default skills directory.
        self.assertNotIn("skills", read_json("plugin.json"))
        self.assertNotIn("skills", read_json(".claude-plugin/plugin.json"))
        codex_path = read_json(".codex-plugin/plugin.json")["skills"]
        self.assertEqual(codex_path, "./skills/")
        canonical = ROOT / "skills/ai-sdlc-skill/SKILL.md"
        for directory in (ROOT / "skills", ROOT / codex_path):
            self.assertEqual(list(directory.rglob("SKILL.md")), [canonical])
        tracked = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, text=True).splitlines()
        self.assertEqual([p for p in tracked if Path(p).name == "SKILL.md"], ["skills/ai-sdlc-skill/SKILL.md"])

    def test_default_package_has_no_automatic_components(self):
        for name in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
            manifest = read_json(name)
            self.assertFalse(set(manifest) & {"hooks", "mcpServers", "apps", "commands", "agents", "extensions"})
        for name in ("hooks", "mcp.json", ".mcp.json", ".app.json", "commands", "agents"):
            self.assertFalse((ROOT / name).exists(), name)

    def run_probe(self, payload):
        return subprocess.run([sys.executable, str(FIXTURE / "probe.py")], input=payload, text=True, capture_output=True, timeout=5)

    def test_distinct_host_payload_fixtures_are_accepted_without_output_context(self):
        for host in ("codex", "claude"):
            result = self.run_probe((FIXTURE / f"{host}-input.json").read_text())
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "ai-sdlc synthetic SessionStart probe received\n")

    def test_invalid_payloads_never_report_success(self):
        for payload in ("not json", "[]", "null", "{}", '{"hook_event_name":"PreToolUse"}', '{"hook_event_name":"SessionStart","source":"resume"}'):
            result = self.run_probe(payload)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout + result.stderr, "")

    def test_hook_adapters_use_host_specific_root_and_startup_only(self):
        for host, variable in (("codex", "PLUGIN_ROOT"), ("claude", "CLAUDE_PLUGIN_ROOT")):
            config = json.loads((FIXTURE / f"{host}-hooks.json").read_text())
            self.assertEqual(list(config["hooks"]), ["SessionStart"])
            groups = config["hooks"]["SessionStart"]
            self.assertEqual(len(groups), 1)
            self.assertEqual(groups[0]["matcher"], "startup")
            self.assertEqual(groups[0]["hooks"], [{"type": "command", "command": 'python3 "${' + variable + '}/probe.py"', "timeout": 5}])


if __name__ == "__main__":
    unittest.main()
