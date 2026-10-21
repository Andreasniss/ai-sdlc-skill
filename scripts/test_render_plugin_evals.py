#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""The plugin eval suite must be the exact rendering of cases.json and the grader spec.

No test here calls a model. They prove what can be proven before a paid run: the tree is current,
prompts are the case prompts byte for byte, every `expected` line has a grader or a stated reason,
scaffolds build the fixtures the cases name, rubrics are blind to the arm, and every deterministic
grader detects the change it exists for (checked with real JavaScript regular expressions).
"""
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import render_plugin_evals as render  # noqa: E402

LINE = re.compile(r"^(?:#.*|[a-z_]+: (?:'(?:[^']|'')*'|[^'\s].*))$")
NODE_CHECK = """
const items = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = items.map(({pattern, flags, text}) => {
  try { return new RegExp(pattern, flags).test(text); } catch (error) { return 'ERROR: ' + error.message; }
});
process.stdout.write(JSON.stringify(out));
"""


def frontmatter_of(text):
    """Parse the emitted YAML subset: returns ({key: raw value}, body)."""
    lines = text.split("\n")
    assert lines[0] == "---", "frontmatter must open with ---"
    end = lines.index("---", 1)
    pairs = {}
    for line in lines[1:end]:
        if line.startswith("#"):
            continue
        key, _, value = line.partition(": ")
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1].replace("''", "'")
        pairs[key] = value
    return pairs, "\n".join(lines[end + 1:])


def js_regex(items):
    """Evaluate [{pattern, flags, text}] with the JavaScript engine the eval runner uses."""
    result = subprocess.run(["node", "-e", NODE_CHECK], input=json.dumps(items), text=True,
                            capture_output=True, timeout=60)
    if result.returncode != 0:
        raise AssertionError("node failed: " + result.stderr)
    return json.loads(result.stdout)


class Suite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases_doc = render.load_json(ROOT / render.CASES_REL)
        cls.cases = {case["id"]: case for case in cls.cases_doc["cases"]}
        cls.spec = render.load_spec()
        cls.builder = render.load_builder()
        cls.rendered = render.render_all(cls.cases_doc, cls.spec, cls.builder)
        cls.fixtures = {}
        for case_id in cls.spec.CASES:
            state = cls.cases[case_id]["fixture"]
            if state not in cls.fixtures:
                cls.fixtures[state] = render.fixture_files(cls.builder, state)

    def variant(self, mutate):
        spec = types.SimpleNamespace(SCHEMA=self.spec.SCHEMA, RUN=self.spec.RUN,
                                     SKILL_INPUT_MATCH=self.spec.SKILL_INPUT_MATCH,
                                     CASES=copy.deepcopy(self.spec.CASES))
        mutate(spec)
        return render.validate(self.cases_doc, spec, self.builder)

    # ------------------------------------------------------------ the tree

    def test_committed_tree_is_the_current_rendering(self):
        self.assertEqual(render.compare(ROOT / "evals", self.rendered), [],
                         "run python3 scripts/render_plugin_evals.py")

    def test_check_command_passes_and_prints_the_digest(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "render_plugin_evals.py"), "--check"],
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(render.digest(self.rendered), result.stdout)

    def test_rendering_is_deterministic(self):
        again = render.render_all(self.cases_doc, self.spec, self.builder)
        self.assertEqual(again, self.rendered)
        self.assertEqual(render.digest(again), render.digest(self.rendered))

    def test_check_reports_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            render.write(out, self.rendered)
            self.assertEqual(render.compare(out, self.rendered), [])
            first = sorted(self.rendered)[0]
            (out / first).write_text("changed\n")
            (out / "stray-case").mkdir()
            (out / "stray-case" / "prompt.md").write_text("x\n")
            (out / sorted(self.rendered)[-1]).unlink()
            problems = render.compare(out, self.rendered)
            self.assertIn("stale " + first, problems)
            self.assertIn("unexpected case directory stray-case", problems)
            self.assertTrue(any(p.startswith("missing ") for p in problems))

    def test_write_removes_case_directories_the_spec_dropped_and_keeps_other_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            render.write(out, self.rendered)
            (out / "dropped-case" / "graders").mkdir(parents=True)
            (out / "dropped-case" / "prompt.md").write_text("x\n")
            (out / "dropped-case" / "graders" / "g.md").write_text("x\n")
            (out / "plugin-eval-run-x").mkdir()
            (out / "plugin-eval-run-x" / "aggregate-result.json").write_text("{}\n")
            render.write(out, self.rendered)
            self.assertFalse((out / "dropped-case").exists())
            self.assertTrue((out / "plugin-eval-run-x" / "aggregate-result.json").exists())
            self.assertEqual(render.compare(out, self.rendered), [])

    def test_forced_variant_differs_only_by_the_appended_system_prompt(self):
        forced = render.render_all(self.cases_doc, self.spec, self.builder, True)
        self.assertEqual(set(forced), set(self.rendered))
        changed = [p for p in forced if forced[p] != self.rendered[p]]
        self.assertEqual(sorted(changed), sorted(case + "/prompt.md" for case in self.spec.CASES))
        for path in changed:
            lines = forced[path][0].split("\n")
            plain = self.rendered[path][0].split("\n")
            extra = [line for line in lines if line not in plain]
            self.assertEqual(extra, ["append_system_prompt: " + render.scalar(render.FORCED_PROMPT)], path)
        self.assertNotEqual(render.digest(forced), render.digest(self.rendered))

    def test_digest_moves_when_a_grader_moves(self):
        changed = dict(self.rendered)
        path = sorted(p for p in changed if "/graders/" in p)[0]
        text, mode = changed[path]
        changed[path] = (text + "\n", mode)
        self.assertNotEqual(render.digest(changed), render.digest(self.rendered))

    def test_only_cases_named_by_the_spec_are_rendered(self):
        self.assertEqual({p.split("/")[0] for p in self.rendered}, set(self.spec.CASES))
        self.assertEqual(len(self.spec.CASES), 8)

    # ------------------------------------------------------------ single source

    def test_prompt_body_is_the_case_prompt_byte_for_byte(self):
        for case_id in self.spec.CASES:
            _, body = frontmatter_of(self.rendered[case_id + "/prompt.md"][0])
            self.assertEqual(body, self.cases[case_id]["prompt"] + "\n", case_id)

    def test_expected_outcome_lists_the_case_criteria_verbatim(self):
        for case_id in self.spec.CASES:
            pairs, _ = frontmatter_of(self.rendered[case_id + "/prompt.md"][0])
            self.assertEqual(pairs["expected_outcome"], " | ".join(self.cases[case_id]["expected"]), case_id)

    def test_disqualifier_rubric_carries_the_disqualifiers_verbatim(self):
        for case_id in self.spec.CASES:
            _, body = frontmatter_of(self.rendered[case_id + "/graders/no-disqualifier.md"][0])
            for name, description in self.cases_doc["disqualifiers"].items():
                self.assertIn("- %s: %s" % (name, description), body, case_id)

    def test_spec_and_cases_agree(self):
        self.assertEqual(render.validate(self.cases_doc, self.spec, self.builder), [])

    # ------------------------------------------------------------ the harness files

    def test_every_case_has_the_documented_files(self):
        for case_id in self.spec.CASES:
            for name in ("prompt.md", "case.yaml", "scaffold.sh"):
                self.assertIn("%s/%s" % (case_id, name), self.rendered)
            graders = [p for p in self.rendered if p.startswith(case_id + "/graders/")]
            self.assertGreaterEqual(len(graders), 5, case_id)

    def test_frontmatter_stays_in_the_emitted_subset(self):
        for path, (text, _) in self.rendered.items():
            if path.endswith("scaffold.sh"):
                continue
            head = text.split("\n---\n")[0] if text.startswith("---\n") else text
            for line in head.split("\n"):
                if line in ("---", "") or line.startswith("schema_version") or line.startswith("name:") \
                        or line.startswith("context:") or line.startswith("  scaffold_script"):
                    continue
                self.assertRegex(line, LINE, "%s: %r" % (path, line[:80]))

    def test_case_yaml_names_the_case_and_its_scaffold(self):
        for case_id in self.spec.CASES:
            text = self.rendered[case_id + "/case.yaml"][0]
            self.assertIn('schema_version: "1.1"', text)
            self.assertIn("name: %s\n" % case_id, text)
            self.assertIn("scaffold_script: scaffold.sh", text)

    def test_only_the_scaffold_is_executable(self):
        for path, (_, mode) in self.rendered.items():
            self.assertEqual(bool(mode & 0o111), path.endswith("/scaffold.sh"), path)

    def test_scaffold_builds_exactly_the_named_fixture_in_an_empty_directory(self):
        for case_id in self.spec.CASES:
            state = self.cases[case_id]["fixture"]
            script = ROOT / "evals" / case_id / "scaffold.sh"
            with tempfile.TemporaryDirectory() as tmp:
                result = subprocess.run(["bash", str(script)], cwd=tmp, capture_output=True, text=True,
                                        timeout=120)
                self.assertEqual(result.returncode, 0, "%s: %s" % (case_id, result.stderr))
                built = {p.relative_to(tmp).as_posix():
                         render.REVISION.sub("<revision>", p.read_text(encoding="utf-8"))
                         for p in Path(tmp).rglob("*")
                         if p.is_file() and p.relative_to(tmp).parts[0] != ".git"}
                # The interrupted state records the commit it branched from, so a revision is masked.
                expected = {k: render.REVISION.sub("<revision>", v) for k, v in self.fixtures[state].items()}
                self.assertEqual(built, expected, case_id)
                self.assertFalse(any("evals" in part for p in Path(tmp).rglob("*")
                                     for part in p.relative_to(tmp).parts), case_id)

    def test_every_rubric_is_blind_to_the_arm(self):
        for path, (text, _) in self.rendered.items():
            if "/graders/" not in path:
                continue
            pairs, body = frontmatter_of(text)
            if pairs.get("type") == "llm":
                self.assertIsNone(render.BLIND.search(body), path)

    def test_the_skill_indicator_never_scores(self):
        for case_id in self.spec.CASES:
            pairs, _ = frontmatter_of(self.rendered[case_id + "/graders/skill-fired.md"][0])
            self.assertEqual(pairs["arm"], "with-only")
            self.assertEqual(pairs["tool"], "Skill")

    def test_each_case_keeps_both_kinds_of_grader(self):
        for case_id in self.spec.CASES:
            types_seen = [frontmatter_of(text)[0]["type"] for path, (text, _) in self.rendered.items()
                          if path.startswith(case_id + "/graders/")]
            self.assertIn("llm", types_seen, case_id)
            self.assertGreaterEqual(sum(t in {"regex", "tool_used", "file_exists"} for t in types_seen), 5,
                                    case_id)

    # ------------------------------------------------------------ the validator refuses bad specs

    def test_validator_refuses_an_unaccounted_expected_line(self):
        problems = self.variant(lambda s: s.CASES["bug-with-reproducible-symptom"]["covers"]["expected"]
                                .__setitem__(1, []))
        self.assertTrue(any("expected[1] names no grader" in p for p in problems), problems)

    def test_validator_accepts_a_stated_reason_and_refuses_an_empty_one(self):
        ok = self.variant(lambda s: s.CASES["bug-with-reproducible-symptom"]["covers"]["expected"]
                          .__setitem__(2, "not_graded: needs a person"))
        self.assertEqual([p for p in ok if "expected[2]" in p], [])
        bad = self.variant(lambda s: s.CASES["bug-with-reproducible-symptom"]["covers"]["expected"]
                           .__setitem__(2, "not_graded:"))
        self.assertTrue(any("expected[2]" in p for p in bad), bad)

    def test_generator_refuses_an_exact_check_on_a_file_that_embeds_a_revision(self):
        def mutate(spec):
            spec.CASES["resume-interrupted-change"]["graders"].append(
                {"name": "unchanged-check-results", "type": "unchanged_file",
                 "file": "docs/check-results.md", "weight": 0.5})
            spec.CASES["resume-interrupted-change"]["covers"]["extra"].append("unchanged-check-results")
        spec = types.SimpleNamespace(SCHEMA=self.spec.SCHEMA, RUN=self.spec.RUN,
                                     SKILL_INPUT_MATCH=self.spec.SKILL_INPUT_MATCH,
                                     CASES=copy.deepcopy(self.spec.CASES))
        mutate(spec)
        with self.assertRaises(render.SpecError) as raised:
            render.render_all(self.cases_doc, spec, self.builder)
        self.assertIn("embeds a commit revision", str(raised.exception))

    def test_validator_refuses_a_rubric_that_names_the_skill(self):
        def mutate(spec):
            for grader in spec.CASES["review-without-edits"]["graders"]:
                if grader["name"] == "report-quality":
                    grader["rubric"] += "\nPASS if it followed the skill."
        self.assertTrue(any("blind to the arm" in p for p in self.variant(mutate)))

    def test_validator_refuses_a_pattern_without_samples(self):
        def mutate(spec):
            for grader in spec.CASES["review-without-edits"]["graders"]:
                if grader["name"] == "read-requirement":
                    grader["samples"] = {"match": [], "no_match": []}
        self.assertTrue(any("needs samples" in p for p in self.variant(mutate)))

    def test_validator_refuses_a_grader_missing_from_covers(self):
        def mutate(spec):
            spec.CASES["review-without-edits"]["graders"].append(
                {"name": "extra-grader", "type": "file_exists", "path": "x", "exists": False})
        self.assertTrue(any("extra-grader is not listed in covers" in p for p in self.variant(mutate)))

    def test_validator_refuses_an_unknown_case_and_a_missing_indicator(self):
        self.assertTrue(any("not a case" in p for p in self.variant(
            lambda s: s.CASES.__setitem__("no-such-case", s.CASES["review-without-edits"]))))
        self.assertTrue(any("missing the generated grader skill-fired" in p for p in self.variant(
            lambda s: s.CASES["review-without-edits"].__setitem__(
                "graders", [g for g in s.CASES["review-without-edits"]["graders"]
                            if g["name"] != "skill-fired"]))))


try:
    import yaml
except ImportError:  # PyYAML is optional: the stdlib-only checks above still cover the emitted subset.
    yaml = None


@unittest.skipIf(yaml is None, "PyYAML is needed to parse the frontmatter as real YAML")
class RealYaml(unittest.TestCase):
    """The harness parses these files with a YAML parser, so parse them with one."""

    @classmethod
    def setUpClass(cls):
        cls.cases_doc = render.load_json(ROOT / render.CASES_REL)
        cls.spec = render.load_spec()
        cls.rendered = render.render_all(cls.cases_doc, cls.spec, render.load_builder())

    @staticmethod
    def load(text):
        lines = text.split("\n")
        return yaml.safe_load("\n".join(lines[1:lines.index("---", 1)]))

    def test_every_frontmatter_block_is_a_yaml_mapping(self):
        for path, (text, _) in self.rendered.items():
            if path.endswith(".md"):
                self.assertIsInstance(self.load(text), dict, path)
            elif path.endswith("case.yaml"):
                data = yaml.safe_load(text)
                self.assertEqual(data["schema_version"], "1.1", path)
                self.assertEqual(data["context"], {"scaffold_script": "scaffold.sh"}, path)

    def test_patterns_and_options_survive_the_round_trip(self):
        for case_id, entry in self.spec.CASES.items():
            for grader in entry["graders"]:
                data = self.load(self.rendered["%s/graders/%s.md" % (case_id, grader["name"])][0])
                where = "%s/%s" % (case_id, grader["name"])
                if grader["type"] == "regex" and "pattern" in grader:
                    self.assertEqual(data["pattern"], grader["pattern"], where)
                    self.assertEqual(data.get("flags"), grader.get("flags"), where)
                    self.assertEqual(data.get("match"), grader.get("match"), where)
                if grader["type"] == "tool_used":
                    self.assertEqual(data["tool"], grader["tool"], where)
                    self.assertEqual(data.get("input_match"), grader.get("input_match"), where)
                    for key in ("min", "max"):
                        self.assertEqual(data.get(key), grader.get(key), where)
                if grader["type"] == "file_exists":
                    self.assertEqual((data["path"], data["exists"]), (grader["path"], grader["exists"]), where)
                if "weight" in grader:
                    self.assertEqual(data["weight"], grader["weight"], where)
                if "file" in grader:
                    self.assertEqual(data["target"], {"source": "file", "path": grader["file"]}, where)

    def test_prompt_frontmatter_has_only_documented_keys(self):
        documented = {"schema_version", "name", "description", "tags", "plugins", "runs",
                      "expected_outcome", "model", "max_turns", "timeout_seconds", "allowed_tools",
                      "append_system_prompt", "env"}
        for case_id in self.spec.CASES:
            data = self.load(self.rendered[case_id + "/prompt.md"][0])
            self.assertLessEqual(set(data), documented, case_id)
            self.assertEqual(data["max_turns"], self.spec.RUN["max_turns"])
            self.assertEqual(data["allowed_tools"], self.spec.RUN["allowed_tools"])


@unittest.skipUnless(shutil.which("node"), "node is needed to evaluate JavaScript regular expressions")
class GraderBehavior(unittest.TestCase):
    """Each deterministic grader must detect the change it exists for, before any paid run."""

    @classmethod
    def setUpClass(cls):
        cls.cases_doc = render.load_json(ROOT / render.CASES_REL)
        cls.cases = {case["id"]: case for case in cls.cases_doc["cases"]}
        cls.spec = render.load_spec()
        cls.builder = render.load_builder()
        cls.rendered = render.render_all(cls.cases_doc, cls.spec, cls.builder)
        cls.fixtures = {}

    def fixture(self, case_id):
        state = self.cases[case_id]["fixture"]
        if state not in self.fixtures:
            self.fixtures[state] = render.fixture_files(self.builder, state)
        return self.fixtures[state]

    def test_every_pattern_compiles_and_its_samples_behave(self):
        items, expectations = [], []
        for case_id, entry in self.spec.CASES.items():
            for grader in entry["graders"]:
                pattern = grader.get("pattern") or grader.get("input_match")
                if not pattern or grader["type"] == "unchanged_file":
                    continue
                samples = grader.get("samples") or {}
                for text in samples.get("match", []):
                    items.append({"pattern": pattern, "flags": grader.get("flags", ""), "text": text})
                    expectations.append((case_id, grader["name"], text, True))
                for text in samples.get("no_match", []):
                    items.append({"pattern": pattern, "flags": grader.get("flags", ""), "text": text})
                    expectations.append((case_id, grader["name"], text, False))
        self.assertGreater(len(items), 100)
        for (case_id, name, text, wanted), got in zip(expectations, js_regex(items)):
            self.assertIsInstance(got, bool, "%s/%s: %s" % (case_id, name, got))
            self.assertEqual(got, wanted, "%s/%s on %r" % (case_id, name, text))

    def test_skill_indicator_matches_the_tool_call_encoding(self):
        pattern = self.spec.SKILL_INPUT_MATCH
        texts = ['{"skill":"ai-sdlc-skill"}', '{"skill":"ai-sdlc:ai-sdlc-skill","args":""}',
                 '{"skill": "ai-sdlc-skill"}', '{"skill":"other-skill"}', '{"skill":"ai-sdlc-skills"}']
        got = js_regex([{"pattern": pattern, "flags": "", "text": text} for text in texts])
        self.assertEqual(got, [True, True, True, False, False])

    def test_file_checks_give_the_declared_verdict_on_the_unmodified_fixture(self):
        items, expectations = [], []
        for case_id, entry in self.spec.CASES.items():
            files = self.fixture(case_id)
            for grader in entry["graders"]:
                if grader["type"] != "regex" or "file" not in grader:
                    continue
                self.assertIn(grader["file"], files, "%s/%s" % (case_id, grader["name"]))
                items.append({"pattern": grader["pattern"], "flags": grader.get("flags", ""),
                              "text": files[grader["file"]]})
                absent = grader.get("match") == "not_contains"
                expectations.append((case_id, grader["name"], absent, grader["on_unmodified"]))
        self.assertGreater(len(items), 15)
        for (case_id, name, absent, declared), found in zip(expectations, js_regex(items)):
            self.assertIsInstance(found, bool, found)
            verdict = "pass" if (not found if absent else found) else "fail"
            self.assertEqual(verdict, declared, "%s/%s: unmodified fixture %s, declared %s"
                             % (case_id, name, verdict, declared))

    def test_every_task_outcome_check_fails_on_the_unmodified_fixture(self):
        # A check that already passes on the starting state cannot detect that the work was done.
        outcome = {"app-under-test-matches-by-identity", "app-js-matches-by-identity", "app-js-sorts",
                   "csv-in-app-js", "csv-in-app-under-test", "escaping-tested", "email-excluded",
                   "todo-resolved", "handler-saves"}
        seen = set()
        for entry in self.spec.CASES.values():
            for grader in entry["graders"]:
                if grader["name"] in outcome:
                    seen.add(grader["name"])
                    self.assertEqual(grader["on_unmodified"], "fail", grader["name"])
        self.assertEqual(seen, outcome)

    def test_unchanged_file_checks_accept_the_original_and_reject_any_edit(self):
        items, expectations = [], []
        for case_id, entry in self.spec.CASES.items():
            files = self.fixture(case_id)
            for grader in entry["graders"]:
                if grader["type"] != "unchanged_file":
                    continue
                pairs, _ = frontmatter_of(self.rendered["%s/graders/%s.md" % (case_id, grader["name"])][0])
                original = files[grader["file"]]
                for text, wanted in ((original, True), (original + "x", False), ("x" + original, False),
                                     (original.replace("\n", "\r\n"), False), (original[:-1], False),
                                     (original[:-2] + "!\n", False),
                                     (original + "\n", False), (original.rstrip("\n") + "\n\n", False)):
                    items.append({"pattern": pairs["pattern"], "flags": "", "text": text})
                    expectations.append((case_id, grader["name"], wanted))
        self.assertGreater(len(items), 30)
        for (case_id, name, wanted), got in zip(expectations, js_regex(items)):
            self.assertEqual(got, wanted, "%s/%s" % (case_id, name))

    def test_js_escape_round_trips_awkward_text(self):
        text = "a.b*c+d?e(f)g[h]i{j}k|l\\m/n^o$p\n\tq\ré ' \""
        got = js_regex([{"pattern": "^" + render.js_escape(text) + "$", "flags": "", "text": text},
                        {"pattern": "^" + render.js_escape(text) + "$", "flags": "", "text": text + "x"}])
        self.assertEqual(got, [True, False])


if __name__ == "__main__":
    unittest.main()
