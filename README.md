# AI SDLC Skill

> [!WARNING]
> **I no longer recommend using this skill.** My latest evaluation found it bought one extra accepted run in twelve on the harder cases for about 28% more median tokens, and on simple tasks it only added cost. Current models and harnesses do this work well from a repository's own instructions. The reasoning and results are in [Does My AI Skill Still Earn Its Place?](https://andreasnissen.dev/projects/ai-sdlc-skill/). This repository stays public as the record of the experiment.

Reusable instructions that help a coding agent carry a software change through implementation, checks, review and handoff.

**Experimental, version 0.6.0.** Test it against no skill before adopting it. In a small October comparison, the earlier full skill and no skill both completed 12/12 tasks; the full skill used 48.2% more median worker tokens. The current reduced edition has not been benchmarked. [Methods and limits](GUIDE.md#evidence-and-limits).

## Reproduce the experiment

Only install it to reproduce or extend the comparison, never as your delivery workflow. From your project directory, with Node.js and npm available:

```sh
npx skills@latest add Andreasniss/ai-sdlc-skill \
  --skill ai-sdlc-skill
```

Choose your coding assistant and installation scope. This installs from the default branch. Use the [pinned installation](GUIDE.md#reduced-edition-and-pinned-installation) to reproduce the reviewed reduced candidate, or the [installation guide](INSTALLATION.md) for other hosts and updates. Local installation does not install the skill into ChatGPT web or mobile.

In a disposable branch, choose a real documentation error and ask your agent:

> Use AI SDLC Skill to fix this documentation example. Follow the repository rules. Report the skill file loaded, the change, checks run and remaining limits.

Inspect the diff and actual check results. Expected result: a scoped correction with honest verification, not a generated plan alone. This trial checks loading and behavior; it does not establish an advantage over no skill.

## Reduced edition and pinned installation

For the exact reviewed reduced candidate, follow the [pinned checkout instructions](GUIDE.md#reduced-edition-and-pinned-installation). That historical pin does not include later README guidance. Existing installations are not updated automatically.

## When to use it

Try it when your agent loses accepted decisions, checks the wrong behavior, or leaves work that another session cannot continue. These are intended uses, not measured benefits.

For clear, authorized work, Auto can be sufficient. Use Plan mode to settle requirements or the approach first. Neither mode changes permissions or release authority.

- [Read the instructions](skills/ai-sdlc-skill/SKILL.md).
- [Compare with no skill](GUIDE.md#compare-with-no-skill).
- [Try the reproducible task-list example](GUIDE.md#reproduce-the-task-list-example).
- [Choose a prompt for your task](skills/ai-sdlc-skill/references/common-cases.md).
- [Improve a repository README](skills/ai-sdlc-skill/references/readme-quality.md).

## Evidence and limits

The skill installs no hooks, grants no permissions and authorizes no release. Ordinary use runs your project's own checks. The [optional Python helper](skills/ai-sdlc-skill/references/adoption.md) records command results; it is not a sandbox or approval system.

The historical 20 October snapshot records **58 passing deterministic tests**. Those checks cover helpers and bundle consistency, not model judgment, cross-host compatibility or productivity. [Detailed evidence](GUIDE.md#evidence-and-limits) keeps the recorded revisions, comparisons and limitations together.

Read the [project article](https://andreasnissen.dev/projects/ai-sdlc-skill/) for the lessons learned, or the [experiment article](https://andreasnissen.dev/writing/does-my-coding-skill-help/) for the measurements.

## Maintain or contribute

Follow [CONTRIBUTING.md](CONTRIBUTING.md) for checks and behavioral evaluation, and [PRIVACY.md](PRIVACY.md) before public uploads. The [optional plugin pilot](PLUGIN.md) packages the same skill. It has no public marketplace listing and does not update itself on startup.

Built by [Andreas Nissen](https://andreasnissen.dev), with AI assistance. Andreas retains product, architecture, risk and release judgment. See [sources and provenance](skills/ai-sdlc-skill/references/sources.md) for the Anthropic, Peter Steinberger and Matt Pocock influences. This independent project implies no employer or provider endorsement.

Copyright 2026 Andreas Nissen. Original code and technical documentation: [Apache-2.0](LICENSE), except where indicated. See [NOTICE](NOTICE); third-party material retains its own terms.
