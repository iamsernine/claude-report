---
name: rapport-academique
description: Structures, formatting standards, academic French phrasing, and jury review criteria for engineering project reports — PFE (Projet de Fin d'Études), PFA (Projet de Fin d'Année), stage d'initiation, stage technicien, projet de module, mémoire, and English IT capstone reports, following Moroccan, Tunisian and French engineering-school conventions. Use this skill whenever the user mentions a PFE, PFA, rapport de stage, stage d'initiation, stage technicien, mémoire, soutenance, projet de fin d'année, projet de fin d'études, capstone, or asks for help planning, outlining, drafting, structuring, reviewing or building any academic engineering or IT project report — including when they only want one piece of it, such as an introduction, an état de l'art, a problématique, a résumé or abstract, a conclusion, a page de garde, or defense slides. Also use it when the user asks whether their report plan is correct, how long a section should be, how many references are normal, or what a jury expects.
---

# Rapport académique

Guidance for planning, drafting, reviewing and building engineering project
reports.

## What this skill assumes about the situation

A student writing one of these documents is optimising for a jury, not for a
reader. The jury reads structure and proportion before it reads content — so a
report with a strong contribution buried under thirty pages of company
presentation grades worse than a modest contribution presented in proportion.
Most of the value here is catching that early, while there is still time to fix
it.

Where the user's own department template exists, it is authoritative. Say so once
and work within it. Never tell someone their school's official guide is wrong.

## The non-negotiable rule

**Anything the user has stated, or that is derivable from their repository, may
be drafted. Anything else is emitted as a `[[TODO]]` or `[[METRIC]]` placeholder,
never invented.**

Never fabricate company names, supervisor names, jury members, dates, measured
results, metrics, client names, or citations to papers you have not verified.

The failure mode this prevents is specific and severe: a drafting tool that
invents plausible French produces text that *reads* finished, and a student under
deadline pressure ships it. A visible gap is always better than an invisible
fabrication.

## Step 1 — Identify the experience type

Infer from what the user has said. Ask at most one question, and only when the
answer changes the structure.

| Type | Experience | Skeleton | Length |
|---|---|---|---|
| Stage d'initiation | 1st/2nd year, observation, 2–6 weeks | `00-stage-initiation` | 10–20 p |
| Stage technicien | 2nd/3rd year, bounded task, 4–8 weeks | `07-stage-technicien` | 20–35 p |
| PFA | 3rd/4th year annual project | `04-pfa-annual-project` | 25–40 p |
| Projet de module | Course project, no company | `05-module-project` | 12–25 p |
| PFE — application | Final year, ships software | `01-pfe-software-engineering` | 50–70 p |
| PFE — research | Final year, ships a model or finding | `02-pfe-research-ml` | 50–80 p |
| PFE — data/cloud | Model **and** production deployment | `03-pfe-data-cloud-deployment` | 60–90 p |
| English capstone | International programme | `06-capstone-en` | 40–70 p |

Two distinctions carry most of the weight:

**Deliverable, not domain.** If the deliverable is a model rather than an
application, the software-engineering skeleton is wrong. A UML class-diagram
chapter in a machine-learning report is filler and juries read it as filler. If a
user brings an ML subject with a Contexte → Analyse → Conception → Réalisation
plan, say so directly.

**Autonomy, not just year.** A stage d'initiation has no problématique and no
contribution. Manufacturing either is the defining mistake of those reports —
honest observation reads as maturity, invented achievement reads as fiction and
collapses under one question.

Then read `references/skeletons/<name>/README.md` and `outline.md`.

## Step 2 — Load only what the task needs

| File | Read it when |
|---|---|
| `references/brief-schema.md` | Setting up, or drafting anything requiring facts |
| `references/placeholder-syntax.md` | Writing or parsing any markdown draft |
| `references/good-vs-weak.md` | Drafting or reviewing prose quality |
| `references/formulations.md` | Writing French — transitions, justifications, limitations |
| `references/length-and-proportions.md` | Planning, or any "how long should X be" |
| `references/formatting-standards.md` | Typography, citations, figures, pagination |
| `references/common-pitfalls.md` | Reviewing a draft |
| `references/defense-checklist.md` | Slides, soutenance, jury questions |
| `references/faq.md` | Questions the outlines do not cover |

## Step 3 — Do the task

### Planning

Produce the outline adapted to the user's actual subject, never the generic
template pasted back. Every heading should name their problem, their data, their
system. Attach a page budget per chapter derived from the proportion rule — that
number is what stops the état de l'art from swelling.

### Drafting

Ask for the material you need. For a **problématique**, push until it is a
problem rather than a task description; the test is whether someone could propose
a different solution to it. For an **état de l'art**, it is incomplete without a
positioning table and an explicit statement of the gap — flag this every time,
it is the most common weakness in AI-track reports. For a **methodology chapter**
in a research report, the test is reproducibility: hyperparameters, splits,
seeds, hardware, versions.

### Reviewing

Check proportions first — count pages per block before reading closely. Then work
through the pitfalls. Report findings ordered by cost, not document order. Be
concrete about what to cut and by how much; "shorten the état de l'art" does not
help anyone.

## Language

Match the user's working language for conversation. Reports for Moroccan,
Tunisian and French institutions are written in academic French even when the
conversation is in English — so headings and drafted prose stay French unless the
user says otherwise or is using `06-capstone-en`. A French résumé is frequently
required even for English reports.

Use `references/formulations.md` rather than inventing transitions. These are
genre conventions, and improvised ones read worse.

## What not to do

- Do not dump a whole outline file when the user asked about one section.
- Do not add chapters or diagrams because a template listed them. Padding is
  visible.
- Do not write the general introduction first. It is written last, and it never
  states results.
- Do not soften a real structural problem. A student who discovers at the
  soutenance that their plan was wrong had no chance to fix it.
- Do not hand-edit generated LaTeX. Fix the markdown and rebuild.
