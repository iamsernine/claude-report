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

## Plugin root — mandatory

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}"
if [ -z "$ROOT" ] || [ ! -f "$ROOT/scripts/cli.py" ]; then
  for cand in \
    "$HOME/.claude/plugins/claude-report" \
    "$HOME/.claude/plugins/pfe-report-skeletons"; do
    [ -f "$cand/scripts/cli.py" ] && ROOT="$cand" && break
  done
fi
```

## Steps

**1. Review first.**

```bash
python3 "$ROOT/scripts/cli.py" review reports_docs
```

If it reports blocking problems, tell the user before building rather than after.

**2. Build.** Forward the user's flags (`--allow-todo`, `--no-compile`). Example:

```bash
python3 "$ROOT/scripts/cli.py" build reports_docs build $ARGUMENTS
```

This generates grey placeholder PNGs for every `[[FIG:]]` (stamped so they are
distinguishable from real screenshots), converts markdown to LaTeX via pandoc
(`--top-level-division=section`), expands typed placeholders, **merges** new
citation stubs into `references.bib` without deleting keys the student already
filled, writes `titlepage.tex`, and runs pdflatex three times.

The build **refuses** while `[[METRIC]]` or `[[TODO]]` remain. This is deliberate:
a report that ships with an invented metric is worse than one that does not
build.

Introduction, conclusion and annexes are emitted as `\chapter*` so Chapitre 1
in the PDF is the first real chapter, matching the markdown plan.

**3. If compilation fails,** read `build/main.log`, find lines starting with `!`,
and fix the generated LaTeX **at its source in the markdown** — never by editing
`build/main.tex`, which is regenerated on every run.

## Reporting

Give the user:

- Path to `build/main.pdf` and its page count against the target budget
- **The figure shopping list** from `build/figures/MANIFEST.md` — état is
  `placeholder`, `fourni` or `manquant`
- Citations still to source, from `build/citations-needed.md`
- Overleaf instructions:

  > Upload the whole `build/` folder to Overleaf. Set the compiler to pdfLaTeX
  > and the bibliography tool to Biber (Menu → Settings). To insert a real image,
  > replace `figures/<slug>.png` with your own file **keeping the same filename** —
  > no LaTeX edit is needed. Cover logos: `figures/logo-institution.png` and
  > `figures/logo-host.png`.

Never tell the user to hand-edit `build/main.tex`. It is generated output.
