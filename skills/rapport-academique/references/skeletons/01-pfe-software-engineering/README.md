# 01 — PFE, software engineering (application deliverable)

**Use this when:** your PFE builds an application — web app, mobile app, ERP
module, internal tool, integration platform. The deliverable is working
software.

**Do not use this when:** the deliverable is a model, an experimental result, or
a benchmark. Use `02-pfe-research-ml` instead. A UML class-diagram chapter in a
machine-learning report is filler and the jury will read it as such.

This is the dominant pattern across Moroccan and Tunisian génie informatique
departments, so it is also the one your jury has read a hundred times. That cuts
both ways: it is safe, and deviations from it need to be justified.

## This skeleton is language-independent

There is no separate English structure. A report in French and a report in
English use **this** skeleton, with the same chapter count, the same proportions
and the same review checks; `lang:` in `report.yaml` selects the heading
vocabulary and the LaTeX chrome. Anglophone programmes name chapters after the
problem ("Problem Analysis") where francophone ones name them after the process
("Analyse des besoins") — that is a label, not a different plan.

Two components come from anglophone capstone practice and are now standard here
in every language, because they are genuinely useful:

- **A standalone abstract** (150–250 words, 5–7 keywords) that works as its own
  artefact — often the only thing a reviewer reads in full.
- **A Project Legacy appendix** — what a successor needs to pick the work up:
  repository layout, environment setup, known issues, unfinished threads,
  credential handling, who to ask.

## Shape

Four chapters, roughly 50–70 pages excluding annexes.

| # | Chapter (fr) | Chapter (en) | Answers |
|---|---|---|---|
| 1 | Contexte général | Introduction and Context | Where does this happen and what is broken? |
| 2 | Analyse et spécification des besoins | Problem Analysis and Requirements | What exactly must be built? |
| 3 | Conception | Design | How is it structured? |
| 4 | Réalisation et tests | Implementation, Testing and Evaluation | Does it work, and how was it built? |

Pick one column and stay in it. Do not mix.

## Variants you may prefer

- **Three chapters** — merge analysis and design when the project is small.
- **Five chapters** — split analysis and design when the modelling work is
  substantial: Contexte → Analyse → Conception → Réalisation → Tests et
  déploiement.
- **Six or seven chapters** — the anglophone capstone expansion, splitting
  chapter 2 into *Literature Review / Existing Systems* and *Technical
  Background*, and chapter 4 into *Design and Implementation* and *Testing and
  Evaluation*. Reach for this only above ~70 pages; below that it thins every
  chapter.
- **2TUP framing** — if your team used the Y-shaped process, name the chapters
  after its branches. Only do this if you actually followed it.

## What the jury tests

- Is the problématique a real problem, or a project brief dressed up as one?
- Is the critique of the existing situation an actual critique or an inventory?
- Are the non-functional requirements real (load, latency, security) or filler?
- Does the architecture follow from the requirements, or was it chosen first?
- Are there tests, and do they test anything meaningful?

See `outline.md` for the fill-in structure.
