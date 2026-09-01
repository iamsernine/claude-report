# Placeholder syntax

Placeholders are typed so that `/report:review` can validate them and
`/report:build` can convert them into LaTeX. Use these forms exactly — the parser
is strict, and a malformed placeholder is reported as an error rather than
silently passed through.

## Forms

```
[[FIG: slug | Caption text | width=0.85]]
[[TAB: slug | Caption text]]
[[CITE: free-text description of the source you need]]
[[METRIC: what number goes here]]
[[TODO: anything you must confirm or write yourself]]
[[CODE: slug | Caption text | lang=python]]
[[EQ: slug | Description of the equation]]
```

`slug` is lowercase, hyphenated, unique across the whole report. It becomes both
the LaTeX label and the expected image filename.

`width` is a fraction of `\textwidth`. Defaults to `0.8` if omitted.

## What each becomes at build time

| Placeholder | LaTeX output | Blocks the build? |
|---|---|---|
| `FIG` | `figure` environment + `\includegraphics{figures/<slug>.png}` + `\label{fig:<slug>}` | No — a generated grey placeholder image is used |
| `TAB` | `table` environment with a stub tabular + `\label{tab:<slug>}` | No |
| `CODE` | `lstlisting` environment | No |
| `EQ` | `equation` environment with a comment | No |
| `CITE` | `\cite{TODO-<n>}` + an entry in `citations-needed.md` | No — warns |
| `METRIC` | Nothing. Build refuses. | **Yes** |
| `TODO` | Nothing. Build refuses. | **Yes** |

`METRIC` and `TODO` are hard blockers by design. They mark places where a number
or a fact must come from the student, and a report that ships with an invented
metric is worse than one that does not build.

Override with `/report:build --allow-todo` when you deliberately want a draft PDF
with gaps. The generated PDF is then watermarked `BROUILLON`.

## Examples

```markdown
L'architecture retenue est présentée en [[FIG: architecture-globale |
Architecture générale de la plateforme | width=0.9]].

Le tableau [[TAB: comparaison-modeles | Comparaison des approches évaluées]]
récapitule les performances obtenues.

Les travaux de [[CITE: YOLOv8 real-time object detection on edge devices]]
montrent qu'une inférence temps réel est atteignable sur ce type de matériel.

Le modèle atteint un mAP@0.5 de [[METRIC: mAP@0.5 sur le jeu de test final]]
sur le jeu de test.

[[TODO: confirmer avec l'encadrant la date exacte de mise en production]]
```

## Referencing a placeholder elsewhere

Once a `FIG` or `TAB` is declared, refer to it anywhere with:

```
[[REF: architecture-globale]]
```

which becomes `\ref{fig:architecture-globale}`. `/report:review` flags any figure
or table that is declared but never referenced in the running text — an
unreferenced illustration is a formatting fault in every institutional guide.

## Image workflow

At build time, every `FIG` gets a generated grey placeholder PNG at
`figures/<slug>.png`, sized to the requested width, with the slug and caption
printed on it. The document compiles immediately and the layout is correct.

To insert a real image: replace `figures/<slug>.png` with your own file, keeping
the name. No LaTeX edit is needed. Rebuild.

`/report:build` writes `figures/MANIFEST.md` listing every expected image, its
slug, its caption, the chapter it appears in, and the recommended minimum pixel
width. That is the shopping list to hand to yourself before a screenshot session.
