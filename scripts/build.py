#!/usr/bin/env python3
"""Convert the markdown tree into an Overleaf-ready LaTeX bundle.

    python3 scripts/build.py reports_docs build [--allow-todo] [--compile]

Produces build/main.tex, build/figures/, build/references.bib, build/titlepage.tex
and build/overleaf.zip. **No PDF is produced locally by default** — the bundle is
meant to be uploaded to Overleaf, which owns compilation.

`--compile` is an opt-in escape hatch for anyone who happens to have a local TeX
installation; nothing in the workflow depends on it.

The .tex is generated output — never hand-edit it. Fix the markdown and rebuild.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from gen_figures import generate as generate_figures  # noqa: E402
from paths import assets_dir, is_report_content  # noqa: E402
from placeholders import scan_text, scan_tree  # noqa: E402
from report_config import ChapterSpec, ReportConfig, load_report_config  # noqa: E402
from i18n import strings  # noqa: E402

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets" / "latex"

LST_LANG = {
    "python": "Python", "py": "Python",
    "java": "Java",
    "c": "C", "cpp": "C++", "c++": "C++",
    "sql": "SQL",
    "bash": "bash", "sh": "bash",
    "r": "R",
}

BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s}]+)")

# Kept for reference; the authoritative filter is paths.is_report_content.
SKIP_NAMES = {
    "BRIEF.md", "report.yaml", "figures", "cover.yaml", "sources",
}


# --------------------------------------------------------------------------
# placeholder -> LaTeX
# --------------------------------------------------------------------------

def expand(text: str, allow_todo: bool, cites: list,
           source: str = "", kinds: Optional[dict] = None,
           S=None) -> str:
    kinds = kinds if kinds is not None else {}
    S = S or strings()

    def repl(m):
        raw = m.group(0)
        items = scan_text(raw)
        if not items:
            return raw
        p = items[0]

        if p.kind == "FIG":
            w = p.options.get("width", "0.8")
            return (
                "\n\\begin{figure}[H]\n\\centering\n"
                f"\\includegraphics[width={w}\\textwidth]"
                f"{{figures/{p.slug}}}\n"
                f"\\caption{{{tex_escape(p.caption)}}}\n"
                f"\\label{{fig:{p.slug}}}\n\\end{{figure}}\n")

        if p.kind == "TAB":
            return (
                "\n\\begin{table}[H]\n\\centering\n"
                f"\\caption{{{tex_escape(p.caption)}}}\n"
                f"\\label{{tab:{p.slug}}}\n"
                "\\begin{tabular}{ll}\n\\hline\n"
                f"{tex_escape(S('tex.table_col_a'))} & "
                f"{tex_escape(S('tex.table_col_b'))} \\\\\n\\hline\n"
                "\\multicolumn{2}{l}{\\textcolor{red}{\\textit{"
                f"{tex_escape(S('tex.table_empty'))}}}}} \\\\"
                "\n\\hline\n\\end{tabular}\n\\end{table}\n")

        if p.kind == "CODE":
            lang = LST_LANG.get(p.options.get("lang", "").lower())
            lang_opt = f"language={lang}," if lang else ""
            return (
                f"\n\\begin{{lstlisting}}[{lang_opt}"
                f"caption={{{tex_escape(p.caption)}}},label={{lst:{p.slug}}}]\n"
                f"% {S('tex.code_empty')}\n"
                "\\end{lstlisting}\n")

        if p.kind == "EQ":
            return (f"\n\\begin{{equation}}\n\\label{{eq:{p.slug}}}\n"
                    f"% {tex_escape(p.caption)}\n"
                    "\\text{\\textcolor{red}{"
                    f"{tex_escape(S('tex.eq_empty'))}}}"
                    "\n\\end{equation}\n")

        if p.kind == "REF":
            prefix = {"TAB": "tab", "CODE": "lst", "EQ": "eq"}.get(
                kinds.get(p.slug, "FIG"), "fig")
            return f"\\ref{{{prefix}:{p.slug}}}"

        if p.kind == "CITE":
            key = p.slug or "cite"
            if not any(k == key for k, *_ in cites):
                cites.append((key, p.caption, source or p.file))
            return f"\\cite{{{key}}}"

        if p.kind in ("METRIC", "TODO"):
            if allow_todo:
                return (f"\\textcolor{{red}}{{[{p.kind} : "
                        f"{tex_escape(p.caption)}]}}")
            return raw
        return raw

    return re.sub(r"\[\[.*?\]\]", repl, text, flags=re.S)


def tex_escape(s: str) -> str:
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")):
        s = s.replace(a, b)
    return s


def bib_escape(s: str) -> str:
    return (s or "").replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


# --------------------------------------------------------------------------
# bibliography merge — never clobber keys the student already filled
# --------------------------------------------------------------------------

def existing_bib_keys(text: str) -> set:
    return set(BIB_KEY_RE.findall(text or ""))


def merge_bib(path: Path, cites: List[Tuple[str, str, str]], S=None) -> int:
    """Append stubs for new keys only. Returns number of stubs added."""
    S = S or strings()
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    keys = existing_bib_keys(existing)
    if keys <= {"placeholder"}:
        existing = ""
        keys = set()
    added = 0
    chunks = [existing.rstrip()] if existing.strip() else []
    for key, desc, where in cites:
        if key in keys:
            continue
        chunks.append(
            f"@misc{{{key},\n"
            f"  title = {{{bib_escape(desc)}}},\n"
            f"  note = {{{bib_escape(S('bib.to_source', where=where))}}},\n"
            f"  year = {{2026}}\n}}"
        )
        keys.add(key)
        added += 1
    if not chunks:
        path.write_text(
            f"@misc{{placeholder, title={{{bib_escape(S('bib.none'))}}}, "
            "year={2026}}\n",
            encoding="utf-8")
        return 0
    path.write_text("\n\n".join(chunks).strip() + "\n", encoding="utf-8")
    return added


# --------------------------------------------------------------------------
# markdown -> LaTeX
# --------------------------------------------------------------------------

_PANDOC_WARNED = False


def md_to_tex(md: str, S=None) -> str:
    global _PANDOC_WARNED
    S = S or strings()
    if shutil.which("pandoc"):
        proc = subprocess.run(
            ["pandoc", "-f", "markdown+raw_tex", "-t", "latex",
             "--wrap=preserve", "--top-level-division=section"],
            input=md, capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout
        print(f"  pandoc failed, using fallback: {proc.stderr.strip()[:120]}",
              file=sys.stderr)
    elif not _PANDOC_WARNED:
        print(S("build.no_pandoc"), file=sys.stderr)
        _PANDOC_WARNED = True
    return _fallback(md)


def _fallback(md: str) -> str:
    out = []
    for line in md.splitlines():
        stripped = line.strip()
        if stripped.startswith(("\\begin{", "\\end{", "\\input{", "\\[")):
            out.append(line)
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            title = line.lstrip("#").strip()
            cmd = {1: "section", 2: "subsection", 3: "subsubsection"}.get(level)
            out.append(f"\\{cmd}{{{title}}}" if cmd else title)
        else:
            out.append(line)
    return "\n".join(out)


def strip_matching_h1(text: str, title: str) -> str:
    m = re.search(r"^#\s+(.*)$", text, re.M)
    if m and m.group(1).strip() == title:
        return re.sub(r"^#\s+.*$", "", text, count=1, flags=re.M)
    return text


# --------------------------------------------------------------------------
# tree
# --------------------------------------------------------------------------

def iter_items(root: Path):
    for item in sorted(root.iterdir()):
        if not is_report_content(item, root):
            continue
        if item.is_file() and item.suffix == ".md":
            yield item
        elif item.is_dir():
            yield item


KIND_ORDER = {"front": 0, "intro": 1, "chapter": 2, "conclusion": 3, "annex": 4}


def classify(item: Path, cfg: ReportConfig) -> ChapterSpec:
    return cfg.spec_for(item.name if item.is_dir() else item.stem)


def chapter_heading(spec: ChapterSpec) -> str:
    title = spec.display_title()
    escaped = tex_escape(title)
    if spec.is_numbered():
        return f"\n\\chapter{{{escaped}}}\n"
    return (
        f"\n\\chapter*{{{escaped}}}\n"
        f"\\addcontentsline{{toc}}{{chapter}}{{{escaped}}}\n"
        f"\\markboth{{{escaped}}}{{{escaped}}}\n"
    )


def convert_item(item: Path, spec: ChapterSpec, root: Path,
                 allow_todo: bool, cites: list, kinds: dict, S=None) -> str:
    S = S or strings()
    parts = [chapter_heading(spec)] if spec.kind != "front" else []
    mds = [item] if item.is_file() else sorted(
        p for p in item.rglob("*.md") if is_report_content(p, root))
    title = spec.display_title()
    for i, md in enumerate(mds):
        text = md.read_text(encoding="utf-8")
        if spec.kind != "front" and i == 0:
            text = strip_matching_h1(text, title)
        rel = str(md.relative_to(root))
        parts.append(md_to_tex(
            expand(text, allow_todo, cites, rel, kinds, S), S))
    return "\n".join(parts)


def cover_macros(cfg: ReportConfig, S=None) -> str:
    S = S or strings(cfg.lang)

    def cmd(name: str, value: Optional[str]) -> str:
        body = tex_escape(value) if value else tex_escape(S("cover.to_complete"))
        return f"\\providecommand{{\\{name}}}{{{body}}}\n"

    values = (
        cmd("reporttitle", cfg.title)
        + cmd("reportauthor", cfg.author)
        + cmd("reportinstitution", cfg.institution)
        + cmd("reportyear", cfg.year)
        + cmd("reportdegree", cfg.degree)
        + cmd("reportsupervisor", cfg.supervisor)
        + cmd("reporttype", cfg.type.upper() if cfg.type else None)
    )
    # Cover labels follow the report language, so the same titlepage.tex
    # renders correctly in every locale.
    labels = "".join(
        f"\\providecommand{{\\{macro}}}{{{tex_escape(S(key))}}}\n"
        for macro, key in (
            ("coverreportof", "cover.report_of"),
            ("coveracademicyear", "cover.academic_year"),
            ("coverpreparedby", "cover.prepared_by"),
            ("coversupervisedby", "cover.supervised_by"),
            ("coverinstitutionlogo", "cover.institution_logo"),
            ("coverhostlogo", "cover.host_logo"),
        )
    )
    return values + labels


def language_package(lang: str) -> str:
    """The babel line for this locale. One mechanism, no per-language branch
    anywhere else in the build."""
    return "\\usepackage[%s]{babel}" % strings(lang)("babel")


# --------------------------------------------------------------------------

def make_zip(out: Path) -> Path:
    """Bundle everything Overleaf needs into one uploadable archive."""
    archive = out / "overleaf.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(out.rglob("*")):
            if not path.is_file() or path == archive:
                continue
            # build artefacts from an opt-in local compile do not belong in it
            if path.suffix in {".aux", ".bbl", ".blg", ".log", ".out",
                               ".toc", ".lof", ".lot", ".synctex.gz", ".pdf"}:
                continue
            zf.write(path, path.relative_to(out))
    return archive


def build(source: Path, out: Path, allow_todo: bool = False,
          no_compile: bool = True, compile_pdf: bool = False) -> int:
    root, out = Path(source), Path(out)
    if not root.is_dir():
        print(strings()("build.not_found", path=root), file=sys.stderr)
        return 1

    cfg = load_report_config(root)
    S = strings(cfg.lang)
    blocking = [p for p in scan_tree(root) if p.blocking]
    if blocking and not allow_todo:
        print(S("build.blocked", n=len(blocking)) + "\n")
        for p in blocking[:15]:
            print(f"  {p.file}:{p.line}  [[{p.kind}]] {p.caption}")
        if len(blocking) > 15:
            print(S("build.and_more", n=len(blocking) - 15))
        print("\n" + S("build.blocked_hint"))
        return 1

    out.mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(exist_ok=True)
    generate_figures(root, out / "figures", cfg.lang)

    titlepage_src = ASSETS / "titlepage.tex"
    if not titlepage_src.is_file():
        titlepage_src = assets_dir() / "latex" / "titlepage.tex"
    if titlepage_src.is_file():
        shutil.copy(titlepage_src, out / "titlepage.tex")

    cites: list = []
    kinds = {p.slug: p.kind for p in scan_tree(root)
             if p.kind in ("FIG", "TAB", "CODE", "EQ")}

    grouped: Dict[str, list] = {k: [] for k in KIND_ORDER}
    for item in iter_items(root):
        spec = classify(item, cfg)
        grouped.setdefault(spec.kind, []).append((item, spec))

    def emit(kind: str) -> List[str]:
        blocks = []
        for item, spec in grouped.get(kind, []):
            blocks.append(convert_item(
                item, spec, root, allow_todo, cites, kinds, S))
        return blocks

    preamble_path = ASSETS / "preamble.tex"
    preamble = preamble_path.read_text(encoding="utf-8")
    if "%%LANG%%" in preamble:
        preamble = preamble.replace("%%LANG%%", language_package(cfg.lang))
    draft = ("\\IfFileExists{draftwatermark.sty}{\\usepackage{draftwatermark}"
             f"\\SetWatermarkText{{{tex_escape(S('tex.watermark'))}}}"
             "\\SetWatermarkScale{0.7}}{}\n"
             if allow_todo else "")

    biblio = "\n\\printbibliography\n"
    body = (
        preamble.replace("%%DRAFT%%", draft + cover_macros(cfg, S))
        + "\n\\begin{document}\n"
        + "\\pagenumbering{roman}\n"
        + "\n".join(emit("front"))
        + "\n\\tableofcontents\n\\listoffigures\n\\listoftables\n"
        + "\\clearpage\\pagenumbering{arabic}\n"
        + "\n".join(emit("intro"))
        + "\n".join(emit("chapter"))
        + "\n".join(emit("conclusion"))
    )
    if cfg.biblio_position != "after_annexes":
        body += biblio
    body += "\n".join(emit("annex"))
    if cfg.biblio_position == "after_annexes":
        body += biblio
    body += "\\end{document}\n"

    (out / "main.tex").write_text(body, encoding="utf-8")

    added = merge_bib(out / "references.bib", cites, S)
    if cites:
        lines = [S("build.citations_title"), ""]
        lines += [f"- `{k}` — {d}  \n  *({S('build.cited_in')} {w})*"
                  for k, d, w in cites]
        (out / "citations-needed.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8")

    archive = make_zip(out)

    print("\n" + S("build.written", path=out / "main.tex"))
    print(S("build.bundle", path=out))
    print(S("build.zip", path=archive))
    print(S("build.citations", n=len(cites), added=added))
    print("\n" + S("build.overleaf"))

    if not compile_pdf:
        print(S("build.no_local_pdf"))
        return 0
    if not shutil.which("pdflatex"):
        print(S("build.no_pdflatex"))
        return 0

    bibtool = "biber" if shutil.which("biber") else None
    if bibtool is None:
        print(S("build.no_biber"))
    for i in range(3):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"],
                       cwd=out, capture_output=True, text=True)
        if i == 0 and bibtool:
            subprocess.run([bibtool, "main"], cwd=out,
                           capture_output=True, text=True)
    pdf = out / "main.pdf"
    if pdf.exists():
        print(S("build.pdf", path=pdf))
    else:
        log = out / "main.log"
        errs = [l for l in log.read_text(errors="ignore").splitlines()
                if l.startswith("!")][:5] if log.exists() else []
        print(S("build.compile_failed"))
        for e in errs:
            print(f"  {e}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", default="reports_docs")
    ap.add_argument("out", nargs="?", default="build")
    ap.add_argument("--allow-todo", action="store_true")
    ap.add_argument("--compile", dest="compile_pdf", action="store_true",
                    help="opt in to a local pdflatex run (not needed for "
                         "Overleaf)")
    ap.add_argument("--no-compile", action="store_true",
                    help="accepted for compatibility; this is the default")
    args = ap.parse_args()
    return build(Path(args.source), Path(args.out),
                 allow_todo=args.allow_todo, compile_pdf=args.compile_pdf)


if __name__ == "__main__":
    raise SystemExit(main())
