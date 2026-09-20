<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Review-loop behavior evaluation

Observed 20 September 2026. The [recorded run](review-loop-run.json) covers all 15 cases in the current set, with no observed disqualifier. This is one host observation, not a baseline comparison, a productivity result, or release approval.

## Conditions and identity

Three fresh evaluator sessions each performed five tasks in separate local workspaces. Sessions shared no task artifacts, but context could carry between the five cases within a session. Each received the skill path, case prompt and starting conditions, without the expected-answer lists or author conclusions. Repository cases used the unchanged fixture builder. Evaluators implemented requested local fixture changes and ran available checks; they did not edit the skill. A coordinating evaluator read every report against the case criteria and reran all saved fixture test suites successfully. Read-only review fixtures remained clean; initialization changed documentation only.

Host: Codex API agent on macOS, with the inherited agent model. Exact model build identifier, token/tool cost and elapsed-time comparison were not captured. Node was 26.9.0; final bundle and report validation used Python 3.14.7. Behavior cases had terminal access but no browser, network, external writes, commits, or further delegation. Chat-only cases used supplied material only; saving a report was not treated as repository execution evidence. One fixture edit required automatic approval reconsideration using the repository's evaluation requirement; no rejected mutation was bypassed and no additional human approval was supplied.

The candidate was uncommitted, based on `1ff865c5c33de30dedc82a0f53f29bb3f43a7f46`. Instruction identity:

| File | SHA-256 |
| --- | --- |
| `SKILL.md` | `afdfb1eb9769f0deda1dc8f2dbc9e6053c250673ff43429010233ff46e9c2579` |
| `references/common-cases.md` | `524f68a665776ce7d9bd29d644f3b75d070677b1732a577ad4f1a672fb1d838f` |
| `references/adoption.md` | `da1ebda199448c8af82a0e867b6a8e5ea90d7c5ceefe81f8f7ee75fa067a7e9b` |

The adoption reference's version label was corrected during the run; its guidance did not change. The entrypoint and common-case guidance stayed unchanged throughout all tasks. Other instruction references matched the base. The case-set digest, including fixture builder and renderer, is `9db369a5da6fafcf2c2dbd28b0552cf510943854a28dd37d41873be6f8c108f7`.

## New regression observations

- **Related findings:** The evaluator reproduced both export-filter failures, traced them to one filtering mistake in two implementations, and repaired them together. Quote tests showed that escaping already worked. The final 13-test suite passed. The optional sorting suggestion stayed outside the repair and received a decision owner in the existing issue record.
- **Focused re-review:** From the supplied code, the evaluator identified in-place sorting followed by save as a storage-order acceptance failure. It kept the defect blocking despite two prior repair rounds, proposed a focused repair and checks, and claimed neither execution nor a fresh review of unrelated code.

These cases supply previous-round context rather than observing an entire multi-round delivery. They check the next decision under that context; they do not measure whether the revised skill reduces review rounds in practice.

## Other observations and limits

The other cases preserved proposal-only, documentation-only and review-only boundaries; reproduced a duplicate-title defect before repair; preserved sorting/storage interactions; and resumed existing work without treating old checks as current. Per-case actions and results are recorded in the JSON rather than duplicated here.

The existing chat-only document-review prompt names attachments but supplies none. Its pass means missing-input handling was bounded and honest, not that a substantive design review completed. Browser-dependent acceptance remains unverified in these terminal-only runs; simulated DOM/storage checks were identified as such. The run does not establish native installation, cross-host compatibility, statistical reliability, or an advantage over the earlier skill. Local reports are observations, not authenticated execution attestations.

Separate packaging checks passed: 53 deterministic bundle tests, five repository documentation checks, skill metadata validation, and generated-case consistency. The JSON reporter accepted this complete run against its recorded case digest. These checks establish different facts from the observed agent behavior.
