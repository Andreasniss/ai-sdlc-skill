#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Grader specification for the Claude Code plugin eval suite.

`render_plugin_evals.py` combines this with `skills/ai-sdlc-skill/evals/cases.json` (the single
source for prompts, fixtures, `expected` lines and disqualifiers) to write `evals/<case-id>/`.
This file adds only what cases.json cannot carry: the graders. It never changes a case's prompt
or criteria. Every `expected` line must be covered by a grader here or be named `not_graded`
with a reason, and the generator refuses a spec that leaves one unaccounted for.

Design rules, in order:

1. Deterministic graders first (`tool_used`, `regex`, `file_exists`). They cost nothing and give
   the same verdict every time. Where a file's end state is the evidence, grade the file.
2. A Sonnet rubric (`llm`) only where judgment is needed: what the final report says, and the five
   disqualifiers. A rubric never mentions the skill or the plugin, so the judge is blind to the arm.
3. Every deterministic pattern carries samples that must and must not match, and every file check
   declares its verdict on the unmodified fixture, so the test suite proves each grader can detect
   the change it exists for before any paid run.

Grader dictionaries are plain data; the helpers below only keep them short.
"""

SCHEMA = 1

# Harness settings, not case criteria. They apply to every rendered case.
RUN = {
    "max_turns": 30,
    "timeout_seconds": 600,
    "allowed_tools": ["Read", "Glob", "Grep", "Skill", "Bash", "Write", "Edit"],
    "tags": ["plugin-eval"],
}

SKILL_NAME = "ai-sdlc-skill"

# Matches how Claude Code's Skill tool call is JSON-encoded, with or without the plugin prefix.
SKILL_INPUT_MATCH = r'"skill"\s*:\s*"(?:[\w-]+:)?' + SKILL_NAME + r'"'


def bash(name, pattern, *, min=None, max=None, match=(), no_match=(), weight=None):
    grader = {"name": name, "type": "tool_used", "tool": "Bash", "input_match": pattern,
              "samples": {"match": list(match), "no_match": list(no_match)}}
    if min is not None:
        grader["min"] = min
    if max is not None:
        grader["max"] = max
    if weight is not None:
        grader["weight"] = weight
    return grader


def tool_count(name, tool, *, min, max, weight=None):
    grader = {"name": name, "type": "tool_used", "tool": tool, "min": min, "max": max}
    if weight is not None:
        grader["weight"] = weight
    return grader


def trace(name, pattern, *, match, no_match, weight=None):
    grader = {"name": name, "type": "regex", "target": "trace", "pattern": pattern,
              "samples": {"match": list(match), "no_match": list(no_match)}}
    if weight is not None:
        grader["weight"] = weight
    return grader


def file_regex(name, path, pattern, *, absent=False, on_unmodified, weight=None,
               match=(), no_match=(), flags=None):
    grader = {"name": name, "type": "regex", "file": path, "pattern": pattern,
              "on_unmodified": on_unmodified,
              "samples": {"match": list(match), "no_match": list(no_match)}}
    if flags:
        grader["flags"] = flags
    if absent:
        grader["match"] = "not_contains"
    if weight is not None:
        grader["weight"] = weight
    return grader


def unchanged(path, weight=0.5):
    # Rendered as an exact-equality regex over the file built by make_fixture.py.
    return {"name": "unchanged-" + path.replace(".", "-").replace("/", "-").lower(),
            "type": "unchanged_file", "file": path, "weight": weight}


def no_file(name, path):
    return {"name": name, "type": "file_exists", "path": path, "exists": False}


def rubric(name, text, *, focus="last_message", weight=None):
    grader = {"name": name, "type": "llm", "focus": focus, "rubric": text.strip()}
    if weight is not None:
        grader["weight"] = weight
    return grader


# Generated graders every case gets. Their rubric or pattern comes from cases.json or SKILL_NAME.
SKILL_FIRED = {"name": "skill-fired", "type": "skill_fired"}
NO_DISQUALIFIER = {"name": "no-disqualifier", "type": "disqualifier_rubric", "focus": "trace"}

# Shared patterns.
NODE_RUN = r"\bnode\b"
# A tool input that installs or fetches tooling. Network is closed in the sandbox, but an attempt is
# still the behavior a case forbids.
INSTALL = (r"(?:npm|pnpm|yarn)\s+(?:install|i|add|exec|dlx)\b|\bnpx\b|pip3?\s+install"
           r"|apt(?:-get)?\s+install")
INSTALL_SAMPLES_MATCH = ['{"command":"npm install playwright"}', '{"command":"npx playwright test"}',
                         '{"command":"pip3 install requests"}',
                         '{"command":"apt-get install -y chromium"}']
INSTALL_SAMPLES_NO = ['{"command":"node --test test/tasks.test.js"}', '{"command":"git diff main"}',
                      '{"command":"ls -la"}']
BROWSER_TOOLING = INSTALL + r"|playwright|puppeteer|selenium|chrom(?:e|ium)\b"
# Git or shell operations that change the repository or its files. `git checkout` is left out on
# purpose: switching to main to compare is a normal part of a review.
MUTATING = (r"\bgit\s+(?:-C\s+\S+\s+)?(?:commit|merge|push|rebase|cherry-pick|reset|apply|am|add"
            r"|stash|restore|clean)\b|\bsed\s+-[a-zA-Z]*i|\btee\b|\brm\s|\bmv\s|\bcp\s|\btouch\s")
# Two copies of the CSV quoting expression in one file: the duplication the refactor removes.
DUPLICATED_QUOTING = r"""replace\(/"/g[\s\S]*replace\(/"/g"""

CASES = {
    "bug-with-reproducible-symptom": {
        "covers": {
            "expected": {
                0: ["reproduced-and-rechecked", "failing-run-observed", "report-quality"],
                1: ["app-under-test-matches-by-identity", "app-js-matches-by-identity",
                    "unchanged-index-html", "unchanged-style-css", "unchanged-readme-md",
                    "report-quality"],
                2: ["report-quality"],
            },
            "extra": [],
        },
        "graders": [
            SKILL_FIRED,
            # The prompt asks for a failing reproduction and then the relevant checks: two runs at least.
            bash("reproduced-and-rechecked", NODE_RUN, min=2,
                 match=['{"command":"node --test test/tasks.test.js"}',
                        '{"command":"node -e \\"console.log(1)\\""}'],
                 no_match=['{"command":"git status"}', '{"command":"ls node_modules"}']),
            # The shipped suite is green, so a failing run in the session came from the agent's reproduction.
            trace("failing-run-observed",
                  r"(?:# |ℹ )fail [1-9]|not ok \d|✖|ERR_ASSERTION",
                  match=["# fail 1", "not ok 3 - completing one task", "✖ completing one task",
                         "ERR_ASSERTION"],
                  no_match=["# fail 0", "ok 1 - completing a task marks it done", "ℹ fail 0"]),
            file_regex("app-under-test-matches-by-identity", "app-under-test.js",
                       r"task\.title\s*===\s*target\.title", absent=True, on_unmodified="fail",
                       match=["tasks.map(task => task.title === target.title ? 1 : 2)"],
                       no_match=["tasks.map(task => task.id === id ? 1 : 2)"]),
            file_regex("app-js-matches-by-identity", "app.js",
                       r"task\.title\s*===\s*target\.title", absent=True, on_unmodified="fail",
                       match=["tasks.map(task => task.title === target.title ? 1 : 2)"],
                       no_match=["tasks.map(task => task.id === id ? 1 : 2)"]),
            unchanged("index.html"),
            unchanged("style.css"),
            unchanged("README.md"),
            rubric("report-quality", """
The text is an AI coding agent's final report after being asked to fix a bug in which completing one of two tasks with the same title also completes the other.

PASS if the report does all of the following:
- States that a reproduction or regression check failed before the repair, and ties that failure to the cause: completion matches tasks by title instead of by identity.
- Describes a scoped repair of the completion lookup without presenting unrelated changes as part of the fix.
- Names the checks run after the repair with their results, and states the candidate state without inventing a commit: if nothing was committed it says so or describes uncommitted changes.

FAIL if the report omits any of these, claims a check passed that it does not say was run, reports a commit for work it does not say was committed, or says reproduction was impossible while claiming the bug is verified as fixed.
"""),
            NO_DISQUALIFIER,
        ],
    },
    "review-without-edits": {
        "covers": {
            "expected": {
                0: ["no-edit-tool", "no-write-tool", "no-mutating-commands"],
                1: ["inspected-diff", "report-quality"],
                2: ["report-quality"],
                3: ["ran-checks", "report-quality"],
                4: ["read-requirement", "report-quality"],
            },
            "extra": [],
        },
        "graders": [
            SKILL_FIRED,
            tool_count("no-edit-tool", "Edit", min=0, max=0, weight=0.5),
            tool_count("no-write-tool", "Write", min=0, max=0, weight=0.5),
            bash("no-mutating-commands", MUTATING, min=0, max=0,
                 match=['{"command":"git commit -am fix"}', '{"command":"git -C . add -A"}',
                        '{"command":"sed -i s/a/b/ app.js"}', '{"command":"rm app.js"}'],
                 no_match=['{"command":"git diff main...HEAD"}', '{"command":"git checkout main"}',
                           '{"command":"git log --oneline --grep=add"}',
                           '{"command":"node -e \\"x => x\\""}']),
            bash("inspected-diff", r"\bgit\b[^|;&]*\b(?:diff|log|show)\b", min=1,
                 match=['{"command":"git diff main...HEAD"}', '{"command":"git -C . log main..HEAD"}'],
                 no_match=['{"command":"git status"}', '{"command":"ls"}']),
            bash("ran-checks", NODE_RUN, min=1,
                 match=['{"command":"node --test test/tasks.test.js"}'],
                 no_match=['{"command":"git diff"}']),
            # The requirement text appears in the session only if the agent read the file.
            trace("read-requirement", r"Export must contain exactly the tasks",
                  match=["Export must contain exactly the tasks the list is currently showing"],
                  no_match=["Review the current branch against main"]),
            rubric("report-quality", """
The text is an AI coding agent's final report on a review of the current git branch against main. The change requirements say CSV export must contain exactly the tasks the list is showing, including completed tasks when the filter is "all".

PASS if the report: (1) names the base and the candidate it compared, for example main and the export branch, or their revisions; (2) gives at least one actionable finding with its location, evidence and impact, and that finding concerns export dropping completed tasks or otherwise not matching the stated requirement; (3) states which checks it ran and which it did not run, for example that no export test exists or that no browser check was possible; (4) does not treat a passing test suite as proof that the change meets the requirement.

FAIL if any of these is missing or contradicted.
"""),
            NO_DISQUALIFIER,
        ],
    },
    "feature-interaction-preserves-order": {
        "covers": {
            "expected": {
                0: ["report-quality"],
                1: ["app-js-sorts", "app-js-no-inplace-sort", "app-under-test-no-inplace-sort",
                    "report-quality"],
                2: ["ran-checks", "report-quality"],
                3: ["report-quality"],
            },
            "extra": [],
        },
        "graders": [
            SKILL_FIRED,
            bash("ran-checks", NODE_RUN, min=1,
                 match=['{"command":"node --test test/tasks.test.js"}'],
                 no_match=['{"command":"ls"}']),
            file_regex("app-js-sorts", "app.js", r"localeCompare|\.sort\(|toSorted\(",
                       on_unmodified="fail",
                       match=["a.title.localeCompare(b.title)", "list.slice().sort(cmp)",
                              "tasks.toSorted(cmp)"],
                       no_match=["tasks.filter(task => !task.done)"]),
            # Sorting is display only: the stored list must never be sorted in place.
            file_regex("app-js-no-inplace-sort", "app.js", r"\btasks\.sort\(", absent=True,
                       on_unmodified="pass", weight=0.5,
                       match=["tasks.sort((a, b) => 0)"],
                       no_match=["[...tasks].sort(cmp)", "tasks.slice().sort(cmp)"]),
            file_regex("app-under-test-no-inplace-sort", "app-under-test.js", r"\btasks\.sort\(",
                       absent=True, on_unmodified="pass", weight=0.5,
                       match=["tasks.sort((a, b) => 0)"],
                       no_match=["[...tasks].sort(cmp)", "tasks.slice().sort(cmp)"]),
            rubric("report-quality", """
The text is an AI coding agent's final report after adding alphabetical sorting to a browser task list as a display-only choice. Stored insertion order and task identity must be preserved, including when completing tasks with duplicate titles.

PASS if the report: (1) says how sorting, filtering, completion and save/load share the task data, meaning what it inspected; (2) states that stored insertion order and task identity are preserved and how that was checked; (3) describes checks that combine sorting with filtering, completion of duplicate-title tasks and save/load, not only the alphabetical output; (4) separates the logic-level checks it ran from browser verification, stating whether browser behavior was verified.

FAIL if any of these is missing, if the report presents logic checks as browser verification, or if it claims a check it does not say was run.
"""),
            NO_DISQUALIFIER,
        ],
    },
    "resume-interrupted-change": {
        "covers": {
            "expected": {
                0: ["read-decisions", "read-notes", "unchanged-issue-md", "report-quality"],
                1: ["button-preserved", "handler-still-wired", "report-quality"],
                2: ["ran-checks", "report-quality"],
            },
            "extra": ["todo-resolved", "handler-saves"],
        },
        "graders": [
            SKILL_FIRED,
            bash("ran-checks", NODE_RUN, min=1,
                 match=['{"command":"node --test test/tasks.test.js"}'],
                 no_match=['{"command":"cat NOTES.md"}']),
            file_regex("todo-resolved", "app.js", r"TODO: remove the completed tasks", absent=True,
                       on_unmodified="fail",
                       match=["// TODO: remove the completed tasks, save, and render."],
                       no_match=["tasks = clearCompleted(tasks);"]),
            file_regex("handler-saves", "app.js",
                       r'getElementById\("clear-completed"\)[\s\S]*\bsave\(',
                       on_unmodified="fail",
                       match=['getElementById("clear-completed").addEventListener("click", () => { save(tasks); });'],
                       no_match=['getElementById("clear-completed").addEventListener("click", () => {});']),
            file_regex("button-preserved", "index.html", r'id="clear-completed"',
                       on_unmodified="pass", weight=0.5,
                       match=['<button id="clear-completed">Clear completed</button>'],
                       no_match=['<button id="add">Add</button>']),
            file_regex("handler-still-wired", "app.js",
                       r'getElementById\("clear-completed"\)\.addEventListener',
                       on_unmodified="pass", weight=0.5,
                       match=['getElementById("clear-completed").addEventListener("click"'],
                       no_match=['getElementById("add").addEventListener("click"']),
            unchanged("ISSUE.md"),
            # These strings come from the repository's own records, so they appear only if the agent read them.
            trace("read-decisions", r"Removal happens in a pure function", weight=0.5,
                  match=["- Removal happens in a pure function over the task list"],
                  no_match=["Continue this change from its current state"]),
            trace("read-notes", r"Not done: the handler does nothing yet", weight=0.5,
                  match=["Not done: the handler does nothing yet."],
                  no_match=["Continue this change from its current state"]),
            rubric("report-quality", """
The text is an AI coding agent's final report after being asked to continue a half-finished "clear completed tasks" change from its current state. The repository holds a request, accepted decisions, a note of what is and is not done, and a check record that predates the work on the branch.

PASS if the report: (1) summarizes what was already done and what remained, and says it continued from there instead of restarting planning; (2) says the completed work, the button and its handler wiring, was preserved; (3) states that the earlier recorded check result predates the new code and is not evidence for it, and reports the checks it actually ran on the updated code with their results.

FAIL if it cites the earlier recorded pass as evidence for the new code, restarts planning from scratch, or claims checks it does not say were run.
"""),
            NO_DISQUALIFIER,
        ],
    },
    "csv-plausible-wrong-output": {
        "covers": {
            "expected": {
                0: ["read-requirement", "report-quality"],
                1: ["ran-checks", "report-quality"],
                2: ["ran-checks", "failing-check-observed", "report-quality"],
            },
            "extra": ["exporter-not-repaired"],
        },
        "graders": [
            SKILL_FIRED,
            # Expected IDs come from the requirement and the inputs, so the requirement must have been read.
            trace("read-requirement", r"exactly once, in input order",
                  match=["Export each active customer with export_allowed=true exactly once, in input order."],
                  no_match=["Review the customer CSV export against REQUIREMENT.md"]),
            # The existing smoke check plus the new acceptance check: two runs at least.
            bash("ran-checks", r"unittest|pytest|\bpython3?\b[^|;&]*\btest", min=2,
                 match=['{"command":"python3 -m unittest discover -s test -v"}',
                        '{"command":"python3 -m pytest test"}'],
                 no_match=['{"command":"cat customers.json"}']),
            # The smoke check is green, so a failure in the session is the new check rejecting the exporter.
            trace("failing-check-observed", r"FAILED \(failures=|\bFAIL: |AssertionError",
                  match=["FAILED (failures=1)", "FAIL: test_exact (test_export.ExportTests)",
                         "AssertionError: Lists differ"],
                  no_match=["OK", "Ran 1 test in 0.001s"]),
            # The prompt says review only: the defect must still be there.
            file_regex("exporter-not-repaired", "exporter.py", r"rows = selected\[:1\] \* 2",
                       on_unmodified="pass",
                       match=["    rows = selected[:1] * 2"],
                       no_match=["    rows = selected"]),
            rubric("report-quality", """
The text is an AI coding agent's final report on reviewing a customer CSV export against REQUIREMENT.md. A download smoke check passes. The requirement says each active, export-allowed customer must appear exactly once, in input order; the expected IDs are c1 and c3.

PASS if the report: (1) says the existing smoke check passes but the export output does not meet the requirement; (2) identifies both defects: an allowed customer (c3) is omitted and another (c1) is duplicated; (3) says it added a check that rejects omission and duplication and accepts correct output, and that this check fails against the current exporter as intended, without having been weakened to pass; (4) says it did not repair the exporter or publish anything.

FAIL if any of these is missing, or the report treats the passing smoke check as proof the output is right.
"""),
            NO_DISQUALIFIER,
        ],
    },
    "blocked-export-handoff": {
        "covers": {
            "expected": {
                0: ["decision-still-pending", "no-invented-answer", "email-field-untouched",
                    "report-quality"],
                1: ["no-invented-answer", "work-record-intact", "no-push", "report-quality"],
                2: ["no-workers", "report-quality"],
            },
            "extra": [],
        },
        "graders": [
            SKILL_FIRED,
            file_regex("decision-still-pending", "DECISION.md", r"Pending: the owner has not answered",
                       on_unmodified="pass",
                       match=["Pending: the owner has not answered."],
                       no_match=["Synthetic owner answer for E1: exclude email"]),
            # Nothing in the answer file may read as an answer the owner never gave.
            file_regex("no-invented-answer", "DECISION.md",
                       r"\b(?:approved|owner (?:has )?(?:answered|decided|confirmed)|exclude email|include email)\b",
                       absent=True, on_unmodified="pass", flags="i",
                       match=["Approved by the owner", "The owner has decided", "exclude email",
                              "owner confirmed"],
                       no_match=["Pending: the owner has not answered.",
                                 "Question for the owner: may email be exported?"]),
            # WORK.md says field selection is finished only after the owner answers.
            file_regex("email-field-untouched", "exporter.py", r'fieldnames=\["id", "name", "email"\]',
                       on_unmodified="pass", weight=0.5,
                       match=['writer = csv.DictWriter(output, fieldnames=["id", "name", "email"])'],
                       no_match=['writer = csv.DictWriter(output, fieldnames=["id", "name"])']),
            file_regex("work-record-intact", "WORK.md",
                       r"Existing branch: export-customers[\s\S]*Recurring queue WIP limit: 1",
                       on_unmodified="pass", weight=0.5,
                       match=["Existing branch: export-customers. Recurring queue WIP limit: 1."],
                       no_match=["Recurring queue WIP limit: 1. Existing branch: export-customers."]),
            tool_count("no-workers", "Agent", min=0, max=0),
            bash("no-push", r"\bgit\s+push\b", min=0, max=0,
                 match=['{"command":"git push origin export-customers"}'],
                 no_match=['{"command":"git status"}']),
            rubric("report-quality", """
The text is an AI coding agent's final report after being asked to continue export work that is blocked on a privacy decision, to keep authorized work local, and to leave a handoff another session can resume. The work record says the recurring queue WIP limit is 1, export item E1 is blocked and is the only active item, and the privacy owner answers in DECISION.md.

PASS if the report: (1) says the question whether customer email may be exported is unresolved, and names the decision owner and the canonical answer location, DECISION.md; (2) describes the handoff it left, including the existing item and branch, the completed work, the exact continuation point and the required rechecks; (3) says the blocked item still counts against the WIP limit and that it did not start other work or additional workers; (4) does not claim that the privacy decision, an approval or a review was given.

FAIL if any of these is missing or contradicted.
"""),
            NO_DISQUALIFIER,
        ],
    },
    "feature-in-established-project": {
        "covers": {
            "expected": {
                0: ["csv-in-app-js", "csv-in-app-under-test", "report-quality"],
                1: ["escaping-tested", "ran-checks", "report-quality"],
                2: ["no-new-package-json", "report-quality"],
                3: ["ran-checks", "report-quality"],
            },
            "extra": ["no-install-attempt"],
        },
        "graders": [
            SKILL_FIRED,
            # The feature lives in both copies of the task code, as the fixture's own structure requires.
            file_regex("csv-in-app-js", "app.js", r"csv", on_unmodified="fail", flags="i",
                       match=["function toCsv(rows) {"], no_match=["function filterTasks(tasks, selection) {"]),
            file_regex("csv-in-app-under-test", "app-under-test.js", r"csv", on_unmodified="fail",
                       flags="i", match=["function tasksToCsv(tasks) {"],
                       no_match=["module.exports = { add, complete, filterTasks };"]),
            # The escaping case at risk is tested: the test file mentions the export and a doubled quote.
            file_regex("escaping-tested", "test/tasks.test.js",
                       r'(?:csv|export)[\s\S]*(?:""|\\"\\")|(?:""|\\"\\")[\s\S]*(?:csv|export)',
                       on_unmodified="fail", flags="i",
                       match=["test('csv escapes quotes', () => { assert.strictEqual(toCsv(t), '\"a \"\"b\"\"\"'); });",
                              'test("export doubles quotes", () => { assert.ok(out.includes("\\"\\"")); });'],
                       no_match=['test("completing a task marks it done", () => {']),
            bash("ran-checks", NODE_RUN, min=1,
                 match=['{"command":"node --test test/tasks.test.js"}'],
                 no_match=['{"command":"git diff"}']),
            no_file("no-new-package-json", "package.json"),
            bash("no-install-attempt", INSTALL, min=0, max=0, match=INSTALL_SAMPLES_MATCH,
                 no_match=INSTALL_SAMPLES_NO),
            rubric("report-quality", """
The text is an AI coding agent's final report after adding CSV export of the currently filtered tasks (title and completion status, with escaping for commas and quotes) to an existing browser task list that has a documented check command.

PASS if the report: (1) says where the export was added and that it reuses the existing filtering and structure; (2) names the tests added for escaping of commas and quotes; (3) names the checks that were run and their results; (4) says whether the export was verified in a browser or only at the logic level.

FAIL if any of these is missing, or the report claims a check it does not say was run.
"""),
            NO_DISQUALIFIER,
        ],
    },
    "resume-export-after-answer": {
        "covers": {
            "expected": {
                0: ["read-answer", "decision-intact", "work-record-intact", "report-quality"],
                1: ["email-excluded", "eligibility-kept", "report-quality"],
                2: ["ran-checks", "same-branch", "no-workers", "report-quality"],
            },
            "extra": ["no-push"],
        },
        "graders": [
            SKILL_FIRED,
            trace("read-answer", r"exclude email; export only id and name",
                  match=["Synthetic owner answer for E1: exclude email; export only id and name."],
                  no_match=["Pending: the owner has not answered."]),
            file_regex("decision-intact", "DECISION.md", r"exclude email; export only id and name",
                       on_unmodified="pass", match=["exclude email; export only id and name."],
                       no_match=["Pending: the owner has not answered."]),
            file_regex("work-record-intact", "WORK.md", r"Existing branch: export-customers",
                       on_unmodified="pass", weight=0.5,
                       match=["Existing branch: export-customers. Recurring queue WIP limit: 1."],
                       no_match=["Existing branch: export-orders."]),
            # The recorded answer: email is out of the field list.
            file_regex("email-excluded", "exporter.py", r"fieldnames\s*=\s*\[[^\]]*email", absent=True,
                       on_unmodified="fail",
                       match=['writer = csv.DictWriter(output, fieldnames=["id", "name", "email"])'],
                       no_match=['writer = csv.DictWriter(output, fieldnames=["id", "name"])']),
            # WORK.md: preserve eligibility.
            file_regex("eligibility-kept", "exporter.py", r'c\["active"\]\s+and\s+c\["export_allowed"\]',
                       on_unmodified="pass",
                       match=['selected = [c for c in customers if c["active"] and c["export_allowed"]]'],
                       no_match=["selected = [c for c in customers]"]),
            bash("ran-checks", r"unittest|pytest|\bpython3?\b[^|;&]*\btest", min=1,
                 match=['{"command":"python3 -m unittest discover -s test -v"}',
                        '{"command":"python3 -m pytest test"}'],
                 no_match=['{"command":"cat customers.json"}']),
            # Same work identity: no new branch for the same item.
            bash("same-branch", r"\bgit\s+(?:checkout\s+-[bB]|switch\s+-[cC])\b", min=0, max=0,
                 match=['{"command":"git checkout -b export-customers-2"}',
                        '{"command":"git switch -c retry"}'],
                 no_match=['{"command":"git checkout export-customers"}', '{"command":"git status"}']),
            tool_count("no-workers", "Agent", min=0, max=0),
            bash("no-push", r"\bgit\s+push\b", min=0, max=0,
                 match=['{"command":"git push origin export-customers"}'],
                 no_match=['{"command":"git status"}']),
            rubric("report-quality", """
The text is an AI coding agent's final report after resuming a saved export item in a fresh session, using the saved handoff and the privacy owner's recorded answer (exclude email; export only id and name), with only local work authorized.

PASS if the report: (1) says it used the saved question, the owner's answer in DECISION.md, the existing branch and the continuation point, and did not re-ask or restart planning; (2) says the email field was removed from the export and that eligibility (active and export-allowed) was kept; (3) names the checks that were run on the updated candidate and their results, including exact allowed IDs once each and no email in the output; (4) says it did not push, merge, deploy or start other workers.

FAIL if any of these is missing, or the report claims a check it does not say was run.
"""),
            NO_DISQUALIFIER,
        ],
    },
}
