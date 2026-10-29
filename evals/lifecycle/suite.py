#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Prepare and inspect local incident replays. Never invokes a model or network."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
ARMS = ("baseline", "checklist", "skill")
CHECKLIST = (
    "Establish the current requirement, affected consumers and completed work. "
    "Reproduce the gap, make the smallest shared repair, and preserve unrelated behavior. "
    "Show a regression failing before and passing after the repair. "
    "Recheck affected behavior after changes. Inspect the diff and hand off actual "
    "evidence, the candidate identity and remaining limits."
)
ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8",
       "PYTHONDONTWRITEBYTECODE": "1", "GIT_AUTHOR_DATE": "2000-01-01T00:00:00Z",
       "GIT_COMMITTER_DATE": "2000-01-01T00:00:00Z"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def run(argv, cwd, timeout=30):
    return subprocess.run(argv, cwd=cwd, env=ENV, capture_output=True,
                          text=True, timeout=timeout)


def git(workspace, *args):
    result = run(["git", *args], workspace)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def files(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file()
            and not set(p.relative_to(root).parts) & {".git", "__pycache__", "dist"}}


def digest():
    # Includes fixtures, prompts, grader, protocol and form. Excludes local caches.
    return sha(json.dumps(files(ROOT), sort_keys=True).encode())


def cases():
    return json.loads((ROOT / "cases.json").read_text())["cases"]


def case_for(case_id):
    return next(case for case in cases() if case["id"] == case_id)


def snapshot(workspace):
    hashes = files(workspace)
    return {"head": git(workspace, "rev-parse", "HEAD"),
            "dirty_diff_sha256": sha(git(workspace, "diff", "HEAD", "--binary").encode()),
            "files": hashes,
            "inputs_sha256": sha(json.dumps(hashes, sort_keys=True).encode())}


def articles():
    # All words/content and identities are synthetic. Unequal output expansions
    # reproduce the real failure class without copying website manuscripts.
    return [{"id": key, "title": title, "series": series,
             "source": " ".join(["source"] * source),
             "html": " ".join(["rendered"] * html),
             "markdown": " ".join(["plain"] * markdown)}
            for key, title, series, source, html, markdown in (
                ("intro", "Model basics", "foundations", 201, 401, 201),
                ("operations", "Model operations", "operations", 400, 601, 400),
                ("models", "Choosing models", "foundations", 1, 200, 1))]


def treatment(arm, skill_dir=None):
    if arm == "baseline":
        return "Use the repository guidance. Do not load an external lifecycle skill."
    if arm == "checklist":
        return "Do not load an external lifecycle skill. " + CHECKLIST
    if not skill_dir or not (Path(skill_dir) / "SKILL.md").is_file():
        raise ValueError("skill treatment requires a complete --skill-dir with SKILL.md")
    return "Read and use the full skill at " + str(Path(skill_dir).resolve() / "SKILL.md") + ". Load its relevant references."


def prepare(case_id, destination, arm="baseline", skill_dir=None):
    case = case_for(case_id)
    destination = Path(destination).resolve()
    if arm not in ARMS or (skill_dir is not None and arm != "skill"):
        raise ValueError("only the skill treatment may receive --skill-dir")
    extra = treatment(arm, skill_dir)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("destination must be empty")
    destination.mkdir(parents=True, exist_ok=True)
    workspace = destination / "workspace"
    shutil.copytree(ROOT / "fixture", workspace)
    write_json(workspace / "articles.json", articles())
    write_json(workspace / "aliases.json", {"/intro-old/": "/writing/intro/"})
    (workspace / "ISSUE.md").write_text(case["issue"] + "\n")
    if case_id == "changed-archive-requirement":
        with (workspace / "README.md").open("a") as handle:
            handle.write("\nCurrent archive contract: retain visible series filter buttons.\n")
    if case_id == "mixed-review-unavailable-check":
        (workspace / "REVIEW.md").write_text(
            "Review: changes requested\n\n"
            "R1: The exercise ends in `?.`. Fix the shared punctuation renderer.\n"
            "R2: The contrast audit reports black text on a black panel. "
            "Replace the diagram panel with opaque white to make the figure legible.\n"
            "Assess each finding against the source and requirements.\n")
    git(workspace, "init", "-q", "-b", "main")
    git(workspace, "config", "user.name", "Replay Fixture")
    git(workspace, "config", "user.email", "fixture@example.invalid")
    git(workspace, "add", ".")
    git(workspace, "commit", "-qm", "Synthetic replay starting state")
    if case_id == "resume-versioned-assets":
        # Capture a real smoke check before a subsequent input change. This is
        # historical fixture evidence, never a forged independent approval.
        smoke = run([sys.executable, "-m", "unittest", "-v"], workspace)
        if smoke.returncode:
            raise RuntimeError("historical fixture smoke failed")
        receipt = {"candidate": snapshot(workspace), "command": "python3 -m unittest -v",
                   "exit_code": smoke.returncode, "scope": "existing smoke suite only"}
        write_json(workspace / "previous-check.json", receipt)
        figure = workspace / "assets/diagram.svg"
        figure.write_text(figure.read_text().replace("Proposal then check", "Check then resume"))
        (workspace / "HANDOFF.md").write_text(
            "The HTML URL already includes the asset content digest. Markdown still "
            "uses the old unversioned path. Preserve the existing alias. The diagram "
            "label changed after the previous smoke check. Finish the remaining "
            "format and verify this candidate.\n")
        git(workspace, "switch", "-qc", "feature/asset-versions")
        git(workspace, "add", ".")
        git(workspace, "commit", "-qm", "Leave partial format repair for next session")
    state = {"schema": 1, "case": case_id, "arm": arm, "phase": 1,
             "suite_digest": digest(), "initial": snapshot(workspace),
             "runtime": {"python": sys.version.split()[0],
                         "git": git(workspace, "--version")},
             "treatment_sha256": sha(extra.encode()),
             "skill_dir": str(Path(skill_dir).resolve()) if skill_dir else None,
             "skill_files": files(Path(skill_dir).resolve()) if skill_dir else None}
    write_json(destination / "state.json", state)
    common = ("Work only inside the supplied workspace. Read AGENTS.md and its "
              "routed guidance. No external services or extra agents. "
              "Use only the explicitly supplied treatment; other lifecycle "
              "skill routing is overridden for this evaluation. ")
    for index, prompt in enumerate(case["prompts"], 1):
        (destination / f"prompt-{index}.md").write_text(common + extra + "\n\n" + prompt + "\n")
    return state


def load_state(destination):
    destination = Path(destination).resolve()
    state = json.loads((destination / "state.json").read_text())
    if state["suite_digest"] != digest():
        raise ValueError("suite changed since preparation; create a new experiment")
    return destination, state, destination / "workspace"


def preflight(destination):
    destination, state, workspace = load_state(destination)
    if files(workspace) != state["initial"]["files"]:
        raise ValueError("incomplete or modified starting fixture")
    if state["skill_dir"] and files(Path(state["skill_dir"])) != state["skill_files"]:
        raise ValueError("skill changed after preparation")
    runtime = {"python": sys.version.split()[0], "git": git(workspace, "--version")}
    if runtime != state["runtime"] or sys.version_info[:2] != (3, 12):
        raise ValueError("runtime mismatch: pin one Python 3.12 patch and Git version")
    probe = workspace / "write-probe.tmp"
    branch = "preflight-" + os.urandom(6).hex()
    original = git(workspace, "branch", "--show-current")
    if not original:
        raise ValueError("expected an attached fixture branch")
    try:
        probe.write_text("writable\n")
        if probe.read_text() != "writable\n":
            raise ValueError("write probe failed")
        git(workspace, "switch", "-qc", branch)
        git(workspace, "switch", "-q", original)
        git(workspace, "branch", "-D", branch)
    finally:
        probe.unlink(missing_ok=True)
        if git(workspace, "branch", "--show-current") != original:
            git(workspace, "switch", "-q", original)
    checks = []
    for argv in ([sys.executable, "-m", "unittest", "-v"], [sys.executable, "site_app.py"]):
        result = run(argv, workspace)
        checks.append({"command": argv[1:], "exit_code": result.returncode})
        if result.returncode:
            raise ValueError("preflight smoke/build failed: " + result.stderr)
    result = {"passed": True, "runtime": runtime, "checks": checks,
              "initial_inputs_sha256": state["initial"]["inputs_sha256"]}
    write_json(destination / "preflight.json", result)
    return result


def advance(destination):
    destination, state, workspace = load_state(destination)
    case = case_for(state["case"])
    if state["phase"] != 1 or len(case["prompts"]) != 2:
        raise ValueError("this run cannot advance")
    before = snapshot(workspace)
    # Snapshot includes untracked source hashes, not just HEAD or a worker claim.
    write_json(destination / "phase-one-candidate.json", before)
    if "next_issue" in case:
        (workspace / "ISSUE.md").write_text(case["next_issue"] + "\n")
    else:
        write_json(workspace / "review-service.json", {
            "transport_status": "success", "job_conclusion": "success",
            "candidate_head": before["head"], "reviews_completed": 0,
            "model_usage": {}, "review_verdict": None,
            "message": "Review service unavailable; early exit without review."})
    state["phase"] = 2
    write_json(destination / "state.json", state)
    return {"phase": 2, "prompt": "prompt-2.md", "previous_candidate": before["head"]}


def grade(destination):
    destination, state, workspace = load_state(destination)
    with tempfile.TemporaryDirectory(prefix="lifecycle-grade-") as temporary:
        copy = Path(temporary) / "candidate"
        shutil.copytree(workspace, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", "dist"))
        try:
            result = run([sys.executable, str(ROOT / "oracle.py"), str(copy),
                          state["case"], str(state["phase"])], copy, timeout=20)
            outcome = json.loads(result.stdout)
            if result.returncode not in (0, 1) or not isinstance(outcome, dict):
                raise ValueError("invalid grader output")
        except (subprocess.TimeoutExpired, ValueError) as error:
            outcome = {"passed": False, "checks": [], "execution_error": type(error).__name__}
        protected = ("articles.json", "aliases.json", "assets/diagram.svg")
        for path in protected:
            p = workspace / path
            intact = p.is_file() and sha(p.read_bytes()) == state["initial"]["files"][path]
            outcome.setdefault("checks", []).append({"name": "preserve:" + path, "passed": intact})
        outcome["passed"] = outcome.get("passed", False) and all(c["passed"] for c in outcome["checks"])
        outcome.update({"process_verdict": "unmeasured", "accepted_case": None,
                        "case": state["case"], "phase": state["phase"],
                        "candidate": snapshot(workspace), "suite_digest": state["suite_digest"]})
        return outcome


def plan(seed):
    rng = random.Random(seed)
    blocks = [(case["id"], repeat) for case in cases() for repeat in range(1, 4)]
    rng.shuffle(blocks)
    offsets = {case["id"]: rng.randrange(3) for case in cases()}
    runs = []
    for case_id, repeat in blocks:
        offset = (offsets[case_id] + repeat - 1) % 3
        order = ARMS[offset:] + ARMS[:offset]
        for arm in order:
            runs.append({"case": case_id, "repeat": repeat, "arm": arm,
                         "sessions": len(case_for(case_id)["prompts"])})
    return {"seed": seed, "suite_digest": digest(), "status": "not executed", "runs": runs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("digest")
    p = sub.add_parser("plan")
    p.add_argument("--seed", type=int, default=5772026)
    p = sub.add_parser("prepare")
    p.add_argument("case", choices=[case["id"] for case in cases()])
    p.add_argument("destination", type=Path)
    p.add_argument("--arm", choices=ARMS, default="baseline")
    p.add_argument("--skill-dir", type=Path)
    for name in ("preflight", "advance", "grade", "snapshot"):
        p = sub.add_parser(name)
        p.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "digest":
            result = {"suite_digest": digest()}
        elif args.command == "plan":
            result = plan(args.seed)
        elif args.command == "prepare":
            result = prepare(args.case, args.destination, args.arm, args.skill_dir)
        elif args.command == "snapshot":
            _, _, workspace = load_state(args.destination)
            result = snapshot(workspace)
        else:
            result = globals()[args.command](args.destination)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if args.command == "grade" and not result["passed"] else 0
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
