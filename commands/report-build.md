---
description: Generate the LaTeX report and compile it, with grey placeholder images so it builds before any figure exists
argument-hint: "[--allow-todo] [--no-compile] [--out build]"
allowed-tools: Read, Glob, Bash, Write
---

Build `reports_docs/` into a compilable LaTeX report.

## Arguments

`$ARGUMENTS`

- `--allow-todo` — build despite unresolved `[[METRIC]]` and `[[TODO]]`
  placeholders. They are rendered in red and the PDF is watermarked `BROUILLON`.
- `--no-compile` — generate the `.tex` without running pdflatex.
- `--out` — output directory, default `build/`.

## Steps

**1. Review first.** Run `python3 scripts/review.py reports_docs`. If it reports
blocking problems, tell the user before building rather than after.

**2. Build.**

```bash
python3 scripts/build.py reports_docs build
```

This generates grey placeholder PNGs for every `[[FIG:]]`, converts markdown to
LaTeX via pandoc, expands typed placeholders into proper float environments with
labels, writes `references.bib` stubs for every `[[CITE:]]`, and runs pdflatex
three times.

The build **refuses** while `[[METRIC]]` or `[[TODO]]` remain. This is deliberate:
a report that ships with an invented metric is worse than one that does not
build.

**3. If compilation fails,** read `build/main.log`, find lines starting with `!`,
and fix the generated LaTeX **at its source in the markdown** — never by editing
`build/main.tex`, which is regenerated on every run.

## Reporting

Give the user:

- Path to `build/main.pdf` and its page count against the target budget
- **The figure shopping list** from `build/figures/MANIFEST.md` — for each: the
  exact filename to produce, the caption, the chapter, and the minimum pixel
  width
- Citations still to source, from `build/citations-needed.md`
- Overleaf instructions:

  > Upload the whole `build/` folder to Overleaf. Set the compiler to pdfLaTeX
  > and the bibliography tool to Biber (Menu → Settings). To insert a real image,
  > replace `figures/<slug>.png` with your own file **keeping the same filename** —
  > no LaTeX edit is needed.

Never tell the user to hand-edit `build/main.tex`. It is generated output.
