---
name: rapport-academique
description: Structures, formatting standards, academic French phrasing, and jury review criteria for engineering project reports — PFE (Projet de Fin d'Études), PFA (Projet de Fin d'Année), stage d'initiation, stage technicien, projet de module, mémoire and capstone reports, in French or English, following Moroccan, Tunisian and French engineering-school conventions. Use this skill whenever the user mentions a PFE, PFA, rapport de stage, stage d'initiation, stage technicien, mémoire, soutenance, projet de fin d'année, projet de fin d'études, capstone, or asks for help planning, outlining, drafting, structuring, reviewing or building any academic engineering or IT project report — including when they only want one piece of it, such as an introduction, an état de l'art, a problématique, a résumé or abstract, a conclusion, a page de garde, or defense slides. Also use it when the user asks whether their report plan is correct, how long a section should be, how many references are normal, or what a jury expects.
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

**Every sentence comes from the repository, from `BRIEF.md`, or from a document
the user put in `reports_docs/sources/`. Anything else is emitted as a
`[[TODO]]` or `[[METRIC]]` placeholder, never invented.**

Never fabricate company names, supervisor names, jury members, dates, measured
results, metrics, client names, or citations to papers you have not verified.

The failure mode this prevents is specific and severe: a drafting tool that
invents plausible prose produces text that *reads* finished, and a student under
deadline pressure ships it. A visible gap is always better than an invisible
fabrication.

When something is missing, do not stall and do not ask one question at a time.
Draft everything the three sources support, mark the rest, and then tell the user
**which document would close which gap** so they can drop it into
`reports_docs/sources/` and run the draft again. That loop — draft, list gaps,
receive documents, redraft — is the intended way to reach a complete report.

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

**Language is not in this table, and that is deliberate.** A capstone written in
English for an international programme is a PFE: same row, same skeleton, same
page budget. Set `lang: en` in `report.yaml` and the headings, the LaTeX chrome
and the CLI output follow. There is no English skeleton to choose.

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

**Language is not a distinction.** It never selects a skeleton, a chapter count,
a proportion or a check. If you catch yourself reasoning "this is in English, so
the plan should be different", stop: the plan is the same and only the words
change.

Then read `references/skeletons/<name>/README.md` and `outline.md`.

If the user says "PFA internship", ask whether they mean a company internship
(`stage-technicien` / `stage-initiation`) or an end-of-year project (`pfa`).
The wrong type invalidates the page budget and the review checks.

Never read `.env` or credential files. Redact tokens and personal data.

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
number is what stops the état de l'art from swelling. Write it into
`reports_docs/report.yaml` (`kind`, `numbered`, `pages`). The Python reviewer
reads those budgets; they are not documentation.

### Drafting

The output of drafting is **markdown the user reads and confirms**, not a PDF.
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

**One rule set, rendered in one language.** Structure, proportions, page budgets
and every review check are language-independent. `lang:` in `report.yaml` is the
single switch, and it governs three things and nothing else: the heading
vocabulary, the LaTeX chrome (babel option, cover-page labels, draft watermark)
and the CLI output.

- Match the user's working language for **conversation**.
- Write the **report** in `lang:`. Do not mix: a French report has French
  headings throughout, an English one English headings throughout.
- Default to `fr` when unset. Reports for Moroccan, Tunisian and French
  institutions are usually written in academic French even when the
  conversation is in English — but confirm rather than assume, because
  international and double-degree programmes routinely require English.
- A résumé in the other language is frequently required in both directions. An
  English report usually still needs a French résumé, and vice versa.

Use `references/formulations.md` rather than inventing transitions. It is
organised by function (opening, handoff, justification, limitation) with French
and English forms side by side — the function is the same in both languages, so
pick the row, then the column. Improvised transitions read worse in either
language.

## What not to do

- Do not dump a whole outline file when the user asked about one section.
- Do not add chapters or diagrams because a template listed them. Padding is
  visible.
- Do not write the general introduction first. It is written last, and it never
  states results.
- Do not soften a real structural problem. A student who discovers at the
  soutenance that their plan was wrong had no chance to fix it.
- Do not hand-edit generated LaTeX. Fix the markdown and rebuild.
- Do not compile a PDF locally, install a TeX distribution, or treat a missing
  `pdflatex` as a problem. The pipeline ends at `build/overleaf.zip`; Overleaf
  compiles it. `pandoc` is the only conversion tool that matters here.
- Do not write a value because it is plausible. If it is not in the repo, the
  brief, or a supplied source, it is a placeholder.
