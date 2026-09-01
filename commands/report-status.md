---
description: Show report progress — pages against budget, brief completeness, blocking placeholders, figures outstanding
allowed-tools: Read, Glob, Bash
---

Report the current state of the report. Read-only — change nothing.

## Steps

1. Read `reports_docs/report.yaml` for type, skeleton and budget.
2. Compute brief completeness: filled fields over total fields in `BRIEF.md`.
3. Run `python3 scripts/review.py reports_docs --json`.
4. Count figures: declared, placeholder still in use, real image supplied.

## Output

A compact table, nothing more:

```
Type            PFE — 03-data-cloud-deployment (fr)
Brief           18/24 champs renseignés (75 %)

Chapitre                          Pages    Cible   État
1. Contexte général                 9.2     8–10   ok
2. État de l'art                   14.1    10–12   dépassement
3. Architecture                     6.8     8–10   incomplet
4. Modélisation                     0.0    12–15   non rédigé

Total corps                        30.1    50–60

Placeholders bloquants   4
Figures                  17 déclarées, 3 fournies, 14 à produire
Citations à sourcer      9

Prochaine action : rédiger le chapitre 4 (/report:draft --chapter 4)
```

End with one concrete next action.
