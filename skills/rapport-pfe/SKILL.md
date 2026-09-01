---
name: rapport-pfe
description: Structures, formatting standards, and review criteria for engineering project reports in IT — PFE (Projet de Fin d'Études), PFA (Projet de Fin d'Année), rapports de stage, mini-projets, and English-language IT capstone reports, following Moroccan, Tunisian, and French engineering-school conventions. Use this skill whenever the user mentions a PFE, PFA, rapport de stage, mémoire, soutenance, projet de fin d'année, projet de fin d'études, capstone report, or asks for help planning, outlining, writing, structuring, or reviewing any academic engineering or IT project report — including when they only ask for one piece of it, such as an introduction, an état de l'art, a problématique, a résumé/abstract, a conclusion, a page de garde, or defense slides. Also use it when the user asks whether their report plan is correct, how long a section should be, or what a jury expects.
---

# Rapport PFE / PFA

Guidance for planning, drafting, and reviewing engineering project reports in IT.

## What this skill assumes about the situation

A student writing one of these documents is usually optimising for a jury, not
for a reader. The jury reads structure and proportion before it reads content —
so a report with a strong contribution buried under thirty pages of company
presentation grades worse than a modest contribution presented in proportion.
Most of the value in this skill is in catching that failure mode early, while
there is still time to fix it.

Take the user's own department template as authoritative whenever it exists. Say
so explicitly, once, and then work within it. Never tell someone their school's
official guide is wrong.

## Step 1 — Identify which skeleton applies

Do not ask a list of questions. Infer from what the user has already said, and
ask at most one question if the answer genuinely changes the structure.

```
Is there a host company / organisme d'accueil?
├── No  → full-year project?  No → 05-module-project
│                             Yes → 04-pfa-annual-project
└── Yes → what is the deliverable?
          ├── An application             → 01-pfe-software-engineering
          ├── A model, pipeline, finding → 02-pfe-research-ml
          └── A model in production      → 03-pfe-data-cloud-deployment

Writing in English → 06-capstone-en
```

The distinction that matters most and is most often got wrong: **if the
deliverable is a model rather than an application, the software-engineering plan
is the wrong plan.** A UML class-diagram chapter in a machine-learning report is
filler, and juries read it as filler. If a user brings a machine-learning subject
with a Contexte → Analyse → Conception → Réalisation plan, say so directly and
show them the research plan instead.

Then read the matching files:

- `references/skeletons/<name>/README.md` — when it fits, what the jury tests
- `references/skeletons/<name>/outline.md` — the structure to fill in

## Step 2 — Load the shared reference as needed

Read only what the current task needs, not all of it:

| File | Read it when |
|---|---|
| `references/length-and-proportions.md` | Planning a report, or the user asks how long anything should be |
| `references/formatting-standards.md` | Formatting, typography, citations, figures, pagination |
| `references/common-pitfalls.md` | Reviewing a draft, or the user asks what to avoid |
| `references/defense-checklist.md` | Slides, soutenance, jury questions |
| `references/templates/page-de-garde.md` | Title page or résumé/abstract |

## Step 3 — Do the task

### Planning a report

Produce the outline adapted to the user's actual subject — not the generic
template pasted back. Every chapter heading should name their problem, their
data, their system. Include a rough page budget per chapter derived from the
proportion rule, because that is what stops the état de l'art from swelling.

### Drafting a section

Ask for the material you need rather than inventing it. Never fabricate figures,
metrics, company names, or citations. If the user has not given you results, say
what the section needs and offer to draft the scaffolding around a placeholder.

For a **problématique**: push until it is a problem, not a task description.
"Develop a web application for stock management" is a brief. "Stock levels are
reconciled manually across three sites, producing a 12-day lag that causes X" is
a problématique.

For an **état de l'art**: it is incomplete without a positioning section — a
comparison table placing the user's work against the approaches reviewed. This is
the single most common weakness in AI-track reports. Flag it every time.

For a **methodology chapter** in a research report: the test is whether a
competent reader could reproduce the work. Hyperparameters, data splits, seeds,
hardware, library versions. If the user's draft lacks these, name the specific
gaps.

### Reviewing a draft

Check proportions first — count pages per block before reading closely. Then work
through `references/common-pitfalls.md`. Report findings ordered by how much they
cost, not in document order. Be concrete about what to cut; students find cutting
harder than writing, and vague advice to "shorten the état de l'art" does not
help.

## Language

Match the user's working language. Reports for Moroccan, Tunisian, and French
institutions are usually written in academic French even when the conversation is
in English — so section headings, chapter titles, and drafted prose stay in
French unless the user says otherwise or is using `06-capstone-en`.

Standard French section vocabulary: *page de garde, remerciements, résumé,
mots-clés, sommaire, liste des figures, introduction générale, contexte général
du projet, organisme d'accueil, étude de l'existant, critique de l'existant,
problématique, besoins fonctionnels, besoins non fonctionnels, état de l'art,
conception, réalisation, expérimentations, conclusion générale et perspectives,
bibliographie, webographie, annexes.*

## What not to do

- Do not dump a whole outline file into the reply when the user asked about one
  section.
- Do not add chapters because a template listed them. A diagram that serves no
  argument is padding, and padding is visible.
- Do not write the general introduction first. It is written last, once the
  reasoning exists — and it never states the results.
- Do not soften a real structural problem. A student who finds out at the
  soutenance that their plan was wrong for their subject had no chance to fix it.
