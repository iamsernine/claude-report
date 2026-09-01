#!/usr/bin/env python3
"""Check a report draft against jury criteria.

    python3 scripts/review.py reports_docs [--json] [--fix]

Exit code 0 = pass, 1 = blocking problems found.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))
from placeholders import (  # noqa: E402
    scan_text, scan_tree, scan_tree_malformed,
)
from report_config import load_report_config  # noqa: E402

FRONT = ("page-de-garde", "dedicace", "remerciement", "resume", "abstract",
         "sommaire", "acronyme", "figures", "tableaux", "declaration",
         "integrite")


def words(text: str) -> int:
    text = re.sub(r"\[\[.*?\]\]", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return len(re.findall(r"\b\w+\b", text))


def load(root: Path) -> dict:
    files = {}
    for md in sorted(root.rglob("*.md")):
        if md.name in ("BRIEF.md", "MANIFEST.md", "citations-needed.md"):
            continue
        if md.name.endswith(".generated"):
            continue
        files[str(md.relative_to(root))] = md.read_text(encoding="utf-8")
    return files


def chapter_of(path: str) -> str:
    parts = Path(path).parts
    return parts[0] if len(parts) > 1 else Path(path).stem


def run(root: Path) -> dict:
    root = Path(root)
    files = load(root)
    ph = scan_tree(root)
    cfg = load_report_config(root)
    issues, warnings, info = [], [], []

    if not files:
        return {"issues": [f"aucun fichier markdown trouvé dans {root}"],
                "warnings": [], "info": [], "pages": {},
                "type": cfg.type, "skeleton": cfg.skeleton}

    counts: Dict[str, int] = {}
    for path, text in files.items():
        counts[chapter_of(path)] = counts.get(chapter_of(path), 0) + words(text)
    wpp = cfg.words_per_page or 350
    pages = {k: round(v / wpp, 1) for k, v in sorted(counts.items())}
    body_total = sum(v for k, v in counts.items()
                     if not any(f in k.lower() for f in FRONT))

    proportions_meaningful = body_total >= 3000

    cap = cfg.company_share_cap()
    for name, wc in counts.items():
        low = name.lower()
        if not proportions_meaningful:
            break
        share = wc / body_total if body_total else 0
        if cap is not None and any(
                k in low for k in ("entreprise", "organisme", "presentation")
        ) and share > cap:
            issues.append(
                f"'{name}' occupe {share:.0%} du corps du rapport. "
                f"La présentation de l'organisme doit rester sous "
                f"{int(cap * 100)} % — c'est le symptôme le plus visible "
                f"de proportions inversées.")
        if "etat" in low or (low.endswith("art") or "-art" in low):
            if share > 0.30:
                issues.append(
                    f"'{name}' occupe {share:.0%} du corps. Un état de l'art "
                    f"plus volumineux que la contribution est "
                    f"systématiquement sanctionné.")
            elif cfg.type == "pfa" and share > 0.20:
                warnings.append(
                    f"'{name}' occupe {share:.0%} du corps. Pour un PFA, "
                    f"l'état de l'art doit rester bref — viser sous 15–20 %.")
        spec = cfg.spec_for(name)
        if spec.kind == "intro" or "introduction" in low:
            if wc > 2 * wpp:
                warnings.append(
                    f"'{name}' fait ~{wc / wpp:.1f} pages. "
                    f"L'introduction générale ne doit pas dépasser 2 pages.")
        if spec.kind == "conclusion" or "conclusion" in low:
            if wc > 2 * wpp:
                warnings.append(
                    f"'{name}' fait ~{wc / wpp:.1f} pages. "
                    f"La conclusion générale ne doit pas dépasser 2 pages.")

    if proportions_meaningful and cfg.chapters:
        for key, spec in cfg.chapters.items():
            if not spec.pages:
                continue
            lo, hi = spec.pages
            actual = None
            for name, pg in pages.items():
                if name == key or name.startswith(key) or key.startswith(name):
                    actual = pg
                    break
            if actual is None:
                continue
            if actual > hi * 1.15 and spec.kind not in ("front",):
                issues.append(
                    f"'{key}' fait ~{actual} p pour une cible de {lo}–{hi} p "
                    f"(report.yaml). Couper d'environ {actual - hi:.1f} p.")
            elif actual > hi and spec.kind not in ("front",):
                warnings.append(
                    f"'{key}' fait ~{actual} p, au-dessus de la cible "
                    f"{lo}–{hi} p de report.yaml.")
            elif 0 < actual < lo * 0.5 and spec.kind == "chapter":
                warnings.append(
                    f"'{key}' fait ~{actual} p, bien en-dessous de la cible "
                    f"{lo}–{hi} p — chapitre probablement incomplet.")

    for p in ph:
        if p.blocking:
            issues.append(
                f"{p.file}:{p.line} — [[{p.kind}]] non résolu : {p.caption}")

    for m in scan_tree_malformed(root):
        issues.append(
            f"{m.file}:{m.line} — placeholder mal formé {m.raw!r}. "
            f"Formes acceptées : FIG, TAB, CODE, EQ, CITE, METRIC, TODO, REF.")

    declared = {p.slug: p for p in ph if p.kind in ("FIG", "TAB")}
    referenced = {p.slug for p in ph if p.kind == "REF"}
    all_text = "\n".join(files.values())
    for slug, p in declared.items():
        if slug in referenced:
            continue
        if re.search(rf"\b(figure|tableau)\s+\S*{re.escape(slug)}",
                     all_text, re.I):
            continue
        warnings.append(
            f"{p.file} — '{slug}' est déclaré mais jamais référencé dans le "
            f"texte. Toute illustration doit être citée et justifiée dans le "
            f"corps du rapport.")

    seen: Dict[str, str] = {}
    for p in ph:
        if p.kind not in ("FIG", "TAB", "CODE", "EQ"):
            continue
        if p.slug in seen and seen[p.slug] != p.file:
            issues.append(
                f"slug dupliqué '{p.slug}' ({seen[p.slug]} et {p.file}) — "
                f"les labels LaTeX doivent être uniques.")
        seen.setdefault(p.slug, p.file)

    pos_level = cfg.requires_positioning_level()
    if pos_level:
        for path, text in files.items():
            low = path.lower()
            if not ("etat" in low or "art" in low or "literature" in low):
                continue
            has_table = "|---" in text or "[[TAB:" in text
            has_pos = re.search(
                r"positionnement|positioning|écart|gap", text, re.I)
            if has_table and has_pos:
                continue
            msg = (
                f"{path} — état de l'art sans positionnement. Il manque un "
                f"tableau comparatif et un paragraphe nommant explicitement "
                f"l'écart que ce travail comble.")
            if pos_level == "issue":
                issues.append(
                    msg + " C'est la faiblesse la plus courante des rapports IA.")
            else:
                warnings.append(
                    msg + " Pour un PFA/module, un tableau court suffit.")

    if cfg.requires_baseline():
        for path, text in files.items():
            low = path.lower()
            if any(k in low for k in (
                    "resultat", "experimentation", "result", "evaluation")):
                if not re.search(
                        r"baseline|référence|de référence|état de l'art",
                        text, re.I):
                    warnings.append(
                        f"{path} — aucune baseline mentionnée. Un chiffre "
                        f"sans point de comparaison n'est pas un résultat.")

    for path, text in files.items():
        spec = cfg.spec_for(chapter_of(path))
        if spec.kind != "intro" and "introduction" not in path.lower():
            continue
        if re.search(
                r"\b\d{1,3}[.,]\d+\s*%|\bmAP\b|\bF1\b|\baccuracy\b|"
                r"\bprécision de\b",
                text, re.I):
            warnings.append(
                f"{path} — l'introduction semble annoncer des résultats "
                f"chiffrés. L'introduction pose le problème, elle ne donne "
                f"jamais les résultats.")

    cites = [p for p in ph if p.kind == "CITE"]
    if cites:
        info.append(f"{len(cites)} citation(s) à sourcer — voir citations-needed.md")

    figs = len({p.slug for p in ph if p.kind == "FIG"})
    total_pages = round(body_total / wpp, 1)
    if total_pages > 4 and figs:
        ratio = total_pages / figs
        if ratio > 4:
            warnings.append(
                f"~{figs} figure(s) pour ~{total_pages} pages de corps "
                f"(1 pour {ratio:.1f} p). Viser environ une figure toutes "
                f"les 2 à 3 pages.")

    info.append(f"corps du rapport : ~{total_pages} pages, {figs} figure(s)")
    info.append(f"type {cfg.type}, squelette {cfg.skeleton}")
    if not proportions_meaningful:
        info.append("brouillon trop court pour évaluer les proportions "
                    "(vérification activée à partir d'environ 8 pages)")
    if cfg.source is None:
        info.append("pas de report.yaml — cibles par chapitre non vérifiées")

    return {
        "issues": issues,
        "warnings": warnings,
        "info": info,
        "pages": pages,
        "type": cfg.type,
        "skeleton": cfg.skeleton,
        "pages_total_target": cfg.pages_total,
        "pages_body": total_pages,
    }


def apply_fixes(root: Path) -> List[str]:
    """Mechanical fixes only: unreferenced figures, duplicate slugs."""
    root = Path(root)
    files = load(root)
    ph = scan_tree(root)
    log: List[str] = []

    declared = [p for p in ph if p.kind in ("FIG", "TAB")]
    referenced = {p.slug for p in ph if p.kind == "REF"}
    all_text = "\n".join(files.values())
    for p in declared:
        if p.slug in referenced:
            continue
        if re.search(rf"\b(figure|tableau)\s+\S*{re.escape(p.slug)}",
                     all_text, re.I):
            continue
        path = root / p.file
        text = path.read_text(encoding="utf-8")
        needle = None
        for m in re.finditer(r"\[\[\s*(FIG|TAB)\s*:.*?\]\]", text, re.S):
            items = scan_text(m.group(0), p.file)
            if items and items[0].slug == p.slug:
                needle = m.group(0)
                break
        if not needle:
            continue
        insertion = needle + f"\nCf. [[REF: {p.slug}]].\n"
        path.write_text(text.replace(needle, insertion, 1), encoding="utf-8")
        log.append(f"référence ajoutée pour '{p.slug}' dans {p.file}")
        referenced.add(p.slug)

    seen: Dict[str, str] = {}
    used_slugs = {p.slug for p in ph if p.kind in ("FIG", "TAB", "CODE", "EQ")}
    for p in ph:
        if p.kind not in ("FIG", "TAB", "CODE", "EQ"):
            continue
        if p.slug not in seen:
            seen[p.slug] = p.file
            continue
        if seen[p.slug] == p.file:
            continue
        n = 2
        new_slug = f"{p.slug}-{n}"
        while new_slug in used_slugs:
            n += 1
            new_slug = f"{p.slug}-{n}"
        path = root / p.file
        text = path.read_text(encoding="utf-8")
        # replace slug only in the declaration of this kind
        pattern = re.compile(
            rf"(\[\[\s*{p.kind}\s*:\s*){re.escape(p.slug)}(\s*[\|\]])",
        )
        new_text, nsub = pattern.subn(rf"\1{new_slug}\2", text, count=1)
        if nsub:
            path.write_text(new_text, encoding="utf-8")
            used_slugs.add(new_slug)
            log.append(
                f"slug '{p.slug}' renommé en '{new_slug}' dans {p.file}")
        seen[p.slug] = p.file

    if not log:
        log.append("rien à corriger mécaniquement")
    return log


def main() -> int:
    raw = sys.argv[1:]
    flags = {a for a in raw if a.startswith("--")}
    args = [a for a in raw if not a.startswith("--")]
    root = Path(args[0] if args else "reports_docs")

    if "--fix" in flags:
        log = apply_fixes(root)
        for line in log:
            print(f"  fix: {line}")

    result = run(root)

    if "--json" in flags:
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
