# 02 — PFE, research / R&D (AI, data science, computer vision)

**Use this when:** the deliverable is a model, a pipeline, a benchmark, an
algorithm, or an experimental finding — not an application. Typical subjects:
detection or classification models, NLP pipelines, forecasting, anomaly
detection, recommender systems, embedded/edge inference.

**Do not use this when:** you built a CRUD application. Use
`01-pfe-software-engineering`. If you built a model *and* shipped it to
production, use `03-pfe-data-cloud-deployment`.

## Why the software plan breaks here

Plan A's design chapter assumes the intellectual work is structural — classes,
sequences, schemas. In a research project the intellectual work is in the
*protocol*: what data, what baseline, what metric, what comparison. Forcing it
into a UML chapter hides exactly what the jury needs to evaluate.

## Shape

Five chapters, roughly 50–80 pages.

| Chapter | Answers |
|---|---|
| 1. Contexte général | What problem, in what setting? |
| 2. État de l'art | What has been tried, and where does this work sit? |
| 3. Méthodologie | What exactly did you do, reproducibly? |
| 4. Expérimentations et résultats | What happened, and what does it mean? |
| 5. Application / valorisation *(optional)* | What can be done with it? |

## The two things that decide your grade

**Positioning.** The état de l'art must end with a comparative analysis placing
your work against existing solutions. A list of papers with no positioning is the
single most common weakness in AI-track PFEs.

**Reproducibility.** The methodology must be complete enough for a competent
reader to reproduce your approach — the validity of the whole report rests on it.
That means hyperparameters, data splits, seeds, hardware, and library versions,
not prose about "training the model".

## Additional jury questions to expect

- What is your baseline, and why is it a fair one?
- How did you split the data? Is there leakage between train and test?
- Why this metric? What does it hide?
- How many runs? What is the variance?
- What does the model get wrong, and is the error structured?

See `outline.md` for the fill-in structure.
