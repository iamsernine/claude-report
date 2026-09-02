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

```
/plugin marketplace add iamsernine/claude-report
/plugin install claude-report@claude-report
```

Restart Claude Code (or run `/plugin`) and `/report:init` is available.

Cloning into `~/.claude/plugins/` does **not** install anything — Claude Code
registers plugins through a marketplace, and only a registered plugin gets
`$CLAUDE_PLUGIN_ROOT` exported to its commands. If the commands cannot find the
plugin, that is almost always the cause.

<details>
<summary>Manual install, for hacking on the plugin locally</summary>

```bash
git clone git@github.com:iamsernine/claude-report.git ~/src/claude-report
/plugin marketplace add ~/src/claude-report
/plugin install claude-report@claude-report
```

A marketplace can be a local directory, so this keeps your checkout editable
while still registering properly. As a last resort the commands also fall back
to `~/.claude/plugins/claude-report`, `~/.claude/skills/claude-report` and the
marketplace cache, so a hand-copied tree still works — it just will not update.

</details>

### Requirements

| | | |
|---|---|---|
| Python 3.9+ | required | no third-party packages needed for `check`, `status`, `review`, `gaps`, `guard` |
| **pandoc** | **strongly recommended** | markdown→LaTeX. Without it the build falls back to headings-only conversion, and lists, tables and quotes come out wrong. It says so when this happens. |
| Pillow | recommended | `pip install -r requirements.txt` — only to generate figure placeholders |
| pdftotext *or* pypdf | optional | only to read PDFs you drop into `reports_docs/sources/` |
| TeX, pdflatex, biber | **not needed** | nothing is compiled locally. Overleaf compiles `build/overleaf.zip`. Do not install a TeX distribution for this. |

Check what you have:

```bash
python3 "$CLAUDE_PLUGIN_ROOT/scripts/cli.py" check
```

Commands run `scripts/cli.py` **from the plugin directory**, never from your
project. The CLI locates its own root, so nothing needs to be on your `PATH`.

You can also call it yourself from anywhere:

```bash
python3 "$CLAUDE_PLUGIN_ROOT/scripts/cli.py" status reports_docs
```

---

## Languages

One skeleton set, one set of rules, rendered in the language you choose.

`lang: fr | en` in `reports_docs/report.yaml` selects three things: heading
vocabulary, LaTeX chrome (babel option, cover-page labels, draft watermark) and
CLI output. It selects **nothing else** — the skeleton, the chapter count, the
page budget and every review check are identical in both languages. A chapter
called `03-etat-de-lart` and one called `03-literature-review` hit the same
checks at the same thresholds.

Adding a language means adding a locale table in `scripts/i18n.py` and its terms
to the shared detection vocabulary. It never means adding a skeleton or a branch
in a rule.

---

## Workflow

```
/report:init  →  fill BRIEF.md  →  /report:draft  →  read the markdown
                       ↑                                    │
                       │        drop documents in           │ confirm
                       └──────  reports_docs/sources/  ←─────┤
                                                            ↓
                                        /report:review  →  /report:build
                                                            ↓
                                                   build/overleaf.zip
                                                            ↓
                                              upload to Overleaf → PDF
```

**The plugin stops at LaTeX.** It never compiles a PDF on your machine, and
needs no TeX installation. `/report:build` writes `build/` plus a ready-to-upload
`build/overleaf.zip`; Overleaf does the rest.

**It never guesses.** Everything comes from your repository, from `BRIEF.md`, or
from documents you drop into `reports_docs/sources/` — PDFs, Markdown, plain
text. Whatever is still missing is left as a visible `[[TODO]]` / `[[METRIC]]`
placeholder and listed back to you, so you can supply the document that closes it
and draft again.

### 1. `/report:init --type pfe`

Reads your repository — stack, architecture, tests, entry points — and mines
`git log` **inside `period_start` / `period_end`** to build a chronogramme from
what actually happened during the project, not the entire life of the repo.

Then it picks the skeleton, writes `reports_docs/report.yaml` with a per-chapter
page budget (read by the Python reviewer, not only by Claude), copies a real
LaTeX cover page and an integrity / AI-use declaration, and generates
`reports_docs/BRIEF.md`.

If you omit `--type`, it asks one question: company internship, PFA, or PFE.
"PFA internship" is ambiguous and the wrong skeleton invalidates the rest.

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

Set `period_start` / `period_end` in `report.yaml` so the chronogramme matches
the internship, not five years of `git log`.

### 3. `/report:draft`

Writes one folder per chapter, one file per section, into `reports_docs/`.
Figures, tables, citations and missing numbers become typed placeholders.

```markdown
L'architecture est présentée en [[REF: architecture-globale]].

[[FIG: architecture-globale | Architecture générale de la plateforme | width=0.9]]

Le modèle atteint un mAP@0.5 de [[METRIC: mAP@0.5 sur le jeu de test]].
```

Redraft one chapter at a time with `--chapter 3`. Files you have edited are never
silently overwritten — even if `reports_docs/` is not in git. Protection is a
`*.md.generated` hash sidecar. `--force` is required to replace those files.

### 4. `/report:review`

The command that makes this worth installing. Auto-generating a report outline is
commoditised. **Critique against jury criteria is not.**

It counts words per chapter against the yaml budget and flags inverted
proportions, finds figures declared but never referenced in the text, detects an
état de l'art with no positioning table (blocking on a PFE, a warning on a PFA,
skipped on a stage), detects a results section with no baseline **on research
skeletons only**, catches an introduction leaking results, and finds duplicate
or malformed placeholders.

`--fix` applies the mechanical subset (missing `[[REF:]]`, duplicate slugs).
Structural problems are reported, never auto-written.

Then Claude adds the judgement pass the script cannot do: is the problématique a
problem or a task description, do the technology justifications tie back to the
constraints, are the limitations honest.

Findings are ordered by how much they cost, not by document order.

### 5. `/report:build`

Generates `build/main.tex`, `build/figures/`, `build/references.bib` and compiles.

Introduction / conclusion / annexes are unnumbered (`\chapter*`), so Chapitre 1
is the first real chapter. Bibliography defaults to *before* annexes
(`biblio_position` in yaml).

**The trick that makes it usable:** every `[[FIG:]]` gets a grey placeholder PNG,
sized correctly, with the slug and caption printed on it. Placeholders are
stamped; `MANIFEST.md` says `placeholder` vs `fourni`. Existing real images are
never overwritten.

To insert a real image, replace `figures/<slug>.png` with your own file keeping
the filename. No LaTeX edit. Rebuild. Cover logos:
`figures/logo-institution.png`, `figures/logo-host.png`.

Citation keys are stable (`[[CITE: knuth84 | The TeXbook]]`). Rebuild **merges**
new stubs into `references.bib`; it does not delete entries you already filled.

The build **refuses** while any `[[METRIC]]` or `[[TODO]]` remains, because a
report shipping an invented metric is worse than one that does not build. Use
`--allow-todo` for a watermarked draft.

### `/report:status`

Pages against budget per chapter, brief completeness, blocking placeholders,
figures outstanding (`fourni` vs `placeholder`), and one concrete next action.

---

## The seven skeletons

| Skeleton | For |
|---|---|
| `00-stage-initiation` | Observation internship. No problématique, no contribution — and inventing one is the defining mistake. |
| `01-pfe-software-engineering` | Contexte → Analyse → Conception → Réalisation. Ships software. |
| `02-pfe-research-ml` | État de l'art → Méthodologie → Expérimentations. Ships a model or a finding. |
| `03-pfe-data-cloud-deployment` | Research plus industrialisation. Operational constraints thread the whole report. |
| `04-pfa-annual-project` | Lighter scope, brief état de l'art, guided rather than autonomous. |
| `05-module-project` | No company. Delete every organisme d'accueil reflex. |
| `07-stage-technicien` | A real but bounded task. Describing it precisely beats inflating it. |

The skeleton follows the **experience type and the deliverable**, never the
language. An English capstone is a PFE with `lang: en`; skeleton
`01-pfe-software-engineering` carries the user-manual and project-legacy
appendices for every language. (`06-capstone-en` was a separate English
structure in 0.2.x; it is retired, and an old `report.yaml` naming it is
migrated automatically.)

Each has a `README.md` explaining when it fits and what the jury tests, plus an
`outline.md` you fill in. Browse them at
`skills/rapport-academique/references/skeletons/`.

---

## Tests

```bash
python3 -m unittest discover -s tests -v      # or: python3 -m pytest tests -q
```

No third-party packages are needed to run them. `tests/test_i18n.py` pins the
language contract: every locale must define the same keys, chapter kinds must be
inferred identically in French and English, and the same draft must produce the
same findings in both languages. If you add a language and forget a string, that
is a test failure, not a silent fallback in someone's PDF.

---

## What it will not do

It will not invent your results, your company, your supervisor, or your
citations. It will not write your problématique for you — it will push you until
yours is a problem rather than a task description.

It will not read `.env` files or put tokens in the report.

The structure, the scaffolding and the formatting are tooling. The engineering
decisions, the results and the interpretation have to be yours. **A report you
cannot defend in front of a jury is worthless regardless of how it was produced.**

Check your institution's policy on AI assistance before using this. Policies
differ and are changing fast. `/report:init` copies a declaration page you must
fill honestly.

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
├── bin/claude-report            CLI wrapper
├── commands/                    the five slash commands
├── skills/rapport-academique/
│   ├── SKILL.md
│   └── references/              8 skeletons + 9 reference documents
├── scripts/
│   ├── cli.py                   unified entry point (use this)
│   ├── placeholders.py          typed placeholder parser
│   ├── gen_figures.py           grey placeholder image generator
│   ├── review.py                jury-criteria checker (reads report.yaml)
│   ├── build.py                 markdown → LaTeX → PDF
│   ├── draft_guard.py           hash sidecars against silent overwrite
│   ├── report_config.py         report.yaml loader
│   └── status.py                progress table
├── assets/latex/                preamble + titlepage
├── assets/markdown/             cover + integrity declaration
├── tests/
└── docs/
```

## Caveats

**Your department's template wins.** Where this plugin and your official guide
disagree, follow the guide. Swap `assets/latex/preamble.tex` and the logos.

**Structure is not content.** A perfectly structured report with a thin
contribution still gets a thin grade. The proportion rule exists precisely to
stop structure from substituting for substance.

**`build/` is generated.** Never hand-edit `main.tex`. Fix the markdown, rebuild.
`references.bib` is merged, not overwritten — you *can* fill real entries there.

## License

MIT.
