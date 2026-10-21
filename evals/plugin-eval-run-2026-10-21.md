---
type: plugin-eval-run
date: 2026-10-21
issue: 27
---

# Plugin eval run, 2026-10-21 (stage 2, Haiku with and without the skill)

Result of `claude plugin eval` on the 8 rendered cases, as observed. Nothing was tuned after the
plan was recorded in PR #29. Raw output: [`plugin-eval-run-2026-10-21/aggregate-result.json`](plugin-eval-run-2026-10-21/aggregate-result.json)
and [`report.html`](plugin-eval-run-2026-10-21/report.html).

## Run record

| Item | Value |
|---|---|
| Skill under test | tree `fd4c9158e83ee0a9a30ed468ecf26d9702d7eb2d` (`git rev-parse HEAD:skills/ai-sdlc-skill`), plugin 0.5.3 |
| Cases digest | `1d0e419b8ad1a343000e38acb6694488e936e7116485e5d51cbd557cee7c354e` (`eval_report.py --digest`) |
| Graders digest | `d29bed225e6339ae85783547c43d1d80ac283b1f6a0957d1a96a8f0f0f130e4b` for the run (`render_plugin_evals.py --digest`). The tree on this branch now has digest `3a3bbf5e2aa9f9ed092baabb0f1fa72a489f3996c92785281cfa6fa1e6c9ca2b`, see below |
| Claude Code | 2.1.306 |
| Agent model, judge | `claude-haiku-5-5`, `claude-sonnet-5-5` |
| Settings | 8 cases, `--runs 3`, `--ablation with-without`, `--threshold 0.8`, `-j 3`, cap `--max-cost-usd 15` |
| Actual cost | $7.04 for the full run (tool estimate at list price, judge included); about $0.45 for two smoke runs |
| Duration | 778 seconds, not partial, no run errors |

The plan (caps, cases, runs, threshold, models) was confirmed by the maintainer and recorded in PR #29
before any run. No case criterion or grader was changed after the smoke run.

## Result

| Case | With | Without | Δ | Skill fired (with arm) |
|---|---|---|---|---|
| blocked-export-handoff | 0.86 | 0.86 | 0.00 | 0 of 3 |
| browser-feedback-unavailable | 1.00 | 1.00 | 0.00 | 0 of 3 |
| bug-with-reproducible-symptom | 0.87 | 0.87 | 0.00 | 0 of 3 |
| csv-plausible-wrong-output | 0.94 | 0.83 | +0.11 | 0 of 3 |
| feature-interaction-preserves-order | 0.80 | 0.80 | 0.00 | 0 of 3 |
| refactor-without-behavior-change | 0.96 | 0.96 | 0.00 | 0 of 3 |
| resume-interrupted-change | 0.87 | 0.87 | 0.00 | 3 of 3 |
| review-without-edits | 0.81 | 0.81 | 0.00 | 3 of 3 |
| **Mean** | **0.89** | **0.87** | **+0.01** | 6 of 24 runs |

Pass rate at threshold 0.8, as the tool reports it: with arm 0.38 overall. Per case the with arm passed
2 of 3 runs on bug-with-reproducible-symptom, csv-plausible-wrong-output and refactor-without-behavior-change, and
3 of 3 on browser-feedback-unavailable. The without arm passed 2 of 3 on refactor and 3 of 3 on
browser-feedback-unavailable, and none on the other cases. The threshold affects pass counts only, not scores.

## Changes to the graders after the run

A code review found that the six exact-content ("unchanged file") graders ended their pattern with `$`, which also
accepts the original text plus one trailing newline. They now end with a true end-of-input assertion, so the tree
digest changed. This is a correctness fix, not a tuning of any case criterion. I checked all 48 kept run workspaces
against the fixtures: 93 files differ from their fixture, none of them only by a trailing newline, so no score in this
run would change. The scores above were produced by the graders with the first digest and were not recomputed.
The run's `--allow-tools` list is also documented differently in `evals/README.md` now (see the audit notes).

## Reading it

- **The skill adds nothing measurable here.** Mean Δ is +0.01, and seven of eight cases have Δ of exactly zero.
  The one positive case (csv, +0.11) is a difference of one check in one run, with 3 runs per arm.
- **Haiku rarely invoked the skill.** It fired in 6 of 24 with-arm runs, all in two cases. In the other six cases the
  with arm behaved like the without arm, so those Δ values say little about the skill's content, only that Haiku did
  not use it. That is itself a finding about Haiku plus a skill it is not prompted to call.
- **Where the skill did fire (resume, review) the scores matched the without arm exactly.**
- **Do not read this as Haiku plus the skill matching Sonnet.** Stage 2 ran Haiku only and cannot show that.
- Differences inside a run-to-run spread of a few points are noise at 3 runs per arm.

## Limits and caveats

- `report-quality` failed in most runs of both arms (for example 3 of 3 in both arms on four cases), which
  pulls every score and Δ toward zero. The judge returns votes only, so the run cannot say whether the rubric is too
  strict for Haiku reports or Haiku reports are weak. The rubric was not changed; see the audit notes below.
- The eval sessions listed the Claude in Chrome tools. In `browser-feedback-unavailable` no run attempted browser
  tooling (score 1.00 in all six runs), so the case was not distorted in this run.
- Only checks the graders can observe are scored. They cannot run the fixtures' tests or a browser.
- Single host (Claude Code), synthetic fixtures, one model family judging itself.
- Audit against the claude-api `eval-audit.md` guide, read after the run (it lives at
  `skills/claude-api/shared/evals/eval-audit.md` in the public anthropics/skills repository). Findings that matter for
  reading the numbers:
  - **Bash permission denials:** 36 tool results across 48 runs were "denied, don't ask mode", in 14 of 16 case-arms.
    The `--allow-tools` grants did not cover every command the agents tried (compound commands, for example), so some
    runs could not run the checks they wanted. This limits both arms and is a harness effect, not model behavior.
  - **Shell wrapper error:** every run logged a "Read-only file system" error from the shell's working-directory
    tracking file, which makes Bash report exit code 1 on commands that ran.
  - **Judge not calibrated:** `report-quality` failed in 33 of 48 runs. No human-labelled calibration or spot-check was
    done before the full run. One failing report read afterwards (feature-interaction-preserves-order) looks like a
    plausible pass, so the judge may be too strict. Unverified.
  - **Mechanism barely engaged:** the skill fired in 6 of 24 with-arm runs, so in six cases the eval did not exercise
    the skill's content.
  - **Noise floor:** the delta of +0.01 has a standard error of about 0.014 across cases (95% interval about
    plus or minus 0.03), with 3 runs per case and arm. The headline recomputes from the raw rows.
  - **Fine:** the served model was `claude-haiku-5-5` in all runs, no run errored, judge cost is recorded
    separately, full traces were kept, and every case and arm started from a fresh scaffold.
  - **Not done:** an oracle run (a known-correct solution through the graders) and a judge check on known negatives.
- The result files had local user-directory path segments masked with placeholders so the repository privacy
  check passes. Scores, costs and judge votes are unchanged, and the masked `aggregate-result.json` carries the
  same aggregates as the unmasked tool output.
