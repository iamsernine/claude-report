# Reference

## `reports_docs/report.yaml`

```yaml
type: pfe                                  # pfe | pfa | stage-initiation |
                                           # stage-technicien | module | memoire
skeleton: 03-pfe-data-cloud-deployment
lang: fr                                   # fr | en
pages_total: 65
words_per_page: 350

chapters:                                  # [min, max] pages
  01-contexte-general: [7, 9]
  02-etat-de-l-art: [9, 11]
  03-architecture: [8, 10]
  04-modelisation: [14, 17]
  05-industrialisation: [10, 13]
  06-evaluation-operationnelle: [7, 9]

figures:
  existing:                                # already in the repo
    - notebooks/eda.ipynb#fig2
    - deploy/archi.png
```

Read by `/report:draft`, `/report:review` and `/report:status`. Edit it freely.

## Placeholder syntax

Full specification in
`skills/rapport-academique/references/placeholder-syntax.md`.

| Form | Becomes | Blocks build |
|---|---|---|
| `[[FIG: slug \| caption \| width=0.85]]` | `figure` + `\includegraphics` + `\label` | no |
| `[[TAB: slug \| caption]]` | `table` + stub tabular + `\label` | no |
| `[[CODE: slug \| caption \| lang=python]]` | `lstlisting` | no |
| `[[EQ: slug \| description]]` | `equation` + `\label` | no |
| `[[REF: slug]]` | `\ref{fig:slug}` | no |
| `[[CITE: description]]` | `\cite{TODOn}` + entry in `citations-needed.md` | no |
| `[[METRIC: description]]` | nothing | **yes** |
| `[[TODO: description]]` | nothing | **yes** |

Slugs are lowercase, hyphenated, and unique across the whole report — they become
LaTeX labels and image filenames.

## Scripts

All are standalone and usable without Claude.

### `placeholders.py`

```bash
python3 scripts/placeholders.py reports_docs        # JSON inventory
```

Importable: `scan_tree(Path)`, `scan_text(str, filename)`, `slugify(str)`.

### `gen_figures.py`

```bash
python3 scripts/gen_figures.py reports_docs figures
```

Generates a grey placeholder PNG per `[[FIG:]]`, sized to `width × 1600 px`, with
the slug and caption printed on it. **Never overwrites an existing file.** Writes
`figures/MANIFEST.md`.

### `review.py`

```bash
python3 scripts/review.py reports_docs
python3 scripts/review.py reports_docs --json
```

Exit 0 = pass, 1 = blocking problems. Suitable for CI.

Checks: per-chapter proportions (above ~8 pages of body), blocking placeholders,
unreferenced figures and tables, duplicate slugs, état de l'art without
positioning, results without a baseline, introduction leaking results,
introduction and conclusion length, figure density.

### `build.py`

```bash
python3 scripts/build.py reports_docs build
python3 scripts/build.py reports_docs build --allow-todo --no-compile
```

Generates figures, converts markdown to LaTeX via pandoc (with a minimal built-in
fallback), expands placeholders, writes `main.tex`, `references.bib` and
`citations-needed.md`, then runs pdflatex three times with biber after the first.

## Output layout

```
build/
├── main.tex                generated — never hand-edit
├── main.pdf
├── references.bib          stubs for each [[CITE:]]
├── citations-needed.md     what to source, and where it is cited
└── figures/
    ├── MANIFEST.md         the screenshot shopping list
    └── <slug>.png          placeholder, or your real image
```

## CI

```yaml
- run: pip install pillow
- run: python3 scripts/review.py reports_docs
```

Fails the build on blocking problems. Useful on a report repository shared with a
supervisor.
