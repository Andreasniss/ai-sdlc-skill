#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Evaluator-only behavioral probes. No process claims are inferred from prose."""
import importlib.util
import json
import math
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlsplit


def evaluate(root, case_id, phase):
    spec = importlib.util.spec_from_file_location("candidate", root / "site_app.py")
    app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app)
    checks = []

    def check(name, function):
        try:
            function()
            checks.append({"name": name, "passed": True})
        except Exception as error:
            checks.append({"name": name, "passed": False,
                           "reason": type(error).__name__ + ": " + str(error)})

    def equal(actual, expected):
        if actual != expected:
            raise AssertionError(f"expected {expected!r}, received {actual!r}")

    rows = json.loads((root / "articles.json").read_text())

    if case_id == "ordinary-reading-time":
        def policy():
            # Boundary and unequal expansion examples, not implementation text.
            for count in (0, 1, 199, 200, 201, 399, 400, 401, 1201):
                row = {"source": "word\t" * count, "html": "extra " * (count + 300),
                       "markdown": "short"}
                for output in ("html", "markdown"):
                    equal(app.reading_time(row, output), max(1, math.ceil(count / 200)))

        def all_surfaces():
            app.build()
            expected = [{"id": row["id"], "minutes": max(1, math.ceil(len(row["source"].split()) / 200))}
                        for row in rows]
            for output in ("html", "markdown"):
                data = json.loads((root / "dist" / (output + ".json")).read_text())
                for surface in ("articles", "cards", "related"):
                    equal([{"id": row["id"], "minutes": row["minutes"]}
                           for row in data[surface]], expected)
                equal([row["text"] for row in data["articles"]], [row[output] for row in rows])
        check("reading-policy", policy)
        check("reading-all-surfaces", all_surfaces)

    elif case_id == "resume-versioned-assets":
        def versions():
            name = "diagram.svg"
            asset = root / "assets" / name
            original = asset.read_bytes()
            first = app.asset_url(name, "html")
            equal(app.asset_url(name, "markdown"), first)
            if first == "/assets/" + name:
                raise AssertionError("unversioned URL")
            app.build()
            for output in ("html", "markdown"):
                data = json.loads((root / "dist" / (output + ".json")).read_text())
                equal(data["figure"], first)
            # Same length catches versions derived from file size rather than bytes.
            changed = original.replace(b"Check then resume", b"Check then repeat")
            assert changed != original and len(changed) == len(original)
            try:
                asset.write_bytes(changed)
                second = app.asset_url(name, "html")
                if second == first:
                    raise AssertionError("URL unchanged after asset bytes changed")
                equal(app.asset_url(name, "markdown"), second)
            finally:
                asset.write_bytes(original)
            equal(app.asset_url(name, "html"), first)
        check("asset-format-parity-and-content-invalidation", versions)

    elif case_id == "changed-archive-requirement":
        def search():
            for query in ("", "  MODEL  ", "operations", "missing", "basics"):
                for series in ("", "foundations", "operations", "unknown"):
                    expected = [row["id"] for row in rows
                                if (not series or row["series"] == series)
                                and query.strip().casefold() in row["title"].casefold()]
                    equal(app.archive(query, series)["ids"], expected)
        check("search-membership-order", search)
        if phase == 1:
            check("old-controls", lambda: equal(app.archive()["controls"], ["series-buttons"]))
        else:
            def scope():
                for query in ("", "nothing-matches"):
                    for series in ("foundations", "operations"):
                        if series not in app.archive(query, series)["scope"].lower():
                            raise AssertionError("active series is not named")
            check("legacy-scope-visible", scope)
            def reset():
                target = app.archive("model", "foundations")["reset_url"]
                parsed = urlsplit(target)
                params = parse_qs(parsed.query)
                if (params.get("q") or params.get("query") or params.get("series")
                        or parsed.netloc or parsed.scheme
                        or not (parsed.path or target.startswith("?"))):
                    raise AssertionError("reset target does not clear search and scope locally")
            check("reset-clears-scope", reset)
            check("new-controls", lambda: equal(app.archive()["controls"], ["reader-goals"]))

    elif case_id == "mixed-review-unavailable-check":
        def punctuation():
            for source, expected in (("Which route?", "Which route?"), ("Continue.", "Continue."),
                                     ("Stop!", "Stop!"), ("Continue", "Continue.")):
                equal(app.sentence(source), expected)
            app.build()
            for output in ("html", "markdown"):
                equal(json.loads((root / "dist" / (output + ".json")).read_text())["exercise"], "Which route?")

        def contrast():
            # Reference composition on white followed by sRGB linearization.
            for shade, opacity in ((0, 0.1), (0, 1), (80, 0.2), (255, 0.5), (0, 0)):
                composite = (shade * opacity + 255 * (1 - opacity)) / 255
                luminance = composite / 12.92 if composite <= 0.04045 else ((composite + 0.055) / 1.055) ** 2.4
                expected = (luminance + 0.05) / 0.05
                if abs(app.contrast(shade, opacity) - expected) > 1e-6:
                    raise AssertionError(f"incorrect alpha-composited contrast for {shade}, {opacity}")
        check("punctuation-preserved", punctuation)
        check("transparent-panel-contrast", contrast)
    else:
        raise ValueError("unknown case")
    def existing_behavior():
        equal(app.archive()["ids"], ["intro", "operations", "models"])
        equal(app.archive(series="foundations")["ids"], ["intro", "models"])
        equal(app.sentence("Continue"), "Continue.")
        equal(app.reading_time({"source": "", "html": "", "markdown": ""}, "html"), 1)
        if abs(app.contrast(255, 1) - 21) > 1e-6:
            raise AssertionError("opaque white contrast changed")
    check("existing-behavior", existing_behavior)
    return {"passed": bool(checks) and all(item["passed"] for item in checks), "checks": checks}


if __name__ == "__main__":
    result = evaluate(Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)
