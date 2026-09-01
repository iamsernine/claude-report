#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from draft_guard import classify, file_hash, stamp, stamp_path  # noqa: E402


class GuardTests(unittest.TestCase):
    def test_user_edit_is_protected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            md = root / "04-x.md"
            md.write_text("generated\n", encoding="utf-8")
            stamp(md)
            self.assertEqual(classify(root)["writable"], ["04-x.md"])

            md.write_text("student edit\n", encoding="utf-8")
            result = classify(root)
            self.assertIn("04-x.md", result["skip"])
            self.assertNotIn("04-x.md", result["writable"])

    def test_unstamped_existing_is_protected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "hand.md").write_text("mine\n", encoding="utf-8")
            result = classify(root)
            self.assertIn("hand.md", result["unstamped"])
            self.assertIn("hand.md", result["skip"])

    def test_stamp_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "a.md"
            md.write_text("hello\n", encoding="utf-8")
            stamp(md)
            self.assertEqual(
                stamp_path(md).read_text(encoding="utf-8").strip(),
                file_hash(md),
            )
