#!/usr/bin/env python3
"""The no-guessing contract: gaps are visible, and sources close them."""
from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build import build  # noqa: E402
from sources import brief_gaps, collect, sources_dir  # noqa: E402


class BriefGaps(unittest.TestCase):
    BRIEF = """# Brief

## Metadata
- Institution: ENSET Mohammedia
- Academic supervisor:
- Jury: TBD

## The project
- Title: Viride AI
- Problem statement:   <!-- must be a problem, not a task -->
"""

    def _gaps(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "BRIEF.md").write_text(text, encoding="utf-8")
            return brief_gaps(root)

    def test_empty_and_sentinel_fields_are_gaps(self):
        gaps = self._gaps(self.BRIEF)
        self.assertIn("Academic supervisor", gaps["Metadata"])
        self.assertIn("Jury", gaps["Metadata"])          # "TBD" is not a value

    def test_a_filled_field_is_not_a_gap(self):
        gaps = self._gaps(self.BRIEF)
        self.assertNotIn("Institution", gaps.get("Metadata", []))
        self.assertNotIn("Title", gaps.get("The project", []))

    def test_a_guidance_comment_is_not_a_value(self):
        gaps = self._gaps(self.BRIEF)
        self.assertIn("Problem statement", gaps["The project"])

    def test_gaps_are_grouped_by_section(self):
        self.assertEqual(set(self._gaps(self.BRIEF)),
                         {"Metadata", "The project"})

    def test_no_brief_is_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(brief_gaps(Path(tmp)), {})


class SourcesFolder(unittest.TestCase):
    def _root(self, files):
        tmp = tempfile.mkdtemp()
        root = Path(tmp)
        sdir = sources_dir(root)
        sdir.mkdir(parents=True)
        for name, text in files.items():
            (sdir / name).write_text(text, encoding="utf-8")
        return root

    def test_missing_folder_is_reported_not_crashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            inv = collect(Path(tmp))
            self.assertFalse(inv.exists)
            self.assertEqual(inv.items, [])

    def test_markdown_and_text_are_read_directly(self):
        inv = collect(self._root({"notes.md": "# Notes\n\ncontent",
                                  "export.txt": "accuracy 0.94"}))
        self.assertEqual(len(inv.readable), 2)
        for item in inv.readable:
            self.assertGreater(item.chars, 0)
            self.assertEqual(item.text_path, item.path)

    def test_credential_files_are_skipped_and_never_read(self):
        root = self._root({".env": "SECRET=hunter2",
                           "key.pem": "-----BEGIN PRIVATE KEY-----"})
        inv = collect(root)
        self.assertEqual(len(inv.skipped_secrets), 2)
        for item in inv.skipped_secrets:
            self.assertFalse(item.readable)
            self.assertEqual(item.chars, 0)
            self.assertIsNone(item.text_path)

    def test_office_documents_ask_to_be_converted(self):
        inv = collect(self._root({"deck.pptx": "binary-ish"}))
        self.assertEqual(len(inv.readable), 0)
        self.assertIn("convert", inv.unreadable[0].note.lower())

    def test_the_folders_own_readme_is_not_a_source(self):
        inv = collect(self._root({"README.md": "# sources/\n\ninstructions",
                                  "company.md": "real material"}))
        self.assertEqual([s.rel for s in inv.items], ["company.md"])

    def test_extracted_output_is_not_itself_a_source(self):
        root = self._root({"a.md": "x"})
        extracted = sources_dir(root) / ".extracted"
        extracted.mkdir()
        (extracted / "old.txt").write_text("stale", encoding="utf-8")
        self.assertEqual([s.rel for s in collect(root).items], ["a.md"])


class SourcesAreNotReportContent(unittest.TestCase):
    """A supplied document must never be drafted, counted or compiled."""

    def _project(self):
        tmp = tempfile.mkdtemp()
        root = Path(tmp) / "reports_docs"
        (root / "sources" / ".extracted").mkdir(parents=True)
        (root / "report.yaml").write_text(
            "type: pfe\nskeleton: 01-pfe-software-engineering\nlang: en\n",
            encoding="utf-8")
        (root / "04-impl.md").write_text("# Implementation\n\nreal prose\n",
                                         encoding="utf-8")
        (root / "BRIEF.md").write_text("# Brief\n\n- Name:\n", encoding="utf-8")
        (root / "sources" / "company.md").write_text(
            "SENTINEL_FROM_A_SUPPLIED_SOURCE\n", encoding="utf-8")
        (root / "sources" / ".extracted" / "deck.txt").write_text(
            "SENTINEL_FROM_AN_EXTRACTED_PDF\n", encoding="utf-8")
        return root, Path(tmp) / "build"

    def test_source_text_never_reaches_the_latex(self):
        root, out = self._project()
        self.assertEqual(build(root, out), 0)
        tex = (out / "main.tex").read_text(encoding="utf-8")
        self.assertIn("real prose", tex)
        self.assertNotIn("SENTINEL_FROM_A_SUPPLIED_SOURCE", tex)
        self.assertNotIn("SENTINEL_FROM_AN_EXTRACTED_PDF", tex)

    def test_sources_is_not_counted_as_a_chapter(self):
        from review import run
        root, _ = self._project()
        self.assertNotIn("sources", run(root)["pages"])

    def test_placeholders_in_a_source_are_not_the_report_s_placeholders(self):
        from placeholders import scan_tree
        root, _ = self._project()
        (root / "sources" / "old-report.md").write_text(
            "[[TODO: someone else's placeholder]]\n", encoding="utf-8")
        self.assertEqual([p.file for p in scan_tree(root)], [])

    def test_the_guard_does_not_offer_to_overwrite_supplied_files(self):
        from draft_guard import classify
        root, _ = self._project()
        everything = sum(classify(root).values(), [])
        self.assertFalse([f for f in everything if "sources" in f])


class BuildStopsAtLatex(unittest.TestCase):
    """The pipeline ends at an Overleaf bundle — never a local PDF."""

    def _build(self):
        tmp = tempfile.mkdtemp()
        root, out = Path(tmp) / "reports_docs", Path(tmp) / "build"
        root.mkdir()
        (root / "report.yaml").write_text(
            "type: pfe\nskeleton: 01-pfe-software-engineering\nlang: en\n",
            encoding="utf-8")
        (root / "04-impl.md").write_text("# Implementation\n\nprose\n",
                                         encoding="utf-8")
        rc = build(root, out)
        return rc, out

    def test_build_succeeds_without_any_tex_installation(self):
        rc, out = self._build()
        self.assertEqual(rc, 0)
        self.assertTrue((out / "main.tex").is_file())

    def test_no_pdf_is_produced_by_default(self):
        _, out = self._build()
        self.assertEqual(list(out.glob("*.pdf")), [])

    def test_an_overleaf_zip_is_produced(self):
        _, out = self._build()
        archive = out / "overleaf.zip"
        self.assertTrue(archive.is_file())
        with zipfile.ZipFile(archive) as zf:
            names = zf.namelist()
        self.assertIn("main.tex", names)
        self.assertIn("references.bib", names)
        self.assertIn("titlepage.tex", names)

    def test_the_zip_carries_no_compilation_artefacts(self):
        _, out = self._build()
        (out / "main.aux").write_text("stale", encoding="utf-8")
        (out / "main.pdf").write_bytes(b"%PDF-1.4")
        from build import make_zip
        with zipfile.ZipFile(make_zip(out)) as zf:
            names = zf.namelist()
        self.assertNotIn("main.aux", names)
        self.assertNotIn("main.pdf", names)


if __name__ == "__main__":
    unittest.main()
