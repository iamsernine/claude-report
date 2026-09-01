# 03 — PFE, data / cloud with production deployment

**Use this when:** you both built a model or data pipeline *and* took it to
production — containerised it, deployed it on a cluster or edge device, wired up
monitoring. Typical of Big Data, Cloud Computing, and MLOps tracks.

This is `02-pfe-research-ml` with a deployment chapter and a slightly reweighted
état de l'art. It is the strongest shape for a data/cloud profile because it
demonstrates both research competence and production competence — which is
exactly the pair a jury and a recruiter are looking for.

## Shape

Six chapters, roughly 60–90 pages.

| Chapter | Answers |
|---|---|
| 1. Contexte général | What problem, in what operational setting? |
| 2. État de l'art | Modelling approaches *and* serving/infrastructure patterns |
| 3. Architecture de la solution | How do data, model and infrastructure fit together? |
| 4. Modélisation et expérimentations | Does the model work? |
| 5. Industrialisation et déploiement | Does it work in production? |
| 6. Évaluation opérationnelle | Does it keep working, and at what cost? |

## The trap

Splitting the report into "half research, half DevOps" with no thread between
them. The two halves must be joined by *constraints*: the latency budget, the
memory ceiling on the target device, the cost per thousand inferences, the
retraining cadence. Those constraints should be stated in Chapter 1, drive model
choices in Chapter 4, and be verified in Chapter 6. If a reader can remove either
half without the other collapsing, the report is two reports.

## Additional jury questions

- What happens when the input distribution shifts?
- What is the rollback path if a new model version is worse?
- What does one inference cost, and what does one retraining cycle cost?
- How is the model versioned alongside the data it was trained on?
- What is monitored, and what triggers an alert?

See `outline.md` for the fill-in structure.
