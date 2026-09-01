---
description: Analyse the project and set up the report — picks the skeleton, generates the brief, estimates length and figures
argument-hint: "[--type pfe|pfa|stage-initiation|stage-technicien|module|memoire] [--lang fr|en] [--pages N]"
allowed-tools: Read, Glob, Grep, Bash, Write
---

Set up an academic report for this project. Use the `rapport-academique` skill for
all structural, formatting and quality decisions — read it before doing anything.

## Arguments

`$ARGUMENTS`

- `--type` — the kind of academic experience. If absent, infer from the project
  and **confirm with the user before proceeding**; getting this wrong invalidates
  everything downstream.

  | Value | Experience | Length |
  |---|---|---|
  | `stage-initiation` | 1st/2nd year observation internship, 2–6 weeks | 10–20 p |
  | `stage-technicien` | 2nd/3rd year application internship, 4–8 weeks | 20–35 p |
  | `pfa` | Projet de Fin d'Année, 3rd/4th year | 25–40 p |
  | `pfe` | Projet de Fin d'Études, final year | 50–80 p |
  | `module` | Course project / mini-projet, no company | 12–25 p |
  | `memoire` | Master's thesis — uses the research skeleton | 60–100 p |

- `--lang` — `fr` (default) or `en`.
- `--pages` — override the target page count.

## Steps

**1. Analyse the repository.** Read the README, manifests (package.json,
requirements.txt, pom.xml, Cargo.toml…), the directory layout, entry points,
test files, existing diagrams and notebooks. Do not read every source file —
sample enough to describe the architecture accurately.

**2. Mine the git history for the chronogramme.** Run
`git log --date=short --pretty='%ad %s'`. Cluster commits into phases by date and
subject. This produces a Gantt grounded in what actually happened rather than a
retrospective fiction. If the repository has no history, skip it and note that
the planning section needs manual input.

**3. Select the skeleton.** Map `--type` to a skeleton, then for `pfe` and
`memoire` determine the deliverable and pick accordingly:

```
stage-initiation → 00-stage-initiation
stage-technicien → 07-stage-technicien
pfa              → 04-pfa-annual-project
module           → 05-module-project
memoire          → 02-pfe-research-ml
pfe              → an application         → 01-pfe-software-engineering
                 → a model or a finding   → 02-pfe-research-ml
                 → a model in production  → 03-pfe-data-cloud-deployment
--lang en        → 06-capstone-en
```

The distinction that matters most: **if the deliverable is a model rather than an
application, the software-engineering skeleton is the wrong one.** Say so
directly if the user's expectation differs.

**4. Write `reports_docs/report.yaml`** — type, skeleton, language, page budget,
per-chapter page targets derived from the proportion rule, and an empty figure
registry. Every later command reads this file.

**5. Write `reports_docs/BRIEF.md`** from the schema in
`references/brief-schema.md`. Pre-fill everything inferable from the repository.
Leave the rest as explicit empty fields.

**6. Report to the user.** Give:

- The skeleton chosen and one sentence on why
- Chapter list with page targets summing to the budget
- Estimated figure count, and **which figures already exist in the repo**
  (diagrams, notebook plots, README images) versus which must be produced
- The exact screenshots needed, derived from routes, endpoints, CLI commands or
  UI components found in the code
- The proposed chronogramme from git history
- **What is missing from the brief and must be filled before drafting**

Do not create any chapter files. `/report:init` only sets up.

Finish by telling the user to fill `BRIEF.md`, then run `/report:draft`.
