# Use AI SDLC Skill with your assistant

Choose the assistant you already use. The same workflow can guide Codex, Claude, and other agents; installation and available tools belong to the host. This repository ships a skill folder, not a marketplace plugin or an MCP server.

## Obtain a reviewed copy

Clone the source and select a reviewed full commit SHA before copying files. This example selects the first published revision; choose a later reviewed commit when updating:

```sh
git clone https://github.com/Andreasniss/ai-sdlc-skill.git
cd ai-sdlc-skill
git checkout --detach 793ca27f23b336e21b50972919146c9bfcacaba2
```

Read `skills/ai-sdlc-skill/SKILL.md` and its `references/adoption.md`. Keep the complete folder so supporting references and the optional helper remain available. Preserve local modifications before updating. Never overwrite an existing installation without reviewing it.

The following shell commands run from that source checkout. They assume a POSIX shell; Windows users can use WSL or copy the folder manually. The optional helper requires POSIX, Python 3.10+, and Git. Instructions can still support planning on a host without those tools.

## ChatGPT and Codex

For local Codex, use `$skill-installer` and give it the repository, `skills/ai-sdlc-skill` directory, and reviewed commit. Alternatively, install a personal copy:

```sh
mkdir -p "$HOME/.agents/skills"
test ! -e "$HOME/.agents/skills/ai-sdlc-skill" && cp -R skills/ai-sdlc-skill "$HOME/.agents/skills/ai-sdlc-skill"
```

A repository-scoped copy belongs in that project's `.agents/skills/ai-sdlc-skill/`. Choose one scope. In Codex CLI or the IDE extension, use `/skills` or `$ai-sdlc-skill`; restart if discovery does not refresh.

In the ChatGPT desktop app, inspect **Skills** and use `@` to select an available skill. A local folder does not automatically install it into ChatGPT web or mobile. Those surfaces support plugin-distributed skills; this repository has no published plugin. Use the manual route below when native installation is unavailable.

These paths and product distinctions follow [OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills). Verify discovery in the environment doing the work, especially when switching between local and cloud sessions.

## Claude Code

Install for your personal projects:

```sh
mkdir -p "$HOME/.claude/skills"
test ! -e "$HOME/.claude/skills/ai-sdlc-skill" && cp -R skills/ai-sdlc-skill "$HOME/.claude/skills/ai-sdlc-skill"
```

For a shared project, copy the folder to that project's `.claude/skills/ai-sdlc-skill/` instead. Invoke `/ai-sdlc-skill` with a concrete task. A fresh remote session needs access to the skill there; a folder on your laptop alone is insufficient. See [Claude Code's skill locations and invocation](https://code.claude.com/docs/en/skills).

## Claude chat and Cowork

Where custom skills are enabled, ZIP the `ai-sdlc-skill` folder from inside `skills/`, preserving its contents. In Claude, open **Customize > Skills**, choose **+ > Create skill > Upload a skill**, upload the ZIP, and enable it. Ask Claude to use AI SDLC Skill for your task. Availability can depend on your organization's settings. See [Claude's custom-skill instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

Loading instructions does not grant access to your development repository, its Git history, or a terminal. Supply the necessary files and use planning/review mode if the environment cannot run the required checks. Do not upload credentials or private sessions as skill resources.

## GitHub Copilot and other coding assistants

GitHub documents project skills under `.github/skills/`, `.claude/skills/`, or `.agents/skills/`. Copy this complete folder to one supported location, for example `.github/skills/ai-sdlc-skill/`, then explicitly ask Copilot to use it. Consult [Copilot's supported skill surfaces](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) for the host you use.

For another assistant with native Agent Skills support, follow that product's documented discovery path. Do not assume it recognizes Codex's `$` syntax or Claude's slash command. Confirm that it loaded this skill before relying on the workflow.

For assistants without native support, keep a reviewed copy at `skills/ai-sdlc-skill/` in your project and explicitly ask the agent to read its `SKILL.md` and relevant references. Add a pointer to the project's existing instruction file when useful, preserving its current rules. In a chat-only interface, attach those files and the relevant diff or requirements. This is manually supplied context, not an installed skill or persistent integration.

## First task and verification

Use a small, reversible change in a disposable branch:

> Use AI SDLC Skill to correct this documentation example. First read the repository's rules and choose the appropriate planning depth. Make only the requested change. Report the revision, checks actually run, any findings, and remaining limits. If you cannot run a required check, say so.

For native invocation, prefix that task with the host's skill selector. Check three observable outcomes: the agent found the repository rules, kept the requested scope, and distinguished completed checks from missing evidence. Ask it which skill file it loaded.

To test the optional helper itself, from the source repository root run:

```sh
python3 -m unittest discover -s skills/ai-sdlc-skill/tests -v
```

For an adopter, review its own `delivery-checks.json`, commit the candidate, and run:

```sh
python3 skills/ai-sdlc-skill/scripts/verify.py --repo . --config delivery-checks.json
```

That second path assumes the project keeps the bundle at `skills/ai-sdlc-skill/`, as the pilots do. Adjust the helper path for a personal installation. The helper executes reviewed commands with your privileges and requires a clean committed candidate. Read its adoption guide first.

## What is verified

As of 6 September 2026, 12 helper tests pass, and 7DayFocus and Runbook Relay have merged repository integrations with application checks and pinned source manifests. Installation instructions above are based on the linked product documentation. File copying and test execution do not establish interactive compatibility or better decisions across those assistants. Record the actual host and observed behavior when you try the first task.

For updates, compare the chosen source revision, preserve local edits, and replace only the reviewed bundle through your project's normal change process. Keep the full source commit and file digests with each adopter. Never update automatically when an agent starts. See the [migration guide](skills/ai-sdlc-skill/README.md#migrate-from-evidence-sdlc) for the old identifier.
