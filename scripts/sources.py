#!/usr/bin/env python3
"""Supporting documents the student supplies to fill gaps.

The drafting rule is that nothing may be invented. Everything comes from one of
three places, in this order of preference:

1. **The repository** — stack, architecture, tests, git history. Derivable, so
   it is never asked for.
2. **`reports_docs/BRIEF.md`** — what only the student knows: the host
   organisation, the problem statement, measured results, supervisors.
3. **`reports_docs/sources/`** — a drop folder. When the brief is missing
   something, the student puts the document that contains it here (a PDF of the
   company presentation, a results export, meeting notes, an old report) and
   drafting runs again.

This module inventories that folder and makes PDFs readable, so the loop is:
draft → see what is still missing → drop a file in → draft again.

Text extraction is intentionally dependency-light: `.md`, `.txt`, `.csv` are
read directly; PDFs go through `pdftotext` (poppler) or `pypdf` if either is
present. Anything unreadable is reported as such rather than skipped silently —
a source the drafter cannot read must not look like one it chose to ignore.
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

SOURCES_DIRNAME = "sources"
EXTRACT_DIRNAME = ".extracted"

TEXT_SUFFIXES = {".md", ".markdown", ".txt", ".text", ".csv", ".tsv", ".rst"}
PDF_SUFFIXES = {".pdf"}
OFFICE_SUFFIXES = {".docx", ".doc", ".odt", ".pptx", ".xlsx"}

# Never read these, even if dropped in by accident.
SECRET_NAMES = {".env", ".env.local", ".env.production", "credentials.json",
                "secrets.json", "id_rsa", "id_ed25519", ".npmrc", ".netrc"}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".keystore"}

# The folder's own instructions are not material the report can draw on.
SELF_DOCS = {"readme.md", "readme.txt", "read-me.md", "_readme.md"}


@dataclass
class Source:
    path: Path
    rel: str
    kind: str                     # text | pdf | office | secret | unknown
    bytes: int
    readable: bool = False
    text_path: Optional[Path] = None
    chars: int = 0
    note: str = ""


@dataclass
class Inventory:
    root: Path
    dir: Path
    exists: bool = False
    items: List[Source] = field(default_factory=list)

    @property
    def readable(self) -> List[Source]:
        return [s for s in self.items if s.readable]

    @property
    def unreadable(self) -> List[Source]:
        return [s for s in self.items if not s.readable and s.kind != "secret"]

    @property
    def skipped_secrets(self) -> List[Source]:
        return [s for s in self.items if s.kind == "secret"]


def sources_dir(root: Path) -> Path:
    return Path(root) / SOURCES_DIRNAME


def _classify(path: Path) -> str:
    if path.name in SECRET_NAMES or path.suffix.lower() in SECRET_SUFFIXES:
        return "secret"
    if path.name.startswith(".env"):
        return "secret"
    suffix = path.suffix.lower()
    if suffix in TEXT_SUFFIXES:
        return "text"
    if suffix in PDF_SUFFIXES:
        return "pdf"
    if suffix in OFFICE_SUFFIXES:
        return "office"
    return "unknown"


def _pdf_to_text(src: Path, dest: Path) -> tuple:
    """Return (ok, note). Tries poppler, then pypdf."""
    if shutil.which("pdftotext"):
        proc = subprocess.run(
            ["pdftotext", "-layout", str(src), str(dest)],
            capture_output=True, text=True)
        if proc.returncode == 0 and dest.is_file():
            return True, "pdftotext"
        return False, f"pdftotext failed: {proc.stderr.strip()[:80]}"
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError:
            return False, ("no PDF reader — install poppler-utils "
                           "(pdftotext) or `pip install pypdf`")
    try:
        reader = PdfReader(str(src))
        text = "\n\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:                     # noqa: BLE001 - report, do not crash
        return False, f"unreadable PDF: {type(exc).__name__}"
    if not text.strip():
        return False, "PDF has no extractable text layer (scanned? needs OCR)"
    dest.write_text(text, encoding="utf-8")
    return True, "pypdf"


def collect(root: Path, extract: bool = True) -> Inventory:
    root = Path(root)
    sdir = sources_dir(root)
    inv = Inventory(root=root, dir=sdir, exists=sdir.is_dir())
    if not inv.exists:
        return inv

    outdir = sdir / EXTRACT_DIRNAME
    for path in sorted(sdir.rglob("*")):
        if not path.is_file():
            continue
        if EXTRACT_DIRNAME in path.parts:
            continue
        if path.name.startswith(".") and path.name not in SECRET_NAMES:
            continue
        if path.parent == sdir and path.name.lower() in SELF_DOCS:
            continue
        kind = _classify(path)
        item = Source(path=path, rel=str(path.relative_to(sdir)),
                      kind=kind, bytes=path.stat().st_size)

        if kind == "secret":
            item.note = "skipped — looks like a credential file, never read"
        elif kind == "text":
            item.readable = True
            item.text_path = path
            try:
                item.chars = len(path.read_text(encoding="utf-8",
                                                errors="replace"))
            except OSError as exc:
                item.readable, item.note = False, str(exc)
        elif kind == "pdf":
            dest = outdir / (path.stem + ".txt")
            if not extract:
                item.note = "not extracted"
            elif dest.is_file() and dest.stat().st_mtime >= path.stat().st_mtime:
                item.readable, item.text_path = True, dest
                item.chars = len(dest.read_text(encoding="utf-8",
                                                errors="replace"))
                item.note = "cached"
            else:
                outdir.mkdir(parents=True, exist_ok=True)
                ok, note = _pdf_to_text(path, dest)
                item.note = note
                if ok:
                    item.readable, item.text_path = True, dest
                    item.chars = len(dest.read_text(encoding="utf-8",
                                                    errors="replace"))
        elif kind == "office":
            item.note = ("convert to PDF or Markdown first "
                         "(File → Save as → PDF)")
        else:
            item.note = "unsupported type — convert to .md, .txt or .pdf"
        inv.items.append(item)
    return inv


# ---------------------------------------------------------------------------
# BRIEF.md gaps
# ---------------------------------------------------------------------------

def brief_gaps(root: Path) -> Dict[str, List[str]]:
    """Empty fields in BRIEF.md, grouped by their `##` section.

    A field is `- Label:` with nothing meaningful after the colon. These are
    exactly the things drafting must not invent.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from i18n import is_empty_value

    path = Path(root) / "BRIEF.md"
    if not path.is_file():
        return {}
    gaps: Dict[str, List[str]] = {}
    section = "(no section)"
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            section = stripped[3:].strip()
            continue
        if stripped.startswith("#"):
            continue
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        label, _, value = stripped[2:].partition(":")
        # a trailing HTML comment is guidance, not a value
        value = value.split("<!--")[0].strip()
        if is_empty_value(value) or not value:
            gaps.setdefault(section, []).append(label.strip())
    return gaps
