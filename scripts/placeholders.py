#!/usr/bin/env python3
"""Parse typed placeholders out of the report markdown tree.

Shared by review.py and build.py. Run directly to dump a JSON inventory:

    python3 scripts/placeholders.py reports_docs
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

KINDS = ("FIG", "TAB", "CODE", "EQ", "CITE", "METRIC", "TODO", "REF")
BLOCKING = ("METRIC", "TODO")

PATTERN = re.compile(
    r"\[\[\s*(" + "|".join(KINDS) + r")\s*:\s*(.*?)\s*\]\]", re.S)
ANY_PLACEHOLDER = re.compile(r"\[\[(.*?)\]\]", re.S)
CITE_KEY_RE = re.compile(r"^[\w.:-]+$")


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


@dataclass
class Malformed:
    file: str
    line: int
    raw: str


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text


def _parse_body(kind: str, body: str) -> Tuple[str, str, dict]:
    """Split 'slug | caption | k=v, k=v' into its parts."""
    parts = [p.strip() for p in body.split("|")]
    options: Dict[str, str] = {}

    if kind == "CITE":
        if (len(parts) >= 2 and parts[0] and CITE_KEY_RE.fullmatch(parts[0])
                and " " not in parts[0]):
            return parts[0], parts[1], options
        desc = body.strip()
        key = slugify(desc)[:60] or "cite"
        return key, desc, options

    if kind in ("METRIC", "TODO"):
        return "", parts[0], options

    if kind == "REF":
        return parts[0], "", options

    slug = slugify(parts[0]) if parts[0] else ""
    caption = parts[1] if len(parts) > 1 else ""
    if len(parts) > 2:
        for opt in parts[2].split(","):
            if "=" in opt:
                k, v = opt.split("=", 1)
                options[k.strip()] = v.strip()
    return slug, caption, options


def scan_text(text: str, filename: str = "<string>") -> List[Placeholder]:
    found = []
    for m in PATTERN.finditer(text):
        kind, body = m.group(1), m.group(2)
        slug, caption, options = _parse_body(kind, body)
        line = text.count("\n", 0, m.start()) + 1
        found.append(Placeholder(kind, slug, caption, options, filename, line))
    return found


def scan_malformed(text: str, filename: str = "<string>") -> List[Malformed]:
    """Placeholders that look like [[...]] but do not match a known kind."""
    issues = []
    for m in ANY_PLACEHOLDER.finditer(text):
        raw = m.group(0)
        if PATTERN.fullmatch(raw):
            continue
        line = text.count("\n", 0, m.start()) + 1
        issues.append(Malformed(filename, line, raw.replace("\n", " ")[:80]))
    return issues


def scan_tree(root: Path) -> List[Placeholder]:
    found = []
    for md in _md_files(root):
        rel = str(md.relative_to(root))
        found.extend(scan_text(md.read_text(encoding="utf-8"), rel))
    return found


def scan_tree_malformed(root: Path) -> List[Malformed]:
    found = []
    for md in _md_files(root):
        rel = str(md.relative_to(root))
        found.extend(scan_malformed(md.read_text(encoding="utf-8"), rel))
    return found


def _md_files(root: Path):
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from paths import is_report_content
    root = Path(root)
    for md in sorted(root.rglob("*.md")):
        if not is_report_content(md, root):
            continue
        if md.name.endswith(".generated"):
            continue
        yield md


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "reports_docs")
    if not root.is_dir():
        print(f"error: {root} not found", file=sys.stderr)
        return 1
    items = scan_tree(root)
    bad = scan_tree_malformed(root)
    payload = {
        "placeholders": [asdict(p) for p in items],
        "malformed": [asdict(m) for m in bad],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
