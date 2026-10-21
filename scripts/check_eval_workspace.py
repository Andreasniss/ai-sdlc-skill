#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Probe fixture writes and Git branching without changing the fixture's contents.

Run after scaffolding, or manually from the evaluated workspace inside the host
sandbox. A successful outside-sandbox probe cannot validate an inside-sandbox mount.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args],
                                   stderr=subprocess.PIPE, text=True, timeout=30).strip()


def probe(root):
    root = Path(root).resolve()
    stage = "worktree-write"
    branch = None
    original = None
    try:
        # Test create/delete as well as writes to existing fixture files. Do not
        # chmod files: a failing permission boundary must remain observable.
        with tempfile.NamedTemporaryFile(dir=root, prefix=".eval-write-probe-") as handle:
            handle.write(b"probe\n")
            handle.flush()
            os.fsync(handle.fileno())
        for path in sorted(root.rglob("*")):
            if path.is_file() and ".git" not in path.relative_to(root).parts:
                with path.open("r+b") as handle:
                    first = handle.read(1)
                    handle.seek(0)
                    handle.write(first)
                    handle.flush()
        stage = "git-switch"
        original = git(root, "symbolic-ref", "--short", "HEAD")
        branch = "eval-write-probe-" + uuid.uuid4().hex
        git(root, "switch", "-c", branch)
        git(root, "switch", original)
        git(root, "branch", "-D", branch)
        branch = None
        return {"status": "writable", "scope": "current-process-only"}
    except (OSError, subprocess.SubprocessError) as error:
        # No raw stderr or paths in a publishable diagnostic. Inspect raw host
        # logs locally when classifying EROFS versus permissions or Git failures.
        return {"status": "blocked", "stage": stage,
                "error_type": type(error).__name__, "errno": getattr(error, "errno", None)}
    finally:
        if branch and original:
            try:
                git(root, "switch", original)
                git(root, "branch", "-D", branch)
            except (OSError, subprocess.SubprocessError):
                pass  # The blocked result is not a successful setup or cleanup.


def main():
    result = probe(Path.cwd())
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "writable" else 2


if __name__ == "__main__":
    sys.exit(main())
