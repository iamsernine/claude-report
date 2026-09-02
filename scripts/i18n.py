#!/usr/bin/env python3
"""Locale layer.

The design rule this module exists to enforce:

    Structure and rules are language-independent.
    Language selects surface strings only.

So there is exactly ONE skeleton set, ONE set of review checks and ONE page
budget model. What `lang` changes is the words used to *say* things — CLI
output, LaTeX chrome, cover-page labels.

Detection is deliberately asymmetric to rendering:

* **Rendering** uses the report's own language (``cfg.lang``).
* **Detection** (does this file look like a state of the art? a results
  chapter?) uses the UNION of every locale's vocabulary.

That asymmetry is what makes the rules identical across languages: a chapter
called ``03-etat-de-lart`` and one called ``03-literature-review`` hit exactly
the same checks with exactly the same thresholds. Adding a locale extends the
vocabulary; it never forks a rule.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Iterable

DEFAULT_LANG = "fr"
SUPPORTED = ("fr", "en")

# ---------------------------------------------------------------------------
# Surface strings, per locale
# ---------------------------------------------------------------------------

_FR: Dict[str, str] = {
    # --- LaTeX -------------------------------------------------------------
    "babel": "french",
    "cover.report_of": "Rapport de",
    "cover.academic_year": "Année universitaire",
    "cover.prepared_by": "Préparé par",
    "cover.supervised_by": "Encadré par",
    "cover.institution_logo": "Logo de l'établissement",
    "cover.host_logo": "Logo de l'organisme d'accueil",
    "cover.to_complete": "À compléter",
    "tex.watermark": "BROUILLON",
    "tex.table_col_a": "Colonne A",
    "tex.table_col_b": "Colonne B",
    "tex.table_empty": "Tableau non renseigné — à remplacer.",
    "tex.code_empty": "CODE NON RENSEIGNÉ — coller le fragment ici",
    "tex.eq_empty": "équation non renseignée",
    "bib.to_source": "À SOURCER — cité dans {where}",
    "bib.none": "Aucune référence",

    # --- CLI: status -------------------------------------------------------
    "status.type": "Type",
    "status.brief": "Brief",
    "status.brief_fields": "{filled}/{total} champs renseignés ({pct} %)",
    "status.col_chapter": "Chapitre",
    "status.col_pages": "Pages",
    "status.col_target": "Cible",
    "status.col_state": "État",
    "status.total_body": "Total corps",
    "status.blocking": "Placeholders bloquants",
    "status.figures": "Figures",
    "status.figures_value": "{declared} déclarées, {provided} fournies, "
                            "{todo} à produire",
    "status.citations": "Citations à sourcer",
    "status.next": "Prochaine action",
    "state.unwritten": "non rédigé",
    "state.over": "dépassement",
    "state.incomplete": "incomplet",
    "state.ok": "ok",
    "next.fill_brief": "compléter BRIEF.md avant de rédiger davantage",
    "next.write": "rédiger {name} (/report:draft --chapter …)",
    "next.fix_blocking": "corriger les problèmes bloquants (/report:review)",
    "next.replace_figures":
        "remplacer les figures grises (voir build/figures/MANIFEST.md)",
    "next.review_then_build": "relancer /report:review puis /report:build",

    # --- CLI: sources & gaps ----------------------------------------------
    "src.title": "Documents fournis",
    "src.none": "Aucun dossier {dir} — créez-le et déposez-y les documents "
                "(PDF, Markdown, texte) contenant ce qui manque au brief.",
    "src.empty": "{dir} est vide. Déposez-y les documents contenant les "
                 "informations manquantes, puis relancez /report:draft.",
    "src.readable": "{n} document(s) lisible(s)",
    "src.unreadable": "{n} document(s) illisible(s)",
    "src.secrets": "{n} fichier(s) ignoré(s) (identifiants — jamais lus)",
    "src.extracted_to": "texte extrait dans {dir}",
    "gaps.title": "Informations manquantes (à ne jamais inventer)",
    "gaps.none": "Aucun champ vide dans BRIEF.md.",
    "gaps.count": "{n} champ(s) vide(s) dans BRIEF.md",
    "gaps.hint": "Renseignez-les dans BRIEF.md, ou déposez dans {dir} un "
                 "document qui les contient, puis relancez /report:draft.",
    "next.add_sources": "combler les manques : compléter BRIEF.md ou déposer "
                        "un document dans {dir}",

    # --- CLI: build / Overleaf --------------------------------------------
    "build.bundle": "dossier Overleaf : {path}",
    "build.zip": "archive Overleaf : {path}",
    "build.overleaf": "Déposez ce dossier (ou l'archive) sur Overleaf, "
                      "compilateur pdfLaTeX, bibliographie Biber.",
    "build.no_local_pdf": "Aucun PDF n'est produit localement — c'est voulu. "
                          "La compilation se fait sur Overleaf.",
    # --- CLI: figures ------------------------------------------------------
    "fig.manifest_title": "# Figures attendues",
    "fig.col_slug": "Slug",
    "fig.col_caption": "Légende",
    "fig.col_chapter": "Chapitre",
    "fig.col_minwidth": "Largeur min.",
    "fig.col_state": "État",
    "fig.state.placeholder": "placeholder",
    "fig.state.provided": "fournie",
    "fig.state.missing": "manquante",
    "fig.summary": "figures : {created} créée(s), {real} réelle(s), "
                   "{placeholder} placeholder(s)",
    "fig.manifest": "manifeste",

    # --- CLI: review -------------------------------------------------------
    "review.pages_header": "=== Pages par section ===",
    "review.blocking": "BLOQUANT",
    "review.warning": "AVERTISSEMENT",
    "review.info": "INFO",
    "review.fail": "ÉCHEC — {n} problème(s) bloquant(s).",
    "review.pass": "OK — {n} avertissement(s), aucun blocage.",
    "review.no_markdown": "aucun fichier markdown trouvé dans {root}",

    # --- CLI: build --------------------------------------------------------
    "build.not_found": "erreur : {path} introuvable",
    "build.blocked": "BLOQUÉ — {n} placeholder(s) METRIC/TODO non résolu(s) :",
    "build.and_more": "  … et {n} de plus",
    "build.blocked_hint": "Renseignez-les, ou relancez avec --allow-todo "
                          "pour un rendu de brouillon (placeholders en rouge, "
                          "filigrane BROUILLON).",
    "build.written": "écrit : {path}",
    "build.citations": "citations à sourcer : {n} ({added} nouvelle(s) "
                       "entrée(s) bib)",
    "build.no_pdflatex": "pdflatex introuvable — compilez main.tex dans Overleaf.",
    "build.no_biber": "biber introuvable — bibliographie non résolue en local "
                      "(Overleaf la résoudra automatiquement).",
    "build.pdf": "PDF : {path}",
    "build.compile_failed": "compilation échouée :",
    "build.no_pandoc": "AVERTISSEMENT: pandoc introuvable — conversion "
                       "minimale (titres seulement). Installez pandoc pour un "
                       "PDF correct (listes, tableaux, citations).",
    "build.citations_title": "# Citations à sourcer",
    "build.cited_in": "cité dans",

    # --- CLI: check --------------------------------------------------------
    "check.missing": "MANQUANT — installer pandoc",
    "check.absent": "absent (Overleaf possible)",

    # --- review findings ---------------------------------------------------
    "issue.company_share":
        "'{name}' occupe {share} du corps du rapport. La présentation de "
        "l'organisme doit rester sous {cap} % — c'est le symptôme le plus "
        "visible de proportions inversées.",
    "issue.soa_share":
        "'{name}' occupe {share} du corps. Un état de l'art plus volumineux "
        "que la contribution est systématiquement sanctionné.",
    "warn.soa_share_pfa":
        "'{name}' occupe {share} du corps. Pour un PFA, l'état de l'art doit "
        "rester bref — viser sous 15–20 %.",
    "warn.intro_long":
        "'{name}' fait ~{pages} pages. L'introduction générale ne doit pas "
        "dépasser 2 pages.",
    "warn.conclusion_long":
        "'{name}' fait ~{pages} pages. La conclusion générale ne doit pas "
        "dépasser 2 pages.",
    "issue.over_budget":
        "'{key}' fait ~{actual} p pour une cible de {lo}–{hi} p "
        "(report.yaml). Couper d'environ {cut} p.",
    "warn.over_target":
        "'{key}' fait ~{actual} p, au-dessus de la cible {lo}–{hi} p de "
        "report.yaml.",
    "warn.under_target":
        "'{key}' fait ~{actual} p, bien en-dessous de la cible {lo}–{hi} p — "
        "chapitre probablement incomplet.",
    "issue.unresolved": "{file}:{line} — [[{kind}]] non résolu : {caption}",
    "issue.malformed":
        "{file}:{line} — placeholder mal formé {raw}. Formes acceptées : "
        "FIG, TAB, CODE, EQ, CITE, METRIC, TODO, REF.",
    "warn.unreferenced":
        "{file} — '{slug}' est déclaré mais jamais référencé dans le texte. "
        "Toute illustration doit être citée et justifiée dans le corps du "
        "rapport.",
    "issue.duplicate_slug":
        "slug dupliqué '{slug}' ({a} et {b}) — les labels LaTeX doivent être "
        "uniques.",
    "msg.no_positioning":
        "{file} — état de l'art sans positionnement. Il manque un tableau "
        "comparatif et un paragraphe nommant explicitement l'écart que ce "
        "travail comble.",
    "issue.no_positioning_suffix":
        " C'est la faiblesse la plus courante des rapports IA.",
    "warn.no_positioning_suffix":
        " Pour un PFA/module, un tableau court suffit.",
    "warn.no_baseline":
        "{file} — aucune baseline mentionnée. Un chiffre sans point de "
        "comparaison n'est pas un résultat.",
    "warn.intro_results":
        "{file} — l'introduction semble annoncer des résultats chiffrés. "
        "L'introduction pose le problème, elle ne donne jamais les résultats.",
    "warn.figure_density":
        "~{figs} figure(s) pour ~{pages} pages de corps (1 pour {ratio} p). "
        "Viser environ une figure toutes les 2 à 3 pages.",
    "info.citations": "{n} citation(s) à sourcer — voir citations-needed.md",
    "info.body": "corps du rapport : ~{pages} pages, {figs} figure(s)",
    "info.type": "type {type}, squelette {skeleton}",
    "info.too_short": "brouillon trop court pour évaluer les proportions "
                      "(vérification activée à partir d'environ 8 pages)",
    "info.no_yaml": "pas de report.yaml — cibles par chapitre non vérifiées",
    "fix.reference_added": "référence ajoutée pour '{slug}' dans {file}",
    "fix.slug_renamed": "slug '{old}' renommé en '{new}' dans {file}",
    "fix.nothing": "rien à corriger mécaniquement",
    "fix.see": "Cf.",
}

_EN: Dict[str, str] = {
    # --- LaTeX -------------------------------------------------------------
    "babel": "english",
    "cover.report_of": "Report —",
    "cover.academic_year": "Academic year",
    "cover.prepared_by": "Prepared by",
    "cover.supervised_by": "Supervised by",
    "cover.institution_logo": "Institution logo",
    "cover.host_logo": "Host organisation logo",
    "cover.to_complete": "To be completed",
    "tex.watermark": "DRAFT",
    "tex.table_col_a": "Column A",
    "tex.table_col_b": "Column B",
    "tex.table_empty": "Table not filled in — replace this.",
    "tex.code_empty": "CODE NOT FILLED IN — paste the snippet here",
    "tex.eq_empty": "equation not filled in",
    "bib.to_source": "TO SOURCE — cited in {where}",
    "bib.none": "No references",

    # --- CLI: status -------------------------------------------------------
    "status.type": "Type",
    "status.brief": "Brief",
    "status.brief_fields": "{filled}/{total} fields filled ({pct} %)",
    "status.col_chapter": "Chapter",
    "status.col_pages": "Pages",
    "status.col_target": "Target",
    "status.col_state": "State",
    "status.total_body": "Body total",
    "status.blocking": "Blocking placeholders",
    "status.figures": "Figures",
    "status.figures_value": "{declared} declared, {provided} provided, "
                            "{todo} to produce",
    "status.citations": "Citations to source",
    "status.next": "Next action",
    "state.unwritten": "not written",
    "state.over": "over budget",
    "state.incomplete": "incomplete",
    "state.ok": "ok",
    "next.fill_brief": "fill in BRIEF.md before drafting further",
    "next.write": "draft {name} (/report:draft --chapter …)",
    "next.fix_blocking": "fix the blocking problems (/report:review)",
    "next.replace_figures":
        "replace the grey figures (see build/figures/MANIFEST.md)",
    "next.review_then_build": "re-run /report:review then /report:build",

    # --- CLI: sources & gaps ----------------------------------------------
    "src.title": "Supplied documents",
    "src.none": "No {dir} folder — create it and drop in the documents (PDF, "
                "Markdown, text) holding what the brief is missing.",
    "src.empty": "{dir} is empty. Drop in the documents holding the missing "
                 "information, then re-run /report:draft.",
    "src.readable": "{n} readable document(s)",
    "src.unreadable": "{n} unreadable document(s)",
    "src.secrets": "{n} file(s) skipped (credentials — never read)",
    "src.extracted_to": "text extracted to {dir}",
    "gaps.title": "Missing information (never to be invented)",
    "gaps.none": "No empty fields in BRIEF.md.",
    "gaps.count": "{n} empty field(s) in BRIEF.md",
    "gaps.hint": "Fill them in BRIEF.md, or drop a document containing them "
                 "into {dir}, then re-run /report:draft.",
    "next.add_sources": "close the gaps: fill in BRIEF.md or drop a document "
                        "into {dir}",

    # --- CLI: build / Overleaf --------------------------------------------
    "build.bundle": "Overleaf folder: {path}",
    "build.zip": "Overleaf archive: {path}",
    "build.overleaf": "Upload this folder (or the archive) to Overleaf, "
                      "compiler pdfLaTeX, bibliography Biber.",
    "build.no_local_pdf": "No PDF is produced locally — by design. "
                          "Compilation happens on Overleaf.",
    # --- CLI: figures ------------------------------------------------------
    "fig.manifest_title": "# Figures required",
    "fig.col_slug": "Slug",
    "fig.col_caption": "Caption",
    "fig.col_chapter": "Chapter",
    "fig.col_minwidth": "Min. width",
    "fig.col_state": "State",
    "fig.state.placeholder": "placeholder",
    "fig.state.provided": "provided",
    "fig.state.missing": "missing",
    "fig.summary": "figures: {created} created, {real} real, "
                   "{placeholder} placeholder(s)",
    "fig.manifest": "manifest",

    # --- CLI: review -------------------------------------------------------
    "review.pages_header": "=== Pages per section ===",
    "review.blocking": "BLOCKING",
    "review.warning": "WARNING",
    "review.info": "INFO",
    "review.fail": "FAILED — {n} blocking problem(s).",
    "review.pass": "OK — {n} warning(s), nothing blocking.",
    "review.no_markdown": "no markdown file found in {root}",

    # --- CLI: build --------------------------------------------------------
    "build.not_found": "error: {path} not found",
    "build.blocked": "BLOCKED — {n} unresolved METRIC/TODO placeholder(s):",
    "build.and_more": "  … and {n} more",
    "build.blocked_hint": "Fill them in, or re-run with --allow-todo for a "
                          "draft bundle (placeholders in red, DRAFT "
                          "watermark).",
    "build.written": "written: {path}",
    "build.citations": "citations to source: {n} ({added} new bib entry/ies)",
    "build.no_pdflatex": "pdflatex not found — compile main.tex in Overleaf.",
    "build.no_biber": "biber not found — bibliography unresolved locally "
                      "(Overleaf resolves it automatically).",
    "build.pdf": "PDF: {path}",
    "build.compile_failed": "compilation failed:",
    "build.no_pandoc": "WARNING: pandoc not found — minimal conversion "
                       "(headings only). Install pandoc for a correct PDF "
                       "(lists, tables, quotes).",
    "build.citations_title": "# Citations to source",
    "build.cited_in": "cited in",

    # --- CLI: check --------------------------------------------------------
    "check.missing": "MISSING — install pandoc",
    "check.absent": "absent (Overleaf possible)",

    # --- review findings ---------------------------------------------------
    "issue.company_share":
        "'{name}' takes up {share} of the report body. The host-organisation "
        "presentation must stay under {cap} % — it is the most visible "
        "symptom of inverted proportions.",
    "issue.soa_share":
        "'{name}' takes up {share} of the body. A state of the art longer "
        "than the contribution is penalised every time.",
    "warn.soa_share_pfa":
        "'{name}' takes up {share} of the body. For a PFA the state of the "
        "art must stay brief — aim under 15–20 %.",
    "warn.intro_long":
        "'{name}' is ~{pages} pages. The general introduction must not "
        "exceed 2 pages.",
    "warn.conclusion_long":
        "'{name}' is ~{pages} pages. The general conclusion must not exceed "
        "2 pages.",
    "issue.over_budget":
        "'{key}' is ~{actual} p against a target of {lo}–{hi} p "
        "(report.yaml). Cut about {cut} p.",
    "warn.over_target":
        "'{key}' is ~{actual} p, above the {lo}–{hi} p target in report.yaml.",
    "warn.under_target":
        "'{key}' is ~{actual} p, well below the {lo}–{hi} p target — chapter "
        "probably incomplete.",
    "issue.unresolved": "{file}:{line} — unresolved [[{kind}]]: {caption}",
    "issue.malformed":
        "{file}:{line} — malformed placeholder {raw}. Accepted forms: FIG, "
        "TAB, CODE, EQ, CITE, METRIC, TODO, REF.",
    "warn.unreferenced":
        "{file} — '{slug}' is declared but never referenced in the text. "
        "Every illustration must be cited and justified in the body.",
    "issue.duplicate_slug":
        "duplicate slug '{slug}' ({a} and {b}) — LaTeX labels must be unique.",
    "msg.no_positioning":
        "{file} — state of the art with no positioning. A comparison table "
        "and a paragraph explicitly naming the gap this work fills are "
        "missing.",
    "issue.no_positioning_suffix":
        " This is the single most common weakness in AI-track reports.",
    "warn.no_positioning_suffix":
        " For a PFA/module a short table is enough.",
    "warn.no_baseline":
        "{file} — no baseline mentioned. A number with nothing to compare it "
        "against is not a result.",
    "warn.intro_results":
        "{file} — the introduction appears to announce numeric results. The "
        "introduction states the problem; it never gives the results.",
    "warn.figure_density":
        "~{figs} figure(s) for ~{pages} pages of body (1 per {ratio} p). Aim "
        "for roughly one figure every 2 to 3 pages.",
    "info.citations": "{n} citation(s) to source — see citations-needed.md",
    "info.body": "report body: ~{pages} pages, {figs} figure(s)",
    "info.type": "type {type}, skeleton {skeleton}",
    "info.too_short": "draft too short to assess proportions (the check "
                      "activates from about 8 pages)",
    "info.no_yaml": "no report.yaml — per-chapter targets not checked",
    "fix.reference_added": "reference added for '{slug}' in {file}",
    "fix.slug_renamed": "slug '{old}' renamed to '{new}' in {file}",
    "fix.nothing": "nothing to fix mechanically",
    "fix.see": "See",
}

LOCALES: Dict[str, Dict[str, str]] = {"fr": _FR, "en": _EN}


def normalise(lang: object) -> str:
    """Map anything the yaml may contain onto a supported locale code."""
    code = str(lang or "").strip().lower().replace("_", "-")
    if not code:
        return DEFAULT_LANG
    head = code.split("-")[0]
    if head in LOCALES:
        return head
    aliases = {"fra": "fr", "french": "fr", "francais": "fr",
               "eng": "en", "english": "en"}
    return aliases.get(head, DEFAULT_LANG)


class Strings:
    """Surface strings for one locale, with fallback to the default."""

    __slots__ = ("lang", "_table", "_fallback")

    def __init__(self, lang: str) -> None:
        self.lang = normalise(lang)
        self._table = LOCALES[self.lang]
        self._fallback = LOCALES[DEFAULT_LANG]

    def __call__(self, key: str, /, **kw) -> str:
        # `key` is positional-only: several messages take a {key} placeholder
        # of their own, and a keyword collision here would raise TypeError.
        text = self._table.get(key)
        if text is None:
            text = self._fallback.get(key, key)
        return text.format(**kw) if kw else text

    # convenience alias
    t = __call__


def strings(lang: object = DEFAULT_LANG) -> Strings:
    return Strings(normalise(lang))


# ---------------------------------------------------------------------------
# Detection vocabulary — the UNION across locales
# ---------------------------------------------------------------------------
#
# These drive *checks*, never output. They are unions on purpose: the same rule
# must fire on `03-etat-de-lart` and on `03-literature-review`. Extending a
# locale means adding words here, never adding a branch.

_VOCAB: Dict[str, Dict[str, Iterable[str]]] = {
    "company": {
        "fr": ("entreprise", "organisme", "presentation", "présentation",
               "societe", "société", "accueil"),
        "en": ("company", "organisation", "organization", "host",
               "presentation"),
    },
    "state_of_art": {
        "fr": ("etat-de-l-art", "etat", "état", "art", "existant",
               "veille", "bibliograph"),
        "en": ("state-of-the-art", "state-of-art", "literature", "related-work",
               "related", "background", "existing", "review", "survey"),
    },
    "results": {
        "fr": ("resultat", "résultat", "experimentation", "expérimentation",
               "evaluation", "évaluation", "validation"),
        "en": ("result", "experiment", "evaluation", "testing", "benchmark",
               "validation"),
    },
    "baseline": {
        "fr": ("baseline", "référence", "de référence", "reference",
               "état de l'art", "etat de l'art", "comparaison"),
        "en": ("baseline", "reference", "state of the art", "prior work",
               "comparison", "control"),
    },
    "front": {
        "fr": ("page-de-garde", "dedicace", "dédicace", "remerciement",
               "resume", "résumé", "sommaire", "acronyme", "declaration",
               "déclaration", "integrite", "intégrité", "tableaux"),
        "en": ("cover", "cover-page", "title-page", "dedication",
               "acknowledgement", "acknowledgment", "abstract", "contents",
               "acronym", "abbreviation", "declaration", "integrity",
               "glossary", "figures", "tables"),
    },
    "intro": {
        "fr": ("introduction-generale", "introduction-générale",
               "introduction_generale", "introduction"),
        "en": ("general-introduction", "introduction"),
    },
    "conclusion": {
        "fr": ("conclusion-generale", "conclusion-générale",
               "conclusion_generale", "conclusion"),
        "en": ("general-conclusion", "conclusion", "future-work"),
    },
    "annex": {
        "fr": ("annexe", "annexes"),
        "en": ("appendix", "appendices", "annex", "annexes"),
    },
    "positioning": {
        "fr": ("positionnement", "écart", "ecart", "verrou", "limite"),
        "en": ("positioning", "gap", "shortcoming", "limitation"),
    },
    # Prose that announces a measured result. Used to catch an introduction
    # that leaks results, which it must never do.
    "metric_prose": {
        "fr": ("précision de", "exactitude de", "taux de réussite",
               "score de", "rappel de", "atteint un"),
        "en": ("accuracy", "precision of", "recall of", "f1", "map",
               "reaches a score", "achieves an"),
    },
    # Words that introduce a cross-reference in running prose, used to decide
    # whether a figure was referenced without an explicit [[REF:]].
    "xref": {
        "fr": ("figure", "tableau", "tab.", "fig."),
        "en": ("figure", "table", "tab.", "fig."),
    },
}


def vocabulary(name: str) -> FrozenSet[str]:
    """Every term for `name`, across every locale."""
    group = _VOCAB.get(name, {})
    out = set()
    for terms in group.values():
        out.update(t.lower() for t in terms)
    return frozenset(out)


def matches(name: str, text: str) -> bool:
    """True if `text` contains any term of the `name` vocabulary."""
    low = (text or "").lower()
    return any(term in low for term in vocabulary(name))


# Sentinel values meaning "this brief field is still empty", in any language.
EMPTY_MARKERS = frozenset({
    "à compléter", "a completer", "to be completed", "to complete",
    "tbd", "todo", "...", "…", "—", "-", "n/a", "na",
})


def is_empty_value(value: str) -> bool:
    return (value or "").strip().lower() in EMPTY_MARKERS
