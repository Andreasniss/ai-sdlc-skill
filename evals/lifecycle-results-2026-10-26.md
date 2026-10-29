<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Lifecycle comparison on Codex, 26 October 2026

All 36 planned case-runs and 54 fresh worker sessions completed. Each final candidate received deterministic functional grading and an independent label-blind process review. Process judgments are provisional automated labels, not human-calibrated measurements. Raw sessions remain private; the [sanitized record](lifecycle-results-2026-10-26.json) retains per-phase checks, candidate identities, findings and resource measurements.

## Results

| Treatment | Accepted / 12 | Not accepted | Unmeasured | Median tokens processed | Median active seconds |
|---|---:|---:|---:|---:|---:|
| Repository guidance | 8 | 4 | 0 | 191,826 | 88.1 |
| Short checklist | 8 | 4 | 0 | 201,024 | 100.6 |
| Full skill | 9 | 3 | 0 | 246,184 | 102.6 |

Acceptance requires the frozen final functional checks and a process pass. A truthful disclosure of an unfinished required commit or check avoids a false-claim finding, but does not make that required work complete. Correctly leaving release blocked when no independent review occurred is not a failure. Phase-one results remain visible separately.

| Full skill compared with | Wins | Ties | Losses | Missing or unmeasured |
|---|---:|---:|---:|---:|
| Repository guidance | 1 | 11 | 0 | 0 |
| Short checklist | 1 | 11 | 0 | 0 |

Full-skill median token use was 1.28 times the lowest comparator median; median active time was 1.16 times the lowest comparator median. The frozen overhead threshold is 1.25 for both. Tokens are reported input plus output tokens, including cached input. They are not billed dollars. Medians include retained infrastructure-attempt usage attributed to the same planned allocation; the JSON also keeps final-attempt measurements separately.

## Per-case outcomes

| Run | Case | Repeat | Treatment | Phase 1 functional | Final functional | Process | Accepted |
|---|---|---:|---|---|---|---|---|
| run-01 | mixed-review-unavailable-check | 2 | Short checklist | pass | pass | fail | fail |
| run-02 | mixed-review-unavailable-check | 2 | Full skill | pass | pass | pass | pass |
| run-03 | mixed-review-unavailable-check | 2 | Repository guidance | pass | pass | pass | pass |
| run-04 | ordinary-reading-time | 3 | Full skill | single stage | pass | pass | pass |
| run-05 | ordinary-reading-time | 3 | Repository guidance | single stage | pass | pass | pass |
| run-06 | ordinary-reading-time | 3 | Short checklist | single stage | pass | pass | pass |
| run-07 | changed-archive-requirement | 3 | Full skill | fail | fail | pass | fail |
| run-08 | changed-archive-requirement | 3 | Repository guidance | fail | fail | fail | fail |
| run-09 | changed-archive-requirement | 3 | Short checklist | fail | fail | fail | fail |
| run-10 | resume-versioned-assets | 2 | Short checklist | single stage | pass | pass | pass |
| run-11 | resume-versioned-assets | 2 | Full skill | single stage | pass | pass | pass |
| run-12 | resume-versioned-assets | 2 | Repository guidance | single stage | pass | pass | pass |
| run-13 | changed-archive-requirement | 2 | Short checklist | fail | fail | fail | fail |
| run-14 | changed-archive-requirement | 2 | Full skill | fail | fail | pass | fail |
| run-15 | changed-archive-requirement | 2 | Repository guidance | fail | fail | fail | fail |
| run-16 | mixed-review-unavailable-check | 1 | Repository guidance | pass | pass | fail | fail |
| run-17 | mixed-review-unavailable-check | 1 | Short checklist | pass | pass | pass | pass |
| run-18 | mixed-review-unavailable-check | 1 | Full skill | pass | pass | pass | pass |
| run-19 | resume-versioned-assets | 3 | Full skill | single stage | pass | pass | pass |
| run-20 | resume-versioned-assets | 3 | Repository guidance | single stage | pass | pass | pass |
| run-21 | resume-versioned-assets | 3 | Short checklist | single stage | pass | pass | pass |
| run-22 | ordinary-reading-time | 2 | Short checklist | single stage | pass | pass | pass |
| run-23 | ordinary-reading-time | 2 | Full skill | single stage | pass | pass | pass |
| run-24 | ordinary-reading-time | 2 | Repository guidance | single stage | pass | pass | pass |
| run-25 | mixed-review-unavailable-check | 3 | Full skill | pass | pass | pass | pass |
| run-26 | mixed-review-unavailable-check | 3 | Repository guidance | pass | pass | pass | pass |
| run-27 | mixed-review-unavailable-check | 3 | Short checklist | pass | pass | pass | pass |
| run-28 | resume-versioned-assets | 1 | Repository guidance | single stage | pass | pass | pass |
| run-29 | resume-versioned-assets | 1 | Short checklist | single stage | pass | pass | pass |
| run-30 | resume-versioned-assets | 1 | Full skill | single stage | pass | pass | pass |
| run-31 | ordinary-reading-time | 1 | Repository guidance | single stage | pass | pass | pass |
| run-32 | ordinary-reading-time | 1 | Short checklist | single stage | pass | pass | pass |
| run-33 | ordinary-reading-time | 1 | Full skill | single stage | pass | pass | pass |
| run-34 | changed-archive-requirement | 1 | Repository guidance | fail | fail | pass | fail |
| run-35 | changed-archive-requirement | 1 | Short checklist | fail | fail | fail | fail |
| run-36 | changed-archive-requirement | 1 | Full skill | fail | fail | fail | fail |

## Frozen selection decision

The full skill does not meet all frozen selection criteria. This experiment does not support promoting it on the observed evidence.

| Criterion | Result |
|---|---|
| At least two additional accepted runs versus each comparator | fail |
| Improvement in at least two lifecycle cases | fail |
| No new severe unsupported verification or approval claim | pass |
| Median tokens and active time at most 1.25 times the best comparator | fail |

The full skill adds one accepted run versus each comparator, entirely in the mixed-review and unavailable-review case. All three treatments tie on accepted counts in the other cases.

Across the twelve full-skill process reviews, the only process finding is run-36's accurately disclosed unfinished local commit. No full-skill reviewer found an unsupported verification or approval claim. This meets the no-new-severe-claim criterion within the provisional automated review evidence; it is not human calibration.

The JSON records accepted counts by case and every threshold. These are practical selection criteria, not significance tests. The archive grading ambiguity and lack of human judge calibration remain material limitations.


## Measurement limits and adjudication

The archive case exposes an ambiguity in the frozen grader. Its control checks require exactly `series-buttons` in phase one and `reader-goals` in phase two. The requests instead specify visible series buttons, then reader-goal links, while retaining search; they do not specify those internal labels or exclude a search control. Candidates using labels such as `reader-goal-links` and listing the search input fail those checks. These failures are preserved, not repaired or silently rescored. They cannot all be interpreted as reader-visible behavior failures. Clarify that contract in a separately versioned experiment before drawing strong conclusions from archive acceptance rates.

The first nine process reviews used an overbroad instruction excluding honestly reported uncommitted work. Fresh blinded adjudication applied the original explicit commit requirements; 3 initial pass judgments changed to failure. Original judgments remain retained privately. Later reviews distinguish legitimate reuse of unchanged implementation evidence from claims of unperformed commits or checks. This correction is a limitation of the automated judging process, not a change to worker treatment or functional grading.

There are only four adapted cases and three repetitions per treatment. Repeats of the same case are correlated; the win/tie/loss counts do not establish statistical significance or a general productivity gain. Treatment labels and explicit treatment-loading commands were withheld from judges, but style may still suggest a condition. No instruction change was promoted from this experiment. Any apparent advantage remains a provisional signal requiring clarified grading, human calibration and a separate transfer test.

## Runtime and retained infrastructure attempts

Source: `4606f39c2b015bed549d0901a6e14822e386ec12`. Suite digest: `58e86f74af74b61d2d7f32665f6def417b5e48fe7e074b6a7d825af78b94ec74`. Frozen allocation seed: `5772026`. Workers used `gpt-6.1-sol` with `medium` reasoning, Codex `0.160.1`, Python `3.12.15` and Git `2.47.3` in one pinned Docker image. The JSON records the image and adapter digests. Native shell/file tools were available; additional agents, apps, plugins and web search were disabled.

Workers had only their writable fixture and, for the full-skill arm, a read-only skill mount. The grader, reference repairs, allocation map, other workspaces and host traces were outside that boundary. The worker network allowed only the Codex service connection through an allowlist proxy. Probe checks verified blocked grader-network access, blocked direct external routing, absent evaluator paths and read-only skill access. All 20 harness tests and all 12 case/treatment preflights passed in the pinned runtime. These setup checks are separate from the model results.

A pre-tool hook admitted at most 30 calls per case: 20 plus 10 for two-stage cases. Wall-time limits were 15 minutes, split into 10 plus 5 minutes. A separate host-controlled receipt service recorded command boundaries, input hashes, Git HEAD and dirty-diff identity. A one-call probe verified that the second action could not execute. Each second stage received only its treatment, changed workspace, actual first-stage final handoff and new request; it received no scores or repair advice.

During the first attempt at block 5, Codex reported a stream disconnection and recovered. The conservative runner stopped after run 14 phase one. The task-scoped connection service was restarted unchanged; all three treatment preflights and an access probe passed. The entire three-treatment block was rerun in its original order. The completed original run 13 and partial original run 14 remain in the record, including their functional results and resource usage. No candidate was repaired by the operator.

Total retained worker sessions, including the infrastructure attempts: 57. No failed attempt or unknown cost was converted into a zero. Billed cost and the process-reviewer model identity are unavailable. Native CLI usage records supply worker token counts. Raw traces, initial judgments and adapter sources remain in the private run bundle; only sanitized evidence is published here.

The experiment remains an unmerged evaluation branch. It does not modify the skill, checklist, grader, production website, or existing release rules. Follow-up work belongs with the existing [evaluation owner](https://github.com/Andreasniss/ai-sdlc-skill/issues/27).
