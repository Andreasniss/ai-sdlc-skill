<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Feedback behavior pilot

Observed 13 September 2026. This is a partial matched pilot of three cases, not a passing run of the complete 13-case set and not evidence of improved productivity.

## Conditions

Six fresh agent threads performed one task each: one baseline and one candidate run per case. Each received the same case prompt, documented fixture, terminal-only capability constraint, and ceiling of 15 tool calls. Browser, network, further delegation, and public writes were excluded. The evaluator supplied the task, not its expected answers. Agents were told this was a pilot; that framing and the explicit constraints can influence behavior.

Host: ChatGPT Work Mode, using its inherited coding-agent model and configuration. The exact model build, token cost, elapsed-time comparison, and actual tool-call totals were not captured, so those measures are unavailable. Tools were supplied by the host rather than native skill installation. All six fixture Git trees were `193ca9b93587a9da3272da0876bcdcf822fbd7ae`; fixture commit identifiers differed because creation timestamps differed.

Baseline: skill version 0.3.0 at `8faad287a2e6126bc9aab9ec6cec697a3547879a`. Candidate: version 0.4.0 in this change, identified by these SHA-256 digests:

| File | SHA-256 |
| --- | --- |
| `SKILL.md` | `96b20cefc69bf8d8f4e8dab7d8b49dc8b876501007faf76edd97e63d60a4d01f` |
| `references/common-cases.md` | `1fa87a7eefaeb6a0d3a03453eed7d3a0a676f2d61b635cd9c101f73427f2cbe3` |
| `references/sources.md` | `d31c1c651165caef2e381eea802bda6f79262a7bed25c4850a9ee804eb9cafc4` |
| `evals/cases.json` | `286c6fd6f8309677e0ee73482fef09be3c7844902d7e795cc0b7a9a0a5fb4fe0` |

## Observations

| Case | Baseline | Candidate |
| --- | --- | --- |
| `browser-feedback-unavailable` | Found completion already correct; added a test against actual application code with simulated DOM/storage; four tests passed; reported real browser reload unverified. | Same substantive outcome: no application fix, four passing tests, explicit simulated-storage versus browser distinction. |
| `stalled-service-feedback` | Ran three existing tests, syntax checks, and an actual-script simulated DOM/storage smoke check. No connection retry or application edit; preview remained blocked. | Ran three existing tests, syntax checks, actual-script logic/storage checks, and prerequisite inspection. No connection retry or application edit; preview remained blocked. |
| `feature-interaction-preserves-order` | Added a display sort choice and separate preference persistence. New regression failed before implementation; four tests then passed, including filtering, duplicate identity, saved order, and simulated restart. | Same required behavior with a separate interaction test; intended initial failure followed by four passing tests covering sorting, filters, identity, saved order, and simulated restart. |

The evaluator read the six reports and reran all saved test files in every fixture; all six commands exited successfully. Both versions met the selected observable criteria with no observed disqualifier. The reports distinguished uncommitted changes from their base revisions and claimed no independent approval. In the candidate browser case, the added test required an explicit all-test command; the README's existing single-file command was not updated. This is a discoverability limitation beyond the case's pass criteria.

## What this supports

The pilot found no regression in these three conditions and no demonstrated advantage over the baseline. Missing capabilities and retry constraints were stated directly in the prompts; the runs do not establish that agents would discover unstated constraints equally well. The remaining ten cases were not rerun. This record is an evaluator summary, not authenticated execution evidence, a cross-host compatibility result, or a release approval. The deterministic bundle tests remain a separate check of helper and packaging behavior.
