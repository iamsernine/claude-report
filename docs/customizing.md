# Customizing

## Your school's LaTeX template

`assets/latex/preamble.tex` is the entire visual identity of the output. Replace
it with your own and everything downstream follows.

If you already have a working template — for instance a repository with
`main.tex` and a `pages/` folder — the fastest path is:

1. Copy your preamble (everything before `\begin{document}`) into
   `assets/latex/preamble.tex`.
2. Keep the `%%DRAFT%%` marker on its own line. `build.py` substitutes the draft
   watermark there.
3. Keep `\addbibresource{references.bib}` — the build writes that filename.

The build emits `\chapter{}`, `\section{}`, `figure`, `table`, `lstlisting` and
`equation` environments. Any preamble that styles those will work.

## The cover page

The build treats `reports_docs/00-page-de-garde.md` as ordinary markdown, which
is rarely what you want for a title page. Two options:

**Raw LaTeX in the markdown.** Pandoc is invoked with `markdown+raw_tex`, so a
LaTeX block in `00-page-de-garde.md` passes through untouched:

```latex
\begin{titlepage}
\centering
\includegraphics[width=0.8\textwidth]{LOGOS/enset-header.png}\\[2cm]
{\LARGE\bfseries Titre du projet}\\[1cm]
...
\end{titlepage}
```

**Or keep it in the preamble** as a `\maketitlepage` macro and call it from the
markdown.

Put your logo in `build/figures/` or add a `LOGOS/` folder and reference it
relatively — anything you place in the output directory survives rebuilds.

## Formatting standard

The shipped preamble implements the UCA-style norm: 2 cm margins, Times-like
body at 12 pt, 1.5 spacing, page number bottom right.

For the ASIIN-aligned norm, change the geometry line:

```latex
\usepackage[margin=2.5cm,headheight=1cm,footskip=1cm]{geometry}
```

Both norms are documented side by side in
`skills/rapport-academique/references/formatting-standards.md`. Whichever you
pick, state it in your repo README so the docs and the code do not contradict
each other.

## Citation style

Default is IEEE numbered, which suits computing work:

```latex
\usepackage[backend=biber,style=ieee,sorting=none]{biblatex}
```

For author–date (APA), swap `style=ieee` for `style=apa` and `sorting=none` for
`sorting=nyt`.

## Page budgets

`reports_docs/report.yaml` holds the per-chapter targets. Edit them freely —
`/report:review` and `/report:status` read from that file, so changing a budget
changes what gets flagged.

```yaml
type: pfe
skeleton: 03-pfe-data-cloud-deployment
lang: fr
pages_total: 65
chapters:
  01-contexte-general: [7, 9]
  02-etat-de-l-art: [9, 11]
```

## Adding a skeleton

Create `skills/rapport-academique/references/skeletons/<nn>-<name>/` with a
`README.md` (when it fits, what the jury tests) and an `outline.md`, then add a
row to the mapping table in `SKILL.md` and in `commands/report-init.md`.

Keep the set small. Eight is already at the edge of useful; a ninth makes the
selection worse, not better. Before adding one, check whether an existing
skeleton plus a note would do.

## Adding a placeholder type

1. Add the kind to `KINDS` in `scripts/placeholders.py`.
2. Add its LaTeX expansion in `expand()` in `scripts/build.py`.
3. Document it in `references/placeholder-syntax.md`.
4. If it should block the build, add it to `BLOCKING`.

## Language

`--lang en` selects `06-capstone-en` and switches drafting to English. A French
résumé is frequently required even for English reports — check your department,
and if so keep `01b-resume.md` in French while the rest is English.
