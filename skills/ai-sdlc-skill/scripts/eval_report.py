#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Validate a recorded evaluation run against a case set; report observations, never authorization."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

OUTCOMES = {"passed", "failed"}
CASE_FIELDS = {"id", "starting_point", "fixture", "prompt", "expected", "watch_for"}
RESULT_FIELDS = {"id", "outcome", "evidence", "disqualifiers_observed"}
RUN_FIELDS = {"schema", "host", "model", "skill_revision", "cases_sha256", "results"}


def label(value, limit=200):
    return isinstance(value, str) and value.strip() and len(value) <= limit


def load(path):
    raw = Path(path).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def cases(document):
    if not isinstance(document, dict) or set(document) != {"schema", "disqualifiers", "fixtures", "cases"}:
        raise ValueError("case set requires schema, disqualifiers, fixtures and cases")
    if document["schema"] != 1:
        raise ValueError("unsupported case schema")
    known = document["disqualifiers"]
    if not isinstance(known, dict) or not known or not all(label(k, 80) and label(v, 400) for k, v in known.items()):
        raise ValueError("disqualifiers must map short names to descriptions")
    fixtures = document["fixtures"]
    if not isinstance(fixtures, dict) or not fixtures or not all(label(k, 80) and label(v, 400) for k, v in fixtures.items()):
        raise ValueError("fixtures must map short names to descriptions")
    entries = document["cases"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("cases must be a non-empty list")
    collected = {}
    for case in entries:
        if not isinstance(case, dict) or set(case) != CASE_FIELDS:
            raise ValueError("invalid case fields")
        if not label(case["id"], 80) or case["id"] in collected:
            raise ValueError("case identifiers must be unique short labels")
        if not label(case["starting_point"], 200) or not label(case["prompt"], 2000):
            raise ValueError("each case needs a starting point and a prompt")
        # A case either runs from nothing, or names a fixture state every evaluator can build.
        if case["fixture"] is not None and case["fixture"] not in fixtures:
            raise ValueError("a case fixture must name a defined starting state")
        expected = case["expected"]
        if not isinstance(expected, list) or not expected or not all(label(e, 400) for e in expected):
            raise ValueError("each case needs expected behaviors")
        # Disqualifiers apply to every case; watch_for names the ones this case most invites.
        flags = case["watch_for"]
        if not isinstance(flags, list) or not flags or len(set(flags)) != len(flags) or not all(f in known for f in flags):
            raise ValueError("watch_for must name unique known disqualifiers")
        collected[case["id"]] = case
    return collected, set(known)


def run(document, expected_ids, known_flags, digest):
    if not isinstance(document, dict) or set(document) != RUN_FIELDS:
        raise ValueError("run requires schema, host, model, skill_revision, cases_sha256 and results")
    if document["schema"] != 1:
        raise ValueError("unsupported run schema")
    if not all(label(document[field]) for field in ("host", "model", "skill_revision")):
        raise ValueError("run must record host, model and skill revision")
    # A run is evidence only for the case set it was actually evaluated against.
    if document["cases_sha256"] != digest:
        raise ValueError("run was recorded against a different case set")
    results = document["results"]
    if not isinstance(results, list) or not results:
        raise ValueError("results must be a non-empty list")
    collected = {}
    for result in results:
        if not isinstance(result, dict) or set(result) != RESULT_FIELDS:
            raise ValueError("invalid result fields")
        identifier = result["id"]
        if identifier not in expected_ids:
            raise ValueError("result names an unknown case")
        if identifier in collected:
            raise ValueError("each case is recorded once")
        if result["outcome"] not in OUTCOMES:
            raise ValueError("outcome must be passed or failed")
        if not label(result["evidence"], 2000):
            raise ValueError("each result needs evidence")
        observed = result["disqualifiers_observed"]
        if not isinstance(observed, list) or len(set(observed)) != len(observed) or not all(f in known_flags for f in observed):
            raise ValueError("observed disqualifiers must be unique known names")
        if observed and result["outcome"] != "failed":
            raise ValueError("an observed disqualifier fails its case")
        collected[identifier] = result
    if set(collected) != expected_ids:
        raise ValueError("every case in the set must be recorded")
    return collected


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--results")
    parser.add_argument("--digest", action="store_true",
                        help="print the case-set digest to record in a run, then exit")
    args = parser.parse_args(argv)
    try:
        case_document, digest = load(args.cases)
        defined, known_flags = cases(case_document)
        if args.digest:
            print(json.dumps({"cases_sha256": digest, "case_count": len(defined)}, indent=2))
            return 0
        if not args.results:
            raise ValueError("a recorded run is required unless --digest is requested")
        run_document, _ = load(args.results)
        recorded = run(run_document, set(defined), known_flags, digest)
    except (OSError, ValueError, TypeError):
        print(json.dumps({"status": "invalid", "reason": "requires a valid case set and a complete run recorded against it"}))
        return 2
    failures = sorted(name for name, result in recorded.items() if result["outcome"] != "passed")
    report = {
        "schema": 1,
        "cases_sha256": digest,
        "case_count": len(defined),
        "host": run_document["host"],
        "model": run_document["model"],
        "skill_revision": run_document["skill_revision"],
        "reported_at": datetime.now(timezone.utc).isoformat(),
        "results": [
            {"id": name, "outcome": recorded[name]["outcome"],
             "disqualifiers_observed": sorted(recorded[name]["disqualifiers_observed"])}
            for name in sorted(recorded)
        ],
        "failed": failures,
        "status": "passed" if not failures else "failed",
        "authority": "self-reported observation of one run; not authenticated, not approval",
    }
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
