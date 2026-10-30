# Repository instructions

The skill in this repository is retired; do not use it as the delivery workflow for this repository either. Follow these instructions for scoped implementation, verification, and review. Existing user authorization persists; never fabricate approval or require repetitive approval for an already authorized action.

Before public upload, follow [PRIVACY.md](PRIVACY.md). Keep private authoring material, raw sessions, secrets, and customer or employer data out of this repository.

Run `python3 -m unittest discover -s skills/ai-sdlc-skill/tests -v` for helper changes and `python3 scripts/test_privacy.py` for privacy infrastructure changes. Preserve the documented authority, privilege, and sampling limitations. Do not claim runtime compatibility from file-copy or deterministic helper tests.

Use a focused PR, verify its current revision and required checks, resolve findings, and merge only within the user's authorization. Pin third-party Actions to full commit SHAs. Keep repository-specific application commands in adopters.

## Route by change

- Installation or host setup: [INSTALLATION.md](INSTALLATION.md).
- Plugin packaging: [PLUGIN.md](PLUGIN.md) and contributor packaging checks.
- Guides and contributor instructions: [guide maintenance](CONTRIBUTING.md#maintain-guides).
- Skill body or reference behavior: [CONTRIBUTING.md](CONTRIBUTING.md), including
  the behavioral cases required before claiming host behavior.
- Public upload: [PRIVACY.md](PRIVACY.md).

Keep application checks in adopters; bundled-document and repository-wide checks cover
different surfaces. Use the contributor commands for the surface being changed.
