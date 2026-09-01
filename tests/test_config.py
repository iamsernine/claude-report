#!/usr/bin/env python3
"""Tests for report.yaml parsing."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from report_config import parse_report_yaml, pretty_title  # noqa: E402


SHORT = """
type: pfa
skeleton: 04-pfa-annual-project
lang: fr
pages_total: 35
biblio_position: before_annexes
period_start: 2026-02-03
chapters:
  01-contexte-general: [7, 9]
  02-etude: [8, 10]
"""

FULL = """
type: pfe
skeleton: 02-pfe-research-ml
title: "Weed detection"
author: 'Ada Lovelace'
internship_start: 2026-01-15
chapters:
  03-introduction-generale:
    title: Introduction générale
    kind: intro
    numbered: false
    pages: [1, 2]
  04-modelisation:
    title: Modélisation
    kind: chapter
    numbered: true
    pages: [12, 16]
  99b-annexes:
    kind: annex
"""


class ConfigTests(unittest.TestCase):
    def test_short_chapter_form(self):
        cfg = parse_report_yaml(SHORT)
        self.assertEqual(cfg.type, "pfa")
        self.assertEqual(cfg.pages_total, 35)
        self.assertEqual(cfg.chapters["01-contexte-general"].pages, (7, 9))
        self.assertEqual(cfg.biblio_position, "before_annexes")
        self.assertEqual(cfg.period_start, "2026-02-03")
        self.assertFalse(cfg.requires_baseline())
        self.assertEqual(cfg.requires_positioning_level(), "warning")

    def test_full_chapter_form(self):
        cfg = parse_report_yaml(FULL)
        intro = cfg.chapters["03-introduction-generale"]
        self.assertEqual(intro.kind, "intro")
        self.assertFalse(intro.is_numbered())
        self.assertEqual(intro.pages, (1, 2))
        self.assertEqual(intro.display_title(), "Introduction générale")
        self.assertTrue(cfg.requires_baseline())
        self.assertEqual(cfg.requires_positioning_level(), "issue")
        self.assertEqual(cfg.title, "Weed detection")
        self.assertEqual(cfg.author, "Ada Lovelace")
        self.assertEqual(cfg.period_start, "2026-01-15")

    def test_stage_initiation_skips_positioning(self):
        cfg = parse_report_yaml("type: stage-initiation\n")
        self.assertIsNone(cfg.requires_positioning_level())
        self.assertIsNone(cfg.company_share_cap())

    def test_pretty_title(self):
        self.assertEqual(
            pretty_title("04-contexte-et-cadrage"),
            "contexte et cadrage",
        )


if __name__ == "__main__":
    unittest.main()
