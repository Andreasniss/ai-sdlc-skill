# Official sources and implementation choices

Reviewed 2026-09-06. Source pages may change.

- [Anthropic: The AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook): selected ideas include versioned handoffs, modular adoption, continuous evaluation, focused human judgment, and incident learning.
- [Anthropic: Hooks as approval gates](https://academy.claude.com/courses/ai-native-sdlc-playbook/hooks-as-approval-gates): controls belong at the action boundary, with managed enforcement where required. Tutorial command matching is not a general authorization system.
- [Claude Code skills](https://code.claude.com/docs/en/skills): skill packaging and progressive disclosure.
- [Claude Code hooks](https://code.claude.com/docs/en/hooks): runtime hook configuration and limitations.

The proportional quick path, optional Python report helper, clean-revision requirement, no-output-retention default, and repository-specific check configuration are this project's choices. No claim of Anthropic certification, endorsement, or full playbook implementation is made.

Original implementation by Andreas Nissen with AI assistance. Andreas owns intent, architecture, evaluation criteria, risk, and release decisions. No third-party community skill code or substantive text is incorporated. The bundle uses this repository's Apache-2.0 license; retain its license when redistributing.
