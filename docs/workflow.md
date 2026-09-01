# Workflow — worked example

A PFE on weed detection deployed to a Jetson Nano, from empty repo to compiling
PDF.

## 0. Starting point

```
~/projects/weed-detection/
├── src/           training, inference, preprocessing
├── notebooks/     exploration, three result plots
├── deploy/        Dockerfile, k8s manifests
├── tests/
└── README.md
```

## 1. Set up

```
/report:init --type pfe
```

Claude reads the repo, sees a training pipeline *and* a deploy folder, and asks
one question: does the report cover the deployment as well as the model? Yes →
skeleton `03-pfe-data-cloud-deployment`.

It then reports something like:

```
Squelette   03-pfe-data-cloud-deployment  (le déploiement fait partie du travail)
Budget      65 pages

Ch. 1 Contexte général            8 p
Ch. 2 État de l'art              10 p
Ch. 3 Architecture                9 p
Ch. 4 Modélisation               16 p
Ch. 5 Industrialisation          12 p
Ch. 6 Évaluation opérationnelle   8 p

Figures    ~22 estimées
  déjà disponibles (3)   notebooks/eda.ipynb fig 2, fig 5 ; deploy/archi.png
  à produire (19)        organigramme, pipeline de données, matrice de confusion,
                         courbes d'apprentissage, dashboard Grafana…

Chronogramme (git log, 2026-02-03 → 2026-06-12)
  Phase 1  03/02 – 21/02  exploration et collecte
  Phase 2  24/02 – 03/04  entraînement et itérations
  Phase 3  07/04 – 15/05  conteneurisation et déploiement
  Phase 4  18/05 – 12/06  monitoring et rédaction

Brief      6/24 champs pré-remplis
Manquant   organisme, problématique, contraintes chiffrées, encadrants, jury,
           résultats mesurés, difficultés
```

## 2. Fill the brief

Open `reports_docs/BRIEF.md`. Fill it in French, in whatever register — it is
input, not prose. Prioritise:

- The problématique in one paragraph
- **Contraintes chiffrées.** These thread the entire report: they are stated in
  chapter 1, drive the model choice in chapter 4, and are verified in chapter 6.
  Retrofitting them later means rewriting several sections.
- The results, with baselines

Twenty minutes here saves several hours later.

## 3. Draft

```
/report:draft
```

Produces `reports_docs/` with one folder per chapter. Read it. It will be wrong
in places — that is expected, it is a scaffold. Edit the markdown directly.

Redraft a single chapter after updating the brief:

```
/report:draft --chapter 4
```

Files you have edited are skipped unless you pass `--force`.

## 4. Review

```
/report:review
```

Typical first pass:

```
BLOQUANT (3)
  Ch. 2 occupe 31 % du corps. L'état de l'art dépasse la contribution.
        → couper 2.3 (rappels sur les CNN, 4 p) et 2.4 (historique de YOLO, 3 p)
  Ch. 2 aucun tableau de positionnement — l'écart comblé n'est jamais nommé
  Ch. 4 résultats sans baseline

À CORRIGER (5)
  'matrice-confusion' déclarée mais jamais référencée dans le texte
  Ch. 3 ne conclut pas vers le chapitre 4
  …

Action prioritaire : ajouter le tableau de positionnement en 2.5. C'est la
faiblesse la plus visible en soutenance pour un sujet IA.
```

Fix, rerun. Iterate until only warnings remain.

## 5. Build

```
/report:build
```

First run usually refuses:

```
BLOQUÉ — 4 placeholder(s) METRIC/TODO non résolu(s)
  04-modelisation/03-resultats.md:22  [[METRIC]] mAP@0.5 sur le jeu de test final
  …
```

Fill them from your actual results, or build a draft:

```
/report:build --allow-todo
```

You get `build/main.pdf` — 62 pages, correct pagination, table of contents, every
figure a labelled grey box. **This is the moment the report becomes real.**

## 6. Replace the figures

`build/figures/MANIFEST.md`:

```
| Slug | Légende | Chapitre | Largeur min. | État |
| `architecture-globale` | Architecture générale | 03-architecture | 1440 px | à fournir |
| `matrice-confusion`    | Matrice de confusion  | 04-modelisation | 1280 px | à fournir |
```

Produce each one, name it exactly `<slug>.png`, drop it into `build/figures/`.
Rebuild. No LaTeX edits.

## 7. Overleaf

Upload the whole `build/` folder. Settings → Compiler: pdfLaTeX, Bibliography:
Biber. Compile.

## Iterating

The loop is `draft → edit → review → build`. Nothing is one-shot. Expect four or
five review passes on a PFE.

Commit `reports_docs/` to git. It is your work; `build/` is disposable and
belongs in `.gitignore`.
