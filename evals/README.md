# Plugin evals for Claude Code

This directory is the behavior case set rendered for
[`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals), so a run can report how Claude
Code scores **with** the `ai-sdlc` plugin, **without** it, and the difference (Δ), case by case.
It automates [evaluation.md](../skills/ai-sdlc-skill/references/evaluation.md) for one host. Other
hosts still need a manual run.

Each `evals/<case-id>/` holds `prompt.md`, `case.yaml`, `scaffold.sh` and `graders/`. All of it is
generated: [`cases.json`](../skills/ai-sdlc-skill/evals/cases.json) stays the single source for
prompts, fixture states, `expected` lines and disqualifiers, and
[`scripts/plugin_eval_spec.py`](../scripts/plugin_eval_spec.py) adds the graders. Change those and
render again; never edit a generated file.

```sh
python3 scripts/render_plugin_evals.py            # write evals/<case-id>/
python3 scripts/render_plugin_evals.py --check    # verify the tree is current; CI runs this
python3 scripts/render_plugin_evals.py --forced  # write evals-forced/ (add --check to verify it)
python3 scripts/render_plugin_evals.py --digest   # sha256 of the rendered tree, for a run record
python3 scripts/render_plugin_evals.py --summary  # grader inventory per case
python3 scripts/test_render_plugin_evals.py       # no model calls
```

## What is rendered

Three of the 30 cases, each needing several stages and carrying a trap that shows up only if state is
tracked across them: `ship-ready-feature` (request to a reviewable branch under written project rules),
`review-round-repair` (three review findings, one to decline with a reason from the repository, and a
stale check record) and `requirement-changed-mid-flight` (the owner widens a request after work started,
contradicting an accepted decision and an earlier check record). The generator refuses a case the spec
does not grade.

The first eight rendered cases (single stage, 7 to 22 turns) are kept as `RETIRED_CASES` in the spec and
are not rendered. Haiku scored 0.86 to 1.00 on them without the plugin, so they could not show a difference;
see [the rerun record](plugin-eval-run-2026-10-21-rerun.md). Move one back into `CASES` to render it again.

`evals-forced/` is the same set with one difference: each prompt appends "Use the ai-sdlc-skill skill
(AI SDLC Skill) for this task." to the agent's system prompt. Run `evals/` to see whether the model finds
and uses the skill by itself, and `evals-forced/` with `--ablation none` to see what the skill's content
adds when it is used. Compare the forced arm with the natural run's no-plugin arm, and leave the
`skill-fired` indicator out of both scores.

Graders, in order of preference:

1. **Deterministic.** `tool_used` and `regex` over the session, `file_exists`, and regex checks on
   the files the run leaves behind, including an exact-content check that a file was not touched.
   The test suite proves each pattern with samples and with real JavaScript regular expressions, and
   proves each outcome check fails on the unmodified fixture, before any paid run.
2. **Sonnet rubrics, only where judgment is needed.** One rubric grades what the final report says;
   one grades the five disqualifiers from `cases.json` over the session excerpt. A rubric never
   mentions the skill or the plugin, so the judge cannot tell the arms apart.
3. **A skill indicator** (`tool_used: Skill`, `arm: with-only`) that shows whether the skill fired and
   never counts toward the score.

Every `expected` line is covered by a grader or carries a stated reason; the generator refuses a spec
that leaves one unaccounted for. The generated comment in each grader names the line it covers.

The [Codex subagent pilot](codex-subagent-pilot-2026-10-21.md) separately compares
explicitly supplied skill instructions with a baseline on the three cases. It is
not a native plugin-discovery test or a score comparable to these Claude runs.

The separate [lifecycle incident replay pack](lifecycle/README.md) prepares four
complete, dependency-free cases for a future baseline/checklist/full-skill
comparison. It includes an ordinary control, an interrupted handoff, a changed
requirement and mixed review with an unavailable service. Its deterministic
fixture and grader checks call no models. These are reduced incident adaptations,
not production website reproductions. The [protocol](lifecycle/protocol.md)
fixes staged delivery, scoring, overhead measures and stopping rules before runs.
Existing plugin case criteria and historical results remain unchanged.

## Running it

This is manual and every run is billed to your account. Nothing in CI calls a model.

Requirements: Claude Code 2.1.269 or later, git 2.31 or later, and on Linux `bubblewrap` and `socat`
for the Bash sandbox. `claude plugin eval` runs `scaffold.sh` only with `--scaffold`, as you and outside
the agent's sandbox; use that flag only on this generated suite.

```sh
claude plugin eval . --scaffold --trust-plugin \
  --model claude-haiku-5-5 --judge-model claude-sonnet-5-5 \
  --runs 3 --ablation with-without --threshold 0.8 --max-cost-usd <cap> -j 3 \
  --no-publish --output-dir <directory> --json <directory>/run.json \
  --allow-tools Write Edit Bash
```

`--allow-tools Bash` grants sandboxed Bash in general. A list of narrow patterns such as `Bash(git:*)` did not
cover compound commands, pipes and redirects the agents naturally use: the recorded run of 2026-10-21 used such a
list and logged 36 permission denials in 14 of 16 case-arms, so some runs could not run their checks. The
OS sandbox, not the pattern list, is what contains the commands.

For the forced-use variant add `--eval-dir evals-forced --ablation none` and drop `--ablation with-without`.
Add `--case <id>` for one case. Pin the models and set a cost cap before you start; the cap is a
list-price estimate, not your plan usage. Record the caps, cases, `--runs`, threshold, models and judge
somewhere reviewable before the full run, so the result cannot be tuned afterwards.

A run record names the skill revision (`git rev-parse HEAD:skills/ai-sdlc-skill`), both digests
(`eval_report.py --digest` for the cases, `render_plugin_evals.py --digest` for the graders), the Claude
Code version, the models, the actual cost and the limits. Results belong under
`evals/plugin-eval-run-<date>/` with a short `evals/plugin-eval-run-<date>.md`.

## Workspace failure classification

The scaffold runs [check_eval_workspace.py](../scripts/check_eval_workspace.py)
after building the fixture. It tests actual file writes and a temporary Git branch,
then restores the starting branch. A blocked result aborts setup. The test runs as
the scaffold user, outside the agent sandbox; it cannot certify a later mount.
See the [investigation and description proposal](harness-trigger-proposal.md).

For the next authorized run, retain the scaffold status and inspect actual tool
results in each arm locally. Classify each attempt separately from its outcome score:

- **Setup blocked:** the scaffold write or branch probe failed. Do not treat this
  as a completed agent trial.
- **Runtime write blocked:** an attempted file or Git write in the agent sandbox
  failed with a concrete filesystem or permission error. Preserve the operation,
  error category and arm in the sanitized run record. If needed, run the same
  probe inside that sandbox through the host's supported diagnostic route.
- **No work, environment unverified:** only the agent claims a read-only mount,
  with no failed write result. Do not infer EROFS from that claim.
- **Writable:** actual runtime writes succeed. Score the work normally.

Keep all attempts and raw outcome scores visible, with counts for each category
per arm. Report environment-blocked attempts separately; any secondary comparison
on writable attempts must disclose its denominator and exclusions. Do not silently
drop failed attempts or convert them into a skill failure or success. Keep raw
traces local and publish only reviewed, sanitized evidence. Do not remount,
disable the sandbox, or broaden permissions to obtain a passing result.

## Limits

- A successful scaffold probe does not establish runtime writability. The reported
  intermittent read-only failure is not reproduced by local fixture tests; its
  host-side cause remains unresolved.
- One host: Claude Code. Nothing here says another host behaves the same way.
- A Claude model judges Claude runs. Deterministic graders carry most of the score for that reason.
- Fixtures are synthetic, small and public.
- A few runs per arm is a small sample; a Δ of a few points is within run-to-run noise.
- A case whose graders pass in both arms shows where the skill adds nothing for this host, and is
  reported that way. Guards that pass in both arms also pull every score and every Δ toward zero.
- The judge sees an excerpt of long transcripts, so the disqualifier rubric can miss what happened
  in the middle of a session. Deterministic graders cover the checkable parts of the same ideas.
- End state is read from files and tool calls. The graders cannot run the fixture's tests or a
  browser, so a passing score does not prove the repaired code works.
- The review-only case catches edits through the `Edit` and `Write` tools and common mutating shell commands. An
  edit made some other way through Bash, for example `cat > file` or a `python3 -c` write, is not caught by the
  tool-count graders, and the case has no end-state check because switching branches legitimately changes files.
  In the recorded run no review run made such an edit; that was checked by reading the traces.
- The multi-stage cases check that undo is wired, not persisted and asserted in a test, but no grader runs the
  code. Whether undo restores tasks to their original positions rests on the agent's report and the judge.
- The search case rejects writing the query to storage under an obvious name. It does not inspect stored values, so
  a query folded into the stored task data would not be caught. Automated review kept finding another way a regex can be
  fooled, so the remaining gaps are accepted and the judge reads the final session. Known ones: the case-insensitive
  check can be met by lowercasing two unrelated strings, and the render and empty-search checks follow data flow
  by pattern only, so an unusual code shape can pass or fail them wrongly.
- Listener, duplicate-title and membership graders recognize common inline JavaScript
  forms. Named callbacks, deeper nested blocks, custom factories and assertions can
  require manual inspection. Regexes do not prove data flow or executable behavior.
- Cost figures are list-price estimates from the tool.

These files carry the repository's [Apache-2.0](../LICENSE) license and [NOTICE](../NOTICE).
