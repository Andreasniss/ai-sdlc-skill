# AI SDLC Skill

An experimental set of reusable instructions for carrying a software change from requirements through implementation, checks, review and release. Built by [Andreas Nissen](https://andreasnissen.dev), with AI assistance. Canonical identifier: `ai-sdlc-skill`, version 0.6.0.

**Try it against no skill before adopting it.** The October controlled website-task comparison accepted 12/12 runs both with and without the skill; the full skill used 48.2% more median worker tokens than no skill. That limited result does not establish value for your workload. Guidance that helped an older model may be unnecessary for your current model and workload.

This README owns the quick start and adoption decision. The [project article](https://andreasnissen.dev/projects/ai-sdlc-skill/) explains what building the skill taught me about evaluating guidance. Detailed host setup lives in [INSTALLATION.md](INSTALLATION.md).

## Reduced edition and pinned installation

The current reduced edition, **0.6.0**, keeps scope, repository rules, meaningful verification, release authority and handoffs in the default instructions. Detailed examples and procedures remain available through task-specific references. It removes mandatory stage/depth narration and repeated general workflow guidance.

**Not yet benchmarked.** The published full-skill versus no-skill results do not measure this reduced edition. Deterministic bundle checks establish packaging and consistency, not model behavior or lower task-level token use. Evaluate this candidate against no skill on your own workload before adopting it.

Use a full source commit with the [pinned installation procedure](INSTALLATION.md#optional-pin-a-reviewed-source-revision). Existing installations are not automatically updated.

## Decide whether it belongs in your workflow

The skill provides conventions for proportional planning, relevant checks, review, and handoffs between sessions. It may be worth testing if your agent repeatedly loses accepted decisions, checks the wrong behavior, or leaves work that another session cannot continue. Those are intended uses, not measured benefits.

If your model already completes the work reliably under your repository's existing instructions, extra general guidance may add little. Keep organization-specific facts, requirements and controls; test whether the reusable process guidance contributes anything beyond them.

### Compare with no skill

1. Choose representative tasks and define acceptable outcomes before running them. Include ordinary work and the failure that motivated adding guidance.
2. For each model, compare fresh sessions with **no skill**, **the full skill**, and **reduced guidance**. Keep task prompts, starting files, tools, permissions and acceptance criteria matched. Remove direct and indirect skill-loading references from the no-skill setup; preserve project requirements and enforced controls.
3. Record the exact model/version, settings, host, skill revision and instructions actually loaded. Repeat cases; one successful run does not establish a reliable advantage.
4. Judge correct outcomes, regressions, review and repair effort. Count total input/output tokens, cache usage, tool costs and elapsed time where available, including failed attempts. Report unavailable measures as unknown.
5. Compare each guidance variant against the no-skill result for that model and task mix. Keep, reduce or remove the guidance according to the result. Repeat when the model or workload changes.

This three-way comparison is an adoption method; the recorded two-arm experiment below does not test a reduced skill or your workload. A shorter prompt can still cause more retries. [Cost per verified outcome](https://andreasnissen.dev/writing/hidden-token-tax-agent-tools/) explains why the complete task matters more than the size of one input or response. The [evaluation reference](skills/ai-sdlc-skill/references/evaluation.md) owns case execution and recorded-run requirements.

## Install and try one bounded task

From your project directory, with Node.js and npm available:

```sh
npx skills@latest add Andreasniss/ai-sdlc-skill --skill ai-sdlc-skill
```

Choose your assistant and scope in the installer. Append `--list` to inspect the available skill first. Use one installation route so duplicate copies do not compete. The [installation guide](INSTALLATION.md) covers reviewed revision pinning, manual copies, chat-only hosts, updates and removal. Local installation does not install the skill into ChatGPT web or mobile.

In a disposable branch, select a real documentation error and ask:

> Use AI SDLC Skill to correct this documentation example. Read the repository rules and choose the appropriate planning depth. Make the requested change. Report the skill file you loaded, its revision, checks actually run, findings and remaining limits.

Inspect the diff and actual check results. The agent should stay within the request and identify unavailable verification. Keep or discard the trial deliberately. This checks loading and scoped behavior; use the matched comparison above to assess added value.

For clear, authorized work, Auto can be sufficient. Use Plan mode when you want to settle requirements or the approach first. Neither mode changes repository permissions or release authority.

### Reproduce the task-list example

Use a disposable task-list app with a known defect: completing one task also completes another task with the same title. You need a POSIX environment (macOS, Linux or WSL), Git, Python 3, Node.js, and a coding assistant with local file and terminal access. The assistant uses your existing subscription or API account.

From a scratch directory, create the example using the [reviewed skill revision](https://github.com/Andreasniss/ai-sdlc-skill/tree/16c686ae68385c3b7bff9c609fab957159d2e4e5):

```sh
git clone https://github.com/Andreasniss/ai-sdlc-skill.git ai-sdlc-source
git -C ai-sdlc-source checkout 16c686ae68385c3b7bff9c609fab957159d2e4e5
python3 ai-sdlc-source/skills/ai-sdlc-skill/scripts/make_fixture.py \
  --state bug --into ai-sdlc-trial
cd ai-sdlc-trial
npx skills@latest add ../ai-sdlc-source --skill ai-sdlc-skill
```

Choose your assistant and project installation scope. The [installation guide](https://github.com/Andreasniss/ai-sdlc-skill/blob/16c686ae68385c3b7bff9c609fab957159d2e4e5/INSTALLATION.md) covers manual installation and other hosts. Then open the trial folder in your assistant and ask:

> Use AI SDLC Skill to fix this task-list bug: when two tasks have the same title, completing one must leave the other open. Reproduce the defect before changing code. Add a regression check, fix the browser app and check the result. Keep adding tasks and filtering working. Do not publish or deploy. Report the skill file loaded, the diff, checks actually run and any checks you could not perform.

**Inspect the result:**

- The original two tests pass even with the defect. A new duplicate-title check should fail before the fix and pass after it.
- Run `node --test test/tasks.test.js`. Check both `app.js` (the browser) and `app-under-test.js` (the test copy); fixing only the test copy leaves the app broken.
- Serve the folder with `python3 -m http.server 8877`, open `http://localhost:8877`, add two tasks named “write”, and click one. Only that task should complete, including after a reload. Check the Open and Completed filters too.
- Inspect `git diff` and the assistant’s report. A browser check that was unavailable should be reported as unavailable.

Stop the local server with Ctrl+C. Keep the trial for inspection or delete the two scratch folders when finished. This example lets you inspect one result; it is not a measurement of productivity or reliability across projects.

## Use it for your change

The reduced workflow is to establish the work, make and verify the change, then review, release or hand off as the task requires. Read [SKILL.md](skills/ai-sdlc-skill/SKILL.md) for the instructions an agent loads.

| Task | Starting prompt | Expected evidence |
| --- | --- | --- |
| Fix a bug | Reproduce the disappearing task label after reload, preserve the data format, fix it and run relevant checks. | A reproduction, scoped repair, check results and remaining limits |
| Start a project | Build a small task tracker that adds and completes tasks and retains them after reload. | A working first slice, setup instructions and checks of those behaviors |
| Document existing code | Inspect source, configuration and CI; add concise project guidance without changing application behavior. | Observed structure, verified commands and clearly marked unknowns |
| Resume work | Read the existing decision and handoff, then continue the same change. | Preserved scope, the continuation point and refreshed checks where needed |

Prefix a task with “Use AI SDLC Skill” and supply the project's actual requirement. See [common cases](skills/ai-sdlc-skill/references/common-cases.md) for complete prompts, review-only work and native `/init` distinctions.

### Where the records belong

Small changes can keep outcome, scope, checks and result in the existing issue or PR. Material changes may need intent, specification, plan and evidence in one change folder. Put these in the adopter project, outside the installed skill bundle. The [artifact guide](skills/ai-sdlc-skill/references/artifact-layout.md) owns the layout and document roles.

For a worked example, inspect [Plan My Week in 7DayFocus](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/tree/main/docs/ai-dlc/changes/P04-plan-my-week). Its requirement prevents an old proposal from overwriting newer edits. The records connect intent, specification, implementation plan and historical checks. This demonstrates a traceable change, not an improvement over no skill.

Keep shared repository rules in their canonical instruction file. The [shared-instructions article](https://andreasnissen.dev/writing/agents-md-claude-md-shared-instructions/) explains how `AGENTS.md` and a thin `CLAUDE.md` can work together.

### Is the Python helper required?

No. Ordinary use runs the project's own checks directly. The optional helper needs Python 3.10+, Git and a POSIX environment, with no Python package dependencies. It records reviewed commands, exit status, revision and configuration digest for a clean committed candidate. Consult [setup and limits](skills/ai-sdlc-skill/references/adoption.md) before using it.

Commands run with the caller's privileges. The helper is not a sandbox, authenticated approval or proof that the checks cover the requirement. The skill installs no hooks, grants no permissions and authorizes no release.

## Evidence and limits

Start with the account that matches your question:

- [Lessons learned: Does My AI Skill Still Earn Its Place?](https://andreasnissen.dev/projects/ai-sdlc-skill/) covers why I now challenge instructions, reduce guidance and evaluate it again when the model or workload changes. It includes my skill, Addy Osmani’s popular collection, and the effort of building useful evals.
- [Detailed experiment: Does My Coding Skill Earn Its Extra Work?](https://andreasnissen.dev/writing/does-my-coding-skill-help/) keeps the methods, results, grader corrections and limitations together. My skill has a matched no-skill comparison; Addy’s collection was compared with mine and has no no-skill control in that experiment.
- [Controlled run report](https://github.com/Andreasniss/ai-sdlc-skill/blob/db9694664434cc95d704ad7619fe7ea3b09609a4/evals/minimal-skill-comparison-2026-10-27.md) and [collection comparison](https://github.com/Andreasniss/ai-sdlc-skill/blob/45d4f3c8b3f9dbe5901dded0788a283eaa516e87/evals/skill-collection-comparison-2026-10-26.md) retain the recorded configurations and per-run evidence.


The [October 27 controlled comparison](https://github.com/Andreasniss/ai-sdlc-skill/blob/db9694664434cc95d704ad7619fe7ea3b09609a4/evals/minimal-skill-comparison-2026-10-27.md) used four synthetic adaptations of website tasks, three repeats per arm. No skill and full skill each accepted 12/12 runs. With **no skill as the baseline**, median worker tokens rose from 193,654 to 287,082.5 (**48.2% more**) and median worker time from 76.5 to 85.0 seconds (**about 11% more**); median tool calls stayed at 20.5. These are worker measurements, not total delivery cost or evidence of equivalent reliability on unfamiliar tasks. The [detailed article](https://andreasnissen.dev/writing/does-my-coding-skill-help/) explains the earlier comparison and grader corrections.

[Claude Code plugin evaluations](evals/README.md) separately test discovery and forced skill use against no plugin, with their own grader and runtime limits. Keep those host-specific scores separate from the website-task results.

The current case inventory contains 30 behavior cases. Historical observations apply to their recorded instruction revisions and case sets, not automatically to today's bundle or models:

- [September 20 review-loop evaluation](skills/ai-sdlc-skill/evals/review-loop-evaluation.md): 15 cases across three Codex sessions met their criteria. No no-skill comparison was run.
- [September 13 feedback pilot](skills/ai-sdlc-skill/evals/feedback-pilot.md): three paired cases compared older and newer skill instructions. Both met the selected criteria; no advantage was demonstrated.
- [October 12 focused evidence pilot](skills/ai-sdlc-skill/evals/focused-evidence-pilot.md): three paired cases compared an older skill with a candidate update. Both CSV runs found the defect; the candidate additionally executed explicit correct-output and wrong-output controls. This is a narrow instruction-version observation, not a no-skill benefit.

Those older pilots did not capture exact model builds or comparative token, elapsed-time and cost measurements. Cross-host runtime compatibility remains unverified. The [focused update PR](https://github.com/Andreasniss/ai-sdlc-skill/pull/21) and [harness-learning PR](https://github.com/Andreasniss/ai-sdlc-skill/pull/25) retain their scoped change and verification records.

The 20 October 2026 deterministic snapshot records **58 passing deterministic tests** plus five repository documentation checks. These cover helpers, schemas and bundle consistency; they do not measure model judgment or prove skill value. Repository integration records for [7DayFocus](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/blob/main/docs/evidence-sdlc-pilot.md) and [Runbook Relay](https://github.com/Andreasniss/runbook-relay-webmcp/blob/main/docs/evidence-sdlc-pilot.md) likewise establish integration facts, not causal benefit.

## Maintain or contribute

The [installation guide](INSTALLATION.md) owns updates and migration. Preserve local edits, pin a reviewed full source commit for reproducibility, and review updates explicitly. The skill never updates itself on startup. The optional [plugin pilot](PLUGIN.md) packages the same bundle without hooks or permissions; it has no public marketplace listing.

For documentation, packaging, helper tests and behavioral evaluation requirements, follow [CONTRIBUTING.md](CONTRIBUTING.md). Changing instructions changes agent configuration; deterministic file checks cannot establish how a model follows them. Follow [AGENTS.md](AGENTS.md) and [PRIVACY.md](PRIVACY.md) before contributing public changes.

The skill independently adapts selected [Anthropic AI-native SDLC guidance](https://claude.com/blog/the-ai-native-sdlc-playbook) and [Peter Steinberger's development practices](skills/ai-sdlc-skill/references/sources.md). See [sources and provenance](skills/ai-sdlc-skill/references/sources.md). The installation-first README and self-contained packaging were inspired by [Matt Pocock's skills repository](https://github.com/mattpocock/skills).

Andreas owns intent, architecture, requirements, evaluation criteria, risk, and release decisions and reviews merged changes. AI tools assisted implementation and documentation. Automated and AI-assisted checks are evidence, not human reviewers or accountability owners.

A personal project by Andreas Nissen. Views are his own; no employer or Anthropic affiliation, endorsement, or certification is implied.

Copyright 2026 Andreas Nissen. Original project code and accompanying technical documentation are licensed under [Apache-2.0](LICENSE), except where separately indicated. See [NOTICE](NOTICE). Third-party dependencies and bundled material retain their own terms. Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, verification, and contribution expectations.

