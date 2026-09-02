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
from i18n import is_empty_value, strings  # noqa: E402
from sources import brief_gaps, collect, sources_dir  # noqa: E402


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
        if value and not is_empty_value(value):
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
        "provided": provided,
        "placeholder": placeholder,
        "missing": missing,
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

    S = strings(cfg.lang)
    label_w = max(len(S("status.type")), len(S("status.brief")),
                  len(S("status.blocking")), len(S("status.figures")),
                  len(S("status.citations"))) + 3
    lines = [
        f"{S('status.type'):<{label_w}}{cfg.type.upper()} — "
        f"{cfg.skeleton} ({cfg.lang})",
        f"{S('status.brief'):<{label_w}}"
        + S("status.brief_fields", filled=filled, total=total, pct=pct),
        "",
        f"{S('status.col_chapter'):<34} {S('status.col_pages'):>6}  "
        f"{S('status.col_target'):>9}  {S('status.col_state')}",
    ]
    for name, pg in result["pages"].items():
        spec = cfg.spec_for(name)
        if spec.pages:
            cible = f"{spec.pages[0]}–{spec.pages[1]}"
        else:
            cible = "—"
        if pg == 0:
            etat = S("state.unwritten")
        elif spec.pages and pg > spec.pages[1] * 1.15:
            etat = S("state.over")
        elif spec.pages and pg < spec.pages[0] * 0.5:
            etat = S("state.incomplete")
        else:
            etat = S("state.ok")
        lines.append(f"{name:<34} {pg:>6}  {cible:>9}  {etat}")

    body = result.get("pages_body", 0)
    lines += [
        "",
        f"{S('status.total_body'):<34} {body:>6}  {str(cfg.pages_total):>9}",
        "",
        f"{S('status.blocking'):<{label_w}}{blocking}",
        f"{S('status.figures'):<{label_w}}"
        + S("status.figures_value", declared=figs["declared"],
            provided=figs["provided"],
            todo=figs["placeholder"] + figs["missing"]),
        f"{S('status.citations'):<{label_w}}{cites}",
    ]

    gaps = brief_gaps(root)
    gap_count = sum(len(v) for v in gaps.values())
    inv = collect(root, extract=False)
    lines += [
        S("gaps.count", n=gap_count),
        S("src.readable", n=len(inv.readable))
        + (f"  ({sources_dir(root)})" if inv.exists else ""),
    ]

    next_action = _next_action(result, filled, total, figs, S,
                               gap_count, sources_dir(root))
    lines += ["", f"{S('status.next')} : {next_action}"]
    return "\n".join(lines) + "\n"


def _next_action(result, filled, total, figs, S,
                 gap_count=0, sdir="") -> str:
    if total and filled / total < 0.4:
        return S("next.fill_brief")
    if gap_count:
        return S("next.add_sources", dir=sdir)
    pages = result.get("pages") or {}
    empty = [n for n, p in pages.items() if p == 0]
    if empty:
        return S("next.write", name=empty[0])
    if result["issues"]:
        return S("next.fix_blocking")
    if figs["placeholder"] + figs["missing"]:
        return S("next.replace_figures")
    return S("next.review_then_build")


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
