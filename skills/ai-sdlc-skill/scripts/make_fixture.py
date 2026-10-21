#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Build the starting repository an evaluation case needs, so runs start from the same bytes."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

PAGE = '''<!doctype html>
<title>Task list</title>
<link rel="stylesheet" href="style.css">
<label for="filter">Show</label>
<select id="filter">
  <option value="all">All</option>
  <option value="open">Open</option>
  <option value="done">Completed</option>
</select>
<ul id="tasks"></ul>
<input id="title" aria-label="Task title">
<button id="add">Add</button>
<!--EXTRA_CONTROLS--><script src="app.js"></script>
'''

EXPORT_BUTTON = ('<button id="export">Export CSV</button>\n'
                 '<pre id="export-output"></pre>\n')
CLEAR_BUTTON = '<button id="clear-completed">Clear completed</button>\n'

EXPORT_WIRING = '''  document.getElementById("export").addEventListener("click", () => {
    document.getElementById("export-output").textContent =
      exportTasks(filterTasks(tasks, selection));
  });
'''

STYLE = """body { font-family: system-ui, sans-serif; margin: 2rem; }
li { cursor: pointer; }
li.done { text-decoration: line-through; }
"""

LOGIC = '''const KEY = "tasks";
const FILTER_KEY = "filter";

function load() {
  try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (error) { return []; }
}

function save(tasks) {
  localStorage.setItem(KEY, JSON.stringify(tasks));
}

function nextId(tasks) {
  // Derived from the highest id in use, so removing tasks cannot make a later add collide.
  return tasks.reduce((highest, task) => Math.max(highest, Number(task.id.split(":")[0])), -1) + 1;
}

function add(tasks, title) {
  return tasks.concat([{ id: String(nextId(tasks)) + ":" + title, title: title, done: false }]);
}

function filterTasks(tasks, selection) {
  if (selection === "open") return tasks.filter(task => !task.done);
  if (selection === "done") return tasks.filter(task => task.done);
  return tasks.slice();
}
'''

CORRECT_COMPLETE = '''
function complete(tasks, id) {
  return tasks.map(task => task.id === id ? { ...task, done: true } : task);
}
'''

BUGGY_COMPLETE = '''
function complete(tasks, id) {
  const target = tasks.find(task => task.id === id);
  // Matches on title, so two tasks sharing a title complete together.
  return tasks.map(task => task.title === target.title ? { ...task, done: true } : task);
}
'''

EXPORT = '''
function toCsvRow(values) {
  return values.map(value => '"' + String(value).replace(/"/g, '""') + '"').join(",");
}

function exportTasks(tasks) {
  return [toCsvRow(["title", "done"])].concat(tasks.map(t => toCsvRow([t.title, t.done]))).join("\\n");
}
'''

DUPLICATED_EXPORT = EXPORT + '''
function exportDone(tasks) {
  // Second copy of the same formatting, kept in step by hand.
  const quote = values => values.map(value => '"' + String(value).replace(/"/g, '""') + '"').join(",");
  const done = tasks.filter(task => task.done);
  return [quote(["title", "done"])].concat(done.map(t => quote([t.title, t.done]))).join("\\n");
}
'''

# The branch state's change: export stops honouring the filter. ISSUE.md says it must.
BRANCH_EXPORT = '''
function toCsvRow(values) {
  return values.map(value => '"' + String(value).replace(/"/g, '""') + '"').join(",");
}

function exportTasks(tasks) {
  const open = tasks.filter(task => !task.done);
  return [toCsvRow(["title", "done"])].concat(open.map(t => toCsvRow([t.title, t.done]))).join("\\n");
}
'''

VIEW = '''
function render(tasks, selection) {
  const list = document.getElementById("tasks");
  list.textContent = "";
  for (const task of filterTasks(tasks, selection)) {
    const item = document.createElement("li");
    item.textContent = task.title;
    item.className = task.done ? "done" : "";
    item.dataset.id = task.id;
    list.appendChild(item);
  }
}

function start() {
  let tasks = load();
  let selection = localStorage.getItem(FILTER_KEY) || "all";
  const filter = document.getElementById("filter");
  filter.value = selection;
  filter.addEventListener("change", () => {
    selection = filter.value;
    localStorage.setItem(FILTER_KEY, selection);
    render(tasks, selection);
  });
  document.getElementById("add").addEventListener("click", () => {
    const title = document.getElementById("title");
    if (!title.value) return;
    tasks = add(tasks, title.value);
    title.value = "";
    save(tasks);
    render(tasks, selection);
  });
  document.getElementById("tasks").addEventListener("click", event => {
    if (!event.target.dataset.id) return;
    tasks = complete(tasks, event.target.dataset.id);
    save(tasks);
    render(tasks, selection);
  });
/*EXTRA_WIRING*/  render(tasks, selection);
}

document.addEventListener("DOMContentLoaded", start);
'''

# The half-finished work: the control is rendered and wired, and does nothing yet. NOTES.md
# claims exactly that and no more.
CLEAR_WIRING = '''  document.getElementById("clear-completed").addEventListener("click", () => {
    // TODO: remove the completed tasks, save, and render.
  });
'''

README = """# Task list

A small browser task list kept in local storage. Open `index.html` in a browser. Tasks can be
added, completed by clicking them, and shown filtered by all, open, or completed.

## Checks

    node --test test/tasks.test.js
"""

PREAMBLE = '''const assert = require("node:assert");
const test = require("node:test");
const { add, complete, filterTasks } = require("../app-under-test.js");

test("completing a task marks it done", () => {
  const tasks = add([], "write");
  assert.strictEqual(complete(tasks, tasks[0].id)[0].done, true);
});

test("filtering to open hides completed tasks", () => {
  const tasks = complete(add(add([], "write"), "review"), "0:write");
  assert.deepStrictEqual(filterTasks(tasks, "open").map(t => t.title), ["review"]);
});
'''

# The bug state ships a green suite that never covers distinct tasks sharing a title, so the
# defect is live and undetected. Reproducing it is the case's work, not the fixture's.
DISTINCT_TASKS_TEST = '''
test("completing one task leaves a same-titled task alone", () => {
  const tasks = add(add([], "write"), "write");
  const completed = complete(tasks, tasks[0].id);
  assert.strictEqual(completed[0].done, true);
  assert.strictEqual(completed[1].done, false);
});
'''

INSTRUCTIONS = """# Project instructions

This project is a React application with a PostgreSQL backend. Run `npm run build`
and `npm test` before every commit. All state lives in Redux.
"""

EXPORT_REQUIREMENT = """# Requirement: CSV export

Export must contain exactly the tasks the list is currently showing, so what a person sees and
what they get are the same. With the filter on "all", every task is exported, completed ones
included.

Acceptance examples:

- Filter "all", two tasks, one completed: both appear in the export.
- Filter "open": only the open tasks appear.
- A title containing a comma or a quote stays one field and survives a round trip.

Out of scope: choosing the file name, and any change to how tasks are stored.
"""

RESUME_ISSUE = """# Request: clear completed tasks

Let someone remove every completed task in one action.

Acceptance examples:

- With two completed tasks and one open, the action leaves only the open task.
- With no completed tasks, the action changes nothing.
- The remaining tasks survive a reload.

Out of scope: undo, and any change to the filter.
"""

RESUME_DECISIONS = """# Accepted decisions

- Removal happens in a pure function over the task list, tested without a browser.
- The stored task list is rewritten once, after the removal, using the existing save helper.
- No new dependency for this change.

Proposed, not accepted: asking for confirmation before removing.
"""

# The recorded run names the revision before the branch work, so an agent that reuses it is
# reporting a check that never saw the current code.
RESUME_CHECKS = """# Recorded checks

Revision: {revision}
Command: node --test test/tasks.test.js
Result: passed, {checks} checks

This record predates the work on this branch. It is evidence for the revision named above and
for nothing later.
"""

RESUME_NOTE = """# Clear completed: work in progress

Done: the Clear completed button is on the page and a click handler is attached to it.
Not done: the handler does nothing yet. The removal itself, the save, the re-render, and a
check covering the acceptance examples are all still open.
"""


# Multi-stage states. They share one set of project rules, so a case can test whether the rules
# survive a change that has several stages and a few traps.
PROJECT_RULES = """# Project instructions

- Run `node --test test/tasks.test.js` before every commit.
- Every behavior change adds or updates a test in `test/tasks.test.js`.
- `app.js` and `app-under-test.js` carry the same task logic. The tests load the second one, the
  browser loads the first, so a change to one goes into both.
- Work on a branch named for the change. Do not push or merge.
- Record the last check in `docs/check-results.md`: the revision it ran on, the command and the
  result. A record is evidence for the revision it names and for nothing later.
- A decision that changes scope goes into `docs/decisions.md` before the code that depends on it.
"""

STANDING_DECISIONS = """# Accepted decisions

- The stored task list keeps insertion order. Anything that only changes what is shown happens
  when rendering, never to the stored list.
- Tasks are identified by `id`, not by title. Two tasks may share a title.
- No new dependency.
"""

SEARCH_ISSUE = """# Request: search the task list

Add a text input with the id `search` above the list. It narrows the visible tasks to those whose
title contains the typed text.

Acceptance examples:

- Typing "wr" shows "write" and "Write report", and hides "review". Matching ignores case.
- The search and the Show filter apply together: with Show set to Open, only open tasks that match
  are listed.
- With the search box empty, the list is what it was before this change.
- With two tasks titled "write", completing the second one from a searched list completes only
  the second one.
- Reloading the page clears the search text. The stored tasks are unaffected.

Out of scope: highlighting the match, and saving the search text.
"""

REVIEW_ISSUE = EXPORT_REQUIREMENT + """
Added by the owner: rows are exported in the order the list shows them.
"""

REVIEW_FINDINGS = """# Review: export-filtered

Status: changes requested
Reviewer: synthetic reviewer (no approval has been given)

## F1 Completed tasks are missing from the export
With Show set to "all", `exportTasks` still returns only open tasks. ISSUE.md says completed tasks
are exported when the filter is "all".

## F2 The export test does not cover the case that broke
`test/tasks.test.js` checks one open task. Nothing covers a completed task or the "all" filter.

## F3 Sort the exported rows by title
Alphabetical rows would be easier to read.
"""

REVIEW_STALE_CHECKS = """# Recorded checks

Revision: {revision}
Command: node --test test/tasks.test.js
Result: passed, {checks} checks

Recorded before this review. It is evidence for the revision named above and for nothing later.
"""

EXPORT_TEST = '''
test("export lists an open task", () => {
  const { exportTasks } = require("../app-under-test.js");
  const tasks = add([], "write");
  assert.ok(exportTasks(filterTasks(tasks, "open")).includes("write"));
});
'''

CHANGE_ISSUE = """# Request: clear completed tasks

Let someone remove every completed task in one action.

Acceptance examples:

- With two completed tasks and one open, the action leaves only the open task.
- With no completed tasks, the action changes nothing.
- The remaining tasks survive a reload.

Out of scope: undo, and any change to the filter.

## Update from the owner, after work started

Removal must be undoable. After clearing, an Undo button restores the removed tasks, in their
original positions, until the page is reloaded. Undo is now in scope. A reload makes the removal
permanent.
"""

CHANGE_DECISIONS = """# Accepted decisions

- Removal happens in a pure function over the task list, tested without a browser.
- The stored task list is rewritten once, after the removal, using the existing save helper.
- Removal is permanent. Nothing is kept for restoring.
- No new dependency for this change.
"""

CHANGE_CHECKS = """# Recorded checks

Revision: {revision}
Command: node --test test/tasks.test.js
Result: passed, {checks} checks

This record covers the work as it was built to the first version of the request.
"""

CLEAR_LOGIC = '''
function clearCompleted(tasks) {
  return tasks.filter(task => !task.done);
}
'''

CLEAR_DONE_WIRING = '''  document.getElementById("clear-completed").addEventListener("click", () => {
    tasks = clearCompleted(tasks);
    save(tasks);
    render(tasks, selection);
  });
'''

CLEAR_TEST = '''
test("clearing completed keeps only open tasks", () => {
  const { clearCompleted } = require("../app-under-test.js");
  const tasks = complete(add(add([], "write"), "review"), "0:write");
  assert.deepStrictEqual(clearCompleted(tasks).map(t => t.title), ["review"]);
});
'''


CUSTOMER_REQUIREMENT = """# Customer export
Export each active customer with export_allowed=true exactly once, in input order.
Columns are id and name. Inputs and names here are synthetic.
For customers.json the expected IDs are c1 and c3, once each; c2 and c4 are excluded.
No remote services or browser are needed: python3 -m unittest discover -s test -v.
"""
CUSTOMERS = [
    {"id": "c1", "name": "Alpha", "active": True, "export_allowed": True, "email": "alpha@example.invalid"},
    {"id": "c2", "name": "Beta", "active": False, "export_allowed": True, "email": "beta@example.invalid"},
    {"id": "c3", "name": "Gamma", "active": True, "export_allowed": True, "email": "gamma@example.invalid"},
    {"id": "c4", "name": "Delta", "active": True, "export_allowed": False, "email": "delta@example.invalid"},
]
CUSTOMER_EXPORT = '''import csv
import io


def export_customers(customers):
    selected = [c for c in customers if c["active"] and c["export_allowed"]]
    rows = selected[:1] * 2
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "name"], extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
'''
CUSTOMER_SMOKE = '''import json
from pathlib import Path
import unittest
from exporter import export_customers


class DownloadTests(unittest.TestCase):
    def test_download(self):
        customers = json.loads(Path("customers.json").read_text())
        self.assertTrue(export_customers(customers).startswith("id,name"))
'''
BLOCKED_WORK = """# Export item E1
Existing branch: export-customers. Recurring queue WIP limit: 1.
E1 is the only active item; it is blocked. E2 is queued, not started. No other worker owns E1.
Question: may customer email be included in the export?
Decision owner: product privacy owner. Canonical answer location: DECISION.md.
Completed: synthetic inputs, CSV serializer and download smoke check.
Continuation: after the owner answers, finish exporter.py field selection; preserve eligibility.
Rechecks: exact allowed IDs once each, CSV fields/privacy, and the existing smoke check on the updated candidate.
Prior smoke pass predates the next implementation; it establishes no new privacy decision.
"""


def customer_fixture(root, state):
    write(root, "customers.json", json.dumps(CUSTOMERS, indent=2) + "\n")
    requirement = CUSTOMER_REQUIREMENT
    exporter = CUSTOMER_EXPORT
    if state != "customer-export":
        requirement = requirement.replace("Columns are id and name.", "Columns include id and name; inclusion of email awaits the privacy owner's answer in DECISION.md.")
        exporter = exporter.replace("rows = selected[:1] * 2", "rows = selected")
        write(root, "WORK.md", BLOCKED_WORK)
        answer = "# Privacy decision\nPending: the owner has not answered.\n"
        if state == "privacy-answered":
            answer = "# Privacy decision\nSynthetic owner answer for E1: exclude email; export only id and name. Continue the existing branch and verify before handoff.\n"
        write(root, "DECISION.md", answer)
        exporter = exporter.replace('fieldnames=["id", "name"]', 'fieldnames=["id", "name", "email"]')
    write(root, "REQUIREMENT.md", requirement)
    write(root, "README.md", "# Synthetic customer export\nRun python3 -m unittest discover -s test -v from this directory.\n")
    write(root, "exporter.py", exporter)
    write(root, "test/test_download.py", CUSTOMER_SMOKE)

STATES = {
    "customer-export": "Synthetic customer CSV with a green download check, an omission and a duplicate.",
    "privacy-blocked": "Synthetic export item with an unanswered privacy decision and a resumable WIP handoff.",
    "privacy-answered": "The same export handoff with the privacy owner answer available to a fresh session.",
    "undocumented": "The application with no README, no instruction file, no tests, and no CSV export.",
    "documented": "The application with a README and a passing check command, and no CSV export yet.",
    "initialized": "The documented application plus an instruction file whose claims the code does not support.",
    "bug": "The documented application with the duplicate-title completion defect, and a green suite that never covers it.",
    "duplication": "The application with CSV formatting already duplicated across two export functions.",
    "branch": "The application with CSV export, its stated requirement, and a review branch that changes what it exports.",
    "rules-feature": "The documented application with project rules, standing decisions and a search request, on main.",
    "review-round": "The application with CSV export on a review branch, a reviewer's three findings and an older check record.",
    "changed-requirement": "A clear-completed branch built to the first version of the request, after the owner widened the request to include undo.",
    "interrupted": "The documented application with a half-finished clear-completed change on a branch, its request, accepted decisions, and a check record from the earlier revision.",
}


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=60)


def git_head(root):
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                   timeout=30).decode().strip()


def write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def application(root, complete_body=CORRECT_COMPLETE, export_body="", controls="", wiring="", tests=True,
                extra_logic="", extra_names=()):
    # Export is what the feature case is asked to build, so most states start without it.
    exported = ["add", "complete", "filterTasks"] + (["exportTasks"] if export_body else []) + list(extra_names)
    logic = LOGIC + complete_body + export_body + extra_logic
    write(root, "index.html", PAGE.replace("<!--EXTRA_CONTROLS-->", controls))
    write(root, "style.css", STYLE)
    write(root, "app.js", logic + VIEW.replace("/*EXTRA_WIRING*/", wiring))
    write(root, "app-under-test.js", logic + "\nmodule.exports = { %s };\n" % ", ".join(exported))
    if tests:
        write(root, "test/tasks.test.js",
              PREAMBLE + ("" if complete_body is BUGGY_COMPLETE else DISTINCT_TASKS_TEST))


def build(root, state):
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ValueError("the destination must be empty")
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Evaluation Fixture")
    git(root, "config", "user.email", "fixture@example.invalid")

    if state in {"customer-export", "privacy-blocked", "privacy-answered"}:
        customer_fixture(root, state)
        git(root, "add", "-A")
        git(root, "commit", "-qm", "Synthetic customer export fixture")
        if state.startswith("privacy-"):
            git(root, "checkout", "-q", "-b", "export-customers")
        return git_head(root)

    if state == "bug":
        application(root, complete_body=BUGGY_COMPLETE)
    elif state == "duplication":
        application(root, export_body=DUPLICATED_EXPORT, controls=EXPORT_BUTTON, wiring=EXPORT_WIRING)
    elif state == "branch":
        application(root, export_body=EXPORT, controls=EXPORT_BUTTON, wiring=EXPORT_WIRING)
        write(root, "ISSUE.md", EXPORT_REQUIREMENT)
    elif state == "undocumented":
        # The init case must be able to observe a repository that genuinely has no checks.
        application(root, tests=False)
    else:
        application(root)
    if state != "undocumented":
        write(root, "README.md", README)
    if state == "initialized":
        write(root, "AGENTS.md", INSTRUCTIONS)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "Task list fixture")

    if state == "branch":
        git(root, "checkout", "-q", "-b", "export-filtered")
        application(root, export_body=BRANCH_EXPORT, controls=EXPORT_BUTTON, wiring=EXPORT_WIRING)
        git(root, "add", "-A")
        git(root, "commit", "-qm", "Export only open tasks")
    if state in {"rules-feature", "review-round", "changed-requirement"}:
        write(root, "AGENTS.md", PROJECT_RULES)
        write(root, "docs/decisions.md", STANDING_DECISIONS if state == "rules-feature" else "")
        if state == "rules-feature":
            write(root, "ISSUE.md", SEARCH_ISSUE)
            git(root, "add", "-A")
            git(root, "commit", "-qm", "Add project rules and the search request")
        elif state == "review-round":
            base = git_head(root)
            git(root, "checkout", "-q", "-b", "export-filtered")
            application(root, export_body=BRANCH_EXPORT, controls=EXPORT_BUTTON, wiring=EXPORT_WIRING)
            tests_path = root / "test" / "tasks.test.js"
            tests_path.write_text(tests_path.read_text() + EXPORT_TEST)
            write(root, "ISSUE.md", REVIEW_ISSUE)
            write(root, "docs/decisions.md", STANDING_DECISIONS)
            write(root, "REVIEW.md", REVIEW_FINDINGS)
            git(root, "add", "-A")
            git(root, "commit", "-qm", "Export only open tasks")
            counted = (root / "test" / "tasks.test.js").read_text().count("\ntest(")
            write(root, "docs/check-results.md", REVIEW_STALE_CHECKS.format(revision=base, checks=counted - 1))
            git(root, "add", "-A")
            git(root, "commit", "-qm", "Record the checks that predate the review")
        else:
            settled = git_head(root)
            git(root, "checkout", "-q", "-b", "clear-completed")
            application(root, controls=CLEAR_BUTTON, wiring=CLEAR_DONE_WIRING, extra_logic=CLEAR_LOGIC,
                        extra_names=["clearCompleted"])
            tests_path = root / "test" / "tasks.test.js"
            tests_path.write_text(tests_path.read_text() + CLEAR_TEST)
            write(root, "ISSUE.md", CHANGE_ISSUE)
            write(root, "docs/decisions.md", CHANGE_DECISIONS)
            git(root, "add", "-A")
            git(root, "commit", "-qm", "Clear completed tasks, first version of the request")
            built = git_head(root)
            counted = (root / "test" / "tasks.test.js").read_text().count("\ntest(")
            write(root, "docs/check-results.md", CHANGE_CHECKS.format(revision=built, checks=counted))
            git(root, "add", "-A")
            git(root, "commit", "-qm", "Record the checks for the first version")
        return git_head(root)
    if state == "interrupted":
        settled = git_head(root)
        git(root, "checkout", "-q", "-b", "clear-completed")
        application(root, controls=CLEAR_BUTTON, wiring=CLEAR_WIRING)
        write(root, "ISSUE.md", RESUME_ISSUE)
        write(root, "docs/decisions.md", RESUME_DECISIONS)
        # Count the checks that file actually declares, so the record cannot claim a wrong number.
        recorded = (root / "test" / "tasks.test.js").read_text().count("\ntest(")
        write(root, "docs/check-results.md",
              RESUME_CHECKS.format(revision=settled, checks=recorded))
        write(root, "NOTES.md", RESUME_NOTE)
        git(root, "add", "-A")
        git(root, "commit", "-qm", "Add the clear-completed control")
    return git_head(root)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, choices=sorted(STATES))
    parser.add_argument("--into", required=True, help="an empty or absent directory to build in")
    args = parser.parse_args(argv)
    if os.name != "posix":
        print(json.dumps({"status": "invalid", "reason": "POSIX runtime required"}))
        return 2
    try:
        root = Path(args.into).resolve()
        head = build(root, args.state)
    except (OSError, ValueError, subprocess.SubprocessError):
        print(json.dumps({"status": "invalid", "reason": "requires Git and an empty destination"}))
        return 2
    print(json.dumps({"status": "built", "state": args.state, "path": str(root),
                      "revision": head, "description": STATES[args.state]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

