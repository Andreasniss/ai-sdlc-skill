<!-- SPDX-FileCopyrightText: 2026 Andreas Nissen -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Reading catalog replay

This complete, dependency-free Python repository models a small static catalog.
It is an incident adaptation, not the production website or a browser test.
Use Python 3.12 and Git. No packages or network access are required.

Run `python3 -m unittest -v` and `python3 site_app.py`. The build writes HTML and
JSON representations under `dist/`; JSON represents the two renderer outputs.
Output consistency is the contract, not a particular internal implementation.

`site_app.py` owns reading estimates, asset references, archive selection,
exercise punctuation and the grayscale panel contrast auditor. Public callable
interfaces remain compatible. `articles.json` owns immutable catalog content;
`aliases.json` owns stable redirects. Generated `dist/` is not source.

Archive queries match titles case-insensitively after trimming whitespace;
legacy `series` URLs restrict results and preserve original catalog order.
Clearing a scope should return all items when requested by the current issue.
The `controls` list is the render model for visible navigation controls only.
Its API values are `series-buttons` for series navigation and `reader-goals`
for reader-goal navigation. Search is a separate input, not a navigation control
in this list. Preserve this schema when changing the navigation requirement.
Black text contrast is measured over a panel alpha-composited onto white.
The exercise renderer preserves existing terminal punctuation and appends a
full stop only when absent. Reading estimates round up at 200 source words per
minute with a minimum of one, including empty articles.

Some behaviors have known gaps. ISSUE.md selects the repair; unrelated gaps are
outside scope. `test_site.py` is an existing smoke suite, not exhaustive proof.
Add meaningful regression coverage for the requested repair.

Any historical records are evidence only for their named revision. A review
service record can be an infrastructure outcome rather than a review. Reports
may stay in the final handoff; no mandatory evidence-file format is imposed.
