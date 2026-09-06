# Adopt without replacing the repository

Version 0.2.0. The skill is portable text with an optional Python 3.10+ helper for POSIX systems. Claude Code and Codex interactive installation behavior must be verified in the user's runtime; repository-level pilots do not establish identical runtime behavior.

1. Review the bundle at a pinned Git commit. Inspect existing skills, instructions, hooks, CI and licenses.
2. Use the runtime's documented skill-installation mechanism, or copy the folder into its supported skill directory only if the destination does not exist. Do not overwrite a same-named skill or replace AGENTS.md, CLAUDE.md, hooks or permissions. Keep the source revision with the installation record. This bundle does not install hooks.
3. For repository use, keep it under `skills/ai-sdlc-skill/` and link SKILL.md from existing instructions. This is an explicit repository routing link, not proof of automatic skill discovery.
4. Run a bounded change and compare behavior with existing requirements. Keep check commands in a repository-owned configuration; review them as executable code before use. Never run an untrusted PR's commands with secrets or deployment credentials.

## Optional verification report

A configuration contains one non-empty `checks` list. Each entry has a unique `name`, an `argv` array of non-empty strings, and an optional positive integer `timeout_seconds` (default 300, maximum 1800). Unknown keys are rejected. All checks must exit zero. Configuration must be a tracked regular file within the clean target repository.

```json
{"checks": [{"name": "application", "argv": ["npm", "run", "verify"], "timeout_seconds": 600}]}
```

Commit the candidate and run from the repository root:

```sh
python3 skills/ai-sdlc-skill/scripts/verify.py --config delivery-checks.json
```

The helper prints only status, check names, return codes, timestamps, and revision/configuration identity. It discards child output to avoid publishing secrets or oversized logs. Diagnose failures separately with the reviewed command in a suitable local environment. Reports are local attestations and can be fabricated by anyone with write access. Protected CI should rerun the checks independently; never use a supplied report as release approval.

Exit 0 means every configured command succeeded and the non-ignored repository state was clean at the same revision before and after each command. Exit 1 means a check failed or the candidate changed; exit 2 means invalid setup. Transient changes restored before a command exits, ignored build outputs, and external state are not covered. `candidate_unchanged` reports these endpoint checks, not continuous observation. This is not a sandbox: commands inherit environment and privileges, can access networks, and may have side effects. Do not include deployments, destructive actions, or credentials in check configurations. A check that tests the wrong property can still pass.

If a check invokes a model, that wrapper must explicitly fail when the model is unavailable and validate its output. The helper only sees the wrapper's exit code. Live-model quality, human review, authenticated approvals and application runtime authorization remain separate.

## Pilot measures

Record the selected workflow depth and its reason; required versus unnecessary interruptions; requirement misses; failed or unavailable checks; fresh-review findings and fixes; and exact candidate revisions. Separate measured outcomes from planned measurements. Two repository adaptations alone cannot establish faster delivery or lower defect rates.
