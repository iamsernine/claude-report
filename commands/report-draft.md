---
description: Draft the report chapters as markdown files with typed placeholders
argument-hint: "[--chapter N] [--section path] [--force]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

Draft the report into `reports_docs/`. Use the `rapport-academique` skill.

## Plugin root — mandatory

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}"
if [ -z "$ROOT" ] || [ ! -f "$ROOT/scripts/cli.py" ]; then
  for cand in \
    "$HOME/.claude/plugins/claude-report" \
    "$HOME/.claude/plugins/pfe-report-skeletons"; do
    [ -f "$cand/scripts/cli.py" ] && ROOT="$cand" && break
  done
fi
python3 "$ROOT/scripts/cli.py" guard reports_docs
```

The JSON lists `skip` (student-edited or unstamped — do not overwrite),
`writable` (still match the generation stamp), and `unstamped`.

## Arguments

`$ARGUMENTS`

- `--chapter N` — redraft only chapter N. Leaves every other file untouched.
- `--section path` — redraft a single file.
- `--force` — overwrite files that have been modified since generation. Without
  it, modified **and** unstamped files are skipped and reported.

## Before drafting

1. Read `reports_docs/report.yaml` for skeleton, language and page budget.
2. Read `reports_docs/BRIEF.md`. **If it is largely empty, stop and say so** —
   drafting without a brief produces confident generic prose that is worse than a
   blank page, because it reads as finished.
3. Read the skeleton's `outline.md` from the skill references.
4. Run the guard command above. Also check `git status`. Files you (the student)
   have edited are never silently overwritten, **including when `reports_docs/`
   is not tracked by git** — protection is a SHA-256 sidecar
   (`*.md.generated`), not git alone.

## The rule that governs everything

**Anything in the brief or derivable from the repository may be drafted. Anything
else is emitted as a `[[TODO]]` or `[[METRIC]]` placeholder, never invented.**

Never fabricate: company names, supervisor names, dates, metrics, measured
results, client names, team sizes, or citations to papers you have not verified
exist. Never copy secrets, tokens, or `.env` values into the report.

| Draft freely from the repo | Requires the brief |
|---|---|
| Stack and its justification | Organisme d'accueil |
| Architecture, design, data model | Problématique |
| Implementation, difficult parts | Results and metrics |
| Tests and test strategy | Difficulties encountered |
| Chronogramme (git history **inside period_start/end**) | Jury, dates, supervisors |

## Heading convention (required for a correct PDF)

- A **chapter folder** does not repeat the chapter title as an `#` heading in
  every file. `build.py` emits `\chapter{…}` from `report.yaml`.
- Inside a chapter file, `#` is a **section** (`\section`), `##` a subsection.
- Introduction, conclusion and annexes are unnumbered (`kind: intro|conclusion|annex`).
- Do not invent extra chapters because a PFE outline listed them.

## Layout

```
reports_docs/
├── report.yaml
├── BRIEF.md
├── 00-page-de-garde.md
├── 00b-declaration-integrite.md
├── 01-remerciements.md
├── 01b-resume.md
├── 01c-abstract.md
├── 02-acronymes.md
├── 03-introduction-generale.md          kind: intro (rédiger en dernier)
├── 04-contexte-et-cadrage/
│   ├── 01-organisme-accueil.md
│   ├── 02-etude-existant.md
│   ├── 03-problematique.md
│   └── 04-methodologie.md
└── 99-conclusion-generale.md
```

One folder per chapter, one file per section. Numeric prefixes fix the order.

## Writing

- Follow `references/formulations.md` for chapter openings, handoffs and
  transitions. Vary them — do not open every chapter the same way.
- Follow `references/good-vs-weak.md` for the standard. A problématique must be a
  problem, not a task. An objective must be measurable. An état de l'art must
  end in a positioning table (brief for a PFA; substantial for a PFE).
- Use `references/placeholder-syntax.md` exactly. Prefer stable cites:
  `[[CITE: knuth84 | Knuth, 1984]]`. Every figure gets a `[[FIG:]]` and every
  figure must also be referenced with `[[REF:]]`.
- Respect the per-chapter page budget in `report.yaml`. Roughly 350 words per
  page.
- Open each chapter with a short introduction and close it with a handoff to the
  next.
- **Do not write the general introduction on the first pass.** Draft it last,
  after the chapters exist, and never let it state results.

After writing each new or replaced file:

```bash
python3 "$ROOT/scripts/cli.py" guard --stamp reports_docs/<path>.md
```

Without that stamp, the next draft will treat the file as student-owned and skip it.

## Finish

Report: files written, files skipped (and why), approximate pages per chapter
against budget, count of blocking placeholders, and the list of figures the user
must prepare. Then tell them to review the markdown and run `/report:review`.
