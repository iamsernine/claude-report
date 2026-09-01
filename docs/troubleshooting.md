# Troubleshooting

## The build refuses

```
BLOQUÉ — 4 placeholder(s) METRIC/TODO non résolu(s)
```

Working as designed. `[[METRIC]]` and `[[TODO]]` mark facts only you can supply.
Fill them, or pass `--allow-todo` for a watermarked draft PDF.

## Commands cannot find `scripts/review.py`

The scripts live in the **plugin**, not in your project. Commands must call
`python3 "$CLAUDE_PLUGIN_ROOT/scripts/cli.py" …`. If you cloned the plugin to
`~/.claude/plugins/claude-report`, that path works as a fallback.

```bash
python3 ~/.claude/plugins/claude-report/scripts/cli.py check
```

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

## pandoc is missing

The build still runs, with a warning. Only headings are converted; lists, tables
and quotes will be raw markdown in the PDF. Install pandoc:

```bash
sudo apt install pandoc        # Debian/Fedora: dnf install pandoc
brew install pandoc            # macOS
```

## My bibliography was deleted on rebuild

That was a bug in 0.1. Rebuild now **merges**: existing keys (including real
`@article{…}` entries you typed) are kept; only missing cite keys get a stub.
Fill `references.bib` with real entries using the same keys as
`[[CITE: key | …]]`.

## Chapitre 1 in the PDF is the introduction

Set `kind: intro` and `numbered: false` on `03-introduction-generale` in
`report.yaml` (and `kind: conclusion` / `kind: annex` likewise). Init writes
this. If you still have the 0.1 yaml short-form only, add those keys.

## `/report:draft` skipped every file after an upgrade

Existing markdown without a `.generated` sidecar is treated as student-owned.
Stamp files you still want regenerated, or pass `--force`:

```bash
python3 "$CLAUDE_PLUGIN_ROOT/scripts/cli.py" guard --stamp reports_docs/04-x/01.md
```

## `/report:draft` overwrote my edits

It checks a SHA-256 sidecar (`*.md.generated`) **and** `git status`. Untracked
edits are protected. **Commit your report directory anyway.** If you lost work
and the directory was tracked, `git checkout` recovers it.

## A figure's MANIFEST line says `placeholder` after I replaced the PNG

The PNG was not written as a real image (export failed, or you kept the grey
file). The detector looks for a PNG text chunk `claude-report=placeholder`.
Export a screenshot, replace `build/figures/<slug>.png` keeping the name,
rebuild. The line should become `fourni`.

## The generated LaTeX has an error I cannot fix from markdown

Read `build/main.log`, find the first line starting with `!`, and trace it back to
the source markdown. Do not fix it in `build/main.tex` — that file is regenerated
on every build and your edit will vanish. If the problem is genuinely in the
conversion, the escape hatch is raw LaTeX in the markdown.

## Overleaf compiles but the table of contents is empty

Compile twice. LaTeX needs a second pass to resolve the TOC, and a third for
cross-references. The local build does three passes automatically.
