# Outline — PFE, software engineering

Replace every `<...>` placeholder. Delete sections that do not apply rather than
padding them.

Headings are given in French with the English equivalent alongside. They are the
same structure: pick the column matching `lang:` in `report.yaml` and stay in
it. Nothing else about the plan, the proportions or the review checks changes
with language.

---

## Front matter

- Page de garde — *obligatoire*
- Dédicaces — *facultatif*
- Remerciements — *obligatoire*
- Résumé / Abstract in the report's language + mots-clés / keywords —
  *obligatoire*, 150–250 words, 5–7 keywords. It must stand alone: objective,
  method, results, main conclusion.
- A second abstract in the other language — *strongly recommended*, and often
  required even for an English report
- Sommaire / table des matières — *obligatoire*
- Liste des figures — *if any*
- Liste des tableaux — *if any*
- Liste des abréviations et acronymes — *if any*

## Introduction générale — 1 to 2 pages

- Sector context in two or three sentences
- The problem
- Objectives of the project
- Host organisation and duration of the internship
- Announcement of the plan (one sentence per chapter)

> Never state the results here. Write this section last.

---

## Chapitre 1 — Contexte général du projet
*(en: Introduction and Context)*

### 1.1 Présentation de l'organisme d'accueil
- Identity, activity, market position
- Organigramme, and where your team sits in it
- Technical environment already in place

### 1.2 Étude de l'existant
- How the process works today
- **Critique de l'existant** — concrete, named weaknesses, ideally quantified
  (time lost, error rate, cost, manual steps)

### 1.3 Problématique
- One paragraph. State it as a question if that sharpens it.

### 1.4 Objectifs du projet
- Functional objectives
- Explicit scope and out-of-scope

### 1.5 Méthodologie et conduite de projet
- Development process chosen (Scrum, 2TUP, XP, cascade) and **why**
- Sprints or phases
- Gantt / chronogramme
- Tools used to run the project

### Conclusion du chapitre

---

## Chapitre 2 — Analyse et spécification des besoins
*(en: Problem Analysis and Requirements)*

### 2.1 Étude comparative des solutions existantes
- Two to four existing products or approaches
- Comparison table on criteria that matter to *this* problem
- Why none of them is sufficient

### 2.2 Identification des acteurs
### 2.3 Besoins fonctionnels
- Grouped by module or by actor
- Numbered (BF-01, BF-02...) so you can trace them later

### 2.4 Besoins non fonctionnels
- Performance, security, availability, maintainability, portability, UX
- Give numbers where you can; "the system must be fast" is not a requirement

### 2.5 Modélisation des besoins
- Diagramme de cas d'utilisation global
- Refined use case diagrams per module
- Textual description of the two or three critical use cases (nominal flow,
  alternative flows, preconditions, postconditions)

### Conclusion du chapitre

---

## Chapitre 3 — Conception
*(en: Design)*

### 3.1 Architecture générale
- Style and justification (n-tier, MVC, microservices, event-driven)
- Deployment view

### 3.2 Conception statique
- Diagramme de classes
- Dictionnaire de données

### 3.3 Conception dynamique
- Sequence diagrams for the critical use cases
- Activity or state diagrams where behaviour is non-obvious

### 3.4 Conception de la base de données
- Logical schema
- Physical schema, indexes, constraints

### 3.5 Conception des interfaces
- Navigation map
- Wireframes / maquettes

### Conclusion du chapitre

---

## Chapitre 4 — Réalisation et tests
*(en: Implementation, Testing and Evaluation)*

### 4.1 Environnement de travail
- Hardware
- Software, with versions

### 4.2 Choix technologiques
- Stack, layer by layer, each with a justification tied back to a requirement

### 4.3 Mise en œuvre
- Architecture of the codebase
- The two or three genuinely difficult parts, explained. Not a walkthrough of
  every file.

### 4.4 Présentation de l'application
- Screenshots of the key screens, captioned, readable

### 4.5 Tests
- Test strategy (unit, integration, acceptance)
- Test cases table with expected and obtained results
- Performance results if relevant

### 4.6 Déploiement
- Target environment, CI/CD, containerisation if used

### Conclusion du chapitre

---

## Conclusion générale et perspectives — max 2 pages
*(en: Conclusion and Future Work)*

- What was accomplished, against the objectives stated in the introduction
- Contributions to the host organisation
- Difficulties encountered and their effect on the outcome
- Limitations, stated honestly
- Perspectives — concrete next steps, not vague ambition
- One short paragraph on personal and technical skills gained

---

## Back matter

- Bibliographie / References — IEEE or ACM style for computing work
- **Annexe A — Manuel utilisateur** *(en: Appendix A — User Manual)*
- **Annexe B — Reprise du projet** *(en: Appendix B — Project Legacy)* — what a
  successor needs to pick this up: repository layout, environment setup, known
  issues, unfinished threads, credential handling, who to ask
- Annexe C — extraits de code / source code excerpts
- Annexe D — résultats bruts / raw results
- Glossaire, if the domain needs one
