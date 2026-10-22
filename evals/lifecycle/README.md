<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Lifecycle incident replays

Four prepared cases, zero model results. Read [protocol.md](protocol.md) for
treatments, provenance limits, staging, scoring and the stopping rule.
[cases.json](cases.json) separates observed source incidents from injected
conditions. These are reduced Python adaptations, not full website checkouts.
They complement the older plugin cases without replacing their criteria.

From the repository root, using Python 3.12 and Git:

```sh
python3 -m unittest discover -s scripts -p 'test_lifecycle_evals.py' -v
python3 evals/lifecycle/suite.py digest
python3 evals/lifecycle/suite.py plan --seed 5772026
python3 evals/lifecycle/suite.py prepare resume-versioned-assets /tmp/replay-one --arm baseline
python3 evals/lifecycle/suite.py preflight /tmp/replay-one
python3 evals/lifecycle/suite.py grade /tmp/replay-one
```

The unmodified fixture should fail functional grading (exit 1) while smoke/build
preflight passes. Grading executes candidate code in a disposable copy; run it
inside the evaluator's sandbox. Exit 2 means invalid setup or command, not a
model outcome. No command calls models, installs dependencies or uses a network.

`prepare` refuses a nonempty destination and creates:

- `workspace/`: the only writable repository mounted for the worker;
- `state.json`: evaluator-side identity and phase state, outside the worker mount;
- `prompt-1.md`, and when applicable `prompt-2.md`: deliver only the current prompt.

For `--arm skill`, also provide `--skill-dir` pointing to the reviewed skill
bundle. Mount it read-only in the worker at the same path and compare its hash
with the recorded one. Other arms must not see it. All workers receive identical
repository bytes; treatment instructions are outside the tree. The CLI creates
directories, not OS access controls or an agent runner. Do not mount the whole
suite, reference solutions in tests or evaluator state into the worker.

For a two-stage case, preserve the actual first-session handoff and run:

```sh
python3 evals/lifecycle/suite.py prepare changed-archive-requirement /tmp/archive-replay --arm baseline
python3 evals/lifecycle/suite.py preflight /tmp/archive-replay
# After the first worker session ends, retain its final handoff and observe:
python3 evals/lifecycle/suite.py grade /tmp/archive-replay
python3 evals/lifecycle/suite.py advance /tmp/archive-replay
```

Use a fresh session with the same treatment, changed workspace, original handoff
and `prompt-2.md`. The earlier `resume-versioned-assets` example has one session
and correctly rejects `advance`. `mixed-review-unavailable-check` also has two
stages; it introduces
a nominally successful service response with zero completed reviews. No real
review service is contacted. An agent that truthfully leaves release blocked can
pass this case.

`snapshot` captures HEAD, dirty diff hash and file identities, including untracked
source. It does not authenticate command execution. Use host-observed traces for
the process review; [review-form.json](review-form.json) defaults unknowns to null
and process judgment to unmeasured. Never infer a process pass from a functional
grade. Historical `previous-check.json` is a genuine fixture smoke result on an
older revision, not independent approval of the new candidate.

[Reviewer calibration examples](reviewer-calibration.md) illustrate supported
handoffs and consequential failures for all four cases. They are authored
examples, not evidence that an automated judge is calibrated.

Tests exercise broken starts, reference repairs, targeted wrong repairs, missing
files, no-op/help-only commands, transitions and immutability. These validate
the deterministic setup and checks, not model behavior or cross-host isolation.
