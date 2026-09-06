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

APP = '''<!doctype html>
<title>Task list</title>
<link rel="stylesheet" href="style.css">
<ul id="tasks"></ul>
<input id="title" aria-label="Task title">
<button id="add">Add</button>
{export_button}<script src="app.js"></script>
'''

EXPORT_BUTTON = '''<button id="export">Export CSV</button>
'''

STYLE = "body { font-family: system-ui, sans-serif; margin: 2rem; }\n.done { text-decoration: line-through; }\n"

CORE = '''const KEY = "tasks";

function load() {
  try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (error) { return []; }
}

function save(tasks) {
  localStorage.setItem(KEY, JSON.stringify(tasks));
}

function add(tasks, title) {
  tasks.push({ id: String(Date.now()) + Math.random(), title: title, done: false });
  return tasks;
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

DUPLICATED_EXPORT = '''
function toCsvRow(values) {
  return values.map(value => '"' + String(value).replace(/"/g, '""') + '"').join(",");
}

function exportTasks(tasks) {
  return [toCsvRow(["title", "done"])].concat(tasks.map(t => toCsvRow([t.title, t.done]))).join("\\n");
}

function exportDone(tasks) {
  // Second copy of the same formatting, kept in step by hand.
  const quote = values => values.map(value => '"' + String(value).replace(/"/g, '""') + '"').join(",");
  const done = tasks.filter(task => task.done);
  return [quote(["title", "done"])].concat(done.map(t => quote([t.title, t.done]))).join("\\n");
}
'''

README = """# Task list

A small browser task list kept in local storage. Open `index.html` in a browser.

## Checks

    node --test test/tasks.test.js
"""

PREAMBLE = '''const assert = require("node:assert");
const test = require("node:test");
const { add, complete } = require("../app-under-test.js");

test("completing a task marks it done", () => {
  const tasks = add([], "write");
  assert.strictEqual(complete(tasks, tasks[0].id)[0].done, true);
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

RESUME_NOTE = """# Filter work in progress

Done: the filter control renders and stores the selection.
Next: apply the selection when listing tasks, and cover it with a check.
"""

RESUME_ISSUE = """# Request: filter the task list

Let someone show all tasks, only open ones, or only completed ones.

Acceptance examples:

- Selecting "open" hides completed tasks and keeps the rest in their existing order.
- Selecting "all" restores every task.
- The selection survives a reload.

Out of scope: sorting, search, and any change to how tasks are stored.
"""

RESUME_DECISIONS = """# Accepted decisions

- The selection lives in local storage under its own key, not mixed into the task records.
- Filtering happens when the list is rendered; stored task data is never rewritten.
- No new dependency for this change.

Proposed, not accepted: replacing the buttons with a dropdown.
"""

# The recorded run names the revision before the branch work, so an agent that reuses it is
# reporting a check that never saw the current code.
RESUME_CHECKS = """# Recorded checks

Revision: {revision}
Command: node --test test/tasks.test.js
Result: passed, 2 checks

This record predates the filter work on this branch. It is evidence for the revision named
above and for nothing later.
"""

STATES = {
    "undocumented": "The application with no README and no instruction file, and no CSV export.",
    "documented": "The application with a README and a passing check command, and no CSV export yet.",
    "initialized": "The documented application plus an instruction file whose claims the code does not support.",
    "bug": "The documented application with the duplicate-title completion defect, and a green suite that never covers it.",
    "duplication": "The application with CSV formatting already duplicated across two export functions.",
    "branch": "The application with CSV export and a review branch that changes what it exports.",
    "interrupted": "The documented application with a half-finished filter change on a branch, its request, accepted decisions, and a check record from the earlier revision.",
}


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=60)


def write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def application(root, complete_body=CORRECT_COMPLETE, export_body=""):
    # Export is what the feature case is asked to build, so most states start without it.
    exported = ["add", "complete"] + (["exportTasks"] if export_body else [])
    write(root, "index.html", APP.format(export_button=EXPORT_BUTTON if export_body else ""))
    write(root, "style.css", STYLE)
    write(root, "app.js", CORE + complete_body + export_body)
    write(root, "app-under-test.js", CORE + complete_body + export_body +
          "\nmodule.exports = { %s };\n" % ", ".join(exported))
    write(root, "test/tasks.test.js", PREAMBLE + ("" if complete_body is BUGGY_COMPLETE else DISTINCT_TASKS_TEST))


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
        application(root, export_body=DUPLICATED_EXPORT)
    elif state == "branch":
        application(root, export_body=EXPORT)
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
        write(root, "app.js", (root / "app.js").read_text().replace(
            "tasks.map(t => toCsvRow([t.title, t.done]))",
            "tasks.filter(t => !t.done).map(t => toCsvRow([t.title, t.done]))"))
        git(root, "add", "-A")
        git(root, "commit", "-qm", "Export only open tasks")
    if state == "interrupted":
        settled = git_head(root)
        git(root, "checkout", "-q", "-b", "filter-tasks")
        write(root, "ISSUE.md", RESUME_ISSUE)
        write(root, "docs/decisions.md", RESUME_DECISIONS)
        write(root, "docs/check-results.md", RESUME_CHECKS.format(revision=settled))
        write(root, "NOTES.md", RESUME_NOTE)
        write(root, "filter.js", "function renderFilter(selected) { return selected; }\n")
        git(root, "add", "-A")
        git(root, "commit", "-qm", "Render the filter control")
    return git_head(root)


def git_head(root):
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                   timeout=30).decode().strip()


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
