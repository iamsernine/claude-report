#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from gen_figures import generate, is_placeholder, make_placeholder  # noqa: E402


class FigureTests(unittest.TestCase):
    def test_stamp_and_never_overwrite_real(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            figs = Path(tmp) / "figures"
            root.mkdir()
            (root / "a.md").write_text(
                "[[FIG: archi | Architecture | width=0.5]]\n",
                encoding="utf-8",
            )
            generate(root, figs)
            ph = figs / "archi.png"
            self.assertTrue(is_placeholder(ph))

            # student drops a real screenshot
            ph.write_bytes(b"\x89PNG\r\n\x1a\n" + b"not-really-a-png-but-not-ours")
            # invalid png: is_placeholder returns False on OSError
            generate(root, figs)
            data = ph.read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG"))
            self.assertNotIn(b"PLACEHOLDER", data)

    def test_placeholder_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.png"
            make_placeholder(path, "slug", "caption", 0.8)
            self.assertTrue(is_placeholder(path))
            # a freshly saved RGB png without our chunk is "real"
            from PIL import Image
            real = Path(tmp) / "real.png"
            Image.new("RGB", (10, 10), (255, 0, 0)).save(real)
            self.assertFalse(is_placeholder(real))
