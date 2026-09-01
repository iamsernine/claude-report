# Good vs. weak — worked pairs

Descriptions of quality do not transfer. Examples do. Use these as the standard
when drafting and when reviewing.

---

## Problématique

**✗ Weak** — a task description wearing the word "problématique":

> Développer une application web de gestion de stock pour l'entreprise X.

**✓ Strong** — a problem that exists whether or not anyone builds anything:

> Les niveaux de stock sont rapprochés manuellement entre les trois sites de
> l'entreprise, à raison d'un relevé hebdomadaire consolidé sous Excel. Ce
> processus introduit un décalage moyen de 12 jours entre l'état réel et l'état
> connu, à l'origine de 14 ruptures d'approvisionnement sur le dernier exercice.

The test: could someone propose a *different* solution to your problématique? If
not, you have written a brief.

---

## Objectif

**✗ Weak** — restates the task, unmeasurable:

> Améliorer les performances du système.

**✓ Strong** — measurable, with a target that can be verified in the results:

> Ramener le temps d'inférence sous 100 ms par image sur Jetson Nano, sans perte
> de mAP@0.5 supérieure à 2 points par rapport au modèle de référence.

---

## Besoin non fonctionnel

**✗ Weak:**

> Le système doit être rapide et sécurisé.

**✓ Strong:**

> Le système doit répondre en moins de 300 ms au 95e percentile pour 50
> utilisateurs simultanés, et l'authentification doit reposer sur des jetons
> JWT d'une durée de validité de 15 minutes avec rotation du jeton de
> rafraîchissement.

---

## Positionnement (état de l'art)

**✗ Weak** — a literature list that stops before doing any work:

> Plusieurs approches ont été proposées. Redmon et al. ont introduit YOLO. Ren et
> al. ont proposé Faster R-CNN. Liu et al. ont proposé SSD. Ces approches ont
> chacune leurs avantages et leurs inconvénients.

**✓ Strong** — a comparison against criteria that matter *here*, ending in a gap:

> | Approche | mAP@0.5 | Latence (Jetson Nano) | Taille | Données requises |
> |---|---|---|---|---|
> | Faster R-CNN | 0.87 | 780 ms | 168 Mo | ~10k images |
> | SSD-MobileNet | 0.71 | 45 ms | 27 Mo | ~5k images |
> | YOLOv8n | 0.83 | 62 ms | 6 Mo | ~5k images |
>
> Aucune de ces approches n'a été évaluée sur des cultures maraîchères en
> conditions d'éclairage variables, et les jeux de données publics du domaine ne
> couvrent pas les espèces adventices présentes dans la région. C'est cet écart
> que le présent travail adresse.

**This section is what distinguishes an état de l'art from a bibliography.** Its
absence is the most common weakness in AI-track reports.

---

## Résultats

**✗ Weak** — a number with nothing to compare it to:

> Le modèle atteint une précision de 91 %.

**✓ Strong** — baselines, protocol, variance:

> | Modèle | mAP@0.5 | Écart-type (5 runs) |
> |---|---|---|
> | Baseline triviale (classe majoritaire) | 0.34 | — |
> | YOLOv8n pré-entraîné, sans fine-tuning | 0.61 | 0.00 |
> | YOLOv8n fine-tuné (ce travail) | 0.83 | ±0.014 |
>
> Les résultats sont obtenus sur le jeu de test de 1 240 images, disjoint au
> niveau des parcelles pour éviter toute fuite d'information entre
> apprentissage et test.

---

## Critique de l'existant

**✗ Weak** — an inventory:

> L'entreprise utilise actuellement un fichier Excel pour la gestion des stocks.

**✓ Strong** — an actual critique, with consequences:

> La gestion repose sur un classeur Excel partagé, sans verrouillage concurrent.
> Trois personnes y accèdent simultanément, ce qui produit régulièrement des
> écrasements silencieux de saisie. L'absence d'historique rend par ailleurs
> impossible tout audit a posteriori d'un écart d'inventaire.

---

## Limite

**✗ Weak** — a limitation that is really a boast:

> La principale limite de ce travail est qu'il pourrait être étendu à d'autres
> domaines.

**✓ Strong** — a limitation that a jury would otherwise raise first:

> Le jeu de test provient d'une seule exploitation et d'une seule saison. Les
> performances rapportées ne garantissent donc pas la robustesse du modèle face
> à un changement de variété cultivée ou de conditions d'éclairage saisonnières.
> Une validation multi-sites reste nécessaire avant tout déploiement.

Naming the weakness before the jury does reads as maturity. Hiding it reads as
not having noticed.
