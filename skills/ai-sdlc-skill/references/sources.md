# Sources and implementation choices

Anthropic references reviewed 2026-09-06; practitioner references reviewed 2026-09-22. Source pages may change.

- [Anthropic: The AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook): selected ideas include versioned handoffs, modular adoption, continuous evaluation, focused human judgment, and incident learning.
- [Anthropic: Hooks as approval gates](https://academy.claude.com/courses/ai-native-sdlc-playbook/hooks-as-approval-gates): controls belong at the action boundary, with managed enforcement where required. Tutorial command matching is not a general authorization system.
- [Claude Code skills](https://code.claude.com/docs/en/skills): skill packaging and progressive disclosure.
- [Claude Code hooks](https://code.claude.com/docs/en/hooks): runtime hook configuration and limitations.

## Practitioner guidance

- [Peter Steinberger: Just Talk To It](https://steipete.me/posts/just-talk-to-it): scoped changes, concrete context, and investigation when progress differs from expectations.
- [Peter Steinberger: Shipping at Inference-Speed](https://steipete.me/posts/2025/shipping-at-inference-speed): executable interfaces, discoverable project documentation, and iteration through using the product.
- [Peter Steinberger on building in the agent era](https://speedrun.substack.com/p/peter-steinberger-building-in-the-agent-era): review-and-repair loops, selective orchestration, and human judgment about interactions between features.
- [Kiro: How we built a software factory with Kiro Crew to merge 1000 PRs in a week](https://kiro.dev/blog/software-factory-1000-prs/): a five-stage account of moving from individual sessions to durable memory, queue-based stage workers, and finally supervisory coordination, with host-enforced permissions, scoped memory, durable coordination, auditability, and cost control.

The three Peter Steinberger sources are accounts of his working practices, not controlled evidence of productivity gains. His orchestration preferences changed between December 2025 and August 2026. This skill does not adopt direct-to-main work, broad machine access, automatic releases, or reduced recovery safeguards as defaults.

The proportional quick path, optional Python report helper, clean-revision requirement, no-output-retention default, repository-specific check configuration, hand-run behavior evaluation set with recorded disqualifiers and reproducible starting fixtures, and the single-location rule for encoding a recurring lesson are this project's choices. The feedback-capability check, explicit inner repair loop, stalled-work rule, and separation of correctness from product feedback are this project's operational adaptations. No claim of certification, endorsement, measured improvement, or full playbook implementation is made.

The queue-before-supervisor ladder and its outcome-oriented measurement rule
are this project's cautious adaptation of Kiro's vendor-authored case study.
Kiro reports 1,000 merged pull requests in seven days across a project with
nearly 500 community contributors, but does not publish PR-size distribution,
escaped-defect or rollback rates, review burden, business value, or total
inference cost. The report supports the architecture as a scaling pattern; it
does not establish that pull-request volume is a quality or value result.

The artifact-ownership test is also this project's choice. As recorded in the 2026-09-06 reading summarized in [artifact-layout.md](artifact-layout.md), the playbook specifies where the repository artifacts sit relative to the code, but does not divide the record between an issue tracker and the repository, and does not say how a tracker item becomes an accepted intent. Projects that keep a tracker need that boundary, so the three-question test, the reference-never-restate rule, and the single-identity rule for change identifiers are stated here rather than inherited.

Original implementation by Andreas Nissen with AI assistance. Andreas owns intent, architecture, evaluation criteria, risk, and release decisions. No third-party community skill code or substantive text is incorporated. The bundle uses this repository's Apache-2.0 license; retain its license when redistributing.
