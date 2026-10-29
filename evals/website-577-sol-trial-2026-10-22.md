<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Website issue 577: three-arm Sol trial

All three treatments fixed the reading-time defect. No functional advantage for
this skill was demonstrated. A treatment-blind reviewer preferred the full-skill
candidate's regression implementation, but one task and one sample per arm cannot
establish a repeatable advantage, and cost was not measured.

## Design and boundaries

Task: [personal-website issue 577](https://github.com/Andreasniss/personal-website/issues/577),
one reading estimate shared across article HTML/Markdown, cards and related reading,
with a regression rejecting the original inconsistent outputs. Series and discovery
are additional existing consumers of the same estimate.

Three fresh sessions requested `gpt-6.1-sol`, with no conversation fork. Reasoning
was inherited rather than explicitly pinned. These are Work Mode subagent results,
not Codex CLI or native plugin discovery results. Each received the same task,
repository guidance, execution permissions and requested limits: 25 tool calls and
about ten minutes. Limits were instructions, not independently enforced counters.
Token counts, cost and comparable runtime measurements were unavailable.

- A: repository guidance only.
- B: repository guidance plus a short checklist: inventory consumers and acceptance,
  reproduce, make the smallest shared repair, show red/green, inspect the diff,
  report evidence and limits.
- C: repository guidance plus the full local AI SDLC skill and relevant references.

The user authorized an evaluation-only override of the website's mandatory skill
routing. A and B did not load it; C loaded the supplied local skill instead of the
website's older external pin. The website's separate bounded pilot was excluded
for all arms. All other repository requirements remained. Workers could not push,
merge, use external services or start more agents. Independent review followed
candidate completion. No candidate received reviewer repair coaching or reruns.

Each worked in its own safe local fixture directory on a shared filesystem.
Cross-arm access was forbidden in the prompts, not isolated by the operating system.
All three initial Git trees were identical:
`7fc7ebe277e55fc6e05038504bdd2bb0731af117`.
The reconstructed snapshot had 1,334 files verified against Git blob hashes and
90 missing files, largely images. It was not a complete checkout.
Skill source commit: `ea85d5d5577d8e48953c985e012fd81ceaf8baf2`.
Skill tree: `aacd3bf1380f112041018917ec5ed21c8efcb6ec`.

## Setup failures retained in the record

Direct Git authentication was unavailable. The connected service returned empty
large binary contents and rejected a blob retrieval as non-UTF-8. Missing files
were not replaced with placeholders. The pinned Hugo render and existing built-site
validator nevertheless passed, allowing this bounded text-output comparison.

Restored executables were truncated between commands. Hugo was observed at
34,030,080 bytes versus 62,578,816 bytes in the package. Every arm encountered the
same crash and received the same correction: extract the pinned package inside
each invocation and execute from its temporary directory. This restored Hugo
0.168.0. Node 22 similarly failed after restoration; all arms used available Node
24.19.0. Arm B also had one transient exec transport failure, resolved before edits.
These are infrastructure limitations, not model outcome failures.

## Independent artifact checks

Before dispatch, the evaluator fixed an output checker that maps article bylines
to their HTML and Markdown consumers. Its URL normalization was corrected before
dispatch to recognize Markdown index links. The baseline had 29 article parity
mismatches and 56 Markdown consumer mismatches. The old built-site validator passed.

After completion, the same independent checker covered 66 article pairs,
267 HTML consumer estimates and 131 Markdown consumer estimates for every arm.
It found zero mismatches in each. Every candidate's new validator also passed its
final output and rejected the original baseline output.

| Observation | A: repository | B: checklist | C: full skill |
| --- | --- | --- | --- |
| Independent final output checks | Pass | Pass | Pass |
| New validator rejects original baseline | Yes, 85 findings | Yes, 29 findings | Yes, 55 findings |
| HTML card changed to 999 minutes is rejected | Yes | No | Yes |
| Markdown card changed to 999 minutes is rejected | Yes | No | Yes |
| Existing built-site checks on final output | Pass | Pass | Pass |
| Changed files | 13 | 12 | 13 |

The card mutations were supplementary robustness probes, not newly imposed
acceptance criteria. They were restored before final validation. Finding counts
are not scores: the validators cover different surfaces and may report overlapping
symptoms. The source-based estimate was explicitly allowed; exact equality with
Hugo's previous estimates was not required. All candidates cache a shared
source-based calculation at 212 words per minute with a one-minute minimum.
A strips shortcode syntax; B and C include shortcode configuration in the count.

## Treatment-blind review

A fourth fresh Sol session read anonymized patches and validator/helper sources,
without treatment identities or author reports. Mapping was candidate 1 = B,
candidate 2 = C, candidate 3 = A. It found no acceptance blockers and favored C's
checker overall. This is another same-model assessment, not independent proof.

Its nonblocking observations were:

- B's regression protects article parity but not linked consumer estimates.
- A skips missing HTML bylines and can accept a later Markdown estimate when the
  article's own metadata is missing. Its linked checks ignore URL origin.
- A and C generally detect incorrect existing linked estimates, but do not ensure
  every expected card estimate remains present.
- C retains explicit missing-single checks and filters external URL origins.

No trial code was repaired after this review. These findings remain recorded here
for any later implementation selection, rather than being silently folded into
this experiment's results.

## Verification limits and retained candidates

All workers reported missing-asset failures in the source and full production
gates. Negotiation unit checks passed; A and B also reported Wrangler integration
blocked by `uv_interface_addresses`. No worker claimed a completed independent
review or browser inspection. The evaluator confirmed final clean working trees,
actual local commits and the output checks above. Complete per-call traces and
usage telemetry were not retained, so every self-reported command was not audited.
Nothing was merged or deployed. The candidates remain local trial commits:

| Arm | Branch | Commit |
| --- | --- | --- |
| A | `trial/577-arm-a` | `f64330fd2a2599f1c387a7d25aaf26ce7aa336bd` |
| B | `trial/577-arm-b` | `fe6707570b44fdf8a3380eeb7944ad67ec3766b8` |
| C | `trial/issue-577-arm-c` | `74a9ce5acfe13cbdc874a720f3a09b937558ea19` |

These hashes are local fixture commits, not upstream website commits. Raw sessions
and private website source are not included in this public report.

## Interpretation and next decision

This realistic task again shows that repository guidance alone can produce a
correct repair. The full skill had a small qualitative advantage in reviewer
preference, while the baseline also produced broad regression coverage. The
checklist's narrower regression still met the original acceptance requirement.
The result does not justify a performance claim, a production release, expanding
the skill, or declaring the checklist superior. Keep existing guidance unchanged.
A later, separately bounded transfer case involving a real handoff or stale
verification would be more informative than repeating increasingly difficult
feature work until a preferred treatment wins.
