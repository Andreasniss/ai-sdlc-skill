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

EXPORT_BUTTON = '<button id="export">Export CSV</button>\n'
CLEAR_BUTTON = '<button id="clear-completed">Clear completed</button>\n'

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

function add(tasks, title) {
  return tasks.concat([{ id: String(tasks.length) + ":" + title, title: title, done: false }]);
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

STATES = {
    "undocumented": "The application with no README, no instruction file, no tests, and no CSV export.",
    "documented": "The application with a README and a passing check command, and no CSV export yet.",
    "initialized": "The documented application plus an instruction file whose claims the code does not support.",
    "bug": "The documented application with the duplicate-title completion defect, and a green suite that never covers it.",
    "duplication": "The application with CSV formatting already duplicated across two export functions.",
    "branch": "The application with CSV export, its stated requirement, and a review branch that changes what it exports.",
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


def application(root, complete_body=CORRECT_COMPLETE, export_body="", controls="", wiring="", tests=True):
    # Export is what the feature case is asked to build, so most states start without it.
    exported = ["add", "complete", "filterTasks"] + (["exportTasks"] if export_body else [])
    logic = LOGIC + complete_body + export_body
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

    if state == "bug":
        application(root, complete_body=BUGGY_COMPLETE)
    elif state == "duplication":
        application(root, export_body=DUPLICATED_EXPORT, controls=EXPORT_BUTTON)
    elif state == "branch":
        application(root, export_body=EXPORT, controls=EXPORT_BUTTON)
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
        application(root, export_body=BRANCH_EXPORT, controls=EXPORT_BUTTON)
        git(root, "add", "-A")
        git(root, "commit", "-qm", "Export only open tasks")
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
