# AI SDLC Skill

[Built by Andreas Nissen](https://github.com/Andreasniss) · [andreasnissen.dev](https://andreasnissen.dev) · [Connect on LinkedIn](https://www.linkedin.com/in/andreasnissen) · [Source on GitHub](https://github.com/Andreasniss/ai-sdlc-skill) · [Apache-2.0](LICENSE)

A reusable, experimental skill for carrying a software change from an agreed problem through design, implementation, verification, review, and learning. Each handoff keeps the decisions and evidence the next agent session needs; humans retain product, architecture, risk, and release judgment.

Independently built from selected [Anthropic AI-native SDLC guidance](https://claude.com/blog/the-ai-native-sdlc-playbook). This is the canonical source for the `ai-sdlc-skill` identifier, version 0.2.0.

## Install

From the project where you want to use the skill, run:

```sh
npx skills@latest add Andreasniss/ai-sdlc-skill --skill ai-sdlc-skill
```

The [Skills CLI](https://github.com/vercel-labs/skills) lets you choose your coding agents and installation scope. It needs Node.js and npm. To inspect the available skill first, append `--list`. See the [installation guide](INSTALLATION.md) for Codex, Claude, chat-only hosts, reviewed revision pinning, and updates. Local installation does not automatically install a skill into ChatGPT web or mobile.

Then ask your agent:

> Use AI SDLC Skill to fix this documentation example. Read the repository rules, make the smallest useful change, and report the revision and checks actually run.

Read the [workflow](skills/ai-sdlc-skill/SKILL.md) to see what the agent loads. The instructions need no Python dependency; the optional helper requires Python 3.10+, Git, and POSIX.

## How the delivery method works

The familiar Plan, Design, Build, Test, Deploy, and Maintain responsibilities remain. The change is the handoff: accepted intent, design decisions, a plan, code and tests, review findings, and incident lessons stay inspectable across sessions. A small fix can keep its record in one issue or PR. A larger change may need a linked artifact packet.

| Handoff | What the next session receives | Judgment retained by the owner |
| --- | --- | --- |
| Problem to design | Outcome, constraints, and acceptance examples | What should change and why |
| Design to implementation | Design choices, boundaries, and a testable plan | Architecture and acceptable risk |
| Implementation to review | Candidate revision, diff, actual checks, and findings | Whether the evidence supports release |
| Operation to next change | Observed failure or new requirement | Whether another change is justified |

The [7DayFocus implementation](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab#the-anthropic-method-this-repository-demonstrates) makes this concrete with `intent.md`, `spec.md`, `plan.md`, and `evidence.md`. Those filenames are project conventions, not required skill output. Existing authorization persists; a new document does not create a new approval ceremony.

The skill adapts selected Anthropic guidance. AWS AI-DLC adds broader lifecycle coordination, while OpenAI's harness engineering focuses on the agent's execution environment. These emphases overlap. The [companion article](https://andreasnissen.dev/writing/ai-native-software-delivery-methods/) explains when each helps; this skill does not implement the complete AWS method or reproduce either company's internal process.

## Verify the optional helper

```sh
python3 -m unittest discover -s skills/ai-sdlc-skill/tests -v
```

Run this from a source checkout. It tests the helper, not the assistant's judgment.

## What it adds

- Planning proportional to the change, with existing repository requirements preserved.
- Verification tied to a candidate revision, with failed and unavailable checks reported explicitly.
- Fresh review when the risk warrants it, followed by checks of the revision that will actually merge.

It does not install hooks, grant approvals, enforce a sandbox, or authorize publication. Configured commands run with the caller's privileges. Read the [execution boundaries](skills/ai-sdlc-skill/references/adoption.md) before running them.

## Evidence and limits

Verification snapshot: 6 September 2026. The helper has 12 passing deterministic tests covering success, failures, timeouts, invalid configuration, and candidate changes. The existing pilots include repository routing, CI integration, and application checks:

| Pilot | Reviewed identifier migration | Evidence |
| --- | --- | --- |
| 7DayFocus | [PR 25](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/pull/25) | [Pilot record](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/blob/main/docs/evidence-sdlc-pilot.md) |
| Runbook Relay | [PR 24](https://github.com/Andreasniss/runbook-relay-webmcp/pull/24) | [Pilot record](https://github.com/Andreasniss/runbook-relay-webmcp/blob/main/docs/evidence-sdlc-pilot.md) |

These are deterministic and repository integration results. They do not establish better model judgment, faster delivery, production readiness, or interactive compatibility across agent runtimes. Repository cleanliness is sampled before and after each command; transient changes restored between observations are outside that check. Reports are observations, not authenticated approvals.

The pilots retain their earlier reviewed bundles. For reproducible team adoption, record the full canonical source commit and review updates through a PR. Ordinary installations can use the CLI's explicit update command; the skill never updates itself on startup.

## Contribute and verify

Preserve the execution boundaries and add meaningful regression coverage when changing the helper. Follow [AGENTS.md](AGENTS.md) and the [publication privacy checks](PRIVACY.md). Keep application-specific check commands in the adopter repository.

See [sources and provenance](skills/ai-sdlc-skill/references/sources.md) and the [Apache-2.0 license](LICENSE). The installation-first README and self-contained packaging were inspired by [Matt Pocock's skills repository](https://github.com/mattpocock/skills).

Andreas owns intent, architecture, requirements, evaluation criteria, risk, and release decisions and reviews merged changes. AI tools assisted implementation and documentation. Automated and AI-assisted checks are evidence, not human reviewers or accountability owners.

A personal project by Andreas Nissen. Views are his own; no employer or Anthropic affiliation, endorsement, or certification is implied.

## Reuse and contributions

Copyright 2026 Andreas Nissen. Original project code and accompanying technical documentation are licensed under [Apache-2.0](LICENSE), except where separately indicated. See [NOTICE](NOTICE). Third-party dependencies and bundled material retain their own terms. Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, verification, and contribution expectations.
