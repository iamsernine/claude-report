#!/usr/bin/env python3
"""Parse typed placeholders out of the report markdown tree.

Shared by review.py and build.py. Run directly to dump a JSON inventory:

    python3 scripts/placeholders.py reports_docs
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

KINDS = ("FIG", "TAB", "CODE", "EQ", "CITE", "METRIC", "TODO", "REF")
BLOCKING = ("METRIC", "TODO")

PATTERN = re.compile(r"\[\[\s*(" + "|".join(KINDS) + r")\s*:\s*(.*?)\s*\]\]", re.S)


@dataclass
class Placeholder:
    kind: str
    slug: str
    caption: str
    options: dict
    file: str
    line: int

    @property
    def blocking(self) -> bool:
        return self.kind in BLOCKING


def _parse_body(kind: str, body: str) -> tuple[str, str, dict]:
    """Split 'slug | caption | k=v, k=v' into its parts."""
    parts = [p.strip() for p in body.split("|")]
    options: dict = {}

    if kind in ("CITE", "METRIC", "TODO"):
        return "", parts[0], options

    if kind == "REF":
        return parts[0], "", options

    slug = parts[0]
    caption = parts[1] if len(parts) > 1 else ""
    if len(parts) > 2:
        for opt in parts[2].split(","):
            if "=" in opt:
                k, v = opt.split("=", 1)
                options[k.strip()] = v.strip()
    return slug, caption, options


def scan_text(text: str, filename: str = "<string>") -> list[Placeholder]:
    found = []
    for m in PATTERN.finditer(text):
        kind, body = m.group(1), m.group(2)
        slug, caption, options = _parse_body(kind, body)
        line = text.count("\n", 0, m.start()) + 1
        found.append(Placeholder(kind, slug, caption, options, filename, line))
    return found


def scan_tree(root: Path) -> list[Placeholder]:
    found = []
    for md in sorted(root.rglob("*.md")):
        if md.name in ("BRIEF.md", "MANIFEST.md", "citations-needed.md"):
            continue
        rel = str(md.relative_to(root))
        found.extend(scan_text(md.read_text(encoding="utf-8"), rel))
    return found


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "reports_docs")
    if not root.is_dir():
        print(f"error: {root} not found", file=sys.stderr)
        return 1
    items = scan_tree(root)
    print(json.dumps([asdict(p) for p in items], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
