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
from i18n import matches, strings, vocabulary  # noqa: E402
from paths import is_report_content  # noqa: E402

# Front-matter detection uses the shared vocabulary (all locales at once),
# so `01-remerciements` and `01-acknowledgements` are excluded from the
# body word count identically.
FRONT = tuple(vocabulary("front"))


def words(text: str) -> int:
    text = re.sub(r"\[\[.*?\]\]", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return len(re.findall(r"\b\w+\b", text))


def load(root: Path) -> dict:
    files = {}
    for md in sorted(root.rglob("*.md")):
        if not is_report_content(md, root):
            continue
        files[str(md.relative_to(root))] = md.read_text(encoding="utf-8")
    return files


def _xref_in_prose(text: str, slug: str) -> bool:
    """True if the slug is referenced in running prose ("see Figure 3.2"),
    in any supported language, without an explicit [[REF:]]."""
    words = "|".join(re.escape(w) for w in sorted(vocabulary("xref")))
    return bool(re.search(rf"\b({words})\s+\S*{re.escape(slug)}",
                          text, re.I))


def chapter_of(path: str) -> str:
    parts = Path(path).parts
    return parts[0] if len(parts) > 1 else Path(path).stem


def run(root: Path) -> dict:
    root = Path(root)
    files = load(root)
    ph = scan_tree(root)
    cfg = load_report_config(root)
    S = strings(cfg.lang)
    issues, warnings, info = [], [], []

    if not files:
        return {"issues": [S("review.no_markdown", root=root)],
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
        if cap is not None and matches("company", low) and share > cap:
            issues.append(S("issue.company_share", name=name,
                            share=f"{share:.0%}", cap=int(cap * 100)))
        if matches("state_of_art", low):
            if share > 0.30:
                issues.append(S("issue.soa_share", name=name,
                                share=f"{share:.0%}"))
            elif cfg.type == "pfa" and share > 0.20:
                warnings.append(S("warn.soa_share_pfa", name=name,
                                  share=f"{share:.0%}"))
        spec = cfg.spec_for(name)
        if spec.kind == "intro" or "introduction" in low:
            if wc > 2 * wpp:
                warnings.append(S("warn.intro_long", name=name,
                                  pages=f"{wc / wpp:.1f}"))
        if spec.kind == "conclusion" or "conclusion" in low:
            if wc > 2 * wpp:
                warnings.append(S("warn.conclusion_long", name=name,
                                  pages=f"{wc / wpp:.1f}"))

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
                issues.append(S("issue.over_budget", key=key, actual=actual,
                                lo=lo, hi=hi, cut=f"{actual - hi:.1f}"))
            elif actual > hi and spec.kind not in ("front",):
                warnings.append(S("warn.over_target", key=key,
                                  actual=actual, lo=lo, hi=hi))
            elif 0 < actual < lo * 0.5 and spec.kind == "chapter":
                warnings.append(S("warn.under_target", key=key,
                                  actual=actual, lo=lo, hi=hi))

    for p in ph:
        if p.blocking:
            issues.append(S("issue.unresolved", file=p.file, line=p.line,
                            kind=p.kind, caption=p.caption))

    for m in scan_tree_malformed(root):
        issues.append(S("issue.malformed", file=m.file, line=m.line,
                        raw=repr(m.raw)))

    declared = {p.slug: p for p in ph if p.kind in ("FIG", "TAB")}
    referenced = {p.slug for p in ph if p.kind == "REF"}
    all_text = "\n".join(files.values())
    for slug, p in declared.items():
        if slug in referenced:
            continue
        if _xref_in_prose(all_text, slug):
            continue
        warnings.append(S("warn.unreferenced", file=p.file, slug=slug))

    seen: Dict[str, str] = {}
    for p in ph:
        if p.kind not in ("FIG", "TAB", "CODE", "EQ"):
            continue
        if p.slug in seen and seen[p.slug] != p.file:
            issues.append(S("issue.duplicate_slug", slug=p.slug,
                            a=seen[p.slug], b=p.file))
        seen.setdefault(p.slug, p.file)

    pos_level = cfg.requires_positioning_level()
    if pos_level:
        for path, text in files.items():
            low = path.lower()
            if not matches("state_of_art", low):
                continue
            has_table = "|---" in text or "[[TAB:" in text
            has_pos = matches("positioning", text)
            if has_table and has_pos:
                continue
            msg = S("msg.no_positioning", file=path)
            if pos_level == "issue":
                issues.append(msg + S("issue.no_positioning_suffix"))
            else:
                warnings.append(msg + S("warn.no_positioning_suffix"))

    if cfg.requires_baseline():
        for path, text in files.items():
            low = path.lower()
            if matches("results", low):
                if not matches("baseline", text):
                    warnings.append(S("warn.no_baseline", file=path))

    for path, text in files.items():
        spec = cfg.spec_for(chapter_of(path))
        if spec.kind != "intro" and "introduction" not in path.lower():
            continue
        # A number with a unit, or any language's way of naming a metric.
        if re.search(r"\b\d{1,3}[.,]\d+\s*%", text) or \
                matches("metric_prose", text):
            warnings.append(S("warn.intro_results", file=path))

    cites = [p for p in ph if p.kind == "CITE"]
    if cites:
        info.append(S("info.citations", n=len(cites)))

    figs = len({p.slug for p in ph if p.kind == "FIG"})
    total_pages = round(body_total / wpp, 1)
    if total_pages > 4 and figs:
        ratio = total_pages / figs
        if ratio > 4:
            warnings.append(S("warn.figure_density", figs=figs,
                              pages=total_pages, ratio=f"{ratio:.1f}"))

    info.append(S("info.body", pages=total_pages, figs=figs))
    info.append(S("info.type", type=cfg.type, skeleton=cfg.skeleton))
    if not proportions_meaningful:
        info.append(S("info.too_short"))
    if cfg.source is None:
        info.append(S("info.no_yaml"))

    return {
        "issues": issues,
        "warnings": warnings,
        "info": info,
        "pages": pages,
        "type": cfg.type,
        "skeleton": cfg.skeleton,
        "pages_total_target": cfg.pages_total,
        "pages_body": total_pages,
        "lang": cfg.lang,
    }


def apply_fixes(root: Path) -> List[str]:
    """Mechanical fixes only: unreferenced figures, duplicate slugs."""
    root = Path(root)
    files = load(root)
    ph = scan_tree(root)
    S = strings(load_report_config(root).lang)
    log: List[str] = []

    declared = [p for p in ph if p.kind in ("FIG", "TAB")]
    referenced = {p.slug for p in ph if p.kind == "REF"}
    all_text = "\n".join(files.values())
    for p in declared:
        if p.slug in referenced:
            continue
        if _xref_in_prose(all_text, p.slug):
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
        insertion = needle + f"\n{S('fix.see')} [[REF: {p.slug}]].\n"
        path.write_text(text.replace(needle, insertion, 1), encoding="utf-8")
        log.append(S("fix.reference_added", slug=p.slug, file=p.file))
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
            log.append(S("fix.slug_renamed", old=p.slug, new=new_slug,
                           file=p.file))
        seen[p.slug] = p.file

    if not log:
        log.append(S("fix.nothing"))
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
    S = strings(result.get("lang"))

    if "--json" in flags:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["issues"] else 0

    print("\n" + S("review.pages_header"))
    for name, pg in result["pages"].items():
        print(f"  {pg:>6} p   {name}")

    for key, label_key, mark in (("issues", "review.blocking", "x"),
                                 ("warnings", "review.warning", "!"),
                                 ("info", "review.info", "i")):
        if result[key]:
            print(f"\n=== {S(label_key)} ({len(result[key])}) ===")
            for item in result[key]:
                print(f"  [{mark}] {item}")

    print()
    if result["issues"]:
        print(S("review.fail", n=len(result["issues"])))
        return 1
    print(S("review.pass", n=len(result["warnings"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
