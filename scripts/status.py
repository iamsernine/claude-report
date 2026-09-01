#!/usr/bin/env python3
"""Compact progress table for /report:status."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_figures import is_placeholder  # noqa: E402
from placeholders import scan_tree  # noqa: E402
from report_config import load_report_config  # noqa: E402
from review import run as review_run  # noqa: E402


def brief_completeness(root: Path) -> tuple:
    path = root / "BRIEF.md"
    if not path.is_file():
        return 0, 0, 0
    total = filled = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("- "):
            continue
        if ":" not in line:
            continue
        total += 1
        _, _, rest = line.partition(":")
        value = rest.strip()
        if value and value not in ("À compléter", "TBD", "...", "—", "-"):
            filled += 1
    pct = round(100 * filled / total) if total else 0
    return filled, total, pct


def figure_counts(root: Path, build_dir: Path) -> dict:
    figs = {p.slug for p in scan_tree(root) if p.kind == "FIG"}
    provided = placeholder = missing = 0
    figdir = build_dir / "figures"
    for slug in figs:
        path = figdir / f"{slug}.png"
        flag = is_placeholder(path)
        if flag is None:
            missing += 1
        elif flag:
            placeholder += 1
        else:
            provided += 1
    return {
        "declared": len(figs),
        "fourni": provided,
        "placeholder": placeholder,
        "manquant": missing,
    }


def status_text(root: Path, build_dir: Path = None) -> str:
    root = Path(root)
    build_dir = Path(build_dir) if build_dir else root.parent / "build"
    cfg = load_report_config(root)
    result = review_run(root)
    filled, total, pct = brief_completeness(root)
    figs = figure_counts(root, build_dir)
    cites = sum(1 for p in scan_tree(root) if p.kind == "CITE")
    blocking = len(result["issues"])

    lines = [
        f"Type            {cfg.type.upper()} — {cfg.skeleton} ({cfg.lang})",
        f"Brief           {filled}/{total} champs renseignés ({pct} %)",
        "",
        f"{'Chapitre':<34} {'Pages':>6}  {'Cible':>9}  État",
    ]
    for name, pg in result["pages"].items():
        spec = cfg.spec_for(name)
        if spec.pages:
            cible = f"{spec.pages[0]}–{spec.pages[1]}"
        else:
            cible = "—"
        if pg == 0:
            etat = "non rédigé"
        elif spec.pages and pg > spec.pages[1] * 1.15:
            etat = "dépassement"
        elif spec.pages and pg < spec.pages[0] * 0.5:
            etat = "incomplet"
        else:
            etat = "ok"
        lines.append(f"{name:<34} {pg:>6}  {cible:>9}  {etat}")

    body = result.get("pages_body", 0)
    lines += [
        "",
        f"{'Total corps':<34} {body:>6}  {str(cfg.pages_total):>9}",
        "",
        f"Placeholders bloquants   {blocking}",
        f"Figures                  {figs['declared']} déclarées, "
        f"{figs['fourni']} fournies, "
        f"{figs['placeholder'] + figs['manquant']} à produire",
        f"Citations à sourcer      {cites}",
    ]

    next_action = _next_action(result, filled, total, figs)
    lines += ["", f"Prochaine action : {next_action}"]
    return "\n".join(lines) + "\n"


def _next_action(result, filled, total, figs) -> str:
    if total and filled / total < 0.4:
        return "compléter BRIEF.md avant de rédiger davantage"
    pages = result.get("pages") or {}
    empty = [n for n, p in pages.items() if p == 0]
    if empty:
        return f"rédiger {empty[0]} (/report:draft --chapter …)"
    if result["issues"]:
        return "corriger les problèmes bloquants (/report:review)"
    if figs["placeholder"] + figs["manquant"]:
        return "remplacer les figures grises (voir build/figures/MANIFEST.md)"
    return "relancer /report:review puis /report:build"


def main() -> int:
    raw = sys.argv[1:]
    as_json = "--json" in raw
    args = [a for a in raw if not a.startswith("--")]
    root = Path(args[0] if args else "reports_docs")
    if as_json:
        print(json.dumps(review_run(root), ensure_ascii=False, indent=2))
    else:
        print(status_text(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
