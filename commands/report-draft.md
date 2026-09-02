---
description: Draft the report chapters as markdown, filling only what the repo, the brief and the supplied sources actually contain
argument-hint: "[--chapter N] [--section path] [--force]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

Draft `reports_docs/` as markdown the user reads and confirms. Use the
`rapport-academique` skill.

Markdown is the deliverable of this command. LaTeX comes later, from
`/report:build`, and only once the user has signed the markdown off.

## Plugin root

Scripts live **in this plugin**, never in the student's repository — do not run
`python3 scripts/cli.py` from the project cwd. `$CLAUDE_PLUGIN_ROOT` is set for you on a
correctly installed plugin; the fallback line covers a manual install. If `$CR`
is empty, the plugin is not installed — say so and stop rather than guessing.

```bash
CR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/claude-report}/scripts/cli.py"
[ -f "$CR" ] || CR=$(ls -1 "$HOME"/.claude/{plugins,skills}/claude-report/scripts/cli.py "$HOME"/.claude/plugins/cache/*/claude-report/*/scripts/cli.py 2>/dev/null | head -1)
CRROOT=$(dirname "$(dirname "$CR")")
python3 "$CR" guard reports_docs
```

The JSON lists `skip` (student-edited or unstamped — do not overwrite),
`writable` (still match the generation stamp), and `unstamped`.

## Arguments

`$ARGUMENTS`

- `--chapter N` — redraft only chapter N. Leaves every other file untouched.
- `--section path` — redraft a single file.
- `--force` — overwrite files modified since generation. Without it, modified
  **and** unstamped files are skipped and reported.

## Where every sentence must come from

Three sources, in this order. Nothing else is permitted.

| Rank | Source | Holds |
|---|---|---|
| 1 | **The repository** | Stack, architecture, data model, API surface, tests, dependencies, chronogramme from `git log` inside `period_start`/`period_end` |
| 2 | **`reports_docs/BRIEF.md`** | What only the student knows: host organisation, problématique, objectives, measured results, difficulties, supervisors, dates |
| 3 | **`reports_docs/sources/`** | Documents the student dropped in to close a gap — PDFs, Markdown, text |

**Anything absent from all three is emitted as `[[TODO]]` or `[[METRIC]]`, never
written as prose.** No exceptions, no plausible filler, no "typically, companies
in this sector…". A visible gap is always better than an invisible fabrication:
the student can fix a `[[TODO]]`, and will ship a fabricated sentence without
noticing it.

Never invent: company names, supervisor or jury names, dates, headcounts,
metrics, measured results, client names, or citations to papers you have not
verified exist. Never copy secrets, tokens or `.env` values into the report.

## Before drafting

1. Read `reports_docs/report.yaml` for skeleton, `lang` and page budget. Write
   every heading and every sentence in `lang`, and do not mix languages across
   files. `lang` changes wording only — never the skeleton, the chapter count or
   the proportions.
2. Read `reports_docs/BRIEF.md`.
3. Read the supplied documents:

   ```bash
   python3 "$CR" sources reports_docs
   ```

   This inventories `reports_docs/sources/` and converts PDFs to text you can
   read (`sources/.extracted/*.txt`). Read every file it marks `[+]`, and use
   what they contain the same way you use the brief. Report anything marked
   `[-]` to the user — an unreadable source must never look like one you chose
   to ignore. Files that look like credentials are skipped and stay skipped.
4. Read the skeleton's `outline.md` from the skill references.
5. Run the guard command above, and check `git status`. Files the student edited
   are never silently overwritten, **including when `reports_docs/` is not
   tracked by git** — protection is a SHA-256 sidecar (`*.md.generated`), not
   git alone.

## The loop this command sits in

Drafting is iterative, and stopping to ask for one missing fact at a time wastes
the student's time. Instead:

1. Draft **everything you can** from the three sources. Do not stall a whole
   chapter because one number is missing.
2. Mark every gap in place with `[[TODO: …]]` / `[[METRIC: …]]`.
3. Finish by listing what is still missing:

   ```bash
   python3 "$CR" gaps reports_docs
   ```

4. **When a supplied source answers a brief field, write the answer into
   `BRIEF.md`.** The brief stays the single record of what is known, so the fact
   survives into the next run instead of being re-derived from a PDF every time.
   Quote or summarise faithfully; do not extrapolate beyond what the document
   says, and note which source it came from.
5. Tell the user, concretely, **which document would close which gap** — "the
   company presentation deck would fill Organisme d'accueil", "the evaluation
   export would fill Results". Ask them to fill `BRIEF.md` or drop those files
   into `reports_docs/sources/`.
6. They run `/report:draft` again. Only the placeholders that new material can
   resolve get rewritten; confirmed text is protected by the guard.

Repeat until `gaps` is empty and the markdown reads correctly. **Only then**
does `/report:build` make sense.

## Heading convention (required for a correct PDF)

- A **chapter folder** does not repeat the chapter title as an `#` heading in
  every file. `build.py` emits `\chapter{…}` from `report.yaml`.
- Inside a chapter file, `#` is a **section** (`\section`), `##` a subsection.
- Introduction, conclusion and annexes are unnumbered
  (`kind: intro|conclusion|annex`).
- Do not invent extra chapters because an outline listed them.

## Layout

```
reports_docs/
├── report.yaml
├── BRIEF.md
├── sources/                             ← documents the student drops in
│   └── .extracted/                      ← text pulled out of PDFs, generated
├── 00-page-de-garde.md
├── 00b-declaration-integrite.md
├── 01-remerciements.md                  01-acknowledgements.md
├── 01b-resume.md                        01b-abstract.md
├── 02-acronymes.md                      02-acronyms.md
├── 03-introduction-generale.md          03-introduction.md      kind: intro
├── 04-contexte-et-cadrage/              04-context/
│   ├── 01-organisme-accueil.md          │   ├── 01-host-organisation.md
│   ├── 02-etude-existant.md             │   ├── 02-existing-situation.md
│   ├── 03-problematique.md              │   ├── 03-problem-statement.md
│   └── 04-methodologie.md               │   └── 04-methodology.md
└── 99-conclusion-generale.md            99-conclusion.md
```

One folder per chapter, one file per section. Numeric prefixes fix the order.
The two columns are the same layout named in `fr` and `en`; pick the one
matching `lang` and use it throughout. Chapter *kind* is inferred from the
filename in either language, but declaring `kind:` in `report.yaml` is what
settles it, and it always wins.

## Writing

- Follow `references/formulations.md` for chapter openings, handoffs and
  transitions. It is organised by function with `fr` and `en` forms side by
  side: pick the function, then the column matching `lang`. Vary them — do not
  open every chapter the same way.
- Follow `references/good-vs-weak.md` for the standard. A problématique must be
  a problem, not a task. An objective must be measurable. An état de l'art must
  end in a positioning table (brief for a PFA; substantial for a PFE).
- Use `references/placeholder-syntax.md` exactly. Prefer stable cites:
  `[[CITE: knuth84 | Knuth, 1984]]`. Every figure gets a `[[FIG:]]`, and every
  figure must also be referenced with `[[REF:]]`.
- Respect the per-chapter page budget in `report.yaml`. Roughly 350 words/page.
- Open each chapter with a short introduction, close it with a handoff.
- **Do not write the general introduction on the first pass.** Draft it last,
  after the chapters exist, and never let it state results.

After writing each new or replaced file:

```bash
python3 "$CR" guard --stamp reports_docs/<path>.md
```

Without that stamp, the next draft treats the file as student-owned and skips it.

## Finish

Report: files written, files skipped and why, approximate pages per chapter
against budget, the output of `gaps`, and — the important part — **which
document the user should supply next to close the biggest remaining gap**.

Then tell them to read the markdown. When they confirm it, `/report:build`
produces the Overleaf bundle.
