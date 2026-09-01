# PFE / PFA report skeletons

Report structures for engineering projects in IT — PFE, PFA, and ordinary
project reports — assembled from published institutional writing guides and a
sample of real reports from Moroccan and Tunisian engineering schools.

Six skeletons, shared formatting reference, and a Claude Skill that applies all
of it.

## Pick a skeleton

| | Use it when | Length |
|---|---|---|
| [`01-pfe-software-engineering`](skeletons/01-pfe-software-engineering) | PFE building an application for a company | 50–70 p |
| [`02-pfe-research-ml`](skeletons/02-pfe-research-ml) | PFE whose deliverable is a model, pipeline or experimental result | 50–80 p |
| [`03-pfe-data-cloud-deployment`](skeletons/03-pfe-data-cloud-deployment) | PFE that both builds a model **and** ships it to production | 60–90 p |
| [`04-pfa-annual-project`](skeletons/04-pfa-annual-project) | End-of-year project, 3rd or 4th year | 25–40 p |
| [`05-module-project`](skeletons/05-module-project) | Course project / mini-projet, no company | 12–25 p |
| [`06-capstone-en`](skeletons/06-capstone-en) | Written in English, international programme | 40–70 p |

Each folder has a `README.md` explaining when the skeleton fits and what the jury
tests, plus an `outline.md` you fill in.

### Decision shortcut

```
Is there a host company?
├── No  → is it a full-year project?
│         ├── No  → 05-module-project
│         └── Yes → 04-pfa-annual-project
└── Yes → what is the deliverable?
          ├── An application            → 01-pfe-software-engineering
          ├── A model or a finding      → 02-pfe-research-ml
          └── A model, in production    → 03-pfe-data-cloud-deployment

Writing in English? → 06-capstone-en (or translate 02 for a thesis)
```

## Shared reference

Applies to all six. Read these once.

- [`reference/formatting-standards.md`](reference/formatting-standards.md) —
  typography, margins, pagination, figure and table conventions, citation styles.
  Two competing standards (UCA-style and ASIIN-aligned), compared.
- [`reference/length-and-proportions.md`](reference/length-and-proportions.md) —
  the 1/5 – 3/5 – 1/5 rule, hard caps, what belongs in the annexes.
- [`reference/defense-checklist.md`](reference/defense-checklist.md) — slide
  budget, grading split, question preparation.
- [`reference/common-pitfalls.md`](reference/common-pitfalls.md) — 21 ways to
  lose marks, ordered by frequency.
- [`reference/sources.md`](reference/sources.md) — where all of this comes from.
- [`templates/page-de-garde.md`](templates/page-de-garde.md) — title page and
  abstract templates.

## Claude Skill

[`skills/rapport-pfe`](skills/rapport-pfe) packages this repository as a Claude
Skill, so Claude picks the right skeleton, applies the formatting rules, and
reviews drafts against the pitfalls list without being told any of it each time.

Install:

```bash
cd skills
zip -r rapport-pfe.skill rapport-pfe
```

Then upload `rapport-pfe.skill` in Claude → Settings → Capabilities → Skills.

Rebuild its bundled references after editing anything in `skeletons/` or
`reference/`:

```bash
./skills/build.sh
```

## Two caveats

**Your department's template wins.** Where these skeletons and your official
guide disagree, follow the guide. Everything here is a starting structure and a
checklist, not a regulation.

**Structure is not content.** A perfectly structured report with a thin
contribution still gets a thin grade. The proportions rule exists precisely to
stop structure from substituting for substance.

## License

MIT. Use it, fork it, adapt it for your school.
