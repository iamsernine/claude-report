#!/usr/bin/env python3
"""Protect drafted files from silent overwrite.

A sidecar ``<file>.md.generated`` stores the SHA-256 of the last generated
content. If the markdown hash no longer matches, the student edited it —
``/report:draft`` must skip the file unless ``--force``.

This works even when ``reports_docs/`` is not tracked by git (the previous
guard only looked at ``git status`` and could overwrite untracked edits).

    python3 scripts/draft_guard.py reports_docs
    python3 scripts/draft_guard.py stamp path/to/file.md
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def stamp_path(md: Path) -> Path:
    return md.with_name(md.name + ".generated")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(md: Path) -> None:
    md = Path(md)
    stamp_path(md).write_text(file_hash(md) + "\n", encoding="utf-8")


def git_dirty(root: Path) -> set:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--", str(root)],
            capture_output=True, text=True, check=False,
        )
    except OSError:
        return set()
    dirty = set()
    for line in proc.stdout.splitlines():
        # " M path" / "?? path"
        path = line[3:].strip()
        if path:
            dirty.add(Path(path).name)
            dirty.add(path)
    return dirty


def classify(root: Path) -> Dict[str, List[str]]:
    root = Path(root)
    skip, writable, unstamped = [], [], []
    dirty = git_dirty(root)
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    from paths import is_report_content
    for md in sorted(root.rglob("*.md")):
        if not is_report_content(md, root):
            continue
        if md.name in ("BRIEF.md",) or md.name.endswith(".generated"):
            continue
        rel = str(md.relative_to(root))
        side = stamp_path(md)
        git_hit = rel in dirty or md.name in dirty
        if not side.is_file():
            unstamped.append(rel)
            skip.append(rel)
            continue
        expected = side.read_text(encoding="utf-8").strip()
        actual = file_hash(md)
        if actual != expected or git_hit:
            skip.append(rel)
        else:
            writable.append(rel)
    return {"skip": skip, "writable": writable, "unstamped": unstamped}


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "stamp":
        if len(args) < 2:
            print("usage: draft_guard.py stamp FILE.md", file=sys.stderr)
            return 2
        path = Path(args[1])
        if not path.is_file():
            print(f"error: {path} introuvable", file=sys.stderr)
            return 1
        stamp(path)
        print(f"stamp: {path}")
        return 0
    root = Path(args[0] if args else "reports_docs")
    if not root.is_dir():
        print(f"error: {root} introuvable", file=sys.stderr)
        return 1
    print(json.dumps(classify(root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
