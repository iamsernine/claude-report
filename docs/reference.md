# Reference

## `reports_docs/report.yaml`

Parsed by `scripts/report_config.py` — used by review, status and build, not
only by Claude. Full example: `assets/report.yaml.example`.

```yaml
type: pfe                                  # pfe | pfa | stage-initiation |
                                           # stage-technicien | module | memoire
skeleton: 03-pfe-data-cloud-deployment       # one set, never chosen by language
lang: fr                                   # fr | en
pages_total: 65
words_per_page: 350
biblio_position: before_annexes            # before_annexes | after_annexes
period_start: 2026-02-03                   # git log window
period_end: 2026-06-12

title: "Titre"
author: "Prénom Nom"
institution: "Établissement"
year: "2025-2026"
degree: "Cycle d'ingénieur"
supervisor: "Encadrant"

chapters:
  03-introduction-generale:
    title: Introduction générale
    kind: intro                            # front | intro | chapter | conclusion | annex
    numbered: false
    pages: [1, 1]
  01-contexte-general: [7, 9]              # short form still valid
```

`kind` + `numbered` control LaTeX: intro/conclusion/annex default to
`\chapter*` so Chapitre 1 is the first real chapter.

## Placeholder syntax

Full specification in
`skills/rapport-academique/references/placeholder-syntax.md`.

| Form | Becomes | Blocks build |
|---|---|---|
| `[[FIG: slug \| caption \| width=0.85]]` | `figure` + `\includegraphics` + `\label` | no |
| `[[TAB: slug \| caption]]` | `table` + stub tabular + `\label` | no |
| `[[CODE: slug \| caption \| lang=python]]` | `lstlisting` | no |
| `[[EQ: slug \| description]]` | `equation` + `\label` | no |
| `[[REF: slug]]` | `\ref{fig:slug}` (or tab/lst/eq) | no |
| `[[CITE: key \| description]]` | `\cite{key}` + merged bib stub | no |
| `[[CITE: description]]` | `\cite{stable-slug}` | no |
| `[[METRIC: description]]` | nothing | **yes** |
| `[[TODO: description]]` | nothing | **yes** |

Malformed `[[...]]` is a review **issue**, not ignored text.

Slugs are unique across the whole report — they become LaTeX labels and image
filenames. Cite keys must match `[\w.:-]+` to be treated as keys.

## Scripts

All are standalone and usable without Claude. Prefer the unified CLI so the
working directory can be the student's project:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" review reports_docs
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" build reports_docs build --allow-todo
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" status reports_docs
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" guard reports_docs
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" guard --stamp reports_docs/04-x/01.md
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" check
```

`bin/claude-report` is the same CLI.

### `placeholders.py`

```bash
python3 scripts/placeholders.py reports_docs        # JSON inventory + malformed
```

Importable: `scan_tree(Path)`, `scan_text(str, filename)`, `scan_malformed`,
`slugify(str)`.

### `gen_figures.py`

```bash
python3 scripts/gen_figures.py reports_docs figures
```

Generates a grey placeholder PNG per `[[FIG:]]`, sized to `width × 1600 px`,
stamped with PNG text `claude-report=placeholder`. **Never overwrites an
existing file.** Writes `figures/MANIFEST.md` with état `placeholder` / `fourni`
/ `manquant`.

### `review.py`

```bash
python3 scripts/review.py reports_docs
python3 scripts/review.py reports_docs --json
python3 scripts/review.py reports_docs --fix
```

Exit 0 = pass, 1 = blocking problems. Suitable for CI.

Reads `report.yaml`. Checks: per-chapter proportions and yaml page budgets
(above ~8 pages of body), blocking and malformed placeholders, unreferenced
figures and tables, duplicate slugs, état de l'art without positioning
(severity depends on `type`), results without a baseline (research skeletons
only), introduction leaking results, introduction and conclusion length, figure
density.

`--fix` inserts missing `[[REF:]]` and renames duplicate slugs. Nothing
substantive is auto-written.

### `build.py`

```bash
python3 scripts/build.py reports_docs build
python3 scripts/build.py reports_docs build --allow-todo
python3 scripts/build.py reports_docs build --compile     # opt-in, rarely needed
```

Generates figures, converts markdown to LaTeX via pandoc
(`--top-level-division=section`; headings-only fallback if pandoc is missing),
expands placeholders, **merges** citation stubs into `references.bib`, writes
`titlepage.tex` with cover labels in the report's language, writes `main.tex` and
`citations-needed.md`, and packs `overleaf.zip`.

**No PDF is produced by default.** Compilation belongs to Overleaf, so no TeX
installation is required. `--compile` runs pdflatex three times with biber after
the first, for the rare case where a local toolchain already exists;
`--no-compile` is accepted and does nothing, since it is the default.

Working material is excluded from the report: `BRIEF.md`, `report.yaml`,
`sources/`, `figures/` and any `.generated` sidecar. A document you drop into
`sources/` is read by the drafter and never compiled into the output.

Unnumbered kinds emit `\chapter*`. `biblio_position` places
`\printbibliography` before or after annexes.

### `draft_guard.py`

```bash
python3 scripts/draft_guard.py reports_docs
python3 scripts/draft_guard.py stamp path/to/file.md
```

A sidecar `file.md.generated` stores the SHA-256 of the last generated
content. If the hash no longer matches, the file is treated as student-owned.
This works when `reports_docs/` is not tracked by git.

## Output layout

```
build/
├── main.tex                generated — never hand-edit
├── overleaf.zip            upload this
├── titlepage.tex           generated from assets + report.yaml
├── references.bib          merged stubs + whatever you filled in
├── citations-needed.md     what to source, and where it is cited
└── figures/
    ├── MANIFEST.md         the screenshot shopping list
    └── <slug>.png          placeholder, or your real image
```

## CI

```yaml
- run: pip install -r requirements.txt
- run: python3 -m unittest discover -s tests -v
- run: python3 scripts/cli.py review reports_docs
```

Fails the build on blocking problems. Useful on a report repository shared with a
supervisor.
