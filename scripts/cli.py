#!/usr/bin/env python3
"""Unified entry point for plugin commands.

Always invoke this file from the plugin root, never from the student's
project as ``python3 scripts/cli.py`` unless CLAUDE_PLUGIN_ROOT is set::

    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" review reports_docs
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" build reports_docs build --allow-todo
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
                 allow_todo=args.allow_todo, no_compile=args.no_compile)


def _cmd_status(args) -> int:
    print(status_text(Path(args.source), Path(args.build)))
    return 0


def _cmd_figures(args) -> int:
    result = generate_figures(Path(args.source), Path(args.out))
    print(
        f"figures: {result['created']} créé(s), "
        f"{result['kept_real']} réelle(s), "
        f"{result['kept_placeholder']} placeholder(s)"
    )
    print(f"manifeste: {result['manifest']}")
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
    root = plugin_root()
    print(f"plugin root : {root}")
    print(f"pandoc      : {shutil.which('pandoc') or 'MANQUANT — installer pandoc'}")
    print(f"pdflatex    : {shutil.which('pdflatex') or 'absent (Overleaf possible)'}")
    print(f"biber       : {shutil.which('biber') or 'absent (Overleaf possible)'}")
    src = Path(args.source)
    if src.is_dir():
        cfg = load_report_config(src)
        print(f"report.yaml : type={cfg.type} skeleton={cfg.skeleton}")
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
    p.add_argument("--no-compile", action="store_true")
    p.set_defaults(func=_cmd_build)

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
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
