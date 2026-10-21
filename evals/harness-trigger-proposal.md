<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Harness and discovery proposal

This candidate starts from `eb9bba9` on `plugin-eval-multistage`, for issue #27 and
PR #31. It changes the harness and only the description line in SKILL.md. It does
not change case prompts, criteria, expected lines, or references. No model run is
part of this change. New run settings remain unconfirmed.

## Read-only investigation

The maintainer reports four ship-ready runs with no edits and a reported read-only
workspace, out of ten runs across both arms. Raw traces for that run are not in
this checkout, so this report does not establish that the kernel returned EROFS.
An agent's explanation alone is not proof of the mount state.

The scaffold invokes `make_fixture.py --into .` in the supplied workspace. The
renderer sets modes only on generated eval files: 0644 for prompts and graders,
0755 for scaffold scripts. `fixture_files()` reads text from temporary fixtures;
it does not stage Git metadata into the evaluated workspace. The builder creates
files with mkdir/write_text and Git init/add/commit. It sets only local Git author
name and email. It contains no chmod, chown, mount, safe.directory, core.fileMode,
hook or lock-file changes. Standard Git object files can be read-only without
making the worktree or branch refs read-only.

All three states use that path. Ship-ready stays on main, while the other two
already have feature branches. That difference makes branch creation a useful
probe, but does not explain a read-only worktree. Ambient Git templates, hooks,
configuration, filesystem permissions and the eval host's later sandbox setup
remain possible external influences. safe.directory errors and stale lock errors
must not be relabeled as read-only mounts.

The generated scaffolds now run `scripts/check_eval_workspace.py`. It creates and
removes a temporary file, opens and writes existing fixture files, creates and
switches a temporary branch, then restores the original branch and deletes the
probe branch. It neither changes permissions nor disables a sandbox. It reports
only a sanitized status, failing stage and error category. A failed probe fails
the scaffold. Regression tests also copy fixtures with modes preserved, edit and
stage app.js, and create a fresh branch in both rendered trees for every case.

This establishes writability at staging time only. The documented scaffold runs
outside the agent sandbox. A later read-only bind mount cannot be repaired by a
chmod in the fixture. No repository-controlled cause has been reproduced; the
precise host-side cause remains unresolved pending inside-sandbox evidence.

## Description candidates

These candidates use implementation, review and requirement-change categories,
not the wording or filenames of the three outcome prompts. Exact description
strings and the selected candidate are in
[trigger-prompts.json](../skills/ai-sdlc-skill/evals/trigger-prompts.json).

1. **Action-led, selected.** Starts with implement, fix, address review feedback,
   and adapt changed requirements. It explicitly requires nontrivial work with
   verification and a reviewable handoff. It retains project setup and delivery
   adoption, while excluding mechanical edits, explanations and standalone README
   writing. This is the most direct discovery cue without making every edit an
   SDLC task.
2. **Outcome-led.** Leads with making software work reviewable. It is compact and
   preserves the scope boundary, but a user may ask for a fix without mentioning
   reviewability, making its entry cue less direct.
3. **Continuation-led.** Emphasizes carrying ongoing work through testing and
   review. It fits repair and changed-scope work well, but could under-trigger for
   a fresh implementation request.

These are hypotheses, not measured improvements. The selected description is an
unreleased proposal on the existing 0.5.3 development tree, not a newly validated
release. The rest of SKILL.md and all references remain byte-identical.

## Held-out trigger check

The separate JSON has ten positive and four negative prompts using other domains.
Freeze it before any test, and do not use its results to tune these descriptions.
A later authorized cheap run should give each prompt a fresh session, identical
skill availability and tool permissions, and no forced invocation. Record actual
Skill tool calls for this skill, not a model's promise to use it. Report positive
trigger rate and negative false-positive rate separately, including individual
misses and counts. Compare the old description with the proposed description on
the same prompts and settings. This checks discovery only, not delivery quality.
If results drive another edit, use a new held-out set to test that edit. Model,
run count, cost cap and timing still require maintainer selection.

## Records affected

- The new description and trigger JSON change the skill tree hash. Every future
  run must record the new `git rev-parse HEAD:skills/ai-sdlc-skill` value.
- Harness fixes change both rendered eval digests. Capture them again for a new
  run. Keep the cases digest and old run records as historical evidence; do not
  rewrite historical scores or settings to refer to this candidate.
- evals/README.md documents the unresolved sandbox boundary and classification.
  The cases.md renderer is rerun, even though the criteria remain unchanged.
- Before releasing a new version, update metadata.version, the bundle README,
  references/adoption.md, the root README's canonical version and release notes,
  and plugin.json, .claude-plugin/plugin.json and .codex-plugin/plugin.json
  together. This proposal deliberately leaves that release-wide version bump
  pending to preserve the requested one-line SKILL.md and unchanged references.
- There is no CHANGELOG file. README.md holds release notes. Documentation and
  packaging consistency tests must pass for this proposal and again at release.
- A later behavioral run must be recorded before claiming the new description
  improves invocation or preserves host behavior. Deterministic tests do not
  establish either claim.
