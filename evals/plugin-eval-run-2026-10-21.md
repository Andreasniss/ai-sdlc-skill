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
| Graders digest | `d29bed225e6339ae85783547c43d1d80ac283b1f6a0957d1a96a8f0f0f130e4b` (`render_plugin_evals.py --digest`) |
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
  strict for Haiku reports or Haiku reports are weak. This was not investigated and the rubric was not changed.
- The eval sessions listed the Claude in Chrome tools. In `browser-feedback-unavailable` no run attempted browser
  tooling (score 1.00 in all six runs), so the case was not distorted in this run.
- Only checks the graders can observe are scored. They cannot run the fixtures' tests or a browser.
- Single host (Claude Code), synthetic fixtures, one model family judging itself.
- The `eval-audit.md` guide from the claude-api skill could not be read, so the suite audit in PR #29 is a manual
  pass against its five areas.
- The result files had local user-directory path segments masked with placeholders so the repository privacy
  check passes. Scores, costs and judge votes are unchanged, and the masked `aggregate-result.json` carries the
  same aggregates as the unmasked tool output.
