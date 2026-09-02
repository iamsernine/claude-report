---
description: Analyse the project and set up the report — picks the skeleton, generates the brief, estimates length and figures
argument-hint: "[--type pfe|pfa|stage-initiation|stage-technicien|module|memoire] [--lang fr|en] [--pages N]"
allowed-tools: Read, Glob, Grep, Bash, Write
---

Set up an academic report for this project. Use the `rapport-academique` skill for
all structural, formatting and quality decisions — read it before doing anything.

## Plugin root

Scripts live **in this plugin**, never in the student's repository — do not run
`python3 scripts/cli.py` from the project cwd. `$CLAUDE_PLUGIN_ROOT` is set for you on a
correctly installed plugin; the fallback line covers a manual install. If `$CR`
is empty, the plugin is not installed — say so and stop rather than guessing.

```bash
CR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/claude-report}/scripts/cli.py"
[ -f "$CR" ] || CR=$(ls -1 "$HOME"/.claude/{plugins,skills}/claude-report/scripts/cli.py "$HOME"/.claude/plugins/cache/*/claude-report/*/scripts/cli.py 2>/dev/null | head -1)
CRROOT=$(dirname "$(dirname "$CR")")
python3 "$CR" check
```

If pandoc is missing, say so once and recommend installing it: without it the
markdown→LaTeX conversion falls back to headings only, and lists, tables and
quotes come out wrong. `pdflatex` and `biber` are reported as *not needed* —
compilation happens on Overleaf, never here.

## Arguments

`$ARGUMENTS`

- `--type` — the kind of academic experience. If absent, infer from the project
  and **confirm with the user before proceeding**; getting this wrong invalidates
  everything downstream.

  | Value | Experience | Length |
  |---|---|---|
  | `stage-initiation` | 1st/2nd year observation internship, 2–6 weeks | 10–20 p |
  | `stage-technicien` | 2nd/3rd year application internship, 4–8 weeks | 20–35 p |
  | `pfa` | Projet de Fin d'Année, 3rd/4th year | 25–40 p |
  | `pfe` | Projet de Fin d'Études, final year | 50–80 p |
  | `module` | Course project / mini-projet, no company | 12–25 p |
  | `memoire` | Master's thesis — uses the research skeleton | 60–100 p |

- `--lang` — `fr` (default) or `en`. **This never changes the structure.** It
  selects heading vocabulary, LaTeX chrome and CLI output only; the skeleton,
  chapter count, proportions and review checks are identical in both languages.
- `--pages` — override the target page count. If it contradicts `--type` (say
  `--type pfa --pages 80`), do not silently obey either — say so and ask which
  one is real, because the page budget drives every later check.

## Steps

**0. Disambiguate PFA vs internship vs PFE.** Students often say "PFA internship".
Ask **one** question if `--type` is missing or the answer would change the plan:

- Company internship, bounded task, a few weeks → `stage-technicien` (or
  `stage-initiation` if observation-only).
- End-of-year project (company or school), 25–40 pages → `pfa`.
- Final-year defended project, 50–80 pages → `pfe`.

Do not guess between these three.

**1. Analyse the repository.** Read the README, manifests (package.json,
requirements.txt, pom.xml, Cargo.toml…), the directory layout, entry points,
test files, existing diagrams and notebooks. Do not read every source file —
sample enough to describe the architecture accurately.

**Confidentiality.** Never read or quote `.env`, `.env.*`, credential files,
private keys, or token stores. Never copy tenant IDs, access tokens, connection
strings, or other people's personal emails into the brief or the report. Redact.

**2. Mine the git history for the chronogramme — only inside the internship
window.** Dates come from `reports_docs/report.yaml` (`period_start` /
`period_end`) or from `BRIEF.md` if already filled. If those dates are absent,
**do not** dump the whole `git log` as if it were the stage. Warn that the
history is the life of the repository, ask for the start (and end) date, and
run:

```bash
git log --since="$START" --until="$END" --date=short --pretty='%ad %s'
```

Cluster commits into phases by date and subject. If the repository has no
history, skip it and note that the planning section needs manual input.

**3. Select the skeleton.** Map `--type` to a skeleton, then for `pfe` and
`memoire` determine the deliverable and pick accordingly:

```
stage-initiation → 00-stage-initiation
stage-technicien → 07-stage-technicien
pfa              → 04-pfa-annual-project
module           → 05-module-project
memoire          → 02-pfe-research-ml
pfe              → an application         → 01-pfe-software-engineering
                 → a model or a finding   → 02-pfe-research-ml
                 → a model in production  → 03-pfe-data-cloud-deployment
```

The distinction that matters most: **if the deliverable is a model rather than an
application, the software-engineering skeleton is the wrong one.** Say so
directly if the user's expectation differs.

**`--lang` is not in this map.** There is one skeleton set for every language;
an English capstone is a `pfe` with `lang: en`. (`06-capstone-en` was retired
and is auto-migrated to `01-pfe-software-engineering` if it appears in an old
`report.yaml`.) Never pick a skeleton because of the language.

**4. Write `reports_docs/report.yaml`** using the schema in
`$CRROOT/assets/report.yaml.example`. Include: type, skeleton, `lang`, page
budget, `biblio_position: before_annexes`, `period_start` / `period_end` if
known, cover-page fields (title, author, institution…), and a per-chapter
block with `title`, `kind` (`front` | `intro` | `chapter` | `conclusion` |
`annex`), `numbered`, and `pages: [min, max]`.

Every later command reads this file — including the Python review, which now
flags chapters against those budgets.

**5. Write `reports_docs/BRIEF.md`** from the schema in
`references/brief-schema.md`. Pre-fill everything inferable from the
repository. Leave the rest as explicit empty fields.

**6. Copy templates (do not overwrite if they already exist).** Take the
integrity declaration matching `lang` — `.fr.md` or `.en.md`:

- `$CRROOT/assets/markdown/00-page-de-garde.md` → `reports_docs/00-page-de-garde.md`
- `$CRROOT/assets/markdown/00b-declaration-integrite.<lang>.md` → `reports_docs/00b-declaration-integrite.md`
- `$CRROOT/assets/markdown/sources-README.md` → `reports_docs/sources/README.md`

Create `reports_docs/sources/` even though it starts empty. It is where the
student drops the documents that close the gaps the repository cannot fill, and
an existing folder gets used where an instruction to create one gets forgotten.

Append `$CRROOT/assets/gitignore.fragment` to the project's `.gitignore` if those
lines are not already present.

After copying, stamp the generated markdown so later drafts will not clobber it:

```bash
python3 "$CR" guard --stamp reports_docs/00-page-de-garde.md
python3 "$CR" guard --stamp reports_docs/00b-declaration-integrite.md
```

The cover page is `\input{titlepage}` — a stub. All cover text comes from the
`report.yaml` fields, and its labels are rendered in `lang`, so there is nothing
language-specific to edit by hand.

**7. Report to the user.** Give:

- The skeleton chosen and one sentence on why
- Chapter list with page targets summing to the budget
- Estimated figure count, and **which figures already exist in the repo**
  (diagrams, notebook plots, README images) versus which must be produced
- The exact screenshots needed, derived from routes, endpoints, CLI commands or
  UI components found in the code
- The proposed chronogramme from git history **inside the period**, or a warning
  if the period is unknown
- **What is missing from the brief and must be filled before drafting**

Do not create any chapter files. `/report:init` only sets up.

## The pipeline this starts

Say plainly where this is going, so the user knows what to expect:

```
/report:init  →  fill BRIEF.md  →  /report:draft  →  read the markdown
                       ↑                                    │
                       │        drop documents in           │ confirm
                       └──────  reports_docs/sources/  ←─────┤
                                                            ↓
                                        /report:review  →  /report:build
                                                            ↓
                                                   build/overleaf.zip
                                                            ↓
                                              upload to Overleaf → PDF
```

**No PDF is produced locally.** The plugin stops at LaTeX; Overleaf compiles.
Do not offer to install a TeX distribution.

Finish by telling the user to fill `BRIEF.md` (and `period_start` /
`period_end` in `report.yaml`), drop any supporting documents into
`reports_docs/sources/`, then run `/report:draft`.
