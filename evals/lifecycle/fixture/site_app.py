# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Small static reading catalog used by the incident replay fixtures."""
import hashlib
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def articles():
    return json.loads((ROOT / "articles.json").read_text())


def reading_time(article, output):
    return max(1, math.ceil(len(article[output].split()) / 200))


def asset_url(name, output):
    content = (ROOT / "assets" / name).read_bytes()
    if output == "markdown":
        return "/assets/" + name
    return "/assets/" + name + "?v=" + hashlib.sha256(content).hexdigest()[:12]


def archive(query="", series=""):
    rows = [row for row in articles() if not series or row["series"] == series]
    return {"ids": [row["id"] for row in rows], "scope": "",
            "reset_url": "?series=" + series, "controls": ["series-buttons"]}


def sentence(text):
    return text + "."


def contrast(background, opacity):
    # Black text over a grayscale panel on a white page.
    channel = background / 255
    luminance = channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
    return (luminance + 0.05) / 0.05


def build():
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    for output in ("html", "markdown"):
        result = {"articles": [], "cards": [], "related": [], "archive": archive()}
        for article in articles():
            minutes = reading_time(article, output)
            result["articles"].append({"id": article["id"], "minutes": minutes,
                                       "title": article["title"], "text": article[output]})
            result["cards"].append({"id": article["id"], "minutes": minutes})
            result["related"].append({"id": article["id"], "minutes": minutes})
        result["figure"] = asset_url("diagram.svg", output)
        result["exercise"] = sentence("Which route?")
        (destination / (output + ".json")).write_text(json.dumps(result, indent=2) + "\n")
    (destination / "index.html").write_text("<h1>Reading catalog</h1>\n" + "\n".join(
        "<p>" + html.escape(row["title"]) + "</p>" for row in articles()))


if __name__ == "__main__":
    build()
