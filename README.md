# claude-report

A Claude Code plugin for writing academic engineering reports — PFE, PFA, stage
d'initiation, stage technicien, projet de module — from a project repository.

Markdown first, LaTeX at the end. The report is drafted as editable markdown you
own, reviewed against the criteria a jury actually applies, then compiled into a
LaTeX document that builds on the first attempt even before you have a single
screenshot.

---

## Why it exists

Two things are hard about these reports and neither is the writing.

**Structure.** Which of eight plans fits your project, and what proportion each
chapter should occupy. Getting this wrong costs marks in a way that is invisible
until the defense.

**The gap between markdown and a submittable PDF.** Most people draft in Word,
fight the table of contents, and discover their figures are unreferenced two days
before the deadline.

This plugin handles both, and refuses to invent the parts only you can supply.

## Install

```bash
git clone https://github.com/<you>/claude-report ~/.claude/plugins/claude-report
```

Or add it as a marketplace plugin:

```
/plugin marketplace add <you>/claude-report
/plugin install claude-report
```

Requirements: Python 3.9+ with Pillow (`pip install pillow`). Optional but
recommended: `pandoc` for markdown→LaTeX conversion, and a TeX distribution for
local compilation. Without a local TeX install the plugin still generates a
`build/` folder you upload to Overleaf.

---

## Workflow

```
/report:init  →  fill BRIEF.md  →  /report:draft  →  edit  →  /report:review  →  /report:build
                      ↑                                            │
                      └────────────────  iterate  ─────────────────┘
```

### 1. `/report:init --type pfe`

Reads your repository — stack, architecture, tests, entry points — and mines
`git log` to build a chronogramme from what actually happened rather than a
retrospective fiction.

Then it picks the skeleton, writes `reports_docs/report.yaml` with a per-chapter
page budget, and generates `reports_docs/BRIEF.md`.

It reports back: the chapter plan with page targets, the estimated figure count,
**which figures already exist in your repo**, the exact screenshots you need
derived from your routes and CLI commands, and what is missing from the brief.

```bash
/report:init --type pfe
/report:init --type stage-initiation --pages 15
/report:init --type pfa --lang en
```

| `--type` | Experience | Length |
|---|---|---|
| `stage-initiation` | 1st/2nd year observation internship, 2–6 weeks | 10–20 p |
| `stage-technicien` | 2nd/3rd year application internship, 4–8 weeks | 20–35 p |
| `pfa` | Projet de Fin d'Année | 25–40 p |
| `pfe` | Projet de Fin d'Études | 50–80 p |
| `module` | Course project, no company | 12–25 p |
| `memoire` | Master's thesis | 60–100 p |

For `pfe`, a second question determines the deliverable — an application, a
model, or a model in production — because that changes the whole plan.

### 2. Fill `BRIEF.md`

**This is the step that makes the rest work.** Claude can read your code; it
cannot know your host organisation, your problématique, your supervisor, your
measured results, or what went wrong in week six.

Anything in the brief gets drafted. Anything absent becomes a visible placeholder.
Nothing is invented. A blank section is always better than plausible fiction you
ship by accident.

### 3. `/report:draft`

Writes one folder per chapter, one file per section, into `reports_docs/`.
Figures, tables, citations and missing numbers become typed placeholders.

```markdown
L'architecture est présentée en [[REF: architecture-globale]].

[[FIG: architecture-globale | Architecture générale de la plateforme | width=0.9]]

Le modèle atteint un mAP@0.5 de [[METRIC: mAP@0.5 sur le jeu de test]].
```

Redraft one chapter at a time with `--chapter 3`. Files you have edited are never
silently overwritten.

### 4. `/report:review`

The command that makes this worth installing. Auto-generating a report outline is
commoditised. **Critique against jury criteria is not.**

It counts words per chapter against budget and flags inverted proportions, finds
figures declared but never referenced in the text, detects an état de l'art with
no positioning table, detects a results section with no baseline, catches an
introduction leaking results and a conclusion introducing new material, and finds
duplicate labels.

Then Claude adds the judgement pass the script cannot do: is the problématique a
problem or a task description, do the technology justifications tie back to the
constraints, are the limitations honest.

Findings are ordered by how much they cost, not by document order.

### 5. `/report:build`

Generates `build/main.tex`, `build/figures/`, `build/references.bib` and compiles.

**The trick that makes it usable:** every `[[FIG:]]` gets a grey placeholder PNG,
sized correctly, with the slug and caption printed on it. So the first build
produces a real-looking PDF with correct pagination and figures in their slots.
You see the layout immediately.

To insert a real image, replace `figures/<slug>.png` with your own file keeping
the filename. No LaTeX edit. Rebuild.

The build **refuses** while any `[[METRIC]]` or `[[TODO]]` remains, because a
report shipping an invented metric is worse than one that does not build. Use
`--allow-todo` for a watermarked draft.

`build/figures/MANIFEST.md` is your screenshot shopping list: filename, caption,
chapter, minimum pixel width.

### `/report:status`

Pages against budget per chapter, brief completeness, blocking placeholders,
figures outstanding, and one concrete next action.

---

## The eight skeletons

| Skeleton | For |
|---|---|
| `00-stage-initiation` | Observation internship. No problématique, no contribution — and inventing one is the defining mistake. |
| `01-pfe-software-engineering` | Contexte → Analyse → Conception → Réalisation. Ships software. |
| `02-pfe-research-ml` | État de l'art → Méthodologie → Expérimentations. Ships a model or a finding. |
| `03-pfe-data-cloud-deployment` | Research plus industrialisation. Operational constraints thread the whole report. |
| `04-pfa-annual-project` | Lighter scope, brief état de l'art, guided rather than autonomous. |
| `05-module-project` | No company. Delete every organisme d'accueil reflex. |
| `06-capstone-en` | English. Adds a user manual and a project legacy appendix. |
| `07-stage-technicien` | A real but bounded task. Describing it precisely beats inflating it. |

Each has a `README.md` explaining when it fits and what the jury tests, plus an
`outline.md` you fill in. Browse them at
`skills/rapport-academique/references/skeletons/`.

---

## What it will not do

It will not invent your results, your company, your supervisor, or your
citations. It will not write your problématique for you — it will push you until
yours is a problem rather than a task description.

The structure, the scaffolding and the formatting are tooling. The engineering
decisions, the results and the interpretation have to be yours. **A report you
cannot defend in front of a jury is worthless regardless of how it was produced.**

Check your institution's policy on AI assistance before using this. Policies
differ and are changing fast.

---

## Documentation

- [`docs/workflow.md`](docs/workflow.md) — the full loop with a worked example
- [`docs/customizing.md`](docs/customizing.md) — your school's template, logo,
  formatting standard, adding a skeleton
- [`docs/troubleshooting.md`](docs/troubleshooting.md) — build failures, pandoc,
  Overleaf, accents
- [`docs/reference.md`](docs/reference.md) — placeholder syntax, `report.yaml`,
  script APIs

## Layout

```
claude-report/
├── commands/                    the five slash commands
├── skills/rapport-academique/
│   ├── SKILL.md
│   └── references/              8 skeletons + 9 reference documents
├── scripts/
│   ├── placeholders.py          typed placeholder parser
│   ├── gen_figures.py           grey placeholder image generator
│   ├── review.py                jury-criteria checker
│   └── build.py                 markdown → LaTeX → PDF
├── assets/latex/preamble.tex    swap in your school's preamble here
└── docs/
```

## Caveats

**Your department's template wins.** Where this plugin and your official guide
disagree, follow the guide.

**Structure is not content.** A perfectly structured report with a thin
contribution still gets a thin grade. The proportion rule exists precisely to
stop structure from substituting for substance.

**`build/` is generated.** Never hand-edit `main.tex`. Fix the markdown, rebuild.

## License

MIT.
