# Use AI SDLC Skill with your assistant

Choose the assistant you already use. The same workflow can guide Codex, Claude, and other agents; installation and available tools belong to the host. This repository ships a skill folder, not a marketplace plugin or an MCP server.

## Recommended: Skills CLI

From your project directory, with Node.js and npm installed:

```sh
npx skills@latest add Andreasniss/ai-sdlc-skill --skill ai-sdlc-skill
```

Choose your agents in the installer. Project scope is the default; add `--global` for a personal installation. Choose one installation route and scope so duplicate copies do not compete.

| Task | Command |
| --- | --- |
| Discover without installing | `npx skills@latest add Andreasniss/ai-sdlc-skill --list` |
| Target Codex | `npx skills@latest add Andreasniss/ai-sdlc-skill --skill ai-sdlc-skill --agent codex` |
| Target Claude Code | `npx skills@latest add Andreasniss/ai-sdlc-skill --skill ai-sdlc-skill --agent claude-code` |
| Inspect installed skills | `npx skills@latest list` |
| Update this skill explicitly | `npx skills@latest update ai-sdlc-skill` |

Preserve local edits and review changes before updating. An installer lockfile tracks installation state; it is not evidence that the agent used the skill or that its changes passed review. The [Skills CLI documentation](https://github.com/vercel-labs/skills) owns current options and supported agents. This is a common distribution tool, not a universal native installer for every chat product.

## Optional: pin a reviewed source revision

For a team or reproducible pilot, replace `REVIEWED_FULL_COMMIT_SHA` below with the full 40-character SHA you reviewed. Check it out before the first installation:

```sh
git clone https://github.com/Andreasniss/ai-sdlc-skill.git
cd ai-sdlc-skill
git checkout --detach REVIEWED_FULL_COMMIT_SHA
git rev-parse HEAD
```

Continue only after checkout succeeds and `git rev-parse HEAD` matches the selected SHA exactly. From the adopter project's directory, pass this local checkout's path to `npx skills@latest add` with `--skill ai-sdlc-skill`. Record that SHA with the adopter's change record and repeat the same checkout before reinstalling or updating a pinned copy. Never substitute the GitHub shorthand here: it selects the current default branch.

Read the [skill instructions](skills/ai-sdlc-skill/SKILL.md) and [adoption guide](skills/ai-sdlc-skill/references/adoption.md). Manual installation below assumes you are in the source checkout. Copy the complete folder, preserve existing installations, and select only one discovery location. The shell examples use POSIX; Windows users can use WSL or copy the folder manually. The optional helper requires POSIX, Python 3.10+, and Git.

## ChatGPT and Codex

Use the CLI route above for local Codex. Its native `$skill-installer` is another option: provide the repository and `skills/ai-sdlc-skill` directory, plus a reviewed commit when pinning. For a manual personal copy:

```sh
mkdir -p "$HOME/.agents/skills"
test ! -e "$HOME/.agents/skills/ai-sdlc-skill" && cp -R skills/ai-sdlc-skill "$HOME/.agents/skills/ai-sdlc-skill"
```

A repository-scoped copy belongs in that project's `.agents/skills/ai-sdlc-skill/`. Choose one scope. In Codex CLI or the IDE extension, use `/skills` or `$ai-sdlc-skill`; restart if discovery does not refresh.

In the ChatGPT desktop app, inspect **Skills** and use `@` to select an available skill. A local folder does not automatically install it into ChatGPT web or mobile. Those surfaces support plugin-distributed skills; this repository has no published plugin. Use the manual route below when native installation is unavailable.

These paths and product distinctions follow [OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills). Verify discovery in the environment doing the work, especially when switching between local and cloud sessions.

## Claude Code

Use the CLI route above, or manually install for your personal projects:

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

Choose a task that matches your starting point from [common cases and prompts](skills/ai-sdlc-skill/references/common-cases.md). For a quick trial in an existing repository, use a small, reversible change in a disposable branch:

> Use AI SDLC Skill to correct this documentation example. First read the repository's rules and choose the appropriate planning depth. Make only the requested change. Report the revision, checks actually run, any findings, and remaining limits. If you cannot run a required check, say so.

For native invocation, prefix that task with the host's skill selector. Check three observable outcomes: the agent found the repository rules, kept the requested scope, and distinguished completed checks from missing evidence. Ask it which skill file it loaded.

## Optional: recorded evaluation runs

Changing `SKILL.md` or its references changes agent configuration. The bundle ships behavior cases in `skills/ai-sdlc-skill/evals/cases.md` for rechecking the obvious failure modes after such a change, and a reporter that validates a recorded run against them:

```sh
python3 skills/ai-sdlc-skill/scripts/eval_report.py \
  --cases skills/ai-sdlc-skill/evals/cases.json --results run.json
```

You run the cases by hand against your own host and record what you observed. Read [evaluating this skill](skills/ai-sdlc-skill/references/evaluation.md) for the recording format and its limits: a run is one person's observation of one host, not authenticated evidence and not approval.

## Optional: recorded check reports

You can use the skill without this helper. The agent normally runs your project's build, tests, or other checks directly and reports what happened. The helper is useful when you want a structured report tying reviewed commands and their results to a clean committed candidate. It does not select suitable checks or review your application.

The following command is for contributors or adopters evaluating the helper's implementation. Run it from a checkout of this skill repository; it tests the bundled Python runner, including its failure handling. It does not test your project or confirm skill discovery:


```sh
python3 -m unittest discover -s skills/ai-sdlc-skill/tests -v
```

For an adopter, review its own `delivery-checks.json`, commit the candidate, and run:

```sh
python3 skills/ai-sdlc-skill/scripts/verify.py --repo . --config delivery-checks.json
```

That second path assumes the project keeps the bundle at `skills/ai-sdlc-skill/`, as the pilots do. Adjust the helper path for a personal installation. The helper executes reviewed commands with your privileges and requires a clean committed candidate. Read its adoption guide first.

## What is verified

As of 6 September 2026, 31 bundle tests pass, and 7DayFocus and Runbook Relay have merged repository integrations with application checks and pinned source manifests. Those pilots were verified against an earlier reviewed bundle and have not been rerun for this revision. Installation instructions follow the linked product and installer documentation. File copying, installer discovery, and helper tests are separate from interactive compatibility or better decisions across assistants. Record the actual host and observed behavior when you try the first task.

For pinned adopters, compare the chosen source revision and replace the reviewed bundle through the project's change process. Keep the full source commit and file digests. For ordinary CLI installations, use the explicit update command above after preserving edits. Never update automatically when an agent starts. See the [migration guide](skills/ai-sdlc-skill/README.md#migrate-from-evidence-sdlc) for the old identifier.
