# AI SDLC Skill

A reusable, experimental skill for taking a software change from intent through verification and review, while preserving the repository's rules and the user's authority.

Independently built from selected [Anthropic AI-native SDLC guidance](https://claude.com/blog/the-ai-native-sdlc-playbook). This is the canonical source for the `ai-sdlc-skill` identifier, version 0.2.0.

## Try it

Read the [workflow](skills/ai-sdlc-skill/SKILL.md), then follow the [installation guide for ChatGPT, Codex, Claude, and other assistants](INSTALLATION.md). Pin a reviewed full commit SHA before installing. The guide includes a bounded documentation-change example and expected outcomes.

Run the deterministic helper tests from the repository root:

```sh
python3 -m unittest discover -s skills/ai-sdlc-skill/tests -v
```

The optional verification helper requires Python 3.10+, Git, and POSIX. It has no third-party Python dependencies. The skill itself consists of instructions and supporting documentation.

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

The pilots retain their earlier reviewed bundles. Adopters should record the full canonical source commit and update through a reviewed PR, never download a new version automatically on startup.

## Contribute and verify

Preserve the execution boundaries and add meaningful regression coverage when changing the helper. Follow [AGENTS.md](AGENTS.md) and the [publication privacy checks](PRIVACY.md). Keep application-specific check commands in the adopter repository.

See [sources and provenance](skills/ai-sdlc-skill/references/sources.md) and the [Apache-2.0 license](LICENSE).

Andreas owns intent, architecture, requirements, evaluation criteria, risk, and release decisions and reviews merged changes. AI tools assisted implementation and documentation. Automated and AI-assisted checks are evidence, not human reviewers or accountability owners.

A personal project by [Andreas Nissen](https://github.com/Andreasniss). Views are his own; no employer or Anthropic affiliation, endorsement, or certification is implied. [Portfolio](https://andreasnissen.dev) · [LinkedIn](https://www.linkedin.com/in/andreasnissen)
