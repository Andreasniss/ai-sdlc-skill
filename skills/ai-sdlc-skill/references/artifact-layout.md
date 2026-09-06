<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Find and organize delivery artifacts

Use this reference when initializing repository documentation, locating a change's records, or choosing where new artifacts belong. Preserve an established layout and link to its canonical records. Do not relocate files merely to match this example.

## Two homes: reusable skill and project records

The reusable instructions in this repository live at `skills/ai-sdlc-skill/SKILL.md`; this guide is `skills/ai-sdlc-skill/references/artifact-layout.md`. Runtime installation may place the bundle elsewhere, as explained in the [installation guide](https://github.com/Andreasniss/ai-sdlc-skill/blob/main/INSTALLATION.md).

The adopting project's intent, specification, plan, and evidence belong in that project's repository, outside the installed skill folder. Installing this bundle does not create change packets. The worked example lives in [7DayFocus's P04 folder](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/tree/main/docs/ai-dlc/changes/P04-plan-my-week); its [lifecycle index](https://github.com/Andreasniss/7dayfocus-ai-delivery-lab/blob/main/docs/ai-dlc/README.md) is the entry point for other changes.

## One folder per scoped change, developed over time

When material work needs a packet and the repository has no existing convention, use `docs/ai-dlc/changes/<change-id>-<short-name>/`. The identifier groups one feature, correction, or other accepted scope across its planning, implementation, review, and release sessions. It is not a new folder per prompt, agent, test run, or review correction.

| File in the change folder | Create or update when | Content |
| --- | --- | --- |
| `intent.md` | Establishing the outcome | User need, constraints, exclusions, success criteria, and unresolved decisions |
| `spec.md` | Turning intent into a testable contract | Behavior, design, interfaces, risks, and failure cases; links to applicable standing policies and ADRs |
| `plan.md` | Planning implementation | Ordered work, dependencies, affected files, verification steps; update when implementation materially departs |
| `evidence.md` | Checks and reviews produce observations | Candidate identity, commands and results, findings and corrections, PR/release links, and remaining limits |

A completed material change normally has all four under this convention. Create useful content as stages progress; do not manufacture completed evidence or four empty files at the start. Update the same packet while addressing its findings. A later separately scoped feature or incident correction gets a new identifier and links back to the earlier packet. Preserve historical results and distinguish new observations from the old candidate's checks.

Add a link from the root README to a lifecycle index, and from that index to change folders. Put the packet path in the issue or PR so the next session can find it. Existing GitHub status remains live; a committed packet records the change and its evidence. A small reversible fix can keep its whole record in the existing issue or PR unless repository rules require more.

### What Anthropic actually specifies

The [Anthropic playbook](https://claude.com/blog/the-ai-native-sdlc-playbook), reviewed 6 September 2026, recommends an `intent/` folder in a single product's repository as a simple shared home. It places `spec.md` alongside `intent.md` and commits an accepted `plan.md`, updated with implementation deviations. It discusses tests, review, and operational evidence, without naming an `evidence.md` file or requiring exactly four colocated files per cycle. The per-change folder and fourth ledger are this adaptation's convention, consistent with keeping the artifact chain beside the code. An existing `intent/` layout is equally valid; do not create both hierarchies.

## Standing documents span many changes

These conventions come from general repository documentation, open-source collaboration, architecture practice, and agent tools. They are useful with AI-assisted delivery; they are not an AI-DLC-required checklist. Inspect what exists before adding anything, and create only documents the project needs.

| Document | Suggested home when starting fresh | When useful and what it owns |
| --- | --- | --- |
| `README.md` | Root | Project entry point, setup, verified commands, and links to deeper records |
| `LICENSE`, applicable `NOTICE` | Root; preserve bundled notices | Actual reuse terms and attribution; preserve existing grants and third-party terms |
| `CONTRIBUTING.md` | Root | Contribution setup, checks, and review expectations; a README section can suffice for a tiny project |
| `SECURITY.md` | Root | Supported scope and an actual private vulnerability-reporting route, with no invented response promises |
| `PRIVACY.md` | Root if a contributor boundary; otherwise the existing policy home | Clearly distinguish publication hygiene from product data handling; link the relevant product privacy explanation where needed |
| `PROVENANCE.md` | Root when origins are material; otherwise a linked `docs/` record | Source origins, inherited material, AI assistance, and attribution; not a substitute for build attestations |
| `AGENTS.md`, `CLAUDE.md` | Host-discovered locations and applicable scopes | Agent instructions and pointers to canonical policies; follow the host's rules and avoid competing copies |
| `REVIEW.md` | Root or linked `docs/` location | Substantial project-specific review criteria, if needed beyond contribution guidance |
| Threat model, architecture, runbooks | `docs/`, for example `docs/THREAT-MODEL.md` | Maintained system boundaries and operational procedures |
| Architectural decision records | `docs/adr/` | Decisions whose rationale matters across changes; link from affected specifications |
| Change packets | `docs/ai-dlc/changes/<change>/` or existing equivalent | One scoped change's intent, specification, plan, and observed evidence |

Reference standing documents from the packet; update their canonical files when the change alters them. For example, a new provider can affect the threat model and data-handling explanation as well as its own spec. Do not copy every policy into every packet. Keep sensitive analysis in its authorized private home and publish only appropriate summaries.

GitHub recognizes specific [community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file), including `SECURITY.md` and `CONTRIBUTING.md`, in `.github/`, root, or `docs/`, with that precedence. Root is this guide's discoverability recommendation, not the only valid location. `PRIVACY.md`, `PROVENANCE.md`, and `REVIEW.md` have no equivalent universal GitHub role; describe their purpose and link them explicitly. Match existing filename case, since links can be case-sensitive.

The [ADR community](https://adr.github.io/) explains architecture decision records. [SLSA provenance](https://slsa.dev/spec/v1.2/provenance) concerns machine-verifiable build origin and process; a human-authored `PROVENANCE.md` is a different kind of record. Markdown supplies readable versioned text, not policy enforcement.
