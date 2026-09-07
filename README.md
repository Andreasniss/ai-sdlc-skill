# AI SDLC Skill

[Built by Andreas Nissen](https://github.com/Andreasniss) · [andreasnissen.dev](https://andreasnissen.dev) · [Connect on LinkedIn](https://www.linkedin.com/in/andreasnissen) · [Source on GitHub](https://github.com/Andreasniss/ai-sdlc-skill) · [Apache-2.0](LICENSE)

A reusable, experimental skill that helps a coding agent turn a requested change into working code, relevant checks, and a reviewable delivery record. Start with the smallest process that preserves the decisions and evidence the next session needs. Humans retain product, architecture, risk, and release judgment.

Independently built from selected [Anthropic AI-native SDLC guidance](https://claude.com/blog/the-ai-native-sdlc-playbook). This is the canonical source for the `ai-sdlc-skill` identifier, version 0.3.0.

Read the [project article](https://andreasnissen.dev/projects/ai-sdlc-skill/) for three explanatory diagrams, a detailed file walkthrough, and the 7DayFocus worked example.

**Recommended starting point:** use Auto for clear, authorized work; use Plan mode when you want to settle the approach before implementation. Keep durable change records in either mode. The [FAQ](#faq) explains the distinction.

## Install

From the project where you want to use the skill, run:

```sh
npx skills@latest add Andreasniss/ai-sdlc-skill --skill ai-sdlc-skill
```

The [Skills CLI](https://github.com/vercel-labs/skills) lets you choose your coding agents and installation scope. It needs Node.js and npm. To inspect the available skill first, append `--list`. See the [installation guide](INSTALLATION.md) for Codex, Claude, chat-only hosts, reviewed revision pinning, and updates. Local installation does not automatically install a skill into ChatGPT web or mobile.

Then give your agent a concrete task. You can start with an empty directory, an undocumented codebase, or an existing project:

For a small fix in an existing project:

> Use AI SDLC Skill to fix the task label disappearing after reload. Reproduce the failure, preserve the existing data format, implement the fix, and run the relevant checks. Keep the outcome and evidence in the existing issue or PR. Follow the repository's review and release rules.

For a new project:

> Use AI SDLC Skill to start a new local task tracker in this directory. Use plain HTML, CSS, and JavaScript with browser storage. Build a first version that can add and complete tasks and keeps them after reload. Add setup instructions and verify those behaviors.

For an existing project without documentation:

> Use AI SDLC Skill to initialize project guidance from this codebase. Inspect the code, configuration, and CI. Add a concise README and instructions for the agent I am using, with verified commands and clearly marked unknowns. Keep application behavior unchanged.

See [common cases and example prompts](skills/ai-sdlc-skill/references/common-cases.md) for native `/init`, features, bugs, refactoring, review, and resuming work.

Read the [workflow](skills/ai-sdlc-skill/SKILL.md) to see what the agent loads. The instructions need no Python dependency; the optional helper requires Python 3.10+, Git, and POSIX.

**Expected result:** a scoped change, observed check results, any unresolved limits, and a linked record another session can continue from. An installation command or a generated plan alone does not establish that the skill was loaded or the change works.

## How the delivery method works

### Where are the artifacts?

The reusable workflow is [`skills/ai-sdlc-skill/SKILL.md`](skills/ai-sdlc-skill/SKILL.md). The [file-location guide](skills/ai-sdlc-skill/references/artifact-layout.md) explains the recommended layout, repository-wide documents, and Anthropic's actual guidance. Your project's change records live in **your project**, outside the installed skill folder.

For the concrete example, open [all four P04 files in 7DayFocus](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/tree/main/docs/ai-dlc/changes/P04-plan-my-week), or start at its [lifecycle index](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/blob/main/docs/ai-dlc/README.md). P04 is the Plan My Week feature's identifier. One material change uses one folder across sessions: `intent.md`, `spec.md`, `plan.md`, then observed `evidence.md`. This folder layout and fourth file are our convention; Anthropic suggests a shared `intent/` home and names the first three artifacts. Small changes can use an issue or PR instead.

Standing files such as `SECURITY.md`, `PRIVACY.md`, `PROVENANCE.md`, and `CONTRIBUTING.md` describe the repository across changes. The guide explains when each helps and how to link them without copying them into every packet.

### The lifecycle and handoffs

The skill names the loop **Plan → Design → Build → Test → Review → Deploy → Maintain**. Start at the current stage and scale the work to the change. The [handoff contract](skills/ai-sdlc-skill/SKILL.md#handoffs) defines what the next session receives and which judgment stays with the owner.

| Your change | Useful starting record | What makes it sufficient |
| --- | --- | --- |
| Small, reversible fix | Existing issue and PR | Clear outcome, scope, relevant checks, and result |
| Material feature or refactor | Existing specification and plan, or a linked change packet | Decisions, boundaries, acceptance examples, and current verification evidence |
| Consequential data, access, or release change | Design plus the actual authorization record | Explicit risk and recovery decisions, with enforced controls where required |

For the disappearing-label example, a save-and-reload check addresses the failure. Formatting checks alone do not. If the fix changes the saved-data format, revisit compatibility and recovery before treating it as routine. Existing authorization persists; generating a document does not create a new approval ceremony.

The skill adapts selected Anthropic guidance. AWS AI-DLC adds broader lifecycle coordination, while OpenAI's harness engineering focuses on the agent's execution environment. These emphases overlap. The [companion article](https://andreasnissen.dev/writing/ai-native-software-delivery-methods/) explains when each helps; this skill does not implement the complete AWS method or reproduce either company's internal process.

## What it adds

- Planning proportional to the change, with existing repository requirements preserved.
- Verification tied to a candidate revision, with failed and unavailable checks reported explicitly.
- Fresh review when the risk warrants it, followed by checks of the revision that will actually merge.
- Recurring lessons encoded where they change future behavior, in one place, without competing rule sets.
- A [behavior evaluation set](skills/ai-sdlc-skill/evals/cases.md), with reproducible starting repositories, to rerun when the instructions themselves change.

It does not install hooks, grant approvals, enforce a sandbox, or authorize publication. Configured commands run with the caller's privileges. Read the [execution boundaries](skills/ai-sdlc-skill/references/adoption.md) before running them.

## FAQ

### Do I need Plan mode if this skill already includes planning?

No. For clear, bounded work, the agent can plan, implement, and verify in Auto while following the skill. Use Plan mode when you want to resolve requirements, compare architectures, or review the approach before implementation. The lifecycle's Plan stage still matters even when a separate Plan-mode session is unnecessary.

### Can I use Auto all the way through?

Yes, within the agreed scope and existing authorization. Continue from accepted artifacts instead of recreating them. Pause for unresolved consequential choices and required approvals. A generated plan is not evidence of acceptance. Mode names and permissions differ between hosts; see [Claude Code modes](https://code.claude.com/docs/en/permission-modes) and [Codex permissions](https://learn.chatgpt.com/docs/agent-approvals-security). Auto does not replace repository or release gates.

### Are native plans deleted when a session ends?

There is no shared rule across Claude and Codex. Claude Code documents age-based cleanup of plan files, with a default retention period of 30 days, rather than deletion at session end. Codex also supports deliberately maintained repository plans. See [Claude Code retention](https://code.claude.com/docs/en/claude-directory#application-data) and [OpenAI's execution-plan approach](https://developers.openai.com/cookbook/articles/codex_exec_plans). These product details were checked on 7 September 2026.

### What do durable artifacts add for auditability?

They connect requirements and decisions to the code revision, actual checks, review findings, and release outcome. Commit and sync file-based records through the project's normal workflow, or use its maintained issue and PR records. A file in a disposable workspace is not durable just because it is Markdown. The skill supplies a working convention, not storage or retention enforcement. Git history alone is not a tamper-proof compliance audit trail.

### Do I need four Markdown files for every change?

No. A small fix can keep its essential record in an issue and PR. For material work, preserve the existing layout; when none exists, the [artifact guide](skills/ai-sdlc-skill/references/artifact-layout.md) recommends one change folder containing intent, specification, plan, and evidence as work progresses. Keep standing security and architecture documents in their canonical homes and link them.

### How do AGENTS.md and CLAUDE.md fit alongside the skill?

Repository instructions describe how to work in the project; the skill supplies a reusable delivery method; the issue or change packet describes this particular change. Keep shared rules in one place. For Claude and Codex together, my [shared-instructions article](https://andreasnissen.dev/writing/agents-md-claude-md-shared-instructions/) explains a thin `CLAUDE.md` importing `AGENTS.md`, host discovery, and when tool-specific guidance helps.

### Does a saved plan or green helper report mean the change is ready?

No. The plan describes intended work; checks provide observations about a candidate. The helper records command results and revision information, but cannot decide whether the checks cover the requirement, authenticate human approval, or authorize release. Review the actual change, resolve material findings, and refresh affected evidence when the candidate changes. See the [helper's documented limits](skills/ai-sdlc-skill/references/adoption.md).

## Read the companion articles

Follow the [AI-Assisted Software Delivery series](https://andreasnissen.dev/series/ai-assisted-software-delivery/) for an ordered path from shared repository instructions through method selection to pull-request evidence. Use the skill walkthrough alongside it for hands-on adoption.

| Reader question | Article |
| --- | --- |
| How do I adopt the skill and follow a real change? | [AI SDLC Skill: From Intent to Verified Changes](https://andreasnissen.dev/projects/ai-sdlc-skill/) |
| When is a minimal workflow enough, and when do Kiro, Anthropic, or AWS AI-DLC help? | [AI-Native Software Delivery: Which Method Fits Your Change?](https://andreasnissen.dev/writing/ai-native-software-delivery-methods/) |
| How should Claude and Codex share repository rules? | [AGENTS.md and CLAUDE.md: Shared Rules, Different Entry Points](https://andreasnissen.dev/writing/agents-md-claude-md-shared-instructions/) |
| What should connect checks and approval to a pull request? | [What Evidence Should an AI-Generated Pull Request Carry?](https://andreasnissen.dev/writing/evidence-for-ai-generated-pull-requests/) |

The articles explain the decisions and trade-offs. The installed [SKILL.md](skills/ai-sdlc-skill/SKILL.md) remains the workflow source. The evidence article describes an architecture proposal, not an attestation system implemented by this skill.

## Evidence and limits

Verification snapshot: 6 September 2026. The bundle has 53 passing deterministic tests: the verification helper's coverage of success, failures, timeouts, invalid configuration, and candidate changes; the evaluation reporter's schema and disqualifier handling; and bundle version, link, and licensing consistency. The existing pilots include repository routing, CI integration, and application checks:

| Pilot | Reviewed identifier migration | Evidence |
| --- | --- | --- |
| 7DayFocus | [PR 25](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/pull/25) | [Pilot record](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/blob/main/docs/evidence-sdlc-pilot.md) |
| Runbook Relay | [PR 24](https://github.com/Andreasniss/runbook-relay-webmcp/pull/24) | [Pilot record](https://github.com/Andreasniss/runbook-relay-webmcp/blob/main/docs/evidence-sdlc-pilot.md) |

These are deterministic and repository integration results. They do not establish better model judgment, faster delivery, production readiness, or interactive compatibility across agent runtimes. Repository cleanliness is sampled before and after each command; transient changes restored between observations are outside that check. Reports are observations, not authenticated approvals.

The pilots retain their earlier reviewed bundles. For reproducible team adoption, record the full canonical source commit and review updates through a PR. Ordinary installations can use the CLI's explicit update command; the skill never updates itself on startup.

## Contribute and verify

The optional Python helper runs a project's reviewed check commands against a clean Git commit and writes a report of the revision, configuration digest, and results. For example, it can record whether that project's build and tests passed for the candidate being reviewed. It does not decide which tests are sufficient or review the code. Ordinary agent use needs no helper setup: the agent can run the project's checks directly. See the [helper setup and limits](skills/ai-sdlc-skill/references/adoption.md) if you need that report.

If you are changing or evaluating the helper itself, run this from a checkout of **this skill repository**:

```sh
python3 -m unittest discover -s skills/ai-sdlc-skill/tests -v
```

This runs the bundle's own regression tests, including command failures, timeouts, and the version, link, and licensing consistency of the documentation. It does not test your application, install the skill, or verify that an agent loaded it.

Changing the instructions is changing agent configuration. When `SKILL.md` or its references change, rerun the [behavior cases](skills/ai-sdlc-skill/evals/cases.md) against the host you actually use and record the run; see [evaluating this skill](skills/ai-sdlc-skill/references/evaluation.md). Those runs are self-reported observations of one host, not authenticated evidence.

Preserve the execution boundaries and add meaningful regression coverage when changing the helper. Follow [AGENTS.md](AGENTS.md) and the [publication privacy checks](PRIVACY.md). Keep application-specific check commands in the adopter repository.

See [sources and provenance](skills/ai-sdlc-skill/references/sources.md) and the [Apache-2.0 license](LICENSE). The installation-first README and self-contained packaging were inspired by [Matt Pocock's skills repository](https://github.com/mattpocock/skills).

Andreas owns intent, architecture, requirements, evaluation criteria, risk, and release decisions and reviews merged changes. AI tools assisted implementation and documentation. Automated and AI-assisted checks are evidence, not human reviewers or accountability owners.

A personal project by Andreas Nissen. Views are his own; no employer or Anthropic affiliation, endorsement, or certification is implied.

## Reuse and contributions

Copyright 2026 Andreas Nissen. Original project code and accompanying technical documentation are licensed under [Apache-2.0](LICENSE), except where separately indicated. See [NOTICE](NOTICE). Third-party dependencies and bundled material retain their own terms. Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, verification, and contribution expectations.
