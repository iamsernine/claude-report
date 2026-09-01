#!/usr/bin/env python3
"""Convert the markdown tree into a compilable LaTeX report.

    python3 scripts/build.py reports_docs build [--allow-todo] [--no-compile]

Produces build/main.tex, build/figures/, build/references.bib and, if pdflatex is
available, build/main.pdf. The .tex is generated output — never hand-edit it.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from placeholders import scan_text, scan_tree  # noqa: E402

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets" / "latex"

FRONT_ORDER = ("00-page-de-garde", "00a-dedicace", "01-remerciements",
               "01b-resume", "01c-abstract", "02-acronymes")


# --------------------------------------------------------------------------
# placeholder -> LaTeX
# --------------------------------------------------------------------------

def expand(text: str, allow_todo: bool, cites: list,
           source: str = "", kinds: dict | None = None) -> str:
    kinds = kinds if kinds is not None else {}
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
                f"\\includegraphics[width={w}\\textwidth]{{figures/{p.slug}}}\n"
                f"\\caption{{{tex_escape(p.caption)}}}\n"
                f"\\label{{fig:{p.slug}}}\n\\end{{figure}}\n")

        if p.kind == "TAB":
            return (
                "\n\\begin{table}[H]\n\\centering\n"
                f"\\caption{{{tex_escape(p.caption)}}}\n"
                f"\\label{{tab:{p.slug}}}\n"
                "\\begin{tabular}{ll}\n\\hline\n"
                "Colonne A & Colonne B \\\\\n\\hline\n"
                "\\multicolumn{2}{l}{\\textit{À compléter}} \\\\\n"
                "\\hline\n\\end{tabular}\n\\end{table}\n")

        if p.kind == "CODE":
            lang = p.options.get("lang", "text")
            return (
                f"\n\\begin{{lstlisting}}[language={lang},"
                f"caption={{{tex_escape(p.caption)}}},label={{lst:{p.slug}}}]\n"
                "% code à insérer\n\\end{lstlisting}\n")

        if p.kind == "EQ":
            return (f"\n\\begin{{equation}}\n\\label{{eq:{p.slug}}}\n"
                    f"% {tex_escape(p.caption)}\n\\end{{equation}}\n")

        if p.kind == "REF":
            prefix = {"TAB": "tab", "CODE": "lst", "EQ": "eq"}.get(
                kinds.get(p.slug, "FIG"), "fig")
            return f"\\ref{{{prefix}:{p.slug}}}"

        if p.kind == "CITE":
            key = f"TODO{len(cites) + 1}"
            cites.append((key, p.caption, source or p.file))
            return f"\\cite{{{key}}}"

        if p.kind in ("METRIC", "TODO"):
            if allow_todo:
                return f"\\textcolor{{red}}{{[{p.kind} : {tex_escape(p.caption)}]}}"
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


# --------------------------------------------------------------------------
# markdown -> LaTeX
# --------------------------------------------------------------------------

def md_to_tex(md: str) -> str:
    if shutil.which("pandoc"):
        proc = subprocess.run(
            ["pandoc", "-f", "markdown+raw_tex", "-t", "latex", "--wrap=preserve"],
            input=md, capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout
        print(f"  pandoc failed, using fallback: {proc.stderr.strip()[:120]}",
              file=sys.stderr)
    return _fallback(md)


def _fallback(md: str) -> str:
    out, in_tex = [], False
    for line in md.splitlines():
        if line.strip().startswith(("\\begin{", "\\end{")):
            in_tex = not line.strip().startswith("\\end{") or in_tex
            out.append(line)
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            title = line.lstrip("#").strip()
            cmd = {2: "section", 3: "subsection", 4: "subsubsection"}.get(level)
            out.append(f"\\{cmd}{{{title}}}" if cmd else title)
        else:
            out.append(line)
    return "\n".join(out)


# --------------------------------------------------------------------------

def collect(root: Path) -> tuple[list, list]:
    front, chapters = [], []
    for item in sorted(root.iterdir()):
        if item.name in ("BRIEF.md", "report.yaml", "figures"):
            continue
        if item.is_file() and item.suffix == ".md":
            (front if any(item.stem.startswith(f[:2]) and f in item.stem
                          for f in FRONT_ORDER) else chapters).append(item)
        elif item.is_dir():
            chapters.append(item)
    return front, chapters


def chapter_title(path: Path) -> str:
    for md in ([path] if path.is_file() else sorted(path.rglob("*.md"))):
        for line in md.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return re.sub(r"^\d+[-_]", "", path.stem).replace("-", " ").title()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", default="reports_docs")
    ap.add_argument("out", nargs="?", default="build")
    ap.add_argument("--allow-todo", action="store_true")
    ap.add_argument("--no-compile", action="store_true")
    args = ap.parse_args()

    root, out = Path(args.source), Path(args.out)
    if not root.is_dir():
        print(f"error: {root} introuvable", file=sys.stderr)
        return 1

    blocking = [p for p in scan_tree(root) if p.blocking]
    if blocking and not args.allow_todo:
        print(f"BLOQUÉ — {len(blocking)} placeholder(s) METRIC/TODO non résolu(s) :\n")
        for p in blocking[:15]:
            print(f"  {p.file}:{p.line}  [[{p.kind}]] {p.caption}")
        if len(blocking) > 15:
            print(f"  … et {len(blocking) - 15} de plus")
        print("\nRenseignez-les, ou relancez avec --allow-todo pour un PDF de brouillon.")
        return 1

    out.mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(exist_ok=True)

    subprocess.run([sys.executable, str(HERE / "gen_figures.py"),
                    str(root), str(out / "figures")], check=False)

    cites: list = []
    kinds = {p.slug: p.kind for p in scan_tree(root)
             if p.kind in ('FIG', 'TAB', 'CODE', 'EQ')}
    front, chapters = collect(root)
    body = []

    for f in front:
        text = expand(f.read_text(encoding="utf-8"), args.allow_todo, cites,
                      str(f.relative_to(root)), kinds)
        body.append(md_to_tex(text))

    for ch in chapters:
        body.append(f"\n\\chapter{{{chapter_title(ch)}}}\n")
        mds = [ch] if ch.is_file() else sorted(ch.rglob("*.md"))
        for md in mds:
            text = md.read_text(encoding="utf-8")
            text = re.sub(r"^#\s+.*$", "", text, count=1, flags=re.M)  # chapter title already emitted
            body.append(md_to_tex(expand(text, args.allow_todo, cites,
                                        str(md.relative_to(root)), kinds)))

    preamble = (ASSETS / "preamble.tex").read_text(encoding="utf-8")
    draft = ("\\IfFileExists{draftwatermark.sty}{\\usepackage{draftwatermark}"
         "\\SetWatermarkText{BROUILLON}\\SetWatermarkScale{0.7}}{}\n"
         if args.allow_todo else "")

    doc = (preamble.replace("%%DRAFT%%", draft)
           + "\n\\begin{document}\n"
           + "\\pagenumbering{roman}\n"
           + "\n".join(body[:len(front)])
           + "\n\\tableofcontents\n\\listoffigures\n\\listoftables\n"
           + "\\clearpage\\pagenumbering{arabic}\n"
           + "\n".join(body[len(front):])
           + "\n\\printbibliography\n\\end{document}\n")

    (out / "main.tex").write_text(doc, encoding="utf-8")

    bib = out / "references.bib"
    entries = [] if bib.exists() else []
    for key, desc, where in cites:
        entries.append(f"@misc{{{key},\n  title = {{{desc}}},\n"
                       f"  note = {{À SOURCER — cité dans {where}}},\n  year = {{2026}}\n}}\n")
    if entries or not bib.exists():
        bib.write_text("\n".join(entries) if entries else
                       "@misc{placeholder, title={Aucune référence}, year={2026}}\n",
                       encoding="utf-8")

    if cites:
        lines = ["# Citations à sourcer", ""]
        lines += [f"- `{k}` — {d}  \n  *(cité dans {w})*" for k, d, w in cites]
        (out / "citations-needed.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nécrit : {out/'main.tex'}")
    print(f"citations à sourcer : {len(cites)}")

    if args.no_compile:
        return 0
    if not shutil.which("pdflatex"):
        print("pdflatex introuvable — compilez main.tex dans Overleaf.")
        return 0

    bibtool = "biber" if shutil.which("biber") else None
    if bibtool is None:
        print("biber introuvable — bibliographie non résolue en local "
              "(Overleaf la résoudra automatiquement).")
    for i in range(3):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"],
                       cwd=out, capture_output=True, text=True)
        if i == 0 and bibtool:
            subprocess.run([bibtool, "main"], cwd=out, capture_output=True, text=True)
    pdf = out / "main.pdf"
    if pdf.exists():
        print(f"PDF : {pdf}")
    else:
        log = (out / "main.log")
        errs = [l for l in log.read_text(errors="ignore").splitlines()
                if l.startswith("!")][:5] if log.exists() else []
        print("compilation échouée :")
        for e in errs:
            print(f"  {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
