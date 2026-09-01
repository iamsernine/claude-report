#!/usr/bin/env python3
"""Load reports_docs/report.yaml — the machine-readable report plan.

Supports the original short form::

    chapters:
      01-contexte-general: [7, 9]

and the explicit form::

    chapters:
      01-contexte-et-cadrage:
        title: Contexte et cadrage du projet
        kind: chapter
        numbered: true
        pages: [6, 9]
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

RESEARCH_SKELETONS = frozenset({
    "02-pfe-research-ml",
    "03-pfe-data-cloud-deployment",
})

# Filename hints used when yaml has no `kind`
_KIND_HINTS = (
    ("front", ("page-de-garde", "dedicace", "remerciement", "resume",
               "abstract", "acronyme", "declaration", "integrite",
               "sommaire")),
    ("intro", ("introduction-generale", "introduction_generale",
               "introduction-generale")),
    ("conclusion", ("conclusion-generale", "conclusion_generale",
                    "conclusion-generale")),
    ("annex", ("annexe", "annexes", "appendix", "appendices")),
)

VALID_TYPES = (
    "pfe", "pfa", "stage-initiation", "stage-technicien", "module", "memoire",
)
VALID_KINDS = ("front", "intro", "chapter", "conclusion", "annex")


@dataclass
class ChapterSpec:
    key: str
    title: Optional[str] = None
    kind: str = "chapter"
    numbered: Optional[bool] = None
    pages: Optional[Tuple[int, int]] = None

    def is_numbered(self) -> bool:
        if self.numbered is not None:
            return self.numbered
        return self.kind == "chapter"

    def display_title(self) -> str:
        if self.title:
            return self.title
        return pretty_title(self.key)


@dataclass
class ReportConfig:
    type: str = "pfe"
    skeleton: str = "01-pfe-software-engineering"
    lang: str = "fr"
    pages_total: int = 60
    words_per_page: int = 350
    biblio_position: str = "before_annexes"
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None
    degree: Optional[str] = None
    supervisor: Optional[str] = None
    chapters: Dict[str, ChapterSpec] = field(default_factory=dict)
    source: Optional[Path] = None

    def spec_for(self, name: str) -> ChapterSpec:
        if name in self.chapters:
            return self.chapters[name]
        stem = Path(name).name
        if stem in self.chapters:
            return self.chapters[stem]
        for key, spec in self.chapters.items():
            if stem.startswith(key) or key.startswith(stem):
                return spec
        kind = infer_kind(stem)
        return ChapterSpec(key=stem, kind=kind)

    def requires_positioning_level(self) -> Optional[str]:
        """Return 'issue', 'warning', or None (skip)."""
        if self.type in ("stage-initiation", "stage-technicien"):
            return None
        if self.type in ("pfa", "module"):
            return "warning"
        return "issue"

    def requires_baseline(self) -> bool:
        if self.type == "memoire":
            return True
        return self.skeleton in RESEARCH_SKELETONS

    def company_share_cap(self) -> Optional[float]:
        if self.type == "stage-initiation":
            return None
        return 0.15


def pretty_title(key: str) -> str:
    text = re.sub(r"^\d+[a-z]?[-_]", "", key)
    return text.replace("-", " ").replace("_", " ").strip()


def infer_kind(name: str) -> str:
    low = name.lower()
    for kind, hints in _KIND_HINTS:
        if any(h in low for h in hints):
            return kind
    return "chapter"


def _strip_comment(line: str) -> str:
    in_s = False
    in_d = False
    out = []
    for ch in line:
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif ch == "#" and not in_s and not in_d:
            break
        out.append(ch)
    return "".join(out).rstrip()


def _parse_scalar(raw: str):
    s = raw.strip()
    if not s:
        return ""
    if s[0] in "\"'" and s[-1] == s[0] and len(s) >= 2:
        return s[1:-1]
    if s in ("true", "True", "yes", "Yes"):
        return True
    if s in ("false", "False", "no", "No"):
        return False
    if s in ("null", "Null", "~", "None"):
        return None
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(p) for p in _split_csv(inner)]
    return s


def _split_csv(inner: str) -> List[str]:
    parts, buf, depth, in_s, in_d = [], [], 0, False, False
    for ch in inner:
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif ch == "[" and not in_s and not in_d:
            depth += 1
        elif ch == "]" and not in_s and not in_d:
            depth -= 1
        if ch == "," and depth == 0 and not in_s and not in_d:
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return parts


def parse_report_yaml(text: str) -> ReportConfig:
    """Parse the documented report.yaml subset. Not a general YAML library."""
    lines = []
    for raw in text.splitlines():
        stripped = _strip_comment(raw)
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.strip()))

    cfg = ReportConfig()
    i = 0
    while i < len(lines):
        indent, content = lines[i]
        if indent != 0 or ":" not in content:
            i += 1
            continue
        key, _, rest = content.partition(":")
        key, rest = key.strip(), rest.strip()
        if key == "chapters":
            chapters, i = _parse_chapters(lines, i + 1)
            cfg.chapters = chapters
            continue
        if rest:
            _assign(cfg, key, _parse_scalar(rest))
        i += 1
    return cfg


def _parse_chapters(lines, start):
    chapters: Dict[str, ChapterSpec] = {}
    i = start
    while i < len(lines):
        indent, content = lines[i]
        if indent == 0:
            break
        if indent != 2 or ":" not in content:
            i += 1
            continue
        key, _, rest = content.partition(":")
        key, rest = key.strip(), rest.strip()
        spec = ChapterSpec(key=key, kind=infer_kind(key))
        if rest:
            val = _parse_scalar(rest)
            if isinstance(val, list) and len(val) >= 2:
                spec.pages = (int(val[0]), int(val[1]))
            elif isinstance(val, str) and val:
                spec.title = val
            chapters[key] = spec
            i += 1
            continue
        i += 1
        while i < len(lines) and lines[i][0] >= 4:
            nindent, ncontent = lines[i]
            if nindent != 4 or ":" not in ncontent:
                i += 1
                continue
            nk, _, nv = ncontent.partition(":")
            nk, nv = nk.strip(), nv.strip()
            parsed = _parse_scalar(nv) if nv else ""
            if nk == "title":
                spec.title = str(parsed)
            elif nk == "kind" and parsed in VALID_KINDS:
                spec.kind = str(parsed)
            elif nk == "numbered":
                spec.numbered = bool(parsed)
            elif nk == "pages" and isinstance(parsed, list) and len(parsed) >= 2:
                spec.pages = (int(parsed[0]), int(parsed[1]))
            i += 1
        chapters[key] = spec
    return chapters, i


def _assign(cfg: ReportConfig, key: str, value) -> None:
    mapping = {
        "type": "type",
        "skeleton": "skeleton",
        "lang": "lang",
        "pages_total": "pages_total",
        "words_per_page": "words_per_page",
        "biblio_position": "biblio_position",
        "period_start": "period_start",
        "period_end": "period_end",
        "title": "title",
        "author": "author",
        "institution": "institution",
        "year": "year",
        "degree": "degree",
        "supervisor": "supervisor",
        "internship_start": "period_start",
        "internship_end": "period_end",
    }
    attr = mapping.get(key)
    if attr is None:
        return
    if attr in ("pages_total", "words_per_page") and not isinstance(value, int):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return
    if attr == "type" and value not in VALID_TYPES:
        pass
    if attr == "biblio_position" and value not in (
            "before_annexes", "after_annexes"):
        value = "before_annexes"
    setattr(cfg, attr, value)


def load_report_config(root: Path) -> ReportConfig:
    path = Path(root) / "report.yaml"
    if not path.is_file():
        cfg = ReportConfig()
        cfg.source = None
        return cfg
    cfg = parse_report_yaml(path.read_text(encoding="utf-8"))
    cfg.source = path
    return cfg
