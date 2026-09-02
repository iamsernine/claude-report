---
description: Critique the draft against jury criteria — proportions, positioning, baselines, unreferenced figures
argument-hint: "[--fix]"
allowed-tools: Read, Glob, Grep, Bash, Edit
---

Review the markdown draft in `reports_docs/` against the criteria a jury
actually applies. Use the `rapport-academique` skill.

This is the gate before `/report:build`. It reviews **markdown**, never LaTeX —
if something is wrong, it is wrong in the markdown, and that is where it gets
fixed.

## Arguments

`$ARGUMENTS` — `--fix` applies the mechanical corrections automatically
(unreferenced figures get a `[[REF:]]`, duplicate slugs are renamed). Structural
and substantive problems are always reported, never auto-fixed.

## Plugin root

Scripts live **in this plugin**, never in the student's repository — do not run
`python3 scripts/cli.py` from the project cwd. `$CLAUDE_PLUGIN_ROOT` is set for you on a
correctly installed plugin; the fallback line covers a manual install. If `$CR`
is empty, the plugin is not installed — say so and stop rather than guessing.

```bash
CR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/claude-report}/scripts/cli.py"
[ -f "$CR" ] || CR=$(ls -1 "$HOME"/.claude/{plugins,skills}/claude-report/scripts/cli.py "$HOME"/.claude/plugins/cache/*/claude-report/*/scripts/cli.py 2>/dev/null | head -1)
CRROOT=$(dirname "$(dirname "$CR")")
```

## Steps

**1. Run the mechanical pass** (it reads `report.yaml` for type, skeleton and
page budgets):

```bash
python3 "$CR" review reports_docs $ARGUMENTS
```

Pass `--fix` through to the CLI when the user asked for it. The script checks
proportions per chapter against yaml targets, blocking and malformed
placeholders, unreferenced figures and tables, duplicate slugs, état de l'art
without positioning (**blocking for PFE/mémoire, warning for PFA/module, skipped
for stages**), results without a baseline (**research skeletons only**), and an
introduction leaking results.

**2. Read the draft and add the judgement pass.** The script cannot evaluate:

- Is the problématique a problem, or a task description? Compare against
  `references/good-vs-weak.md`.
- Are the objectives measurable, and does the results chapter answer them one by
  one?
- Is the *critique de l'existant* an actual critique or an inventory?
- Do the technology justifications tie back to the constraints stated in
  chapter 1, or are they post-hoc?
- Does each chapter hand off to the next?
- Is the conclusion introducing new material?
- Are limitations named honestly, or are they disguised boasts?
- For research reports: is the methodology reproducible? Hyperparameters, splits,
  seeds, hardware, versions.

**3. Cross-check against `references/common-pitfalls.md`.**

## Reporting

Order findings by **how much they cost**, not by document order. Use three tiers:

- **Bloquant** — will visibly damage the grade. Inverted proportions, no
  positioning on a PFE, unresolved metrics.
- **À corriger** — will be noticed. Unreferenced figures, missing handoffs,
  inconsistent citation style.
- **À considérer** — improvements, not faults.

Be concrete about what to cut. Students find cutting harder than writing, and
"shorten the état de l'art" is useless advice. Say which subsection, and how many
pages it should lose.

End with the single highest-value change to make next.

If the blocking findings are unresolved `[[TODO]]` / `[[METRIC]]` placeholders
rather than prose problems, say so plainly and point at the loop: fill the field
in `BRIEF.md`, or drop the document holding it into `reports_docs/sources/` and
re-run `/report:draft`. Do not suggest writing the missing value.
