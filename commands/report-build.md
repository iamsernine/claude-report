---
description: Generate the Overleaf-ready LaTeX bundle from the confirmed markdown
argument-hint: "[--allow-todo] [--out build]"
allowed-tools: Read, Glob, Bash, Write
---

Turn the confirmed `reports_docs/` markdown into a LaTeX bundle the user uploads
to Overleaf.

**No PDF is produced on this machine, and that is deliberate.** Overleaf owns
compilation. Never install a TeX distribution, never run `pdflatex` to "check",
and never offer a local PDF as a convenience — the deliverable is `build/`.

## Arguments

`$ARGUMENTS`

- `--allow-todo` — build despite unresolved `[[METRIC]]` / `[[TODO]]`
  placeholders. They render in red and the PDF is watermarked as a draft.
- `--out` — output directory, default `build/`.

## Plugin root

Scripts live **in this plugin**, never in the student's repository — do not run
`python3 scripts/cli.py` from the project cwd. `$CLAUDE_PLUGIN_ROOT` is set for you on a
correctly installed plugin; the fallback line covers a manual install. If `$CR`
is empty, the plugin is not installed — say so and stop rather than guessing.

```bash
CR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/claude-report}/scripts/cli.py"
[ -f "$CR" ] || CR=$(ls -1 "$HOME"/.claude/{plugins,skills}/claude-report/scripts/cli.py "$HOME"/.claude/plugins/cache/*/claude-report/*/scripts/cli.py 2>/dev/null | head -1)
CRROOT=$(dirname "$(dirname "$CR")")
```

## Steps

**1. Confirm the markdown is signed off.** This command is the end of the
pipeline, not part of drafting. If the user has not reviewed the markdown, say
so and offer `/report:review` first — regenerating LaTeX from unreviewed prose
wastes their Overleaf round-trip.

**2. Review first.**

```bash
python3 "$CR" review reports_docs
```

If it reports blocking problems, tell the user **before** building, not after.

**3. Build.**

```bash
python3 "$CR" build reports_docs build $ARGUMENTS
```

This generates grey placeholder PNGs for every `[[FIG:]]` (stamped so they are
distinguishable from real screenshots), converts markdown to LaTeX via pandoc
(`--top-level-division=section`), expands typed placeholders, **merges** new
citation stubs into `references.bib` without deleting keys the student already
filled, writes `titlepage.tex` with cover labels in the report's language, and
packs everything into `build/overleaf.zip`.

The build **refuses** while `[[METRIC]]` or `[[TODO]]` remain. This is
deliberate: a report that ships with an invented metric is worse than one that
does not build.

Introduction, conclusion and annexes are emitted as `\chapter*`, so Chapter 1 in
the PDF is the first real chapter, matching the markdown plan.

## Reporting

Give the user:

- The path to `build/overleaf.zip` and to `build/`
- Estimated page count against the target budget in `report.yaml`
- **The figure shopping list** from `build/figures/MANIFEST.md` — each figure is
  `placeholder`, `provided` or `missing`
- Citations still to source, from `build/citations-needed.md`
- These Overleaf instructions, verbatim:

  > Upload `build/overleaf.zip` to Overleaf (New Project → Upload Project). Set
  > the compiler to **pdfLaTeX** and the bibliography tool to **Biber**
  > (Menu → Settings). To insert a real image, replace `figures/<slug>.png` with
  > your own file **keeping the same filename** — no LaTeX edit is needed. Cover
  > logos go in `figures/logo-institution.png` and `figures/logo-host.png`.

If the user reports a compilation error from Overleaf, fix it **in the markdown**
and rebuild. Never tell them to hand-edit `build/main.tex`; it is regenerated on
every run. The one file they may edit directly is `references.bib`, which the
build merges rather than overwrites.
