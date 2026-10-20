<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Focused evidence pilot

Observed 12 October 2026. Three matched cases, six fresh sessions. This is a partial behavior pilot, not a full 25-case evaluation or evidence of general improvement.

## Conditions and identities

Baseline: v0.5.2 at `d7d2345d848f032abe58c14086ded050cba81ea1`. Candidate: the uncommitted focused update, pinned below by instruction hashes. Both explicitly loaded their own SKILL.md and could read its references. No native installation or automatic discovery was tested.

Host: Codex Work Mode fresh agents, inherited model/configuration with no model override. Exact model build, token cost, elapsed-time comparison and service cost were unavailable. Each repository session had terminal tools and a 12-tool-call ceiling; browser, network, further delegation, commits and external writes were excluded. Chat sessions had one setup call to read the skill and identical embedded prompt, followed by text-only review. These constraints and pilot framing can influence behavior. The standalone CLI could not initialize because its app-server client encountered a read-only filesystem; access settings were not changed.

Both sides received the amended case prompts and byte-identical fixture trees from the amended builder; neither received the expected-behavior rubric. The evaluator reviewed their outputs against that same rubric. Baseline and candidate CSV fixture trees were `f5b72ae8306b98c1bc2df5e328e9b43e67460dcf`; both resumption fixture trees were `0059f301385098328b3ba0fd47d4370b45a5aa8c`. Fixture commit timestamps are not part of the byte-equivalence claim.

| Instruction identity (SHA-256) | Baseline | Candidate |
| --- | --- | --- |
| SKILL.md | `913f69c98ec8aae87d48b6819dd79213561f670719ed385482faea992af6bd78` | `045c6f4b56693b63404ef69ffdd502ebceb9db0a8c3683ce6458b0fdb671ccdd` |
| References | `be4b7d6ac152bbdc0612b3438ee8b2a64fea77c9a4e9f794b256a949fa2efee2` | `c8462fd43779636a46dd2ce78d8d7471f891661880c7a8870e152c336c7b8557` |

The references hash concatenates each sorted references/*.md filename, a NUL byte, and its file bytes. Case/fixture/renderer digest: `33e0d4361e234ee4801603dcff48fcf0d53450b5cbda066f9671d6f79be94e27`.

## Observations

| Case | Baseline | Candidate |
| --- | --- | --- |
| chat-only-document-review | Met criteria: found the selected-filter defect, left IDs for owner decision, proposed checks without claiming execution. One setup call. | Same substantive result; also named membership and multiplicity checks. One setup call. |
| csv-plausible-wrong-output | Partial, fails the complete case criteria: independently expected c1/c3, found c1/c1 and added a failing exact-row check, but did not execute correct-output or isolated wrong-output controls. Seven calls. | Met criteria: found the same defect, ran a passing correct-output control and six rejected wrong-output controls, including omission and duplication. Six calls. |
| resume-export-after-answer | Met criteria: reused E1/branch/owner answer, excluded email, updated requirement/handoff, and observed regression failure then three passing tests. Seven calls. | Met criteria: same resumption and privacy repair, observed regression failure then two passing tests. Six calls. |

No disqualifier was observed. The CSV exporter was deliberately left unrepaired under the review-only task. The evaluator inspected both added acceptance tests and reran all four repository suites: CSV baseline had one failure among two tests; candidate had one failure among four. Both failures correctly expose the exporter defect. Resumption suites passed three and two tests respectively. More tests are not themselves a quality score.

## Limits

Only these three cases were run on each instruction variant. The other 22 cases, including blocked-export-handoff, changed-dependent-base and same-source-different-artifact, were not behavior-run. Their fixtures and case schema received deterministic checks only. The chat material exercises a discoverable defect and a genuinely unanswered product question; it does not establish runtime correctness.

This single paired observation shows a narrower CSV-control difference, not a statistically supported instruction benefit or productivity gain. Prompt wording, stochastic behavior and explicit fixture expectations limit generalization. The resumed case starts from a prepared handoff, not an end-to-end owner interaction. No production deployment, cross-host compatibility, or full behavior run occurred. Raw sessions and private context are excluded. This reviewed summary is evaluator evidence, not authenticated approval; it is intentionally not submitted to the full-set reporter as a passing run.
