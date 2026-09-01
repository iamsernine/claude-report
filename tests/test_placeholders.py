#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from placeholders import scan_malformed, scan_text, slugify  # noqa: E402


class PlaceholderTests(unittest.TestCase):
    def test_cite_stable_key(self):
        items = scan_text("voir [[CITE: knuth84 | The TeXbook]]")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].kind, "CITE")
        self.assertEqual(items[0].slug, "knuth84")
        self.assertEqual(items[0].caption, "The TeXbook")

    def test_cite_slugified_when_no_key(self):
        a = scan_text("[[CITE: YOLOv8 real-time object detection]]")[0]
        b = scan_text("[[CITE: YOLOv8 real-time object detection]]")[0]
        self.assertEqual(a.slug, b.slug)
        self.assertTrue(a.slug)
        self.assertNotIn(" ", a.slug)

    def test_fig_and_ref(self):
        text = (
            "voir [[REF: architecture-globale]].\n"
            "[[FIG: architecture-globale | Architecture | width=0.9]]\n"
        )
        items = scan_text(text)
        kinds = {p.kind: p for p in items}
        self.assertEqual(kinds["FIG"].options["width"], "0.9")
        self.assertEqual(kinds["REF"].slug, "architecture-globale")

    def test_malformed_reported(self):
        bad = scan_malformed("texte [[figure: oops]] et [[FIG: ok | cap]]")
        self.assertEqual(len(bad), 1)
        self.assertIn("figure:", bad[0].raw)

    def test_slugify_unicode(self):
        self.assertEqual(slugify("État de l'art"), "etat-de-lart")


if __name__ == "__main__":
    unittest.main()
