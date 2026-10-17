# Contributing

Read [README.md](README.md) for prerequisites and the supported project scope,
[AGENTS.md](AGENTS.md) for repository instructions, and [PRIVACY.md](PRIVACY.md)
before uploading public changes. Use fictional examples and keep credentials and
private working material outside the repository.

## Verify a change

Run from the repository root with the documented runtime:

```sh
python3 -m unittest discover -s skills/ai-sdlc-skill/tests -v
python3 scripts/test_docs_consistency.py
python3 scripts/test_plugin_packaging.py
python3 scripts/check_privacy.py --staged
python3 scripts/check_privacy.py --range origin/main HEAD
```

Changing `SKILL.md` or anything under `references/` changes agent configuration. Rerun the
behavior cases in `skills/ai-sdlc-skill/evals/cases.md` against the host you use, record the
run, and validate it before claiming the instructions still behave:

```sh
python3 skills/ai-sdlc-skill/scripts/eval_report.py \
  --cases skills/ai-sdlc-skill/evals/cases.json --digest
python3 skills/ai-sdlc-skill/scripts/eval_report.py \
  --cases skills/ai-sdlc-skill/evals/cases.json --results run.json
```

Record the digest in the run as `cases_sha256`. A run recorded against a different case
set is rejected rather than reported. Build the starting repository a case names with
`skills/ai-sdlc-skill/scripts/make_fixture.py`, and after changing `evals/cases.json` render
the readable copy with `skills/ai-sdlc-skill/scripts/render_cases.py`.

A recorded run is one person's observation of one host. Report it as that.

Include the problem, scoped change, actual checks and affected revision in a focused
pull request. Add regression coverage for behavior changes and preserve documented
limitations. Required CI must pass before merge. Documentation-only changes should
verify links and licensing consistency without claiming application behavior tests
that were not run.

## Licensing and reporting

Submit only work you have the right to contribute. Contributions intended for
inclusion follow [Apache-2.0](LICENSE), unless explicitly agreed otherwise. Preserve
third-party license and copyright notices; identify copied material and its source.
Report sensitive vulnerabilities through [SECURITY.md](SECURITY.md), not a public
issue. Ordinary bugs and improvements can use this repository's GitHub issues.

## Maintain guides

Use this standard for repository instructions, contributor documentation and
workflow references. It governs guide quality, not the receiving project's
authority or release process. Keep local constraints with their existing owner.

- Give each rule one canonical home. Route readers there by task; say when to
  load specialist context instead of repeating its procedure in every entry file.
- Make consequential instructions actionable: trigger, prerequisites, action,
  expected result, and relevant exception. Separate requirements from optional
  techniques and examples. Verify commands against the actual configuration.
- Preserve user steering, existing authorization and receiving-repository gates.
  References and historical plans do not authorize new work. Do not copy private
  source material or impose another project's workflow.
- Distinguish planned, attempted, passed and blocked checks. Name the revision and
  surfaces covered; a file check is not runtime verification, and source retrieval
  is not a complete factual review. Keep current execution status in its existing
  PR or check system rather than in standing instructions.
- Review the motivating failure and an ordinary case that should stay simple.
  If a rule was present but missed, improve its entry route or execution check
  before adding prose. Search consumers for obsolete duplicates and preserve
  historical evidence as historical. Report observed improvements, not assumed
  productivity gains.

For example, correcting a setup command should let a new contributor run it from
the stated directory while leaving a documentation-only change free of unrelated
service calls. Keep deterministic requirements in existing checks where practical;
judgment still needs review. Use the repository's ordinary contribution path, not
a separate guide approval packet.

These practices are informed by [OpenAI's AGENTS.md guidance](https://developers.openai.com/codex/guides/agents-md/)
and [Anthropic's Claude Code best practices](https://code.claude.com/docs/en/best-practices).
They are authoring guidance, not a claim of measured agent performance.
