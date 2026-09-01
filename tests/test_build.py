#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build import build  # noqa: E402


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


MINI_YAML = """
type: pfa
skeleton: 04-pfa-annual-project
lang: fr
pages_total: 30
biblio_position: before_annexes
title: Plateforme de test
author: Ada
institution: ENSET
year: 2025-2026
degree: PFA
supervisor: Encadrant
chapters:
  03-introduction-generale:
    title: Introduction générale
    kind: intro
    numbered: false
    pages: [1, 1]
  04-contexte:
    title: Contexte et cadrage
    kind: chapter
    numbered: true
    pages: [6, 9]
  99-conclusion-generale:
    title: Conclusion générale
    kind: conclusion
    numbered: false
    pages: [1, 2]
  99b-annexes:
    title: Annexes
    kind: annex
    numbered: false
"""


class BuildTests(unittest.TestCase):
    def test_numbering_and_stable_cite_and_biblio_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "reports_docs"
            out = Path(tmp) / "build"
            _write(root, "report.yaml", MINI_YAML)
            _write(root, "00-page-de-garde.md", "\\input{titlepage}\n")
            _write(
                root, "03-introduction-generale.md",
                "# Introduction générale\n\nLe problème est posé ici.\n",
            )
            _write(
                root, "04-contexte/01-cadre.md",
                "# Cadre du projet\n\n"
                "L'architecture est en [[REF: architecture-globale]].\n\n"
                "[[FIG: architecture-globale | Architecture générale | width=0.8]]\n\n"
                "Voir [[CITE: knuth84 | The TeXbook]].\n",
            )
            _write(
                root, "99-conclusion-generale.md",
                "# Conclusion générale\n\nBilan.\n",
            )
            _write(
                root, "99b-annexes/01.md",
                "# Annexe A\n\nDétail.\n",
            )
            rc = build(root, out, allow_todo=True, no_compile=True)
            self.assertEqual(rc, 0)
            tex = (out / "main.tex").read_text(encoding="utf-8")
            self.assertIn(r"\chapter*{Introduction générale}", tex)
            self.assertIn(r"\chapter{Contexte et cadrage}", tex)
            self.assertIn(r"\chapter*{Conclusion générale}", tex)
            self.assertIn(r"\cite{knuth84}", tex)
            self.assertIn(r"\printbibliography", tex)
            # biblio before annexes
            biblio_at = tex.index(r"\printbibliography")
            annex_at = tex.index("Annexes")
            self.assertLess(biblio_at, annex_at)
            self.assertTrue((out / "titlepage.tex").is_file())
            self.assertTrue((out / "figures" / "architecture-globale.png").is_file())

            # second build must not clobber a real bib entry
            (out / "references.bib").write_text(
                "@article{knuth84,\n  title={The TeXbook},\n  year={1984}\n}\n",
                encoding="utf-8",
            )
            build(root, out, allow_todo=True, no_compile=True)
            bib = (out / "references.bib").read_text(encoding="utf-8")
            self.assertIn("@article{knuth84", bib)
            self.assertIn("The TeXbook", bib)

    def test_blocks_on_todo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "reports_docs"
            out = Path(tmp) / "build"
            _write(root, "report.yaml", "type: pfa\n")
            _write(root, "04-x.md", "Manque [[TODO: la date]].\n")
            rc = build(root, out, allow_todo=False, no_compile=True)
            self.assertEqual(rc, 1)
            self.assertFalse((out / "main.tex").exists())
