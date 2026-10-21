<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Codex subagent pilot: explicit skill versus baseline

The six-run exploratory pilot found no functional advantage on the checked
acceptance behaviors. Both arms passed all 14 parent-authored behavior checks
across three cases. The skill-assisted review run preserved the reviewer's status
header; the baseline changed it while still explicitly denying approval. This is
one observed process difference, not evidence of a repeatable performance gain.

## Design fixed before execution

The user authorized this pilot after being told that native Codex CLI/plugin
execution was unavailable and that fresh Codex subagents would be used instead.
One fresh session per case and arm ran the unchanged prompts from cases.json:

- ship-ready-feature
- review-round-repair
- requirement-changed-mid-flight

Each pair started from copied, identical fixture files and Git history. Sessions
received no parent conversation history. Both arms received the same workspace
boundary, local-tool restriction, requested 30-tool-call and 10-minute limits, and
request to report actual changes, checks, revisions and limitations. The with-skill
arm additionally received the bundle location and an instruction to read SKILL.md
and relevant references. The baseline received no skill location or instruction.
Workers could not push, merge, use external services, or start further agents.
There was no intervention, repair coaching, or rerun after an outcome was seen.

All six used the same inherited model and reasoning configuration, with no model
overrides. The host does not expose the exact runtime model ID in the available
agent-management results, so this report cannot name or pin it. This is a Codex
Work Mode subagent observation, not a result for a named Codex CLI/API model.

The limits were instructions, not independently enforced counters. Workspaces
were separate directories on a shared filesystem, with explicit read boundaries,
not separate OS sandboxes. Shared host instructions and tools were present in both
arms. No native plugin was installed or ablated. Skill loading was explicitly
requested; independent activation telemetry is unavailable. This does not measure
automatic discovery or the proposed description's trigger rate.

## Source identity

- Published source commit: `bccde726a52dd9107c9c83388579841b69b34bee`
- Locally tested source commit: `25fc8b76879243fc972fdb130dc714e8245f16c7`
- Identical source tree: `ee20a8b3edf9ed88fc55f0b1103907355a1cdabb`
- Skill tree: `aacd3bf1380f112041018917ec5ed21c8efcb6ec`
- Cases digest: `bc492a8804f96927ee3a3efcc06a975b7963f34d93df277ef7500fc0581c1826`
- Natural grader digest: `ad87f2c3e7855d01608a9544c36a42584c5e1d3c3250184b277e09b695bf26b9`
- Forced grader digest: `7ddbfdb4d7b3d7df9548fad44759d7339050f11b99c9cd3e1c866124a17383b1`

The two source commit IDs differ because publication used the connected GitHub
service after CLI push authentication failed. Their file trees are identical.
The pilot did not change case prompts, criteria, expected lines, skill contents,
or graders. The other 27 behavior cases and the held-out trigger prompts were not run.

## Observed results

The parent reran `node --test test/tasks.test.js` in every finished workspace.
It also executed each final app.js with a separately authored minimal DOM and
localStorage double. Those checks were prepared from the fixture requirements
while workers ran, before inspecting their completed implementations. They verify
JavaScript behavior, not real-browser layout, accessibility, or rendering.

| Case | Baseline behavior checks | With skill behavior checks | Baseline authored tests | With skill authored tests |
| --- | --- | --- | --- | --- |
| ship-ready-feature | 6/6 passed | 6/6 passed | 9/9 passed | 8/8 passed |
| review-round-repair | 3/3 passed | 3/3 passed | 8/8 passed | 15/15 passed |
| requirement-changed-mid-flight | 5/5 passed | 5/5 passed | 13/13 passed | 9/9 passed |

Authored test counts describe differently grouped suites; more tests do not by
themselves indicate better coverage. Parent checks covered:

- Search: control placement, case-insensitive input updates, composition with
  open/done filters, empty query, completion of only the selected duplicate ID,
  and reload reset without search persistence or changed stored task order.
- Export: exact membership, displayed order and CSV quoting under all/open/done.
- Undo: clear persistence, restored original positions and completion flags,
  reload making removal permanent, empty clear, and unchanged filter selection.

All six produced commits and clean working trees. Each check record names an
existing implementation revision. Inspection of the difference from that revision
to final HEAD found only docs/check-results.md changes in every run. The parent's
reruns passed on final HEAD. The fixture AGENTS.md remained unchanged in all six.
No runtime write failure was observed in this host; that does not resolve the
previous Claude sandbox failure.

Both review runs fixed F1/F2 and declined F3 using the owner's displayed-order
requirement. Neither claimed reviewer approval. The baseline replaced the header
with `Status: findings addressed; awaiting reviewer re-review (no approval)`. The
skill-assisted run retained `Status: changes requested` and added author responses.
The latter preserves ownership of reviewer state more clearly.

Both undo runs replaced the old permanent-removal decision and marked earlier
checks as historical. Both handled repeated clears and reserved removed IDs.
The baseline copied the whole browser module into app-under-test.js and guarded
its startup; the skill-assisted run retained the smaller test-module structure.
Both passed the checks. This implementation difference is not a measured gain.

## Frozen grader diagnostics

The existing file-regex graders were evaluated with Node's real RegExp engine
against final artifacts. These are unweighted diagnostic counts only. Tool-use,
trace-order, skill-fired, unchanged-file and LLM graders are not included; no full
plugin-eval score or cross-host delta is claimed.

| Case | Baseline file regex checks | With skill file regex checks | Explanation |
| --- | --- | --- | --- |
| ship-ready-feature | 13/14 | 13/14 | Both fail search-test-identity despite working duplicate-title DOM-event tests. |
| review-round-repair | 10/11 | 11/11 | Baseline fails status-kept; with-skill run retains the reviewer header. |
| requirement-changed-mid-flight | 12/12 | 12/12 | All evaluated file regex checks pass in both arms. |

The search failure is a verified grader false negative. One run builds duplicates
with an array reduce; the other uses a shared fixture array. Both drive the actual
search and task-click handlers and assert stored completion state and IDs. The
regex recognizes narrower construction, searchTasks and direct complete-call
patterns, so it rejects these valid tests. Parent behavior checks independently
confirmed the duplicate-selection behavior. The grader remains unchanged in this
pilot; changing it after seeing these results would create a different harness
revision requiring its own validation.

The baseline review header change is a real difference, not a regex false
negative. However, the baseline still explicitly denies approval, so this does not
establish an invented-approval disqualifier.

## Evidence boundaries

The parent inspected code, tests, decisions, review records, Git history, revision
references and working-tree status, and independently reran the final tests.
Worker reports also describe initial reads, regression reproduction, pre-commit
tests and self-review. Those execution-order claims were not independently audited
against complete traces. The parent cannot certify every frozen process criterion
or the absence of every disqualifier across the entire session. Do not turn the
artifact results into an all-criteria pass or an authenticated review verdict.

The synthetic run commits below identify the local evaluated artifacts. They are
not published repository commits and are not expected to resolve on GitHub:

| Run | Case/arm | Final local revision |
| --- | --- | --- |
| 01 | Search, baseline | `bf64c9914bdd6d3ef725d43c4423141eb793c324` |
| 02 | Search, with skill | `0d251b86daf49b8e99cbd4ad055c578c22a5e649` |
| 03 | Review, baseline | `0792eac94efd7b0006bc34927292a763b173d418` |
| 04 | Review, with skill | `14b9bbd3a66143518083fcb95b1d6e6a34ce6ca2` |
| 05 | Changed requirement, baseline | `e3375f2acff9a0bee2577e4639d491ac2c5258d8` |
| 06 | Changed requirement, with skill | `9a62cd7ea0666132a5a219188ebe5282130f36a7` |

Raw worker sessions, temporary paths and run artifacts are not published. This is
a reviewed summary, not a replayable trace archive. Token counts, model cost and
reliable per-run latency are unavailable; no efficiency claim is made. No separate
paid API setup or model judge was used.

## Interpretation

The baseline already succeeds on the checked functionality. This pilot therefore
has a ceiling problem for detecting added functional value. The reviewer-state
observation is a useful hypothesis to retest, but one matched run per case cannot
separate a skill effect from ordinary sampling variation. These results cannot be
compared numerically with the earlier Haiku scores, because the host, grading
coverage and execution conditions differ.

The next useful measurement remains a separately configured, native-host run with
an identified model and recorded traces, plus the held-out discovery test. Review
and validate support for DOM-event-based identity tests before interpreting that
regex as a quality measure. Do not tune the skill against these six outputs or
represent this partial pilot as a full behavior-suite pass.
