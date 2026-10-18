<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Bounded harness learning

Use this optional procedure when asked to test a harness change or when a recurring
execution failure justifies one. A harness is the instructions, tools, context and
memory around a model. Keep model weights fixed. This is an adaptation of
[Harness²](https://github.com/google-research/harness2), not an implementation or
installation of its research runner. Ordinary fixes retain the normal delivery path.

## Define the comparison

Use the existing issue or PR to name the observed failure, one proposed harness
change, acceptance examples, and a stop condition before running candidates.
Record the source and instruction revisions, host, model, available tools and
time or cost limit. If usage telemetry is unavailable, say so. Extra execution
is part of the cost, not evidence of efficiency.

For a first pilot, use one baseline and one candidate in fresh isolated sessions
against the same task and starting tree, with the same model, tools, permission
boundary and per-run budget. Keep each run's edits separate. A useful task is a
bounded renderer repair with a known acceptance gap; a typo is not a reason to
run an optimization loop. Stop after that comparison unless the accepted scope
and remaining budget cover another. No candidate may publish, deploy, send
messages or change external state as part of a probe.

Choose acceptance checks before seeing candidate output. Keep any reserved
regression task and its judging evidence outside candidate context. Ordinary
repository requirements stay visible; do not conceal the actual task contract.
Do not expose benchmark answers or grading files through network or filesystem
access. Isolation must be enforced by the host; if unavailable, report that limit
and keep the experiment to read-only proposals or a safe local fixture.

## Propose, probe, compose

1. **Propose:** change one relevant instruction, context selection, tool guide or
   reusable skill. State why it might address the failure. Approval rules,
   permissions, acceptance tests and release gates are not optimization variables.
2. **Probe:** execute baseline and candidate, inspect actual outputs and traces,
   and compare acceptance failures, regressions, repair effort and available cost
   evidence. A proposed run is not an execution. Failed or timed-out runs remain
   visible; do not silently discard them from the comparison.
3. **Compose:** keep only changes supported by the contrast. Retain the baseline
   when the evidence is inconclusive. Any combined or further edited harness is
   a new candidate and needs its own checks; it does not inherit its inputs' pass.

Behavioral contrast can suggest a useful change when no ground-truth answer is
available. It cannot establish correctness. Keep independent review and the
receiving project's acceptance checks separate from the agent's self-assessment.
Compare at equal budgets before attributing a gain to the harness; a more costly
candidate may still be useful, but report the tradeoff.

## Retain a lesson, then test transfer

Before promoting a candidate to reusable guidance, exercise it on a different
reserved task and an ordinary case that should remain simple. Treat a single
successful comparison as a local signal, not a general productivity improvement.
If transfer evidence or an independent required check is unavailable, leave the
candidate experimental and the current default unchanged.

Persist a concise supported lesson in its existing project owner through the
normal review and merge path: trigger, action, source evidence, scope and limits.
Reference the run or revision instead of copying raw sessions. Replace a
superseded rule at that owner; do not append competing instructions or create a
second memory store. Task evidence stays with its existing PR or execution system.
Use a normal revert for an adopted lesson that causes regressions, preserving
the evidence and the project's existing recovery rules.

Continuous learning here means that later authorized tasks read reviewed lessons
and contribute new evidence. It does not create a daemon, schedule, recurring API
spend, automatic self-modification or a broader authority grant. Installing the
upstream runner is a separate integration task requiring an adapter for the
project workload, host-enforced isolation and an explicit execution budget.
