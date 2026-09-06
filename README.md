# AI SDLC Skill

[Built by Andreas Nissen](https://github.com/Andreasniss) · [andreasnissen.dev](https://andreasnissen.dev) · [Connect on LinkedIn](https://www.linkedin.com/in/andreasnissen) · [Source on GitHub](https://github.com/Andreasniss/ai-sdlc-skill) · [Apache-2.0](LICENSE)

A reusable, experimental skill for carrying a software change from an agreed problem through design, implementation, verification, review, and learning. Each handoff keeps the decisions and evidence the next agent session needs; humans retain product, architecture, risk, and release judgment.

Independently built from selected [Anthropic AI-native SDLC guidance](https://claude.com/blog/the-ai-native-sdlc-playbook). This is the canonical source for the `ai-sdlc-skill` identifier, version 0.3.0.

Read the [project article](https://andreasnissen.dev/projects/ai-sdlc-skill/) for three explanatory diagrams, a detailed file walkthrough, and the 7DayFocus worked example.

## Install

From the project where you want to use the skill, run:

```sh
npx skills@latest add Andreasniss/ai-sdlc-skill --skill ai-sdlc-skill
```

The [Skills CLI](https://github.com/vercel-labs/skills) lets you choose your coding agents and installation scope. It needs Node.js and npm. To inspect the available skill first, append `--list`. See the [installation guide](INSTALLATION.md) for Codex, Claude, chat-only hosts, reviewed revision pinning, and updates. Local installation does not automatically install a skill into ChatGPT web or mobile.

Then give your agent a concrete task. You can start with an empty directory, an undocumented codebase, or an existing project:

> Use AI SDLC Skill to start a new local task tracker in this directory. Use plain HTML, CSS, and JavaScript with browser storage. Build a first version that can add and complete tasks and keeps them after reload. Add setup instructions and verify those behaviors.

For an existing project without documentation:

> Use AI SDLC Skill to initialize project guidance from this codebase. Inspect the code, configuration, and CI. Add a concise README and instructions for the agent I am using, with verified commands and clearly marked unknowns. Keep application behavior unchanged.

See [common cases and example prompts](skills/ai-sdlc-skill/references/common-cases.md) for native `/init`, features, bugs, refactoring, review, and resuming work.

Read the [workflow](skills/ai-sdlc-skill/SKILL.md) to see what the agent loads. The instructions need no Python dependency; the optional helper requires Python 3.10+, Git, and POSIX.

## How the delivery method works

The familiar Plan, Design, Build, Test, Deploy, and Maintain responsibilities remain, as a loop rather than a pipeline. The change is the handoff: accepted intent, design decisions, a plan, code and tests, review findings, and incident lessons stay inspectable across sessions. A small fix can keep its record in one issue or PR. A larger change may need a linked artifact packet.

The stages are the familiar loop, and the [handoff contract in SKILL.md](skills/ai-sdlc-skill/SKILL.md#handoffs) is what the agent actually loads: what each stage must leave behind, and which judgment stays with the owner. It is stated once, there, rather than duplicated here.

The [7DayFocus implementation](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab#the-anthropic-method-this-repository-demonstrates) makes this concrete with `intent.md`, `spec.md`, `plan.md`, and `evidence.md`. Those filenames are project conventions, not required skill output. Existing authorization persists; a new document does not create a new approval ceremony.

The skill adapts selected Anthropic guidance. AWS AI-DLC adds broader lifecycle coordination, while OpenAI's harness engineering focuses on the agent's execution environment. These emphases overlap. The [companion article](https://andreasnissen.dev/writing/ai-native-software-delivery-methods/) explains when each helps; this skill does not implement the complete AWS method or reproduce either company's internal process.

## What it adds

- Planning proportional to the change, with existing repository requirements preserved.
- Verification tied to a candidate revision, with failed and unavailable checks reported explicitly.
- Fresh review when the risk warrants it, followed by checks of the revision that will actually merge.
- Recurring lessons encoded where they change future behavior, in one place, without competing rule sets.
- A [behavior evaluation set](skills/ai-sdlc-skill/evals/cases.md), with reproducible starting repositories, to rerun when the instructions themselves change.

It does not install hooks, grant approvals, enforce a sandbox, or authorize publication. Configured commands run with the caller's privileges. Read the [execution boundaries](skills/ai-sdlc-skill/references/adoption.md) before running them.

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
