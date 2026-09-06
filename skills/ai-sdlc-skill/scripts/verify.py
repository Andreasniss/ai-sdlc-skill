#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Run reviewed repository checks; report observations, never authorization."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], stderr=subprocess.DEVNULL, timeout=30
    ).decode().strip()


def identity(root):
    head = git(root, "rev-parse", "HEAD")
    if git(root, "status", "--porcelain", "--untracked-files=all", "--ignore-submodules=none"):
        raise ValueError("candidate is not clean")
    return head


def configuration(root, filename):
    supplied = Path(filename)
    if not supplied.is_absolute():
        supplied = root / supplied
    path = supplied.resolve(strict=True)
    relative = path.relative_to(root)
    # Reject symlinks in every path component, including within the repository.
    current = root
    for part in supplied.absolute().relative_to(root).parts:
        current /= part
        if current.is_symlink():
            raise ValueError("configuration path contains a symlink")
    if not path.is_file():
        raise ValueError("configuration is not a regular file")
    git(root, "ls-files", "--error-unmatch", "--", str(relative))
    raw = path.read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict) or set(data) != {"checks"}:
        raise ValueError("configuration requires only checks")
    checks = data["checks"]
    if not isinstance(checks, list) or not checks:
        raise ValueError("checks must be a non-empty list")
    names = set()
    for check in checks:
        if not isinstance(check, dict) or set(check) - {"name", "argv", "timeout_seconds"}:
            raise ValueError("invalid check fields")
        name, argv = check.get("name"), check.get("argv")
        if not isinstance(name, str) or not name or len(name) > 80 or not all(c.isalnum() or c in " _-." for c in name) or name in names:
            raise ValueError("check names must be unique short labels")
        names.add(name)
        if not isinstance(argv, list) or not argv or not all(isinstance(a, str) and a and "\0" not in a for a in argv):
            raise ValueError("argv must contain non-empty strings")
        timeout = check.get("timeout_seconds", 300)
        if type(timeout) is not int or not 1 <= timeout <= 1800:
            raise ValueError("timeout must be an integer between 1 and 1800")
    return checks, hashlib.sha256(raw).hexdigest()


def run_check(root, check):
    result = {"name": check["name"], "status": "failed", "returncode": None}
    try:
        with subprocess.Popen(check["argv"], cwd=root, stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              start_new_session=True) as process:
            try:
                result["returncode"] = process.wait(timeout=check.get("timeout_seconds", 300))
                result["status"] = "passed" if result["returncode"] == 0 else "failed"
            except subprocess.TimeoutExpired:
                result["status"] = "timeout"
            finally:
                # Prevent ordinary descendants surviving a timed-out check.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
    except OSError:
        result["status"] = "unavailable"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args(argv)
    if os.name != "posix":
        print(json.dumps({"status": "invalid", "reason": "POSIX runtime required"}))
        return 2
    try:
        root = Path(git(Path(args.repo).resolve(), "rev-parse", "--show-toplevel")).resolve()
        head = identity(root)
        checks, digest = configuration(root, args.config)
    except (OSError, ValueError, subprocess.SubprocessError):
        print(json.dumps({"status": "invalid", "reason": "requires a clean committed repository and valid tracked configuration"}))
        return 2
    report = {"schema": 1, "revision": head, "config_sha256": digest,
              "started_at": datetime.now(timezone.utc).isoformat(), "checks": [], "status": "failed"}
    unchanged = True
    for check in checks:
        result = run_check(root, check)
        report["checks"].append(result)
        try:
            unchanged = identity(root) == head and configuration(root, args.config)[1] == digest
        except (OSError, ValueError, subprocess.SubprocessError):
            unchanged = False
        if result["status"] != "passed" or not unchanged:
            break
    report["candidate_unchanged"] = unchanged
    if unchanged and len(report["checks"]) == len(checks) and all(r["status"] == "passed" for r in report["checks"]):
        report["status"] = "passed"
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
