# Outline — PFE, data / cloud with deployment

---

## Front matter

Same as `01`. Include the English abstract.

## Introduction générale — 1 to 2 pages

Context, problem, objectives (both modelling and operational), contributions,
plan.

---

## Chapitre 1 — Contexte général et cadrage

### 1.1 Organisme d'accueil — short
### 1.2 Contexte métier et enjeux
### 1.3 Problématique
### 1.4 Objectifs
- Modelling objectives
- **Operational constraints, quantified** — latency budget, throughput, memory
  ceiling, cost envelope, availability target, data residency. These are the
  thread that ties the whole report together; state them here as numbers.

### 1.5 Méthodologie et planification
### Conclusion du chapitre

---

## Chapitre 2 — État de l'art

### 2.1 Fondements théoriques
### 2.2 Approches de modélisation existantes
### 2.3 Architectures de données et patrons de déploiement
- Batch vs streaming, lambda/kappa, feature stores
- Serving patterns: online, batch, edge
- Orchestration and MLOps tooling landscape

### 2.4 Positionnement
- Comparison table covering **both** modelling and infrastructure criteria
- The gap this work fills

### Conclusion du chapitre

---

## Chapitre 3 — Architecture de la solution

### 3.1 Vue d'ensemble
- One end-to-end diagram: ingestion → storage → processing → training → registry
  → serving → monitoring

### 3.2 Architecture de données
- Sources, ingestion, storage layer, partitioning, schema and its evolution
- Data quality gates

### 3.3 Architecture applicative et d'infrastructure
- Cloud or on-prem components, and why
- Containerisation, orchestration
- Networking and security posture

### 3.4 Choix technologiques
- Each component justified against a constraint stated in 1.4

### Conclusion du chapitre

---

## Chapitre 4 — Modélisation et expérimentations

Compress `02`'s chapters 3 and 4 into one, keeping the reproducibility content.

### 4.1 Données — collection, annotation, splits, leakage control
### 4.2 Prétraitement
### 4.3 Modèles et protocole d'entraînement
- Hyperparameters, seeds, hardware, training time
### 4.4 Protocole d'évaluation et baselines
### 4.5 Résultats et ablations
### 4.6 Optimisation pour la cible
- Quantisation, pruning, distillation, ONNX/TensorRT export
- **Accuracy/latency/size trade-off table** — this is the bridge to Chapter 5
### 4.7 Analyse des erreurs et discussion
### Conclusion du chapitre

---

## Chapitre 5 — Industrialisation et déploiement

### 5.1 Pipeline d'entraînement automatisé
- Orchestration, triggers, retraining cadence
### 5.2 Versionnement
- Code, data, and model versioning; how a model is traced back to its training data
### 5.3 Registre de modèles et promotion
- Staging → production, approval gates, rollback path
### 5.4 Service d'inférence
- API contract, scaling policy, cold start behaviour
### 5.5 CI/CD
- Build, test, deploy stages; what blocks a release
### 5.6 Sécurité et conformité
- Secrets, access control, data protection
### Conclusion du chapitre

---

## Chapitre 6 — Évaluation opérationnelle

### 6.1 Observabilité
- Metrics, logs, traces; dashboards; alert rules
### 6.2 Performance en production
- Latency percentiles (p50/p95/p99), throughput, error rate
- Measured against the budget set in 1.4
### 6.3 Détection de dérive
- Data drift and concept drift monitoring; thresholds and response
### 6.4 Coûts
- Cost per inference, per training run, monthly run rate
### 6.5 Tests de charge et résilience
### 6.6 Discussion et limites
### Conclusion du chapitre

---

## Conclusion générale et perspectives — max 2 pages

---

## Back matter

- Bibliographie
- Annexes — infrastructure-as-code excerpts, full metric tables, API
  specification, runbook, cost model
- Glossaire
