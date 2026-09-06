# AI SDLC Skill

An experimental delivery skill that preserves repository rules, scales planning to the change, and records verification for the candidate revision. Independently implemented by Andreas Nissen from selected [Anthropic AI-native SDLC guidance](https://claude.com/blog/the-ai-native-sdlc-playbook).

Version 0.2.0. Skill identifier and invocation: `ai-sdlc-skill` and `$ai-sdlc-skill`.

## Start here

Read [SKILL.md](SKILL.md) for the workflow and [adoption.md](references/adoption.md) for execution limits. The bundle has no Python package dependencies. Its optional helper needs Python 3.10+, Git, and a POSIX environment. It does not install hooks, change permissions, or authorize releases.

Start with [common cases and example prompts](references/common-cases.md), including a new project and initialization of an undocumented codebase. The skill can guide these tasks without its optional helper.

The helper runs a project's reviewed check commands and records results for a clean commit. To evaluate or change the helper itself, run `python3 -m unittest discover -s tests -v` from this bundle's directory. These are the runner's regression tests; they do not test your application or confirm that an agent loaded the skill.

The initial [7DayFocus pilot](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/blob/main/docs/evidence-sdlc-pilot.md) and [Runbook Relay pilot](https://github.com/Andreasniss/runbook-relay-webmcp/blob/main/docs/evidence-sdlc-pilot.md) record repository integration and verification results. They do not establish faster delivery, better model judgment, or interactive runtime compatibility.

## Install

From your project directory:

```sh
npx skills@latest add Andreasniss/ai-sdlc-skill --skill ai-sdlc-skill
```

Choose your coding agent and scope in the installer. Use the [cross-assistant installation guide](https://github.com/Andreasniss/ai-sdlc-skill/blob/main/INSTALLATION.md) for reviewed revision pinning, manual installation, chat-only hosts, invocation, and a first task to check discovery and behavior.

Copy the complete bundle. Native installation, manually supplied instructions, and verified execution are different states. Preserve existing repository rules and report required checks that the host cannot run.

## Migrate from evidence-sdlc

This is an intentional identifier change. Inventory existing installations and any local edits before changing them. Preserve local edits outside skill discovery, install the reviewed new bundle only into an absent destination, and archive the old directory outside all discovery paths. Then update explicit invocations, repository instruction links, CI paths, and check configurations to `ai-sdlc-skill`. Do not retain an old-name alias that loads the same instructions twice.

The pilot repositories retain their original dated evidence records. Historical mentions of `evidence-sdlc` explain the migration; they are not current installation paths.

## Updates and the standalone repository

The canonical source is [Andreasniss/ai-sdlc-skill](https://github.com/Andreasniss/ai-sdlc-skill). Ordinary CLI installations use `npx skills@latest update ai-sdlc-skill` after preserving local edits. For reproducible team adoption, pin a reviewed full source commit, verify the bundle and tests, and update through a PR. Never silently replace skills on agent startup. Repository-specific `delivery-checks.json` files stay with their applications.

The initial implementation and rename were verified in the two pilot repositories before extraction. Only installation documentation changed during extraction. The pilot bundles remain earlier reviewed copies until explicitly updated; they are not automatic mirrors.

## Evidence and authority

The helper runs reviewed commands with the caller's privileges and discards child output. A passing report is an observation, not authenticated approval. It checks repository identity before and after each command, not continuously. Consult the adoption guide before use with untrusted code, secrets, or external systems.

Andreas owns intent, architecture, evaluation criteria, risk, and release decisions. AI assisted with implementation and review. See [sources.md](references/sources.md) for provenance and [LICENSE](LICENSE) for redistribution terms. This is independent work with no Anthropic endorsement or certification.
