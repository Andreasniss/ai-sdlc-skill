<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Comparing two skill collections on the same lifecycle tasks

12 matched pairs, comprising 24 case-runs and 36 fresh sessions, compare AI SDLC with Addy Osmani's agent-skills. Both received the same four synthetic lifecycle cases, three repetitions, model, runtime and budgets. Every candidate received external functional grading and a treatment-blind process review. These are provisional automated judgments, not human calibration. The [sanitized run record](skill-collection-comparison-2026-10-26.json) includes all outcomes, checks, identities and findings.

This comparison does not establish enough benefit to replace AI SDLC with Addy's collection under the predefined thresholds.

## Outcomes and overhead

| Collection | Accepted / 12 | Process failures / 12 | Median tokens processed | Median tool calls | Median active seconds |
|---|---:|---:|---:|---:|---:|
| AI SDLC | 8 | 4 | 294,600.0 | 22.0 | 97.8 |
| Addy agent-skills | 7 | 5 | 553,000.0 | 27.0 | 117.9 |

Matched Addy outcomes versus AI SDLC: wins 1, ties 9, losses 2, 0 unmeasured. Addy median processed-token ratio: 1.877; active-time ratio: 1.206.

Processed tokens are reported input plus output, including cached input. The JSON preserves cached input separately. These are not billed dollars; subscription billing is unknown. Medians use cumulative resource use per planned allocation, including retained infrastructure attempts. Honest unfinished commits or checks remain process failures when the task required them; accurate disclosure is distinguished from false claims.

| Case | AI SDLC accepted / 3 | Addy accepted / 3 |
|---|---:|---:|
| changed-archive-requirement | 0 | 0 |
| mixed-review-unavailable-check | 2 | 1 |
| ordinary-reading-time | 3 | 3 |
| resume-versioned-assets | 3 | 3 |

## Predefined decision

Replacement required at least two additional accepted runs, improvement in at least two distinct lifecycle cases, no new severe unsupported verification/approval or scope violation, and median tokens and active time no more than 25% above AI SDLC. These are practical thresholds, not statistical significance.

| Criterion | Result |
|---|---|
| at least two more accepted | fail |
| improvement in two lifecycle cases | fail |
| no new severe failure | unresolved |
| token overhead at most 25 percent | fail |
| time overhead at most 25 percent | pass |

Addy run-10 leaves an unsupported commit statement in the durable review record while its conversational handoff correctly discloses uncommitted work. It is counted as a process failure. The reviews do not independently calibrate whether this meets the predefined severe unsupported-verification/approval threshold, so that criterion remains unresolved rather than being treated as a pass. No replacement claim depends on resolving it because the acceptance-gain and token-overhead criteria already fail.

## What was actually compared

AI SDLC source: [`4606f39c2b015bed549d0901a6e14822e386ec12`](https://github.com/Andreasniss/ai-sdlc-skill/tree/4606f39c2b015bed549d0901a6e14822e386ec12). Addy source: [`aeac41d4d005999432bb7312f7ff06383a91d59d`](https://github.com/addyosmani/agent-skills/tree/aeac41d4d005999432bb7312f7ff06383a91d59d). Both source skill bodies and their references were unmodified. The upstream MIT license was retained privately with the Addy checkout; no third-party skill text is republished in this report.

A neutral catalog listed each collection's skill names, descriptions and paths. Workers chose what to load, including relevant references. Addy's meta-skill was available but not forced into the prompt. The collection was mounted read-only, including its shared references. This tests explicit catalog-guided use, not native plugin installation or automatic skill discovery, upstream hooks, browser integrations, or specialist subagents. External services and additional agents were disabled equally. The host never installed either collection globally.

Workers used `gpt-6.1-sol` at `medium` reasoning, Codex `0.160.1`, Python `3.12.15`, Git `2.47.3`, and ripgrep `14.1.1`. Image: `sha256:9332eb9d3a77efd7813bcc2608070160b44c7cf647cbeaaffaacc784abc0717e`. Suite digest: `58e86f74af74b61d2d7f32665f6def417b5e48fe7e074b6a7d825af78b94ec74`. Allocation seed: `5772027`, shuffled matched blocks with alternating collection order. Each case had 30 calls and 900 seconds; staged cases split that into 20/600 and 10/300. No candidate repairs or treatment tuning occurred.

All eight case/collection preflights passed. Independent setup review confirmed arm mounting and isolation. A live probe verified subscription access and denial of the second action under a one-call budget. Additional probes verified blocked external destinations, direct routing and skill writes. Complete bundle and execution-source hashes were checked before and after sessions; preflight binds the manifest. These are setup observations, not candidate acceptance scores.

## Limits and interpretation

The archive grader still requires exact internal control labels that the task does not specify. Its failures remain unchanged and cannot all be interpreted as reader-visible defects. Functional grades and consequential process findings are reported separately. Resolving the grader requires a new versioned experiment, not rescoring to favor either collection.

The four cases were already known from the previous experiment and are not held-out transfer tasks. Three repeats are small and correlated. Treatment names and loading commands were withheld from process reviewers, but writing style may reveal a collection. Reviews are automated and provisional.

The earlier 36-run experiment used explicit full-skill loading and lacked ripgrep. This comparison provides ripgrep equally and uses a catalog for both collections. Earlier results are historical context, not pooled controls. There is no fresh repository-only or minimal-harness arm here, so these results cannot establish that removing all skills improves website work. The 30-call cap is an experimental constraint; unfinished delivery under it may not predict an unrestricted website session. No production website delivery or live reader outcome was measured. No skill replacement or harness reduction was performed.

## Per-run evidence

| Run | Case | Repeat | Collection | Final functional | Process | Accepted |
|---|---|---:|---|---|---|---|
| run-01 | resume-versioned-assets | 3 | AI SDLC | pass | pass | pass |
| run-02 | resume-versioned-assets | 3 | Addy agent-skills | pass | pass | pass |
| run-03 | mixed-review-unavailable-check | 2 | Addy agent-skills | pass | pass | pass |
| run-04 | mixed-review-unavailable-check | 2 | AI SDLC | pass | fail | fail |
| run-05 | ordinary-reading-time | 3 | AI SDLC | pass | pass | pass |
| run-06 | ordinary-reading-time | 3 | Addy agent-skills | pass | pass | pass |
| run-07 | ordinary-reading-time | 2 | Addy agent-skills | pass | pass | pass |
| run-08 | ordinary-reading-time | 2 | AI SDLC | pass | pass | pass |
| run-09 | mixed-review-unavailable-check | 1 | AI SDLC | pass | pass | pass |
| run-10 | mixed-review-unavailable-check | 1 | Addy agent-skills | pass | fail | fail |
| run-11 | resume-versioned-assets | 1 | Addy agent-skills | pass | pass | pass |
| run-12 | resume-versioned-assets | 1 | AI SDLC | pass | pass | pass |
| run-13 | changed-archive-requirement | 3 | AI SDLC | fail | fail | fail |
| run-14 | changed-archive-requirement | 3 | Addy agent-skills | fail | fail | fail |
| run-15 | ordinary-reading-time | 1 | Addy agent-skills | pass | pass | pass |
| run-16 | ordinary-reading-time | 1 | AI SDLC | pass | pass | pass |
| run-17 | changed-archive-requirement | 2 | AI SDLC | fail | fail | fail |
| run-18 | changed-archive-requirement | 2 | Addy agent-skills | fail | fail | fail |
| run-19 | changed-archive-requirement | 1 | Addy agent-skills | fail | fail | fail |
| run-20 | changed-archive-requirement | 1 | AI SDLC | fail | fail | fail |
| run-21 | resume-versioned-assets | 2 | AI SDLC | pass | pass | pass |
| run-22 | resume-versioned-assets | 2 | Addy agent-skills | pass | pass | pass |
| run-23 | mixed-review-unavailable-check | 3 | Addy agent-skills | pass | fail | fail |
| run-24 | mixed-review-unavailable-check | 3 | AI SDLC | pass | pass | pass |

Retained infrastructure-attempt records: 2, adding 4 sessions beyond the 36 planned sessions. A recovered service-stream disconnection stopped the first attempt at pair 7. The unchanged connection proxy was restarted once; both preflights and an access probe passed, then the whole pair was rerun in its original order. Original states, grades and usage remain recorded. Both stages, failures and unknown metrics remain in the JSON. Raw sessions, reviewer packets and complete manifests remain private. The result remains on an unmerged evaluation branch; it does not change either skill or the website.
