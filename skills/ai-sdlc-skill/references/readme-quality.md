<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Write a useful README

Use when creating a public repository, initializing its documentation, changing how users start, or reviewing a README. For an unrelated code change, check whether setup or public claims changed; do not rewrite the README by default.

## Inspect before drafting

Identify the primary reader and their first useful action. Read repository rules, the existing README, manifests, scripts, license, and relevant evidence. Check whether the README is generated and edit its source when it is. Confirm current repository visibility and ownership; a public website does not imply a public source repository.

Distinguish a runnable project, library, skill, profile and learning fork. Preserve upstream ownership and reuse terms. Do not turn a personal experiment into a production claim or copy a mentor's marketing language as evidence.

## Build the first reading path

Use this order when it fits the project, not as mandatory headings:

1. **What it does:** a concrete sentence naming the task and intended user. Put experimental, archived or fork status near the introduction when it changes the adoption decision.
2. **Try it:** one recommended demo, installation or reading path. Put prerequisites before commands and a visible expected result after them. State the working directory and distinguish no-key fixtures from paid or connected modes.
3. **Why inspect it:** a few distinguishing behaviors, each supported by code, a real capture or evidence. Describe outcomes before internal terminology.
4. **Limits and deeper reading:** retain material data, cost, compatibility and evidence limits near the relevant action. Link architecture, reference material and historical evaluations from their canonical homes.
5. **Contribute and reuse:** link contribution, reporting, privacy and license documents as applicable. Preserve attribution and third-party exceptions.

A profile needs useful project choices, not installation steps. A learning fork needs an upstream link and an honest starting path, not a claim of authorship. A library needs a minimal usage example; a skill needs an invocation and expected result, not just a copy command.

Do not impose an arbitrary total word count. As a review heuristic, reconsider paragraphs longer than about 80 words or sentences longer than about 25 words. Keep technical precision where needed; explain unfamiliar terms once. Delete repeated claims before adding navigation. Prefer a few descriptive links over a large table of contents.

## Make it work on a phone

- Keep the default path in a single column. Replace prose-heavy tables with short lists; retain genuinely comparative tables only when the narrow layout works.
- Use descriptive link labels instead of raw long URLs in prose. Avoid a long opening row of badges or social links.
- Keep code examples short. Split shell commands only with syntax valid for the stated shell; do not break a copyable command just to meet a line length. Long identifiers can scroll inside a code block.
- Use informative alternative text and genuine screenshots. Do not make essential instructions available only inside an image. Avoid fixed-width side-by-side screenshots and wide ASCII diagrams.
- Use sequential heading levels. Put optional platform variants in linked guides or clearly labeled disclosure blocks. Never hide the main quick start or a material warning in a collapsed block.
- Moving content is a navigation change: fix relative paths, image paths and incoming section links. Where an old README anchor is used externally, keep a short pointer under that heading when practical.

## Verify the candidate

Review the complete diff against the existing claims and actual configuration. Check local link targets and section anchors, license and attribution, prerequisites, command order and expected output. Run commands when proportionate and safe; distinguish source inspection from execution. Do not run paid model calls or deploy just to check a documentation edit.

Inspect the rendered candidate at 320 and 390 CSS pixels and a desktop width when browser access permits. Check the opening, the first action, code blocks, images, tables and expanded details. Normal prose should not require horizontal scrolling. A code block may scroll internally without pushing the whole page wide. GitHub owns its interface; assess the README content separately from site chrome.

A Markdown preview is only a proxy for GitHub. State the renderer and widths actually inspected. Without rendering access, report source-only mobile review, not visual verification or WCAG conformance. Static checks cannot prove that readers understand the page.

Use a short outcome checklist in the existing PR:

- Can a new reader explain what it does and who it serves?
- Can they reach one useful action without reading the implementation history?
- Are setup, costs, data replacement and compatibility limits clear where needed?
- Can they find the evidence and contribution route?
- Were narrow-screen rendering and links actually checked, or explicitly left unverified?

## Improve the guidance from feedback

When a reader reports a problem, retain one concrete before/after example in the existing issue or PR. Identify the cause: unclear purpose, excess detail, jargon, broken setup, hidden limitation or layout. Change the smallest relevant rule here, and recheck the motivating example plus an ordinary short README that should remain simple. Do not create a new recurring audit, score dashboard or duplicate rule file.

If setup is wrong, success means the stated path works. If prose is dense, success means readers can find and explain the first action. Fewer words alone is not success. Keep model behavior, human comprehension, link validity and rendering evidence distinct. Follow [evaluation guidance](evaluation.md) when changing these agent instructions; never describe deterministic checks as a behavior benchmark.

## Research and adaptations

Sources inspected 27 October 2026. These are examples and rationale, not proof that a popular project has the best README. Borrow structure, not wording or unsupported claims.

- [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes): explain the project and getting started; use relative links within a repository and move lengthy documentation out of the entry page.
- [GitHub: accessible profile pages](https://github.com/orgs/community/discussions/64778): plain language, meaningful alternative text and heading order also apply to project READMEs.
- [W3C: Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html): 320 CSS pixels motivates the narrow-width check. This does not establish GitHub or project WCAG conformance.
- [Peter Steinberger: Summarize](https://github.com/steipete/summarize): concrete purpose, a real example, early installation and a no-key extraction path; optional capabilities link to focused guides. Its tables still need narrow-screen scrutiny.
- [Addy Osmani: Agent Skills](https://github.com/addyosmani/agent-skills): reader tasks map to commands, with host-specific details separated from the quick start. Do not copy the wide lifecycle diagram or infer quality from “production-grade” language.
- [Matt Pocock: Skills](https://github.com/mattpocock/skills): explicit installation choices and an expected setup action. Adapt its progressive disclosure without hiding the primary path or introducing unnecessary setup steps.
- [Simon Willison: LLM](https://github.com/simonw/llm): task-oriented capabilities, executable examples and linked reference documentation. Its README is generated, illustrating why the editable source matters. Multiple installation alternatives need not all occupy another project's opening.

The paragraph heuristics, selected reading order and feedback loop above are this project's adaptations, not requirements imposed by those sources.
