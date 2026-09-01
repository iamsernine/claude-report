---
description: Draft the report chapters as markdown files with typed placeholders
argument-hint: "[--chapter N] [--section path] [--force]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

Draft the report into `reports_docs/`. Use the `rapport-academique` skill.

## Arguments

`$ARGUMENTS`

- `--chapter N` — redraft only chapter N. Leaves every other file untouched.
- `--section path` — redraft a single file.
- `--force` — overwrite files that have been modified since generation. Without
  it, modified files are skipped and reported.

## Before drafting

1. Read `reports_docs/report.yaml` for skeleton, language and page budget.
2. Read `reports_docs/BRIEF.md`. **If it is largely empty, stop and say so** —
   drafting without a brief produces confident generic prose that is worse than a
   blank page, because it reads as finished.
3. Read the skeleton's `outline.md` from the skill references.
4. Check `git status`. If `reports_docs/` has uncommitted changes, warn before
   overwriting anything.

## The rule that governs everything

**Anything in the brief or derivable from the repository may be drafted. Anything
else is emitted as a `[[TODO]]` or `[[METRIC]]` placeholder, never invented.**

Never fabricate: company names, supervisor names, dates, metrics, measured
results, client names, team sizes, or citations to papers you have not verified
exist.

| Draft freely from the repo | Requires the brief |
|---|---|
| Stack and its justification | Organisme d'accueil |
| Architecture, design, data model | Problématique |
| Implementation, difficult parts | Results and metrics |
| Tests and test strategy | Difficulties encountered |
| Chronogramme (git history) | Jury, dates, supervisors |

## Layout

```
reports_docs/
├── report.yaml
├── BRIEF.md
├── 00-page-de-garde.md
├── 01-remerciements.md
├── 01b-resume.md
├── 01c-abstract.md
├── 02-acronymes.md
├── 03-introduction-generale.md
├── 04-contexte-general/
│   ├── 01-organisme-accueil.md
│   ├── 02-etude-existant.md
│   ├── 03-problematique.md
│   └── 04-methodologie.md
├── 05-etat-de-l-art/
│   └── …
└── 99-conclusion-generale.md
```

One folder per chapter, one file per section. Numeric prefixes fix the order.

## Writing

- Follow `references/formulations.md` for chapter openings, handoffs and
  transitions. Vary them — do not open every chapter the same way.
- Follow `references/good-vs-weak.md` for the standard. A problématique must be a
  problem, not a task. An objective must be measurable. A state of the art must
  end in a positioning table.
- Use `references/placeholder-syntax.md` exactly. Every figure gets a `[[FIG:]]`
  and every figure must also be referenced in the prose with `[[REF:]]`.
- Respect the per-chapter page budget in `report.yaml`. Roughly 350 words per
  page.
- Open each chapter with a short introduction and close it with a handoff to the
  next.
- **Do not write the general introduction on the first pass.** Draft it last,
  after the chapters exist, and never let it state results.

## Finish

Report: files written, approximate pages per chapter against budget, count of
blocking placeholders, and the list of figures the user must prepare. Then tell
them to review the markdown and run `/report:review`.
