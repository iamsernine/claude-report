# Troubleshooting

## The build refuses

```
BLOQUÉ — 4 placeholder(s) METRIC/TODO non résolu(s)
```

Working as designed. `[[METRIC]]` and `[[TODO]]` mark facts only you can supply.
Fill them, or pass `--allow-todo` for a watermarked draft PDF.

## `pdflatex: command not found`

You have no local TeX distribution. The plugin still writes `build/`. Upload that
folder to Overleaf and compile there.

To install locally: `sudo apt install texlive-full` (Debian/Ubuntu), MiKTeX on
Windows, MacTeX on macOS. `texlive-full` is ~5 GB; `texlive-latex-extra
texlive-lang-french texlive-bibtex-extra biber` is enough and much smaller.

## `Package babel Error: Unknown option 'french'`

Missing French language support:

```bash
sudo apt install texlive-lang-french
```

Overleaf has it by default.

## `biber introuvable`

The bibliography will not resolve locally, but the PDF still builds with `[?]`
citation marks. Install `biber`, or compile in Overleaf with Bibliography Tool set
to Biber (Menu → Settings).

## Accents render as `Ã©`

The markdown file is not UTF-8. Re-save it as UTF-8 without BOM. All scripts read
and write UTF-8 exclusively.

## pandoc turns my table into something strange

Pandoc handles pipe tables well and grid tables poorly. Use pipe tables. For a
table you need precise control over, write the LaTeX directly in the markdown —
pandoc is invoked with `markdown+raw_tex`, so `\begin{tabular}` blocks pass
through untouched.

## A figure does not appear

Check three things in order:

1. `build/figures/<slug>.png` exists — the slug in the filename must match the
   slug in `[[FIG:]]` exactly, lowercase and hyphenated.
2. The extension is `.png`. The build emits `\includegraphics{figures/<slug>}`
   without an extension, so `.pdf` and `.jpg` also work, but if two files share
   the slug LaTeX picks unpredictably. Keep one.
3. You rebuilt after replacing the file.

## My real image was overwritten by a placeholder

It was not — `gen_figures.py` never overwrites an existing file. If you see a grey
box, the filename does not match the slug. Check `build/figures/MANIFEST.md` for
the exact expected name.

## `/report:review` says my état de l'art has no positioning

It looks for a comparison table (a markdown table or a `[[TAB:]]`) together with
wording about positioning or a gap. If you have both and it still fires, the
detection is keyword-based — add an explicit "Positionnement" subsection heading.

If you genuinely do not have one, that is the finding, and it is the most common
weakness in AI-track reports.

## Proportion warnings on a short draft

Suppressed below roughly 8 pages of body text — there is not enough material to
judge. They activate as the draft grows.

## Claude drafted something factually wrong about my company

It should not have. Check whether the fact was in `BRIEF.md` — if it was absent
and got written anyway, that is a bug worth reporting. If it was in the brief and
was wrong there, fix the brief and rerun `/report:draft --chapter N`.

## `/report:draft` overwrote my edits

It checks `git status` and skips modified files, but only if `reports_docs/` is
tracked. **Commit your report directory.** If you lost work and the directory was
tracked, `git checkout` recovers it.

## The generated LaTeX has an error I cannot fix from markdown

Read `build/main.log`, find the first line starting with `!`, and trace it back to
the source markdown. Do not fix it in `build/main.tex` — that file is regenerated
on every build and your edit will vanish. If the problem is genuinely in the
conversion, the escape hatch is raw LaTeX in the markdown.

## Overleaf compiles but the table of contents is empty

Compile twice. LaTeX needs a second pass to resolve the TOC, and a third for
cross-references. The local build does three passes automatically.
