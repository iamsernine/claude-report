#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from review import apply_fixes, run  # noqa: E402


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ReviewTests(unittest.TestCase):
    def test_pfa_positioning_is_warning_not_issue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "report.yaml", "type: pfa\nskeleton: 04-pfa-annual-project\n")
            _write(
                root, "05-etat-de-l-art/01.md",
                "# État de l'art\n\n" + ("texte " * 400) + "\n",
            )
            _write(
                root, "06-realisation/01.md",
                "# Réalisation\n\n" + ("texte " * 400) + "\n",
            )
            result = run(root)
            joined_i = " ".join(result["issues"])
            joined_w = " ".join(result["warnings"])
            self.assertNotIn("sans positionnement", joined_i)
            self.assertIn("sans positionnement", joined_w)

    def test_software_pfa_no_baseline_nag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "report.yaml",
                   "type: pfa\nskeleton: 04-pfa-annual-project\n")
            _write(root, "06-resultats/01.md",
                   "# Résultats\n\nLes écrans fonctionnent.\n")
            result = run(root)
            self.assertFalse(any("baseline" in w.lower()
                                 for w in result["warnings"]))

    def test_malformed_is_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "04-x/01.md", "voir [[figure: oops]]\n")
            result = run(root)
            self.assertTrue(any("mal formé" in i for i in result["issues"]))

    def test_fix_adds_missing_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root, "04-x/01.md",
                "Texte.\n\n[[FIG: archi | Architecture]]\n",
            )
            log = apply_fixes(root)
            text = (root / "04-x/01.md").read_text(encoding="utf-8")
            self.assertTrue(any("archi" in line for line in log))
            self.assertIn("[[REF: archi]]", text)
            result = run(root)
            self.assertFalse(any("jamais référencé" in w
                                 for w in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
