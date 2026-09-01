#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build import existing_bib_keys, merge_bib  # noqa: E402


class BibMergeTests(unittest.TestCase):
    def test_appends_without_clobber(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "references.bib"
            path.write_text(
                "@article{knuth84,\n  title={The TeXbook},\n  year={1984}\n}\n",
                encoding="utf-8",
            )
            added = merge_bib(path, [
                ("knuth84", "should not replace", "ch1"),
                ("yolo8", "YOLOv8 paper", "ch2.md"),
            ])
            text = path.read_text(encoding="utf-8")
            self.assertEqual(added, 1)
            self.assertIn("The TeXbook", text)
            self.assertNotIn("should not replace", text)
            self.assertIn("@misc{yolo8", text)
            self.assertIn("knuth84", existing_bib_keys(text))
            self.assertIn("yolo8", existing_bib_keys(text))

    def test_drops_placeholder_dummy(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "references.bib"
            path.write_text(
                "@misc{placeholder, title={Aucune référence}, year={2026}}\n",
                encoding="utf-8",
            )
            merge_bib(path, [("alpha", "A", "x.md")])
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("placeholder", text)
            self.assertIn("@misc{alpha", text)
