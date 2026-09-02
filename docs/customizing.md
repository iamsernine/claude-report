# Customizing

## Your school's LaTeX template

`assets/latex/preamble.tex` is the entire visual identity of the output. Replace
it with your own and everything downstream follows.

If you already have a working template — for instance a repository with
`main.tex` and a `pages/` folder — the fastest path is:

1. Copy your preamble (everything before `\begin{document}`) into
   `assets/latex/preamble.tex`.
2. Keep the `%%DRAFT%%` marker on its own line. `build.py` substitutes the draft
   watermark **and** the cover-page macros (`\reporttitle`, …) there.
3. Keep `\addbibresource{references.bib}` — the build writes that filename.

The build emits `\chapter{}` / `\chapter*{}`, `\section{}`, `figure`, `table`,
`lstlisting` and `equation` environments. Any preamble that styles those will
work. Keep `\usepackage[hidelinks]{hyperref}` **after** biblatex (the shipped
file already does).

## The cover page

`/report:init` copies `assets/markdown/00-page-de-garde.md`, which is just
`\input{titlepage}`. The title page itself is `assets/latex/titlepage.tex`,
copied into `build/` on every build. Fill `title`, `author`, `institution`,
`year`, `degree`, `supervisor` in `report.yaml` — they become `\reporttitle`
and friends.

Drop logos at `build/figures/logo-institution.png` and
`build/figures/logo-host.png` (optional; grey boxes otherwise).

To use a school cover, replace `assets/latex/titlepage.tex` and keep the
`\reporttitle` macros, or put raw LaTeX in `00-page-de-garde.md` (pandoc is
invoked with `markdown+raw_tex`).

Init also copies `00b-declaration-integrite.md` (integrity + AI-use). Fill the
`[[TODO]]` fields before a non-draft build.

## Formatting standard

The shipped preamble implements the UCA-style norm: 2 cm margins, Times body
(`newtxtext` / `mathptmx`) at 12 pt, 1.5 spacing, page number bottom right.
`hyperref` is loaded last, after `biblatex`.

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
the Python reviewer and `/report:status` parse that file, so changing a budget
changes what gets flagged. Full schema: `assets/report.yaml.example`.

The short form still works:

```yaml
type: pfe
skeleton: 03-pfe-data-cloud-deployment
lang: fr
pages_total: 65
biblio_position: before_annexes
period_start: 2026-02-03
period_end: 2026-06-12
chapters:
  01-contexte-general: [7, 9]
  02-etat-de-l-art: [9, 11]
```

Prefer the explicit form (`title`, `kind`, `numbered`, `pages`) so introduction,
conclusion and annexes stay unnumbered in the PDF.

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

`lang: fr | en` in `report.yaml` is the only switch. It selects heading
vocabulary, LaTeX chrome (babel option, cover labels, draft watermark) and CLI
output. It does **not** select a skeleton, a chapter count, a page budget or a
check — those are identical in every language.

A résumé in the other language is frequently required in both directions — check
your department. If so, keep that one file in the other language while the rest
of the report stays in `lang`.

### Adding a language

1. Add a locale table to `LOCALES` in `scripts/i18n.py`. `tests/test_i18n.py`
   asserts every locale defines exactly the same keys, so a missing string is a
   test failure rather than a silent fallback at build time.
2. Add the language's terms to `_VOCAB` in the same file. Detection uses the
   **union** of every locale, which is what keeps one rule firing on
   `03-etat-de-lart` and `03-literature-review` alike.
3. Add the `babel` key for the new locale — `build.py` reads it and injects the
   package line at `%%LANG%%` in `assets/latex/preamble.tex`.
4. Add `assets/markdown/00b-declaration-integrite.<lang>.md`.

Nothing else should need touching. If adding a language makes you want to write
`if lang == …` in a rule, the rule is wrong, not the language.
