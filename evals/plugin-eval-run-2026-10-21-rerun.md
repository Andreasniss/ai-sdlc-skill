---
type: plugin-eval-run
date: 2026-10-21
issue: 27
---

# Plugin eval rerun, 2026-10-21 (Haiku, natural and forced skill use)

Second `claude plugin eval` run on the revised cases. The first run ([record](plugin-eval-run-2026-10-21.md)) was a
pilot to learn the harness. Results are reported as observed.

## Run record

| Item | Value |
|---|---|
| Skill under test | tree `fd4c9158e83ee0a9a30ed468ecf26d9702d7eb2d`, plugin 0.5.3 |
| Cases digest | `1d0e419b8ad1a343000e38acb6694488e936e7116485e5d51cbd557cee7c354e` |
| Evals digest (natural) | `f1d30661989c3fe26cd1cf8877f9013bc75e5e80a37b5faac06079da80ed265f` |
| Evals digest (forced) | `960152eaffeab6618d5635006d3729924915d9d21e7a3fcf4dc28c3779652941` |
| Claude Code | 2.1.306 |
| Agent model, judge | `claude-haiku-5-5`, `claude-sonnet-5-5` |
| Settings | 8 cases, `--runs 5`, `--ablation with-without` (natural) and with only (forced), `--threshold 0.8`, `--allow-tools Write Edit Bash`, cap $25 total |
| Cost of the results used | about $15.60 (natural $7.16 + $1.12 + $1.73, forced $5.59), judge included |
| Cost of discarded runs | about $1.17 (see below). Total spend about $16.8 |
| Natural arms | "with" = plugin loaded, prompt unchanged. "without" = no plugin |
| Forced arm | plugin loaded, prompt ends with "Use the ai-sdlc-skill skill (AI SDLC Skill) for this task." |

Files: [`natural/aggregate-result.json`](plugin-eval-run-2026-10-21-rerun/natural/aggregate-result.json),
[`forced/aggregate-result.json`](plugin-eval-run-2026-10-21-rerun/forced/aggregate-result.json) and
[`forced/report.html`](plugin-eval-run-2026-10-21-rerun/forced/report.html). The natural result is a merge of two tool
outputs (see below), so there is no single natural report. The per-run reports are in `natural/` and `natural-completion/`.

## Result

Scores are the share of weighted checks passed, excluding the `skill-fired` indicator, mean of 5 runs.
Δ is the natural "with" arm minus the "without" arm. The forced arm has no own baseline, so its Δ is against the
natural "without" arm.

| Case | Without | Natural with | Δ | Forced with | Δ forced | Skill fired (natural / forced) |
|---|---|---|---|---|---|---|
| blocked-export-handoff | 0.857 | 0.886 | +0.029 | 0.863 | +0.005 | 0 of 5 / 5 of 5 |
| bug-with-reproducible-symptom | 1.000 | 0.893 | -0.107 | 1.000 | 0.000 | 0 / 5 |
| csv-plausible-wrong-output | 1.000 | 1.000 | 0.000 | 1.000 | 0.000 | 0 / 5 |
| feature-in-established-project | 0.875 | 0.900 | +0.025 | 0.911 | +0.036 | 2 / 5 |
| feature-interaction-preserves-order | 0.960 | 0.960 | 0.000 | 0.933 | -0.027 | 0 / 5 |
| resume-export-after-answer | 0.981 | 1.000 | +0.019 | 0.983 | +0.002 | 0 / 5 |
| resume-interrupted-change | 1.000 | 0.973 | -0.027 | 0.953 | -0.047 | 5 / 5 |
| review-without-edits | 1.000 | 0.943 | -0.057 | 0.900 | -0.100 | 1 / 5 |
| **Mean** | | | **-0.015** (se 0.017) | | **-0.016** (se 0.015) | |

Pass rate at threshold 0.8, per the tool, natural with vs without: 0.2 vs 0 (blocked-export-handoff), 0.8 vs 1
(bug), 1 vs 1 (csv), 0.2 vs 0 (feature-in-established-project), 0.8 vs 0.8 (interaction), 1 vs 0.8
(resume-export), 0.8 vs 1 (resume-interrupted), 0.6 vs 1 (review). Forced with: 0, 1, 1, 0.2, 0.6, 0.8, 0.6, 0.2.

## Reading it

- **No measurable gain from the skill on Haiku.** Mean Δ is slightly negative in both arms and within about one
  standard error of zero (se across the 8 case means). Three cases have a negative Δ, three a small positive one, two are zero.
  Cases where the skill adds nothing or scores lower are reported as they came out.
- **Ceiling effect.** The no-plugin arm already scores 0.86 to 1.00 on every case, so these cases leave little room
  to show a gain. The result says the skill did not help on these cases, not that it cannot help.
- **Natural use is rare.** Haiku invoked the skill by itself in 8 of 40 natural runs (5 of them in one case).
  Forcing the invocation did not raise scores (mean Δ -0.016).
- **review-without-edits** is the weakest case for the skill in both arms. One reason I did not rule out: its edit
  check does not catch edits made through Bash, so this case cannot separate "did not edit" from "edited with a shell".
- This run cannot show that Haiku plus the skill matches Sonnet. No Sonnet arm was run.

## What was discarded or re-run

- The natural run stopped early (`partial: true`, reason `interrupted`, cause unknown) after 6 of 8 cases. Its
  `resume-interrupted-change` data had 3 of 10 runs errored "interrupted" and was dropped (about $0.75). The 6
  complete cases from that run are kept as produced.
- The two missing cases were then run on their own. The first attempt ($0.42, `rerun/part2`) hit the account's session
  limit mid-run, so most runs scored 0 with a "session limit" error. All of it was dropped. The second attempt
  completed with 0 errors and is the one used. Settings were identical to the main run.
- Raw files from the dropped attempts are not committed. The first-6-cases report in `natural/` still shows the
  interrupted case.

## Limits

- Judge scores (`report-quality`, Sonnet, 3 votes) are low confidence. Rubrics were shortened and validated on a few
  runs before the main run, not calibrated against human labels.
- 5 runs per arm leaves visible noise. A change of 0.03 to 0.06 in one case is one failed check in one run.
- Cases are small synthetic projects, written for this skill.
- **Two runs lost the ability to write at all.** In natural bug-with-reproducible-symptom (with arm, run 1, score 0.47)
  the agent reported its working directory as mounted read-only and wrote nothing. Forced blocked-export-handoff
  (with arm, run 4) reported the same ("I couldn't make the change"). Both are sandbox failures, not skill behavior,
  and are scored as observed. Without the first one, the bug case natural Δ would be 0.000 instead of -0.107 and the
  natural mean Δ about -0.002 instead of -0.015. Many other runs mention that the `.git` directory is read-only
  (so no commit or branch), which applies to both arms alike.
- Permission denials were not zero in the full runs: 13 of 80 natural runs and 2 of 40 forced runs had at least one
  (natural: 6 Bash, 3 Write, 4 Chrome MCP tool attempts; forced: 2 Write to paths outside the workspace). The denied
  Bash and Write calls could have cost a run some checks, so scores for those runs may be slightly low in both arms.
  The sandbox "Read-only file system" cwd error also appears in run logs.
- Stage 3 (a small Sonnet run) is not started. That decision is the maintainer's.
