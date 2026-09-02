#!/usr/bin/env python3
"""The language contract.

One rule set, rendered in several languages. These tests pin the two halves of
that contract: locales must be complete and interchangeable, and the *rules*
must not vary with language.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import i18n  # noqa: E402
from build import cover_macros, language_package  # noqa: E402
from report_config import (  # noqa: E402
    VALID_SKELETONS, infer_kind, parse_report_yaml,
)
from review import run  # noqa: E402


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class LocaleCompleteness(unittest.TestCase):
    def test_every_locale_defines_the_same_keys(self):
        reference = set(i18n.LOCALES[i18n.DEFAULT_LANG])
        for lang, table in i18n.LOCALES.items():
            self.assertEqual(
                set(table), reference,
                f"locale {lang!r} does not define the same keys as "
                f"{i18n.DEFAULT_LANG!r}: "
                f"missing={sorted(reference - set(table))} "
                f"extra={sorted(set(table) - reference)}")

    def test_supported_matches_the_tables(self):
        self.assertEqual(set(i18n.SUPPORTED), set(i18n.LOCALES))

    def test_no_locale_leaves_a_string_empty(self):
        for lang, table in i18n.LOCALES.items():
            for key, value in table.items():
                self.assertTrue(value.strip(), f"{lang}:{key} is empty")

    def test_normalise_handles_tags_aliases_and_junk(self):
        for raw, expected in (("fr", "fr"), ("FR", "fr"), ("en", "en"),
                              ("en-GB", "en"), ("en_US", "en"),
                              ("English", "en"), ("francais", "fr"),
                              (None, "fr"), ("", "fr"), ("kl", "fr")):
            self.assertEqual(i18n.normalise(raw), expected, f"for {raw!r}")

    def test_unknown_key_falls_back_rather_than_raising(self):
        self.assertEqual(i18n.strings("en")("no.such.key"), "no.such.key")

    def test_a_message_may_use_key_as_its_own_placeholder(self):
        # `warn.over_target` takes {key}; the lookup argument must not collide.
        for lang in i18n.SUPPORTED:
            rendered = i18n.strings(lang)(
                "warn.over_target", key="04-impl", actual=9.9, lo=4, hi=6)
            self.assertIn("04-impl", rendered)

    def test_empty_marker_detection_is_language_neutral(self):
        for value in ("À compléter", "to be completed", "TBD", "—", "n/a"):
            self.assertTrue(i18n.is_empty_value(value), value)
        self.assertFalse(i18n.is_empty_value("ENSET Mohammedia"))


class VocabularyIsAUnion(unittest.TestCase):
    """Detection must see every language at once, or the rules fork."""

    def test_state_of_the_art_covers_both_languages(self):
        vocab = i18n.vocabulary("state_of_art")
        self.assertIn("etat", vocab)
        self.assertIn("literature", vocab)

    def test_front_matter_covers_both_languages(self):
        vocab = i18n.vocabulary("front")
        self.assertIn("remerciement", vocab)
        self.assertIn("acknowledgement", vocab)

    def test_matches_is_case_insensitive(self):
        self.assertTrue(i18n.matches("state_of_art", "03-Literature-Review"))
        self.assertTrue(i18n.matches("state_of_art", "03-État-de-l-art"))


class KindInferenceIsLanguageNeutral(unittest.TestCase):
    EQUIVALENTS = (
        ("00-page-de-garde", "00-cover-page", "front"),
        ("01-remerciements", "01-acknowledgements", "front"),
        ("01b-resume", "01b-abstract", "front"),
        ("02-acronymes", "02-acronyms", "front"),
        ("03-introduction-generale", "03-introduction", "intro"),
        ("99-conclusion-generale", "99-conclusion", "conclusion"),
        ("99b-annexes", "99b-appendices", "annex"),
    )

    def test_french_and_english_names_classify_identically(self):
        for fr, en, expected in self.EQUIVALENTS:
            self.assertEqual(infer_kind(fr), expected, fr)
            self.assertEqual(infer_kind(en), expected, en)

    def test_a_real_chapter_is_still_a_chapter(self):
        for name in ("04-conception", "05-design", "06-implementation"):
            self.assertEqual(infer_kind(name), "chapter", name)


class SkeletonSetIsLanguageIndependent(unittest.TestCase):
    def test_the_english_fork_is_gone(self):
        self.assertNotIn("06-capstone-en", VALID_SKELETONS)

    def test_a_retired_skeleton_is_migrated_not_kept(self):
        cfg = parse_report_yaml(
            "type: pfe\nlang: en\nskeleton: 06-capstone-en\n")
        self.assertEqual(cfg.skeleton, "01-pfe-software-engineering")
        self.assertEqual(cfg.lang, "en")

    def test_language_does_not_change_the_page_budget(self):
        body = "type: pfe\nskeleton: 01-pfe-software-engineering\n" \
               "pages_total: 60\nchapters:\n  04-x:\n    pages: [8, 12]\n"
        fr = parse_report_yaml(body + "lang: fr\n")
        en = parse_report_yaml(body + "lang: en\n")
        self.assertEqual(fr.pages_total, en.pages_total)
        self.assertEqual(fr.chapters["04-x"].pages,
                         en.chapters["04-x"].pages)
        self.assertEqual(fr.requires_positioning_level(),
                         en.requires_positioning_level())
        self.assertEqual(fr.company_share_cap(), en.company_share_cap())


class LatexFollowsTheLocale(unittest.TestCase):
    def test_babel_option_comes_from_the_locale(self):
        self.assertIn("french", language_package("fr"))
        self.assertIn("english", language_package("en"))

    def test_preamble_marker_is_present_and_unique(self):
        preamble = (Path(__file__).resolve().parents[1]
                    / "assets" / "latex" / "preamble.tex"
                    ).read_text(encoding="utf-8")
        self.assertEqual(preamble.count("%%LANG%%"), 1)
        self.assertNotIn("\\usepackage[french]{babel}", preamble)

    def test_cover_labels_are_localised(self):
        cfg = parse_report_yaml("type: pfe\nlang: en\n")
        self.assertIn("Prepared by", cover_macros(cfg))
        cfg = parse_report_yaml("type: pfe\nlang: fr\n")
        self.assertIn("Préparé par", cover_macros(cfg))

    def test_titlepage_has_no_hardcoded_language(self):
        tex = (Path(__file__).resolve().parents[1]
               / "assets" / "latex" / "titlepage.tex"
               ).read_text(encoding="utf-8")
        for french in ("Préparé par", "Encadré par", "Année universitaire"):
            self.assertNotIn(french, tex)
        for macro in ("\\coverpreparedby", "\\coversupervisedby",
                      "\\coveracademicyear"):
            self.assertIn(macro, tex)


class ReviewRulesDoNotForkOnLanguage(unittest.TestCase):
    """The point of the whole refactor: same draft, same findings."""

    FR = {
        "report.yaml": "type: pfe\nskeleton: 01-pfe-software-engineering\n"
                       "lang: fr\npages_total: 60\n",
        "02-etat-de-l-art.md": "# État de l'art\n\n" + ("mot " * 4000),
        "04-realisation.md": "# Réalisation\n\n" + ("mot " * 900),
    }
    EN = {
        "report.yaml": "type: pfe\nskeleton: 01-pfe-software-engineering\n"
                       "lang: en\npages_total: 60\n",
        "02-literature-review.md": "# Literature review\n\n" + ("word " * 4000),
        "04-implementation.md": "# Implementation\n\n" + ("word " * 900),
    }

    def _run(self, files):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, text in files.items():
                _write(root, name, text)
            return run(root)

    def test_an_oversized_state_of_the_art_is_caught_in_both_languages(self):
        fr, en = self._run(self.FR), self._run(self.EN)
        self.assertTrue(any("etat-de-l-art" in i for i in fr["issues"]),
                        fr["issues"])
        self.assertTrue(any("literature-review" in i for i in en["issues"]),
                        en["issues"])

    def test_the_same_draft_yields_the_same_number_of_findings(self):
        fr, en = self._run(self.FR), self._run(self.EN)
        self.assertEqual(len(fr["issues"]), len(en["issues"]))
        self.assertEqual(len(fr["warnings"]), len(en["warnings"]))

    def test_findings_are_reported_in_the_report_language(self):
        fr, en = self._run(self.FR), self._run(self.EN)
        self.assertEqual(fr["lang"], "fr")
        self.assertEqual(en["lang"], "en")
        self.assertTrue(any("corps" in i for i in fr["issues"]))
        self.assertTrue(any("body" in i for i in en["issues"]))


if __name__ == "__main__":
    unittest.main()
