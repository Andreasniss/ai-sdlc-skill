# AI SDLC Skill

An experimental delivery skill that preserves repository rules, scales planning to the change, and records verification for the candidate revision. Independently implemented by Andreas Nissen from selected [Anthropic AI-native SDLC guidance](https://claude.com/blog/the-ai-native-sdlc-playbook).

Version 0.2.0. Skill identifier and invocation: `ai-sdlc-skill` and `$ai-sdlc-skill`.

## Start here

Read [SKILL.md](SKILL.md) for the workflow and [adoption.md](references/adoption.md) for execution limits. The bundle has no Python package dependencies. Its optional helper needs Python 3.10+, Git, and a POSIX environment. It does not install hooks, change permissions, or authorize releases.

From this bundle's directory, run its deterministic tests:

```sh
python3 -m unittest discover -s tests -v
```

The initial [7DayFocus pilot](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/blob/main/docs/evidence-sdlc-pilot.md) and [Runbook Relay pilot](https://github.com/Andreasniss/runbook-relay-webmcp/blob/main/docs/evidence-sdlc-pilot.md) record repository integration and verification results. They do not establish faster delivery, better model judgment, or interactive runtime compatibility.

## Install a reviewed revision

Obtain a source checkout at a reviewed full commit SHA. From the source repository root, use one installation location for the runtime you are using. Do not install multiple copies in the same runtime's discovery paths.

For Claude Code personal skills:

```sh
mkdir -p "$HOME/.claude/skills"
test ! -e "$HOME/.claude/skills/ai-sdlc-skill" && cp -R skills/ai-sdlc-skill "$HOME/.claude/skills/ai-sdlc-skill"
```

For Codex, use its current documented skill-installation flow with this bundle's directory. Repository instructions can also explicitly link `skills/ai-sdlc-skill/SKILL.md`, as both pilots do. Verify discovery in the actual runtime before claiming installation success. File copying alone does not test agent invocation.

Try a bounded request: “Use $ai-sdlc-skill to correct this documentation example. Preserve existing repository rules, choose the appropriate planning depth, and report the checks you actually ran.” The expected outcome is a scoped change with evidence. Existing mandatory acceptance requirements still apply.

## Migrate from evidence-sdlc

This is an intentional identifier change. Inventory existing installations and any local edits before changing them. Preserve local edits outside skill discovery, install the reviewed new bundle only into an absent destination, and archive the old directory outside all discovery paths. Then update explicit invocations, repository instruction links, CI paths, and check configurations to `ai-sdlc-skill`. Do not retain an old-name alias that loads the same instructions twice.

The pilot repositories retain their original dated evidence records. Historical mentions of `evidence-sdlc` explain the migration; they are not current installation paths.

## Updates and the standalone repository

The canonical source is [Andreasniss/ai-sdlc-skill](https://github.com/Andreasniss/ai-sdlc-skill). Pin a reviewed full source commit in each adopter, verify the bundle contents and tests, and update through a PR. Never silently download or replace skills on agent startup. Repository-specific `delivery-checks.json` files stay with their applications.

The initial implementation and rename were verified in the two pilot repositories before extraction. Only installation documentation changed during extraction. The pilot bundles remain earlier reviewed copies until explicitly updated; they are not automatic mirrors.

## Evidence and authority

The helper runs reviewed commands with the caller's privileges and discards child output. A passing report is an observation, not authenticated approval. It checks repository identity before and after each command, not continuously. Consult the adoption guide before use with untrusted code, secrets, or external systems.

Andreas owns intent, architecture, evaluation criteria, risk, and release decisions. AI assisted with implementation and review. See [sources.md](references/sources.md) for provenance and [LICENSE](LICENSE) for redistribution terms. This is independent work with no Anthropic endorsement or certification.
