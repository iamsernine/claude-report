#!/usr/bin/env python3
"""Unified entry point for plugin commands.

Invoke it by absolute path; it locates its own plugin root from ``__file__``,
so no wrapper needs to compute one::

    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" review reports_docs
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" build reports_docs build --allow-todo

All human-readable output follows ``lang:`` in the project's report.yaml.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from draft_guard import classify, stamp  # noqa: E402
from gen_figures import generate as generate_figures  # noqa: E402
from report_config import load_report_config  # noqa: E402
from review import apply_fixes  # noqa: E402
from build import build  # noqa: E402
from status import status_text  # noqa: E402
from paths import plugin_root  # noqa: E402
from sources import brief_gaps, collect, sources_dir  # noqa: E402
from i18n import strings  # noqa: E402


def _cmd_review(args) -> int:
    if args.fix:
        for line in apply_fixes(Path(args.source)):
            print(f"  fix: {line}")
    # Re-run review.main-style output via the script's flags
    sys.argv = ["review.py", args.source]
    if args.json:
        sys.argv.append("--json")
    from review import main as review_main
    return review_main()


def _cmd_build(args) -> int:
    out = args.out_opt or args.out
    return build(Path(args.source), Path(out),
                 allow_todo=args.allow_todo, compile_pdf=args.compile_pdf)


def _cmd_sources(args) -> int:
    """Inventory reports_docs/sources/ and make PDFs readable."""
    root = Path(args.source)
    S = strings(load_report_config(root).lang)
    inv = collect(root, extract=not args.no_extract)
    rel = sources_dir(root)
    if not inv.exists:
        print(S("src.none", dir=rel))
        return 1
    if not inv.items:
        print(S("src.empty", dir=rel))
        return 1

    print(S("src.title"))
    for item in inv.items:
        mark = "+" if item.readable else ("-" if item.kind != "secret" else "!")
        size = f"{item.bytes // 1024} kB"
        detail = f"{item.chars} chars" if item.readable else item.note
        print(f"  [{mark}] {item.rel:<44} {size:>8}  {detail}")
        if item.readable and item.text_path != item.path:
            print(f"      -> {item.text_path}")

    print()
    print(S("src.readable", n=len(inv.readable)))
    if inv.unreadable:
        print(S("src.unreadable", n=len(inv.unreadable)))
    if inv.skipped_secrets:
        print(S("src.secrets", n=len(inv.skipped_secrets)))
    return 0


def _cmd_gaps(args) -> int:
    """What is still missing, and therefore must not be written."""
    root = Path(args.source)
    S = strings(load_report_config(root).lang)
    gaps = brief_gaps(root)
    total = sum(len(v) for v in gaps.values())
    if not total:
        print(S("gaps.none"))
        return 0
    print(S("gaps.title"))
    for section, fields in gaps.items():
        print(f"\n  {section}")
        for field in fields:
            print(f"    - {field}")
    print()
    print(S("gaps.count", n=total))
    print(S("gaps.hint", dir=sources_dir(root)))
    return 1


def _cmd_status(args) -> int:
    print(status_text(Path(args.source), Path(args.build)))
    return 0


def _cmd_figures(args) -> int:
    S = strings(load_report_config(Path(args.source)).lang)
    result = generate_figures(Path(args.source), Path(args.out), S.lang)
    print(S("fig.summary", created=result["created"],
            real=result["kept_real"],
            placeholder=result["kept_placeholder"]))
    print(f"{S('fig.manifest')}: {result['manifest']}")
    return 0


def _cmd_placeholders(args) -> int:
    import json
    from dataclasses import asdict
    from placeholders import scan_tree, scan_tree_malformed
    root = Path(args.source)
    payload = {
        "placeholders": [asdict(p) for p in scan_tree(root)],
        "malformed": [asdict(m) for m in scan_tree_malformed(root)],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if payload["malformed"] else 0


def _cmd_guard(args) -> int:
    import json
    if args.stamp:
        path = Path(args.stamp)
        stamp(path)
        print(f"stamp: {path}")
        return 0
    print(json.dumps(classify(Path(args.source)), ensure_ascii=False, indent=2))
    return 0


def _cmd_check(args) -> int:
    from gen_figures import have_pillow
    root = plugin_root()
    src = Path(args.source)
    cfg = load_report_config(src) if src.is_dir() else None
    S = strings(cfg.lang if cfg else None)
    missing, absent = S("check.missing"), S("check.absent")
    print(f"plugin root : {root}")
    print(f"pandoc      : {shutil.which('pandoc') or missing}")
    print(f"pillow      : {'ok' if have_pillow() else 'pip install pillow'}")
    print(f"pdftotext   : {shutil.which('pdftotext') or 'optional — only to '
                                                        'read PDF sources'}")
    # Not needed: the bundle is compiled on Overleaf, not here.
    print(f"pdflatex    : {shutil.which('pdflatex') or 'not needed (Overleaf)'}")
    print(f"biber       : {shutil.which('biber') or 'not needed (Overleaf)'}")
    if cfg:
        print(f"report.yaml : type={cfg.type} skeleton={cfg.skeleton} "
              f"lang={cfg.lang}")
    return 0 if shutil.which("pandoc") else 1


def main() -> int:
    ap = argparse.ArgumentParser(prog="claude-report")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("review")
    p.add_argument("source", nargs="?", default="reports_docs")
    p.add_argument("--json", action="store_true")
    p.add_argument("--fix", action="store_true")
    p.set_defaults(func=_cmd_review)

    p = sub.add_parser("build")
    p.add_argument("source", nargs="?", default="reports_docs")
    p.add_argument("out", nargs="?", default="build")
    p.add_argument("--out", dest="out_opt", default=None)
    p.add_argument("--allow-todo", action="store_true")
    p.add_argument("--compile", dest="compile_pdf", action="store_true")
    p.add_argument("--no-compile", action="store_true")   # default; kept for compat
    p.set_defaults(func=_cmd_build)

    p = sub.add_parser("sources")
    p.add_argument("source", nargs="?", default="reports_docs")
    p.add_argument("--no-extract", action="store_true")
    p.set_defaults(func=_cmd_sources)

    p = sub.add_parser("gaps")
    p.add_argument("source", nargs="?", default="reports_docs")
    p.set_defaults(func=_cmd_gaps)

    p = sub.add_parser("status")
    p.add_argument("source", nargs="?", default="reports_docs")
    p.add_argument("--build", dest="build", default="build")
    p.set_defaults(func=_cmd_status)

    p = sub.add_parser("figures")
    p.add_argument("source", nargs="?", default="reports_docs")
    p.add_argument("out", nargs="?", default="build/figures")
    p.set_defaults(func=_cmd_figures)

    p = sub.add_parser("placeholders")
    p.add_argument("source", nargs="?", default="reports_docs")
    p.set_defaults(func=_cmd_placeholders)

    p = sub.add_parser("guard")
    p.add_argument("source", nargs="?", default="reports_docs")
    p.add_argument("--stamp", metavar="FILE")
    p.set_defaults(func=_cmd_guard)

    p = sub.add_parser("check")
    p.add_argument("source", nargs="?", default="reports_docs")
    p.set_defaults(func=_cmd_check)

    args = ap.parse_args()
    try:
        return args.func(args)
    except RuntimeError as exc:
        # Missing optional dependency (Pillow) — a one-line cause beats a
        # traceback the student has to read past.
        print(f"claude-report: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
