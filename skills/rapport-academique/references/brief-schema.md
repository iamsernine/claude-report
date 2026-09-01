# The brief

`reports_docs/BRIEF.md` holds everything the report needs that is not in the
code. It is the single most important file in the workflow.

## Why it exists

Claude can read a repository and describe an architecture, a stack, a test suite,
and a commit history. It cannot know the host organisation, the problématique,
the supervisor's name, the measured results, or what went wrong in week six.

Without a brief, a drafting command will produce those sections anyway, in
fluent generic French. That output is worse than a blank page because it reads as
finished, and a student under deadline pressure will ship it.

So: **anything in the brief may be used in drafting. Anything absent from the
brief and absent from the repository is emitted as a `[[TODO]]` or `[[METRIC]]`
placeholder, never invented.** This rule is not negotiable and applies to every
command in this package.

## Structure

`/report:init` generates this file, pre-filling what it can infer from the
repository and leaving the rest as explicit questions.

```markdown
# Brief

## Métadonnées
- Type: pfe | pfa | stage-initiation | stage-technicien | module | memoire
- Établissement:
- Filière:
- Année universitaire:
- Auteur(s):
- Encadrant académique:
- Encadrant entreprise:
- Jury:
- Date de soutenance:
- Langue: fr | en

## Organisme d'accueil
- Nom:
- Secteur d'activité:
- Effectif / taille:
- Service d'accueil:
- Activité du service:

## Le projet
- Titre:
- Problématique (un paragraphe):
- Objectifs:
- Périmètre inclus:
- Périmètre exclu:
- Durée:
- Date de début (AAAA-MM-JJ):
- Date de fin (AAAA-MM-JJ):

## Contraintes chiffrées
<!-- These are the thread of the whole report. Numbers, not adjectives. -->
- Latence / temps de réponse cible:
- Volumétrie:
- Budget matériel ou coût:
- Contraintes réglementaires:

## Existant
- Comment le processus fonctionne aujourd'hui:
- Faiblesses constatées (chiffrées si possible):

## Résultats
- Baseline de référence:
- Résultats obtenus:
- Protocole d'évaluation:

## Difficultés et limites
- Difficultés rencontrées:
- Limites du travail:
- Perspectives:

## Notes libres
<!-- Anything else. Supervisor remarks, constraints, anecdotes worth including. -->
```

## Filling it

Sections may be left empty. Every empty section becomes a placeholder in the
draft rather than an error — the point is to make the gap visible, not to block
progress. `/report:status` reports brief completeness as a percentage.

Fill `Contraintes chiffrées` early even if the numbers are rough. They shape
technology justifications throughout the report, and retrofitting them later
means rewriting several sections.
