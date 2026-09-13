# Sources and implementation choices

Anthropic references reviewed 2026-09-06; practitioner references reviewed 2026-09-13. Source pages may change.

- [Anthropic: The AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook): selected ideas include versioned handoffs, modular adoption, continuous evaluation, focused human judgment, and incident learning.
- [Anthropic: Hooks as approval gates](https://academy.claude.com/courses/ai-native-sdlc-playbook/hooks-as-approval-gates): controls belong at the action boundary, with managed enforcement where required. Tutorial command matching is not a general authorization system.
- [Claude Code skills](https://code.claude.com/docs/en/skills): skill packaging and progressive disclosure.
- [Claude Code hooks](https://code.claude.com/docs/en/hooks): runtime hook configuration and limitations.

## Practitioner guidance

- [Peter Steinberger: Just Talk To It](https://steipete.me/posts/just-talk-to-it): scoped changes, concrete context, and investigation when progress differs from expectations.
- [Peter Steinberger: Shipping at Inference-Speed](https://steipete.me/posts/2025/shipping-at-inference-speed): executable interfaces, discoverable project documentation, and iteration through using the product.
- [Peter Steinberger on building in the agent era](https://speedrun.substack.com/p/peter-steinberger-building-in-the-agent-era): review-and-repair loops, selective orchestration, and human judgment about interactions between features.

These are accounts of his working practices, not controlled evidence of productivity gains. His orchestration preferences changed between December 2025 and August 2026. This skill does not adopt direct-to-main work, broad machine access, automatic releases, or reduced recovery safeguards as defaults.

The proportional quick path, optional Python report helper, clean-revision requirement, no-output-retention default, repository-specific check configuration, hand-run behavior evaluation set with recorded disqualifiers and reproducible starting fixtures, and the single-location rule for encoding a recurring lesson are this project's choices. The feedback-capability check, explicit inner repair loop, stalled-work rule, and separation of correctness from product feedback are this project's operational adaptations. No claim of certification, endorsement, measured improvement, or full playbook implementation is made.

Original implementation by Andreas Nissen with AI assistance. Andreas owns intent, architecture, evaluation criteria, risk, and release decisions. No third-party community skill code or substantive text is incorporated. The bundle uses this repository's Apache-2.0 license; retain its license when redistributing.
