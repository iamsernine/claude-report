---
description: Critique the draft against jury criteria — proportions, positioning, baselines, unreferenced figures
argument-hint: "[--fix]"
allowed-tools: Read, Glob, Grep, Bash, Edit
---

Review the draft in `reports_docs/` against the criteria a jury actually applies.
Use the `rapport-academique` skill.

## Arguments

`$ARGUMENTS` — `--fix` applies the mechanical corrections automatically
(unreferenced figures get a `[[REF:]]`, duplicate slugs are renamed). Structural
and substantive problems are always reported, never auto-fixed.

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
```

## Steps

**1. Run the mechanical pass** (it reads `report.yaml` for type, skeleton and
page budgets):

```bash
python3 "$ROOT/scripts/cli.py" review reports_docs $ARGUMENTS
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
