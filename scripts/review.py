#!/usr/bin/env python3
"""Check a report draft against jury criteria.

    python3 scripts/review.py reports_docs [--json]

Exit code 0 = pass, 1 = blocking problems found.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from placeholders import scan_tree  # noqa: E402

WORDS_PER_PAGE = 350  # dense academic French with figures

FRONT = ("page-de-garde", "dedicace", "remerciement", "resume", "abstract",
         "sommaire", "acronyme", "figures", "tableaux")


def words(text: str) -> int:
    text = re.sub(r"\[\[.*?\]\]", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return len(re.findall(r"\b\w+\b", text))


def load(root: Path) -> dict:
    files = {}
    for md in sorted(root.rglob("*.md")):
        if md.name in ("BRIEF.md", "MANIFEST.md", "citations-needed.md"):
            continue
        files[str(md.relative_to(root))] = md.read_text(encoding="utf-8")
    return files


def chapter_of(path: str) -> str:
    parts = Path(path).parts
    return parts[0] if len(parts) > 1 else Path(path).stem


def run(root: Path) -> dict:
    files = load(root)
    ph = scan_tree(root)
    issues, warnings, info = [], [], []

    if not files:
        return {"issues": [f"aucun fichier markdown trouvé dans {root}"],
                "warnings": [], "info": [], "pages": {}}

    # ---- proportions -------------------------------------------------------
    counts: dict[str, int] = {}
    for path, text in files.items():
        counts[chapter_of(path)] = counts.get(chapter_of(path), 0) + words(text)
    pages = {k: round(v / WORDS_PER_PAGE, 1) for k, v in sorted(counts.items())}
    body_total = sum(v for k, v in counts.items()
                     if not any(f in k.lower() for f in FRONT))

    # proportions are only meaningful once there is enough text to judge
    proportions_meaningful = body_total >= 3000  # ~8+ pages

    for name, wc in counts.items():
        low = name.lower()
        if not proportions_meaningful:
            break
        share = wc / body_total if body_total else 0
        if any(k in low for k in ("entreprise", "organisme", "presentation")) and share > 0.15:
            issues.append(
                f"'{name}' occupe {share:.0%} du corps du rapport. "
                f"La présentation de l'organisme doit rester sous 15 % — c'est le "
                f"symptôme le plus visible de proportions inversées.")
        if "etat" in low or "art" in low:
            if share > 0.30:
                issues.append(
                    f"'{name}' occupe {share:.0%} du corps. Un état de l'art plus "
                    f"volumineux que la contribution est systématiquement sanctionné.")
        if any(k in low for k in ("introduction",)) and wc > 900:
            warnings.append(
                f"'{name}' fait ~{wc / WORDS_PER_PAGE:.1f} pages. "
                f"L'introduction générale ne doit pas dépasser 2 pages.")
        if "conclusion" in low and wc > 900:
            warnings.append(
                f"'{name}' fait ~{wc / WORDS_PER_PAGE:.1f} pages. "
                f"La conclusion générale ne doit pas dépasser 2 pages.")

    # ---- blocking placeholders --------------------------------------------
    for p in ph:
        if p.blocking:
            issues.append(f"{p.file}:{p.line} — [[{p.kind}]] non résolu : {p.caption}")

    # ---- unreferenced figures and tables ----------------------------------
    declared = {p.slug: p for p in ph if p.kind in ("FIG", "TAB")}
    referenced = {p.slug for p in ph if p.kind == "REF"}
    all_text = "\n".join(files.values())
    for slug, p in declared.items():
        if slug in referenced:
            continue
        if re.search(rf"\b(figure|tableau)\s+\S*{re.escape(slug)}", all_text, re.I):
            continue
        warnings.append(
            f"{p.file} — '{slug}' est déclaré mais jamais référencé dans le texte. "
            f"Toute illustration doit être citée et justifiée dans le corps du rapport.")

    # ---- duplicate slugs ---------------------------------------------------
    seen: dict[str, str] = {}
    for p in ph:
        if p.kind not in ("FIG", "TAB", "CODE", "EQ"):
            continue
        if p.slug in seen and seen[p.slug] != p.file:
            issues.append(f"slug dupliqué '{p.slug}' ({seen[p.slug]} et {p.file}) — "
                          f"les labels LaTeX doivent être uniques.")
        seen.setdefault(p.slug, p.file)

    # ---- état de l'art without positioning --------------------------------
    for path, text in files.items():
        low = path.lower()
        if "etat" in low or "art" in low or "literature" in low:
            has_table = "|---" in text or "[[TAB:" in text
            has_pos = re.search(r"positionnement|positioning|écart|gap", text, re.I)
            if not (has_table and has_pos):
                issues.append(
                    f"{path} — état de l'art sans positionnement. Il manque un tableau "
                    f"comparatif et un paragraphe nommant explicitement l'écart que ce "
                    f"travail comble. C'est la faiblesse la plus courante des rapports IA.")

    # ---- results without a baseline ---------------------------------------
    for path, text in files.items():
        low = path.lower()
        if any(k in low for k in ("resultat", "experimentation", "result", "evaluation")):
            if not re.search(r"baseline|référence|de référence|état de l'art", text, re.I):
                warnings.append(
                    f"{path} — aucune baseline mentionnée. Un chiffre sans point de "
                    f"comparaison n'est pas un résultat.")

    # ---- introduction leaking results -------------------------------------
    for path, text in files.items():
        if "introduction" not in path.lower():
            continue
        if re.search(r"\b\d{1,3}[.,]\d+\s*%|\bmAP\b|\bF1\b|\baccuracy\b|\bprécision de\b",
                     text, re.I):
            warnings.append(
                f"{path} — l'introduction semble annoncer des résultats chiffrés. "
                f"L'introduction pose le problème, elle ne donne jamais les résultats.")

    # ---- citations needed --------------------------------------------------
    cites = [p for p in ph if p.kind == "CITE"]
    if cites:
        info.append(f"{len(cites)} citation(s) à sourcer — voir citations-needed.md")

    figs = len({p.slug for p in ph if p.kind == "FIG"})
    total_pages = round(body_total / WORDS_PER_PAGE, 1)
    if total_pages > 4 and figs:
        ratio = total_pages / figs
        if ratio > 4:
            warnings.append(
                f"~{figs} figure(s) pour ~{total_pages} pages de corps "
                f"(1 pour {ratio:.1f} p). Viser environ une figure toutes les 2 à 3 pages.")

    info.append(f"corps du rapport : ~{total_pages} pages, {figs} figure(s)")
    if not proportions_meaningful:
        info.append("brouillon trop court pour évaluer les proportions "
                    "(vérification activée à partir d'environ 8 pages)")

    return {"issues": issues, "warnings": warnings, "info": info, "pages": pages}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0] if args else "reports_docs")
    result = run(root)

    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["issues"] else 0

    print("\n=== Pages par section ===")
    for name, pg in result["pages"].items():
        print(f"  {pg:>6} p   {name}")

    for label, key, mark in (("BLOQUANT", "issues", "x"),
                             ("AVERTISSEMENT", "warnings", "!"),
                             ("INFO", "info", "i")):
        if result[key]:
            print(f"\n=== {label} ({len(result[key])}) ===")
            for item in result[key]:
                print(f"  [{mark}] {item}")

    print()
    if result["issues"]:
        print(f"ÉCHEC — {len(result['issues'])} problème(s) bloquant(s).")
        return 1
    print(f"OK — {len(result['warnings'])} avertissement(s), aucun blocage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
