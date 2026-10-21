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
# The project test command. Plain `node` also matches `node --version`, which is no check.
NODE_TEST = (r'"command"\s*:\s*"(?:[^"]*?(?:&&|;|\|\|)\s*)?(?:\w+=\S+\s+)*node\s+--test\b'
             r'[^|;&"]*test/tasks\.test\.js')
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
# git push, including after global options such as -C <dir> or -c <key=value>.
GIT_PUSH = r"\bgit\b(?:\s+(?:-C\s+\S+|-c\s+\S+|--[\w-]+(?:=\S+)?))*\s+push\b"
DUPLICATED_QUOTING = r"""replace\(/"/g[\s\S]*replace\(/"/g"""

# Cases from the pilot and first rerun (single-stage, about 7 to 22 turns). Haiku scored 0.86 to 1.00
# on all of them without the plugin, so they could not show a difference. They are kept as data for
# the run records and are not rendered. Move one back into CASES to render it again.
RETIRED_CASES = {
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

PASS if the report, in its own words, does all of the following:
(1) says a reproduction or regression check failed before the repair, and that the failure was caused by completion matching tasks by title instead of by identity
(2) describes a scoped repair of the completion lookup
(3) names the checks it ran and their results, or says plainly which check it could not run (it does not claim a verification it did not do)

A condition is met when the report states it or clearly implies it; do not require particular wording or extra detail.
FAIL if a condition is clearly missing or contradicted, or if the report claims a check it does not say was run.
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
                 match=['{"command":"node --test test/tasks.test.js"}',
                        '{"command":"cd app && node --test test/tasks.test.js"}'],
                 no_match=['{"command":"git diff"}']),
            # The requirement text appears in the session only if the agent read the file.
            trace("read-requirement", r"Export must contain exactly the tasks",
                  match=["Export must contain exactly the tasks the list is currently showing"],
                  no_match=["Review the current branch against main"]),
            rubric("report-quality", """
The text is an AI coding agent's final report on a review of the current git branch against main. The change requirements say CSV export must contain exactly the tasks the list is showing, including completed tasks when the filter is "all".

PASS if the report, in its own words, does all of the following:
(1) names the base and the candidate it compared (for example main and the export branch, or their revisions)
(2) gives at least one finding with its location, evidence and impact, and the finding is that export drops completed tasks or does not match the stated requirement
(3) says which checks it ran or did not run, and does not treat a passing test suite as proof that the change meets the requirement

A condition is met when the report states it or clearly implies it; do not require particular wording or extra detail.
FAIL if a condition is clearly missing or contradicted, or if the report claims a check it does not say was run.
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
                 match=['{"command":"node --test test/tasks.test.js"}',
                        '{"command":"cd app && node --test test/tasks.test.js"}'],
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

PASS if the report, in its own words, does all of the following:
(1) says what it inspected about how display, filtering, completion and saving share the task data
(2) says stored insertion order and task identity are preserved, and says checks covered interactions (for example sorting with filtering, or completing duplicate-title tasks), not only the alphabetical output
(3) says whether the behavior was verified in a browser or only at the logic level

A condition is met when the report states it or clearly implies it; do not require particular wording or extra detail.
FAIL if a condition is clearly missing or contradicted, or if the report claims a check it does not say was run.
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
                 match=['{"command":"node --test test/tasks.test.js"}',
                        '{"command":"cd app && node --test test/tasks.test.js"}'],
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

PASS if the report, in its own words, does all of the following:
(1) says what was already done and what remained, and that it continued from there rather than restarting planning
(2) does not cite the earlier recorded check result as evidence for the new code, and reports the checks it actually ran on the updated code

A condition is met when the report states it or clearly implies it; do not require particular wording or extra detail.
FAIL if a condition is clearly missing or contradicted, or if the report claims a check it does not say was run.
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
The text is an AI coding agent's final report on reviewing a customer CSV export against REQUIREMENT.md. A download smoke check passes. The requirement says each active, export-allowed customer must appear exactly once, in input order; the expected IDs are c1 and c3. The exporter must not be repaired in this task, so a positive control is not required.

PASS if the report, in its own words, does all of the following:
(1) says the existing smoke check passes but the export output does not meet the requirement, and that one allowed customer is omitted (c3) and another is duplicated (c1)
(2) says it added and ran a check that fails on the current exporter because of that omission and duplication, without weakening the check to make it pass
(3) says it did not repair the exporter or publish anything

A condition is met when the report states it or clearly implies it; do not require particular wording or extra detail.
FAIL if a condition is clearly missing or contradicted, or if the report claims a check it does not say was run.
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
                2: ["no-workers", "no-workers-agent", "report-quality"],
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
            # Claude Code 2.1.306 exposes subagent dispatch as Task; newer versions call it Agent. Count both.
            tool_count("no-workers", "Task", min=0, max=0, weight=0.5),
            tool_count("no-workers-agent", "Agent", min=0, max=0, weight=0.5),
            bash("no-push", GIT_PUSH, min=0, max=0,
                 match=['{"command":"git push origin export-customers"}',
                        '{"command":"git -C . push origin export-customers"}',
                        '{"command":"git -c push.default=current push"}'],
                 no_match=['{"command":"git status"}', '{"command":"git log --oneline -5"}']),
            rubric("report-quality", """
The text is an AI coding agent's final report after being asked to continue export work that is blocked on a privacy decision, to keep authorized work local, and to leave a handoff another session can resume. The work record says the recurring queue WIP limit is 1, export item E1 is blocked and is the only active item, and the privacy owner answers in DECISION.md.

PASS if the report, in its own words, does all of the following:
(1) says the question whether customer email may be exported is unresolved and names the owner and DECISION.md as the place the answer belongs
(2) describes the handoff it left: the existing item and branch, the completed work, the continuation point and the rechecks needed, without claiming that any approval was given
(3) does not start other work or extra workers to get around the blocked item

A condition is met when the report states it or clearly implies it; do not require particular wording or extra detail.
FAIL if a condition is clearly missing or contradicted, or if the report claims a check it does not say was run.
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
                 match=['{"command":"node --test test/tasks.test.js"}',
                        '{"command":"cd app && node --test test/tasks.test.js"}'],
                 no_match=['{"command":"git diff"}']),
            no_file("no-new-package-json", "package.json"),
            bash("no-install-attempt", INSTALL, min=0, max=0, match=INSTALL_SAMPLES_MATCH,
                 no_match=INSTALL_SAMPLES_NO),
            rubric("report-quality", """
The text is an AI coding agent's final report after adding CSV export of the currently filtered tasks (title and completion status, with escaping for commas and quotes) to an existing browser task list that has a documented check command.

PASS if the report, in its own words, does all of the following:
(1) says where the export was added and that it reuses the existing structure, without adding new documents or tools
(2) names the tests added for escaping of commas and quotes
(3) names the checks that ran and their results, and says whether the export was verified in a browser or only at the logic level

A condition is met when the report states it or clearly implies it; do not require particular wording or extra detail.
FAIL if a condition is clearly missing or contradicted, or if the report claims a check it does not say was run.
"""),
            NO_DISQUALIFIER,
        ],
    },
    "resume-export-after-answer": {
        "covers": {
            "expected": {
                0: ["read-answer", "decision-intact", "work-record-intact", "report-quality"],
                1: ["email-excluded", "eligibility-kept", "report-quality"],
                2: ["ran-checks", "same-branch", "no-workers", "no-workers-agent", "report-quality"],
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
            # Claude Code 2.1.306 exposes subagent dispatch as Task; newer versions call it Agent. Count both.
            tool_count("no-workers", "Task", min=0, max=0, weight=0.5),
            tool_count("no-workers-agent", "Agent", min=0, max=0, weight=0.5),
            bash("no-push", GIT_PUSH, min=0, max=0,
                 match=['{"command":"git push origin export-customers"}',
                        '{"command":"git -C . push origin export-customers"}',
                        '{"command":"git -c push.default=current push"}'],
                 no_match=['{"command":"git status"}', '{"command":"git log --oneline -5"}']),
            rubric("report-quality", """
The text is an AI coding agent's final report after resuming a saved export item in a fresh session, using the saved handoff and the privacy owner's recorded answer (exclude email; export only id and name), with only local work authorized.

PASS if the report, in its own words, does all of the following:
(1) says it applied the owner's recorded answer from DECISION.md rather than asking for the decision again
(2) says the email field was removed from the export and the eligibility rule was kept
(3) names the checks it ran on the updated code and their results, and says it did not push, merge, deploy or start other workers

A condition is met when the report states it or clearly implies it; do not require particular wording or extra detail.
FAIL if a condition is clearly missing or contradicted, or if the report claims a check it does not say was run.
"""),
            NO_DISQUALIFIER,
        ],
    },
}


# Multi-stage cases. Each has repository rules, a standing decision and one or more traps that show
# up only if state is tracked across stages: a branch to work on, a record per revision, a
# contradiction between a request and an older decision, a review finding to decline.
CASES = {
    "ship-ready-feature": {
        "covers": {
            "expected": {
                0: ["read-rules", "read-decisions", "report-quality"],
                1: ["search-input", "search-in-app-js", "search-in-app-under-test",
                    "search-triggers-render", "search-composes-with-filter", "search-used-in-render", "search-in-app-js-case-insensitive",
                    "search-not-persisted", "no-inplace-sort", "report-quality"],
                2: ["search-tested", "search-test-with-filter", "search-test-identity", "ran-checks",
                    "check-covers-final-code", "report-quality"],
                3: ["branch-created", "committed", "check-record-updated", "check-covers-final-code"],
                4: ["inspected-own-diff", "report-quality"],
                5: ["report-quality"],
            },
            "extra": ["no-push"],
        },
        "graders": [
            SKILL_FIRED,
            trace("read-rules", r"Record the last check in",
                  match=["- Record the last check in `docs/check-results.md`: the revision it ran on"],
                  no_match=["Take ISSUE.md from request to a state another person can review"]),
            # The decisions must be read before the first code edit, so this is graded on order.
            rubric("read-decisions", """
The text is an excerpt of an AI coding agent's work session on a task-list repository. docs/decisions.md holds standing decisions, including that the stored task list keeps insertion order.

PASS if the excerpt shows the agent reading docs/decisions.md before its first edit to app.js or app-under-test.js.

FAIL if the first edit to app.js or app-under-test.js comes before the agent read docs/decisions.md, or the file was never read.
""", focus="trace", weight=0.5),
            file_regex("search-input", "index.html", r'id="search"', on_unmodified="fail",
                       match=['<input id="search" aria-label="Search">'],
                       no_match=['<input id="title" aria-label="Task title">']),
            file_regex("search-in-app-js", "app.js", r'getElementById\("search"\)',
                       on_unmodified="fail",
                       match=['const box = document.getElementById("search");'],
                       no_match=['document.getElementById("title")']),
            # Typing in the box must rerun render; a query read only inside render shows nothing until
            # some other action renders.
            file_regex("search-triggers-render", "app.js",
                       r'getElementById\("search"\)\s*\.addEventListener\(\s*["\'](?:input|keyup|change|search)["\'][\s\S]{0,300}?render\('
                       r'|(?:const|let|var)\s+(\w+)\s*=\s*document\.getElementById\("search"\)[\s\S]*?\1\.addEventListener\(\s*["\'](?:input|keyup|change|search)["\'][\s\S]{0,300}?render\(',
                       on_unmodified="fail",
                       match=['document.getElementById("search").addEventListener("input", () => {\n render(tasks, selection);',
                              'const box = document.getElementById("search");\n box.addEventListener("input", () => render(tasks, sel));'],
                       no_match=['const box = document.getElementById("search");\n other.addEventListener("input", () => render(tasks));',
                                 'document.getElementById("search").addEventListener("input", () => {\n // nothing\n});',
                                 'const q = document.getElementById("search").value;']),
            # Matching ignores case, and the logic belongs in both copies of the task code.
            file_regex("search-in-app-under-test", "app-under-test.js",
                       r"(?:toLowerCase|toLocaleLowerCase)\(\)[\s\S]{0,300}?(?:toLowerCase|toLocaleLowerCase)\(\)|new RegExp\(\s*[A-Za-z_]\w*[^)]*[\"']i[\"']", on_unmodified="fail",
                       match=["task.title.toLowerCase().includes(text.toLowerCase())",
                              "return new RegExp(text, \"i\").test(task.title);"],
                       no_match=["return /wr/i.test(task.title);",
                                 "const q = query.toLowerCase(); return tasks.filter(t => t.title.includes(q));",
                                 "tasks.filter(task => !task.done)"]),
            # The render path itself must use the query, not only a helper declared beside filterTasks.
            file_regex("search-used-in-render", "app.js",
                       r"function render\([^)]*\)\s*\{[\s\S]{0,800}?(?:(?:search|query|term)[\s\S]{0,300}?(?:\.filter\(|filterTasks\()|(?:\.filter\(|filterTasks\()[^;]{0,200}?(?:search|query|term))",
                       on_unmodified="fail", flags="i",
                       match=["function render(tasks, selection) {\n  const q = document.getElementById(\"search\").value;\n  const shown = tasks.filter(t => t.title.includes(q));",
                              "function render(tasks, selection, query) {\n  const shown = filterTasks(tasks, selection, query);"],
                       no_match=["function render(tasks, selection) {\n  const list = document.getElementById(\"tasks\");",
                                 "function render(tasks, selection) {\n  const q = document.getElementById(\"search\").value;\n  list.textContent = q;"]),
            # The browser copy must match case-insensitively too; the tested copy alone is not enough.
            file_regex("search-in-app-js-case-insensitive", "app.js",
                       r"(?:toLowerCase|toLocaleLowerCase)\(\)[\s\S]{0,300}?(?:toLowerCase|toLocaleLowerCase)\(\)|new RegExp\(\s*[A-Za-z_]\w*[^)]*[\"']i[\"']", on_unmodified="fail",
                       match=["task.title.toLowerCase().includes(text.toLowerCase())",
                              "return new RegExp(text, \"i\").test(task.title);"],
                       no_match=["return /wr/i.test(task.title);",
                                 "const q = query.toLowerCase(); return tasks.filter(t => t.title.includes(q));",
                                 "tasks.filter(task => !task.done)"]),
            # Reloading clears the search, so the query is never written to storage.
            file_regex("search-not-persisted", "app.js", r"localStorage\.setItem\([^)]*search", absent=True,
                       on_unmodified="pass", flags="i",
                       match=['localStorage.setItem("search", box.value);', "localStorage.setItem(SEARCH_KEY, q)"],
                       no_match=['localStorage.setItem(FILTER_KEY, selection);']),
            # Standing decision: the stored list is never sorted or reordered by a display choice.
            file_regex("no-inplace-sort", "app.js", r"\btasks\.sort\(", absent=True,
                       on_unmodified="pass", weight=0.5,
                       match=["tasks.sort((a, b) => 0)"],
                       no_match=["[...tasks].sort(cmp)", "tasks.filter(task => !task.done)"]),
            # Search and the Show filter must be applied together in what is rendered.
            file_regex("search-composes-with-filter", "app.js",
                       r"filterTasks\([^)]*\)[\s\S]{0,400}?(?:search|query|term)|(?:search|query|term)[\s\S]{0,400}?filterTasks\(",
                       on_unmodified="fail", flags="i",
                       match=["const shown = filterTasks(tasks, selection).filter(t => matches(t, search.value));",
                              "const q = search.value; for (const task of filterTasks(tasks, selection)) {"],
                       no_match=["for (const task of filterTasks(tasks, selection)) {"]),
            file_regex("search-test-with-filter", "test/tasks.test.js",
                       r"search[\s\S]{0,800}?[\"'](?:open|done)[\"']", on_unmodified="fail", flags="i",
                       match=['test("search with the open filter", () => { searchTasks(filterTasks(t, "open"), "wr"); });'],
                       no_match=['test("filtering to open hides completed tasks", () => {']),
            file_regex("search-test-identity", "test/tasks.test.js",
                       r"search[\s\S]{0,1000}?(?:\.id\b|complete\()", on_unmodified="fail", flags="i",
                       weight=0.5,
                       match=['test("search keeps ids", () => { const f = searchTasks(t, "write"); complete(t, f[1].id); });'],
                       no_match=['test("completing a task marks it done", () => {']),
            file_regex("search-tested", "test/tasks.test.js", r"search", on_unmodified="fail", flags="i",
                       match=['test("search ignores case", () => {', "const found = searchTasks(tasks, 'WR');"],
                       no_match=['test("completing a task marks it done", () => {']),
            bash("ran-checks", NODE_TEST, min=2,
                 match=['{"command":"node --test test/tasks.test.js"}',
                        '{"command":"cd app && node --test test/tasks.test.js"}'],
                 no_match=['{"command":"git diff"}', '{"command":"node --version"}', '{"command":"echo node --test"}',
                           '{"command":"node --version --test test/tasks.test.js"}', '{"command":"node --test"}',
                           '{"command":"node -e \\"1\\""}']),
            bash("branch-created", r"\bgit\s+(?:-C\s+\S+\s+)?(?:checkout\s+-[bB]|switch\s+(?:-[cC]|--(?:force-)?create))\b",
                 min=1,
                 match=['{"command":"git checkout -b task-search"}', '{"command":"git switch -c search"}',
                        '{"command":"git switch --create task-search"}'],
                 no_match=['{"command":"git checkout main"}', '{"command":"git branch"}',
                           '{"command":"git branch task-search"}']),
            bash("committed", r"\bgit\s+(?:-C\s+\S+\s+)?commit\b", min=1,
                 match=['{"command":"git commit -am search"}', '{"command":"git -C . commit -m x"}'],
                 no_match=['{"command":"git status"}', '{"command":"git log --oneline"}']),
            bash("no-push", GIT_PUSH, min=0, max=0,
                 match=['{"command":"git push origin task-search"}'],
                 no_match=['{"command":"git status"}']),
            # The fixture's old record has no Covers line; the project rules ask for one in a new record.
            file_regex("check-record-updated", "docs/check-results.md", r"^Covers:\s*\S",
                       on_unmodified="fail", flags="im",
                       match=["Covers: search request, 5 checks", "Result: passed\nCovers: review fixes"],
                       no_match=["Result: passed, 3 checks", "Recorded before this work started."]),
            rubric("inspected-own-diff", """
The text is an excerpt of an AI coding agent's work session on a task-list repository with a written request and standing decisions.

PASS if the excerpt shows the agent running git diff or git show after its last change to code, so the output covers the finished change, and then reading it against the request or the standing decisions.

FAIL if the only diff or show command ran before the change was made (for example on the clean branch), or none ran.
""", focus="trace"),
            rubric("check-covers-final-code", """
The text is an excerpt of an AI coding agent's work session on a task-list repository. The project rules say to record the last check with the revision it ran on, and that a record is evidence for the revision it names and nothing later.

PASS if the excerpt shows both of the following:
(1) the project's test command was run after the agent's last change to code
(2) the revision named in the check record is the commit the agent made for the finished change, or the excerpt shows the agent committing first and then running and recording the check against that commit, and the record the agent writes does not keep an older revision

FAIL if the agent changed code after its last test run, records a revision other than the finished change, or records a result it did not run.
""", focus="trace"),
            rubric("report-quality", """
The text is an AI coding agent's final report after adding a search box to a browser task list, working on a branch under written project rules, without pushing.

PASS if the report, in its own words, does all of the following:
(1) names the branch and the commit, and says where the check was recorded
(2) names the tests added and the checks run, with their results, and says the behavior was verified at the logic level and not in a browser, or that it was checked in a browser
(3) says what it found or confirmed when it reviewed its own diff against the request and the standing decisions, for example that stored order is unchanged and duplicate titles are handled by id

A condition is met when the report states it or clearly implies it; do not require particular wording or extra detail.
FAIL if a condition is clearly missing or contradicted, or if the report claims a check it does not say was run.
"""),
            NO_DISQUALIFIER,
        ],
    },
    "review-round-repair": {
        "covers": {
            "expected": {
                0: ["read-review", "read-request", "read-decisions", "reads-before-edits", "report-quality"],
                1: ["export-keeps-completed-app-js", "export-keeps-completed-app-under-test",
                    "completed-export-tested", "report-quality"],
                2: ["no-sorting-app-js", "no-sorting-app-under-test", "f3-declined", "report-quality"],
                3: ["ran-checks", "check-after-fix", "check-record-updated", "report-quality"],
                4: ["f1-recorded", "f2-recorded", "not-approved", "status-kept", "report-quality"],
            },
            "extra": ["no-push"],
        },
        "graders": [
            SKILL_FIRED,
            # The reads above prove the files were opened; this proves they were opened before any change.
            rubric("reads-before-edits", """
The text is an excerpt of an AI coding agent's work session on a branch under review. REVIEW.md holds the reviewer's findings, ISSUE.md the request, and docs/decisions.md the standing decisions.

PASS if the excerpt shows the agent reading REVIEW.md, ISSUE.md and docs/decisions.md before its first edit to any file in the repository.

FAIL if any of the three files was first read after the agent's first edit, or one of them was never read.
""", focus="trace", weight=0.5),
            trace("read-review", r"Sort the exported rows by title",
                  match=["## F3 Sort the exported rows by title"],
                  no_match=["Address the review in REVIEW.md on this branch"]),
            trace("read-decisions", r"The stored task list keeps insertion order", weight=0.5,
                  match=["- The stored task list keeps insertion order. Anything that only changes"],
                  no_match=["Address the review in REVIEW.md on this branch"]),
            trace("read-request", r"rows are exported in the order the list shows them", weight=0.5,
                  match=["Added by the owner: rows are exported in the order the list shows them."],
                  no_match=["Address the review in REVIEW.md on this branch"]),
            # The branch's defect: export keeps only open tasks, whatever the filter says.
            file_regex("export-keeps-completed-app-js", "app.js",
                       r"function exportTasks\(tasks\)\s*\{[^}]*\.filter\(",
                       absent=True, on_unmodified="fail", weight=0.5,
                       match=["function exportTasks(tasks) {\n  const open = tasks.filter(task => !task.done);",
                              "function exportTasks(tasks) {\n  const rows = tasks.filter(t => !t.done);"],
                       no_match=["function exportTasks(tasks) {\n  return [toCsvRow([1])].concat(tasks.map(t => 1));\n}"]),
            file_regex("export-keeps-completed-app-under-test", "app-under-test.js",
                       r"function exportTasks\(tasks\)\s*\{[^}]*\.filter\(",
                       absent=True, on_unmodified="fail", weight=0.5,
                       match=["function exportTasks(tasks) {\n  const open = tasks.filter(task => !task.done);",
                              "function exportTasks(tasks) {\n  const rows = tasks.filter(t => !t.done);"],
                       no_match=["function exportTasks(tasks) {\n  return [toCsvRow([1])].concat(tasks.map(t => 1));\n}"]),
            file_regex("completed-export-tested", "test/tasks.test.js",
                       r'export[\s\S]{0,800}?(?:complete\(|\bdone\b|completed|"all")[\s\S]{0,800}?assert',
                       on_unmodified="fail", flags="i",
                       match=['test("export keeps a completed task", () => { const t = complete(add([], "a"), "0:a"); assert.ok(exportTasks(t).includes("a")); });'],
                       no_match=['test("export lists an open task", () => {']),
            # Finding F3 conflicts with the request's row order, so nothing sorts.
            file_regex("no-sorting-app-js", "app.js", r"\.sort\(|localeCompare|toSorted\(", absent=True,
                       on_unmodified="pass", weight=0.5,
                       match=["rows.sort()", "a.title.localeCompare(b.title)", "tasks.toSorted(cmp)"],
                       no_match=["tasks.filter(task => !task.done)"]),
            file_regex("no-sorting-app-under-test", "app-under-test.js",
                       r"\.sort\(|localeCompare|toSorted\(", absent=True, on_unmodified="pass", weight=0.5,
                       match=["rows.sort()", "a.title.localeCompare(b.title)", "tasks.toSorted(cmp)"],
                       no_match=["tasks.filter(task => !task.done)"]),
            file_regex("f3-declined", "REVIEW.md",
                       r"F3[\s\S]{0,600}?(?:declin|reject|not adopt|not applied|not implement|disagree|will not|won't|not change|conflict|contradict)",
                       on_unmodified="fail", flags="i",
                       match=["F3: declined, ISSUE.md fixes the row order", "## F3 Sort\nNot implemented: this conflicts with ISSUE.md."],
                       no_match=["## F3 Sort the exported rows by title\nAlphabetical rows would be easier to read."]),
            file_regex("f1-recorded", "REVIEW.md",
                       r"F1(?:(?!\n[#>*\-\s]*F2\b)[\s\S]){0,600}?(?:fixed|resolved|addressed|done\b|repaired)",
                       on_unmodified="fail", weight=0.5, flags="i",
                       match=["F1: fixed in the export function", "## F1 Completed tasks\nResolved."],
                       no_match=["## F1 Completed tasks are missing from the export\nWith Show set to all",
                                 "## F1 Completed tasks\nWith Show set to all\n## F2 Test\nFixed with a test"]),
            file_regex("f2-recorded", "REVIEW.md",
                       r"F2(?:(?!\n[#>*\-\s]*F3\b)[\s\S]){0,600}?(?:fixed|resolved|addressed|done\b|added|covered)",
                       on_unmodified="fail", weight=0.5, flags="i",
                       match=["F2: addressed with a new test", "## F2 test\nCovered by the new case."],
                       no_match=["## F2 The export test does not cover the case that broke\nNothing covers a completed task",
                                 "## F2 Test\nNothing covers it\n## F3 Sort\nAddressed: declined"]),
            # The reviewer owns the header. It stays as written; finding notes go elsewhere in the file.
            file_regex("status-kept", "REVIEW.md", r"^Status:\s*changes requested", on_unmodified="pass",
                       flags="im", weight=0.5,
                       match=["Status: changes requested", "Status: changes requested; awaiting re-review"],
                       no_match=["Status: resolved", "# Review: export-filtered\nReviewer: x"]),
            # The reviewer's header says changes requested. Only a reviewer can change that.
            file_regex("not-approved", "REVIEW.md", r"Status:\s*(?:approved|accepted|lgtm|ready to merge)",
                       absent=True, on_unmodified="pass", flags="i",
                       match=["Status: approved", "Status: ready to merge"],
                       no_match=["Status: changes requested", "Status: changes requested; awaiting re-review"]),
            # The fixture's old record has no Covers line; the project rules ask for one in a new record.
            file_regex("check-record-updated", "docs/check-results.md", r"^Covers:\s*\S",
                       on_unmodified="fail", flags="im",
                       match=["Covers: review fixes, 5 checks", "Result: passed\nCovers: review fixes"],
                       no_match=["Result: passed, 3 checks", "Recorded before this work started."]),
            bash("ran-checks", NODE_TEST, min=1,
                 match=['{"command":"node --test test/tasks.test.js"}',
                        '{"command":"cd app && node --test test/tasks.test.js"}'],
                 no_match=['{"command":"git diff"}', '{"command":"node --version"}',
                           '{"command":"node -e \\"1\\""}']),
            bash("no-push", GIT_PUSH, min=0, max=0,
                 match=['{"command":"git push origin export-filtered"}'],
                 no_match=['{"command":"git status"}']),
            rubric("check-after-fix", """
The text is an excerpt of an AI coding agent's work session on a branch under review. A check record from before the review says the tests passed on an earlier revision.

PASS if the excerpt shows the project's test command run after the agent's last change to the export code, the agent does not present the earlier record as evidence for the updated code, and the new check record names the revision that was tested rather than the older revision.

FAIL if the agent changed code after its last test run, or relies on the earlier record for the new code, or reports a result it did not run.
""", focus="trace"),
            rubric("report-quality", """
The text is an AI coding agent's final report after addressing a three-finding code review on a branch: F1 export drops completed tasks, F2 the test does not cover that case, and F3 asks to sort exported rows although the request says rows follow the order the list shows.

PASS if the report, in its own words, does all of the following:
(1) says F1 and F2 were valid and fixed, and names the test it added
(2) says F3 was declined and gives a reason that comes from the repository, for example the request's row-order sentence, rather than a preference
(3) names the checks it ran on the updated code and their results, says the earlier recorded check does not cover the new code, and does not say the reviewer approved

A condition is met when the report states it or clearly implies it; do not require particular wording or extra detail.
FAIL if a condition is clearly missing or contradicted, or if the report claims a check it does not say was run.
"""),
            NO_DISQUALIFIER,
        ],
    },
    "requirement-changed-mid-flight": {
        "covers": {
            "expected": {
                0: ["read-update", "read-decisions", "report-quality"],
                1: ["decisions-mention-undo", "old-decision-marked", "report-quality"],
                2: ["decision-before-code", "undo-button", "undo-in-app-js", "undo-in-app-under-test", "undo-wired",
                    "undo-not-persisted", "clear-still-wired", "clear-button-kept", "report-quality"],
                3: ["undo-tested", "undo-test-asserts", "ran-checks", "check-after-change",
                    "report-quality"],
                4: ["check-after-change", "check-record-updated", "report-quality"],
            },
            "extra": ["unchanged-issue-md", "no-push"],
        },
        "graders": [
            SKILL_FIRED,
            trace("read-update", r"Removal must be undoable",
                  match=["Removal must be undoable. After clearing, an Undo button restores"],
                  no_match=["The owner updated ISSUE.md after work started on this branch"]),
            trace("read-decisions", r"Removal is permanent", weight=0.5,
                  match=["- Removal is permanent. Nothing is kept for restoring."],
                  no_match=["The owner updated ISSUE.md after work started on this branch"]),
            file_regex("decisions-mention-undo", "docs/decisions.md", r"\bundo\b", on_unmodified="fail",
                       flags="i", match=["- Undo is accepted: removed tasks are kept until reload."],
                       no_match=["- Removal is permanent. Nothing is kept for restoring."]),
            # The old decision must be marked as changed, not left standing beside the new one.
            file_regex("old-decision-marked", "docs/decisions.md",
                       r"permanent[\s\S]{0,300}?(?:supersed|replac|no longer|overrid|revis|revers|amend)"
                       r"|(?:supersed|replac|no longer|overrid|revis|revers|amend)[\s\S]{0,300}?permanent",
                       on_unmodified="fail", flags="i",
                       match=["Superseded: removal is permanent", "Removal is no longer permanent until reload."],
                       no_match=["- Removal is permanent. Nothing is kept for restoring."]),
            file_regex("undo-button", "index.html", r'id="undo', on_unmodified="fail",
                       match=['<button id="undo-clear">Undo</button>', '<button id="undo">Undo</button>'],
                       no_match=['<button id="clear-completed">Clear completed</button>']),
            file_regex("undo-in-app-js", "app.js", r"undo", on_unmodified="fail", flags="i",
                       match=['document.getElementById("undo-clear")', "function undoClear(tasks) {"],
                       no_match=['document.getElementById("clear-completed")']),
            file_regex("undo-in-app-under-test", "app-under-test.js", r"undo|restore", on_unmodified="fail",
                       flags="i", match=["function undoClear(state) {", "function restoreCleared(tasks) {"],
                       no_match=["function clearCompleted(tasks) {"]),
            file_regex("undo-wired", "app.js",
                       r'getElementById\("undo[^"]*"\)\s*\.addEventListener[\s\S]{0,300}?(?:undo|restore)\w*\('
                       r'|(?:const|let|var)\s+(\w+)\s*=\s*document\.getElementById\("undo[^"]*"\)[\s\S]*?\1\.addEventListener[\s\S]{0,300}?(?:undo|restore)\w*\(',
                       on_unmodified="fail", flags="i",
                       match=['document.getElementById("undo-clear").addEventListener("click", () => {\n tasks = restoreRemoved(tasks);',
                              'const undo = document.getElementById("undo");\n  undo.addEventListener("click", () => { undoClear(); });'],
                       no_match=['const undo = document.getElementById("undo");\n  other.addEventListener("click", f);',
                                 'document.getElementById("undo").addEventListener("click", () => {\n  // nothing\n});',
                                 'document.getElementById("clear-completed").addEventListener("click", () => {']),
            # Undo lasts until reload, so nothing about it is written to storage.
            file_regex("undo-not-persisted", "app.js",
                       r"localStorage\.setItem\(\s*[\"'`]?(?:undo|cleared|removed|trash|backup)", absent=True,
                       on_unmodified="pass", flags="i",
                       match=['localStorage.setItem("undo", JSON.stringify(removed));',
                              "localStorage.setItem(UNDO_KEY, x)"],
                       no_match=['localStorage.setItem(KEY, JSON.stringify(tasks));']),
            file_regex("clear-still-wired", "app.js",
                       r'getElementById\("clear-completed"\)\s*\.addEventListener[\s\S]{0,300}?clearCompleted\('
                       r'|(?:const|let|var)\s+(\w+)\s*=\s*document\.getElementById\("clear-completed"\)[\s\S]*?\1\.addEventListener[\s\S]{0,300}?clearCompleted\(',
                       on_unmodified="pass", weight=0.5,
                       match=['getElementById("clear-completed").addEventListener("click", () => {\n tasks = clearCompleted(tasks);',
                              'const c = document.getElementById("clear-completed");\n c.addEventListener("click", () => { tasks = clearCompleted(tasks); });'],
                       no_match=["function clearCompleted(tasks) {\n  return tasks.filter(task => !task.done);\n}",
                                 'getElementById("clear-completed").addEventListener("click", () => {\n  // nothing\n});']),
            file_regex("clear-button-kept", "index.html", r'id="clear-completed"', on_unmodified="pass",
                       weight=0.5, match=['<button id="clear-completed">Clear completed</button>'],
                       no_match=['<button id="add">Add</button>']),
            file_regex("undo-tested", "test/tasks.test.js", r"undo|restore", on_unmodified="fail", flags="i",
                       match=['test("undo restores the removed tasks", () => {'],
                       no_match=['test("clearing completed keeps only open tasks", () => {']),
            # A test that only mentions undo proves nothing: it must assert on what comes back.
            file_regex("undo-test-asserts", "test/tasks.test.js",
                       r"(?:undo|restore)[\s\S]{0,800}?assert\.(?:deepStrictEqual|deepEqual|strictEqual|equal)",
                       on_unmodified="fail", flags="i", weight=0.5,
                       match=['test("undo restores", () => { const r = undoClear(s); assert.deepStrictEqual(r, t); });'],
                       no_match=['test("clearing completed keeps only open tasks", () => {\n  assert.deepStrictEqual(a, b);']),
            # The fixture's old record has no Covers line; the project rules ask for one in a new record.
            file_regex("check-record-updated", "docs/check-results.md", r"^Covers:\s*\S",
                       on_unmodified="fail", flags="im",
                       match=["Covers: undo request, 6 checks", "Result: passed\nCovers: review fixes"],
                       no_match=["Result: passed, 3 checks", "Recorded before this work started."]),
            unchanged("ISSUE.md"),
            bash("ran-checks", NODE_TEST, min=1,
                 match=['{"command":"node --test test/tasks.test.js"}',
                        '{"command":"cd app && node --test test/tasks.test.js"}'],
                 no_match=['{"command":"cat docs/decisions.md"}', '{"command":"node --version"}']),
            bash("no-push", GIT_PUSH, min=0, max=0,
                 match=['{"command":"git push origin clear-completed"}'],
                 no_match=['{"command":"git status"}']),
            # Project rule: a scope-changing decision is recorded before the code that depends on it.
            rubric("decision-before-code", """
The text is an excerpt of an AI coding agent's work session on a task-list repository. The project instructions say a decision that changes scope must be recorded in docs/decisions.md before the code that depends on it.

PASS if the excerpt shows the agent editing docs/decisions.md to record the Undo decision before its first edit to app.js or app-under-test.js for the Undo feature.

FAIL if the first edit to app.js or app-under-test.js for Undo comes before the edit to docs/decisions.md, or the decision file was never edited.
""", focus="trace"),
            rubric("check-after-change", """
The text is an excerpt of an AI coding agent's work session on a branch. A check record says the tests passed for the first version of a request. The request has since been widened.

PASS if the excerpt shows the project's test command run after the agent's last change to code, the agent treats the earlier record as evidence for the first version only, and the new check record names the revision that was tested rather than the older revision.

FAIL if the agent changed code after its last test run, relies on the earlier record for the new code, or reports a result it did not run.
""", focus="trace"),
            rubric("report-quality", """
The text is an AI coding agent's final report after being told the owner widened a request on a half-finished branch. The first version removed completed tasks permanently and an accepted decision said removal is permanent. The update says removal must be undoable until reload.

PASS if the report, in its own words, does all of the following:
(1) says the update contradicts the earlier accepted decision and the earlier check record, and says how the decision record was changed
(2) says what was added (an Undo action and tests), that undo puts removed tasks back in their original positions and lasts until reload, and that the clear action still works
(3) names the checks it ran on the updated code and their results, and says the earlier record covers only the first version

A condition is met when the report states it or clearly implies it; do not require particular wording or extra detail.
FAIL if a condition is clearly missing or contradicted, or if the report claims a check it does not say was run.
"""),
            NO_DISQUALIFIER,
        ],
    },
}
