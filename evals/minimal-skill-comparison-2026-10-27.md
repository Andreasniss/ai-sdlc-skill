<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Minimal setup versus the current AI SDLC skill

24 isolated case-runs, comprising 36 fresh sessions, compare repository guidance alone with the same guidance plus the website-pinned AI SDLC skill. Four known incident adaptations were repeated three times per arm. The [sanitized record](minimal-skill-comparison-2026-10-27.json) retains per-phase grades, candidate identities, process findings and usage. Independent automated process judgments are provisional, not human-calibrated.

## Results

| Measure | Minimal | Full skill |
|---|---:|---:|
| Accepted / 12 | 12 | 12 |
| Unmeasured / 12 | 0 | 0 |
| Process failures / 12 | 0 | 0 |
| Median processed tokens | 193,654 | 287,082 |
| Median admitted tool calls | 20.5 | 20.5 |
| Median session wall seconds | 76.5 | 85.0 |

Matched minimal outcomes: 0 wins, 12 ties, 0 losses and 0 unmeasured. Minimal/full-skill median token ratio: 0.675; wall-time ratio: 0.901.

Acceptance requires every phase to pass external functional checks and the complete task to pass process review. Honest unfinished required work remains incomplete; correctly reporting a required review as unavailable does not fail the local task. Tokens sum reported input and output, including cached input once. They are worker processed volume, not billed dollars. Setup, evaluator/reviewer and article-production usage are not included in these worker medians. Cumulative metrics include retained attempts; missing session usage makes its allocation and arm median unmeasured. Session wall time includes worker startup and cleanup.

| Case | Minimal accepted / 3 | Full skill accepted / 3 |
|---|---:|---:|
| changed-archive-requirement | 3 | 3 |
| mixed-review-unavailable-check | 3 | 3 |
| ordinary-reading-time | 3 | 3 |
| resume-versioned-assets | 3 | 3 |

## Predeclared decision

A bounded efficiency signal requires no lower accepted count, at least 20% lower median cumulative processed tokens, session wall time no more than 25% higher, and no new severe unsupported verification, approval or scope failure. These are practical criteria, not a significance or equivalence test. Even a pass supports reserved transfer testing, not automatic reusable adoption.

| Criterion | Result |
|---|---|
| accepted count no lower | pass |
| tokens at least 20 percent lower | pass |
| time no more than 25 percent higher | pass |
| no new severe failure | pass |

All24 independent automated process judgments pass with no unsupported verification, approval, revision or scope finding. Within that provisional review coverage, neither arm introduces a severe claim. This is not human calibration or proof that every possible defect was excluded.

Bounded efficiency criterion met: true.

## Design and repaired ambiguity

Skill source: [`16c686ae68385c3b7bff9c609fab957159d2e4e5`](https://github.com/Andreasniss/ai-sdlc-skill/tree/16c686ae68385c3b7bff9c609fab957159d2e4e5), the website pin at setup. Skill and relevant references are unmodified. Minimal receives no external skill or checklist; both arms retain the same fixture instructions, task, tools, tests, permissions and review requirements. Explicit skill loading is tested, not native plugin discovery. Neither arm has browser services, extra agents or publishing authority.

The archive task now documents its navigation-control API: series-buttons first, then reader-goals; search is a separate input. The earlier oracle required these exact labels without specifying them to workers. The visible contract was clarified before dispatch and the behavioral oracle left unchanged. Earlier results remain preserved. This experiment is not pooled with them: the source/loading, task contract and budget differ, and this acceptance rule explicitly requires all phase grades.

Workers: gpt-6.1-sol, medium reasoning, Codex 0.160.1, Python 3.12.15, Git 2.47.3, ripgrep 14.1.1. Image `sha256:9332eb9d3a77efd7813bcc2608070160b44c7cf647cbeaaffaacc784abc0717e`. Suite digest `a5a01aa19b83ad69d28c1529851b2d567a175cb73d1f38f0e6ee0fb43b78a9f4`. Seed5772028 randomized matched blocks with alternating arm order. Equal limits:60calls/1800seconds for single-session cases;40/1200 then20/600 for staged cases. CPU2, memory1GiB, fresh writable fixture, read-only skill, empty home/config, evaluator outside the worker. Subscription access only, no API key.

20 harness regressions and eight case/arm preflights passed in the pinned image. Live probes verified subscription access, one-call enforcement, denied unapproved network destinations/direct routing and read-only skill contents. A setup probe initially mistook the image's ordinary /run directory for evaluator exposure; the corrected probe checks unavailable evaluator state and actual completed command output. Both setup attempts are retained separately from scored runs.

## Review and limits

Random packet IDs hide allocations; explicit loading commands and treatment names are removed. Setup review found two receipt entries that retained a treatment name. A documented blinding-only correction masks names in command/receipt strings, preserves original packets and hashes, and applies before judgment. The reviewer exposed to that packet did not score it; a fresh reviewer received the corrected packet. Style can still reveal a treatment, and omitted combined commands can remove useful evidence. Missing proof is unmeasured.

The four small Python cases adapt website incidents; they are familiar development cases, not held-out production website tasks. Three repetitions are correlated, and equal accepted counts do not establish equivalence. No model upgrade, live reader outcome, unrestricted delivery, native collection integration or general productivity gain is measured. The cooperative external grader is not an adversarial anti-cheating benchmark. No reusable minimal default or skill replacement is adopted by this report.

## Per-run evidence

| Run | Case | Repeat | Arm | All phases functional | Process | Accepted |
|---|---|---:|---|---|---|---|
| run-01 | changed-archive-requirement | 1 | minimal | pass | pass | pass |
| run-02 | changed-archive-requirement | 1 | skill | pass | pass | pass |
| run-03 | changed-archive-requirement | 2 | skill | pass | pass | pass |
| run-04 | changed-archive-requirement | 2 | minimal | pass | pass | pass |
| run-05 | changed-archive-requirement | 3 | minimal | pass | pass | pass |
| run-06 | changed-archive-requirement | 3 | skill | pass | pass | pass |
| run-07 | resume-versioned-assets | 3 | skill | pass | pass | pass |
| run-08 | resume-versioned-assets | 3 | minimal | pass | pass | pass |
| run-09 | mixed-review-unavailable-check | 1 | minimal | pass | pass | pass |
| run-10 | mixed-review-unavailable-check | 1 | skill | pass | pass | pass |
| run-11 | resume-versioned-assets | 1 | skill | pass | pass | pass |
| run-12 | resume-versioned-assets | 1 | minimal | pass | pass | pass |
| run-13 | mixed-review-unavailable-check | 2 | minimal | pass | pass | pass |
| run-14 | mixed-review-unavailable-check | 2 | skill | pass | pass | pass |
| run-15 | ordinary-reading-time | 1 | skill | pass | pass | pass |
| run-16 | ordinary-reading-time | 1 | minimal | pass | pass | pass |
| run-17 | ordinary-reading-time | 3 | minimal | pass | pass | pass |
| run-18 | ordinary-reading-time | 3 | skill | pass | pass | pass |
| run-19 | resume-versioned-assets | 2 | skill | pass | pass | pass |
| run-20 | resume-versioned-assets | 2 | minimal | pass | pass | pass |
| run-21 | mixed-review-unavailable-check | 3 | minimal | pass | pass | pass |
| run-22 | mixed-review-unavailable-check | 3 | skill | pass | pass | pass |
| run-23 | ordinary-reading-time | 2 | skill | pass | pass | pass |
| run-24 | ordinary-reading-time | 2 | minimal | pass | pass | pass |

Retained scored infrastructure attempts: 0, adding 0 sessions. Raw sessions, authoring and complete private manifests are not published. Reports remain on an unmerged evaluation branch.
