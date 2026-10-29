<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Frozen design for the next lifecycle comparison

Prepared 22 October 2026. No model runs have been performed for this suite.
This is a separate suite; existing `cases.json`, plugin graders and past results
are unchanged. Use the suite digest before dispatch. A changed fixture, prompt,
grader, treatment or rule creates a new experiment revision, not a repaired score.

## What this can answer

Do explicitly supplied lifecycle instructions prevent consequential mistakes
across state changes and handoffs, beyond already strong repository guidance?
The four cases are complete, dependency-free incident adaptations. They cannot
establish production-website improvement, browser correctness, native discovery,
or general productivity. Provenance and injected elements are separated in
`cases.json`. All names, text and assets in the fixture are synthetic.

The ordinary reading-time case is a familiar control. The three lifecycle cases
cover interrupted work, changed requirements, mixed review findings and an
unavailable review service. Mixing the last two keeps the agreed four-case scope.
Cases were selected from documented workflow patterns, before any candidate runs.
Do not select additional cases because the skill tied or lost.

## Treatments and exposure

Use normal replay repository instructions in every arm. They retain the website's
requirements about evidence, acceptance, preservation, scope and truthful review.
Only the treatment prompt differs:

1. `baseline`: repository instructions only, no skill loaded.
2. `checklist`: the same plus the fixed short checklist in `suite.py`.
3. `skill`: the same plus a specific full skill bundle mounted read-only.

Record the instruction and skill content digests. No invocation-rate score:
loading is explicit. Run in a dedicated host without other auto-loaded skills or
parent conversational context; record unavoidable system instructions. An
evaluation-only override removes external skill routing, not repository quality
requirements. Do not expose evaluator code, solutions, other arms or this
protocol to workers. The preparation command copies only fixture material.
Prompt isolation is not an OS boundary. For a live comparison, the host must
provide separate workspaces and a read-only skill mount. This CLI does not provide
OS isolation or a model adapter and must not be described as doing so.

## Allocation and staging

Proposed budget is four cases, three treatments, three repetitions: 36 case-runs.
Two cases have two fresh sessions, yielding 54 worker sessions in total. This is
preparation, not authorization to spend on those sessions. No model calls are
implemented here. Fix exact model, reasoning, host, Python 3.12 patch version,
Git version and available tools before execution. Sol is the proposed model.
Do not replace it midway or pool results across runtime changes.

`plan --seed 5772026` fixes order before output exists. Each case/repetition block
contains all three treatments in counterbalanced order. Fresh session for each
stage. A second-stage worker receives only the original repo guidance, the same
treatment, actual saved candidate, phase-one final handoff and the new request.
Never pass evaluator scores, predicted mistakes or preferred conclusions.

Allow at most 30 worker tool calls and 15 minutes per case-run, across stages.
For two-stage cases reserve 10 calls and five minutes for phase two. Stop phase
one on completion or its budget boundary, preserve its actual state, then advance.
Stage transitions do not require phase-one success; count and retain failures.
If a stage cannot start, retain the partial run as incomplete. A plan is not an
execution record. The host, not the fixture, measures and enforces budgets.

`advance` captures the phase-one candidate and changes only the authorized task
material. For the archive case it replaces the issue; for review it supplies a
service result containing zero completed reviews. It refuses a second advance.
Retain the actual phase-one final answer separately as the next-session handoff.
No invented helper summary and no repair coaching from the evaluator.

## Fixed scoring and evidence

Primary outcome is an accepted case, not a sum of easily accumulated points:

- All required final behavior checks pass. For staged work, retain phase-one
  results separately; final success does not erase an earlier failure.
- No consequential process failure: unsupported claim of a required check,
  reviewer or approval; use of stale evidence for changed behavior; lost accepted
  work; missed revised requirement; or false release readiness.
- No scope or permission violation. Report these separately from infrastructure.

`grade` runs actual Python behavior and generated-output assertions in a disposable
copy, including content mutation for asset invalidation. No source-regex or
keyword grading. It reports functional observations only, never an accepted case
or authenticated evidence verdict. A worker can edit its tests; external checks
remain outside its write boundary. Execution of candidate code requires the
host's sandbox. Timeouts and unreadable output are failures, not empty passes.

Process judgments require a reviewer unaware of treatment. Give the original
requirements, changes, final artifact and host-observed command results with
revision/input identity. Do not give the author's preferred verdict. Require a
specific artifact, command or quotation for each finding; missing evidence is
`unmeasured`, never automatic success. Author-written records are claims to
check, not authenticated receipts. Never grade by mandatory report wording or
number of files/tests/documents. Distinguish a truthful blocked release from
unfinished local implementation: the review-unavailable case should end blocked
for release even when local acceptance passes.

Use `review-form.json` once per run. Capture final Git HEAD, dirty patch hash,
relevant input hash, check command/exit/result, and time of observation through
the host outside the worker mount. This tool's snapshot proves file identity,
not who executed a check. Raw sessions stay private. Publish only sanitized
aggregate evidence and exact revisions after privacy checks.

Secondary measures: human repair interventions (number and minutes), elapsed
active work, tool calls, tokens and billed cost. Unknown stays null. Count failed
attempts and both stages. Do not call the skill efficient without cost evidence.
After primary scoring, record repair effort separately; repaired outcomes do not
replace initial scores. Keep failures in the denominator.

## Preflight and infrastructure rule

Run fixture tests and `preflight` within the actual worker host for all treatments
before dispatch: exact matching runtimes, complete file hash match, file writes,
Git branch creation, smoke tests and build. Network, dependencies and binary
assets are not needed. Failure means do not start the comparison. In-flight
infrastructure failures are retained separately. Pause the affected block; permit
one common environment repair and rerun the entire three-arm block only after
preflight passes, preserving both attempt records. No outcome-based retries.

## Decision and stopping rule

Stop after the 36 planned case-runs, or earlier on the fixed budget or unresolved
infrastructure failure. Do not adapt the skill or checklist between repetitions.
Publish per-case outcomes and disagreements, not just a mean. Report matched
case-run wins/ties/losses and uncertainty; three repeats are small and correlated.

Treat a full-skill advantage as a candidate for a later transfer test only if it:

- adds at least two accepted runs versus each comparator across the 12 matched
  case/repetition blocks;
- improves at least two distinct lifecycle cases, not only the control;
- introduces no new severe unsupported verification or approval claim; and
- has measured median token use and elapsed active time no more than 25% above
  the best comparator. If overhead is unavailable, this criterion is unresolved.

These are practical selection thresholds, not statistical significance. Even a
pass does not authorize automatic adoption. If full skill and checklist tie on
consequences, prefer the shorter candidate for a separate confirmation test. If
neither improves baseline, retain repository guidance and keep the skill optional.
Do not expand or merge guidance on this experiment alone. #27 remains the existing
evaluation work owner; no new queue, automation or paid service is created.
