# Outline — PFE, research / R&D

Replace every `<...>` placeholder. Delete what does not apply.

---

## Front matter

Same as `01`. Résumé + mots-clés and Abstract + keywords both matter more here —
this is the version of your work that gets indexed and found.

## Introduction générale — 1 to 2 pages

- Scientific and applicative context
- The problem, stated precisely
- Objectives and research questions
- Contributions, in three or four bullets
- Announcement of the plan

> No results here.

---

## Chapitre 1 — Contexte général du projet

### 1.1 Organisme d'accueil
- Identity, activity, research or technical environment
- (Shorten aggressively. Two to four pages. This is not the subject of the report.)

### 1.2 Cadre applicatif
- The domain the problem lives in and why it matters
- Operational constraints that will shape the solution (latency budget, hardware,
  data availability, cost, regulation)

### 1.3 Problématique et objectifs
- The problem as a technical question
- Success criteria, defined *now*, before any result is shown

### 1.4 Méthodologie de conduite du projet
- Working method, iterations, tooling
- Planning

### Conclusion du chapitre

---

## Chapitre 2 — État de l'art

### 2.1 Fondements théoriques
- The concepts a reader needs and no more. Resist writing a textbook chapter.
  If you find yourself explaining backpropagation from scratch, cut it.

### 2.2 Revue des approches existantes
- Organised by family of approach, not chronologically
- For each: principle, strengths, limits, typical reported performance

### 2.3 Jeux de données et protocoles d'évaluation de référence
- Standard datasets and benchmarks in this problem space
- Metrics conventionally used, and their known weaknesses

### 2.4 Positionnement
- **Comparison table**: existing approaches × criteria that matter here
- Where the gap is
- What this work does that the reviewed approaches do not

> This section is not optional. It is what turns a literature list into a state
> of the art.

### Conclusion du chapitre

---

## Chapitre 3 — Méthodologie et conception de la solution

### 3.1 Vue d'ensemble de l'approche
- One diagram of the whole pipeline, end to end

### 3.2 Données
- Source and acquisition
- Volume, class distribution, known biases
- Annotation protocol, annotation tooling, inter-annotator agreement if relevant
- Cleaning and filtering rules
- **Split strategy** — train/validation/test, and how leakage was prevented
  (grouped splits, temporal splits, subject-level splits)

### 3.3 Prétraitement et augmentation
- Every transformation, in order, with parameters

### 3.4 Modèles retenus
- Architecture(s), with justification against the état de l'art
- Pretrained weights and their provenance
- Loss function and why

### 3.5 Protocole d'entraînement
- Hyperparameters, optimiser, schedule, epochs, batch size
- Early stopping and selection criterion
- Seeds and number of runs
- Hardware and training time

### 3.6 Protocole d'évaluation
- Metrics, defined formally
- Baselines: a trivial one and a prior-work one
- Statistical treatment (mean ± std over n runs)

### Conclusion du chapitre

---

## Chapitre 4 — Expérimentations et résultats

### 4.1 Environnement expérimental
- Hardware, framework versions, seeds

### 4.2 Résultats principaux
- Results table: your approach against every baseline, on the same protocol
- Curves (learning, ROC, PR) where they add something

### 4.3 Études d'ablation
- What each component contributes, removed one at a time

### 4.4 Analyse des erreurs
- Confusion matrix or equivalent
- Qualitative failure cases, with images or examples
- Is the error structured? On which subpopulation?

### 4.5 Discussion
- Interpretation of every result — **including the ones that contradict what you
  expected.** That is often where the interesting finding is.
- Comparison with figures reported in the literature, and the caveats of that
  comparison
- Limitations and threats to validity

### Conclusion du chapitre

---

## Chapitre 5 *(optional)* — Valorisation et démonstrateur

Include only if you built something on top of the model.

### 5.1 Architecture du démonstrateur
### 5.2 Intégration du modèle
### 5.3 Interface et cas d'usage
### 5.4 Retours utilisateurs, si applicable

---

## Conclusion générale et perspectives — max 2 pages

- Contributions restated against the objectives
- What the results establish, and what they do not
- Difficulties encountered
- Perspectives — the concrete next experiment, not "future work could explore..."

---

## Back matter

- Bibliographie (IEEE numbered style recommended)
- Annexes — full result tables, additional ablations, annotation guidelines,
  code listings, dataset samples
- Glossaire
