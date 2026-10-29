# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
import hashlib
import unittest
import site_app as app


class CatalogTests(unittest.TestCase):
    def test_catalog_order(self):
        self.assertEqual(app.archive()["ids"], ["intro", "operations", "models"])

    def test_legacy_series_filter(self):
        self.assertEqual(app.archive(series="foundations")["ids"], ["intro", "models"])

    def test_empty_reading_time(self):
        self.assertEqual(app.reading_time({"html": "", "markdown": "", "source": ""}, "html"), 1)

    def test_plain_sentence(self):
        self.assertEqual(app.sentence("Continue"), "Continue.")

    def test_opaque_white_panel(self):
        self.assertAlmostEqual(app.contrast(255, 1), 21)

    def test_html_asset_matches_current_bytes(self):
        digest = hashlib.sha256((app.ROOT / "assets/diagram.svg").read_bytes()).hexdigest()[:12]
        self.assertEqual(app.asset_url("diagram.svg", "html"), "/assets/diagram.svg?v=" + digest)


if __name__ == "__main__":
    unittest.main()
