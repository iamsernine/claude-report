# 01 — PFE, software engineering (company project)

**Use this when:** your PFE is building an application for a host organisation —
web app, mobile app, ERP module, internal tool, integration platform. The
deliverable is working software.

**Do not use this when:** the deliverable is a model, an experimental result, or
a benchmark. Use `02-pfe-research-ml` instead. A UML class-diagram chapter in a
machine-learning report is filler and the jury will read it as such.

This is the dominant pattern across Moroccan and Tunisian génie informatique
departments, so it is also the one your jury has read a hundred times. That cuts
both ways: it is safe, and deviations from it need to be justified.

## Shape

Four chapters, roughly 50–70 pages excluding annexes.

| Chapter | Answers |
|---|---|
| 1. Contexte général | Where does this happen and what is broken? |
| 2. Analyse et spécification des besoins | What exactly must be built? |
| 3. Conception | How is it structured? |
| 4. Réalisation et tests | Does it work, and how was it built? |

## Variants you may prefer

- **Three chapters** — merge analysis and design when the project is small.
- **Five chapters** — split *Analyse* and *Conception* when the modelling work is
  substantial, giving Contexte → Analyse → Conception → Réalisation → Tests et
  déploiement.
- **2TUP framing** — if your team used the Y-shaped process, name the chapters
  after its branches (functional branch, technical branch, design-and-realisation
  branch). Only do this if you actually followed it.

## What the jury tests

- Is the problématique a real problem, or a project brief dressed up as one?
- Is the *critique de l'existant* an actual critique or an inventory?
- Are the non-functional requirements real (load, latency, security) or filler?
- Does the architecture follow from the requirements, or was it chosen first?
- Are there tests, and do they test anything meaningful?

See `outline.md` for the fill-in structure.
