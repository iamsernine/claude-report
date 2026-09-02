---
description: Show report progress — pages against budget, brief completeness, blocking placeholders, figures outstanding
allowed-tools: Read, Glob, Bash
---

Report the current state of the report. Read-only — change nothing.

## Plugin root

Scripts live **in this plugin**, never in the student's repository — do not run
`python3 scripts/cli.py` from the project cwd. `$CLAUDE_PLUGIN_ROOT` is set for you on a
correctly installed plugin; the fallback line covers a manual install. If `$CR`
is empty, the plugin is not installed — say so and stop rather than guessing.

```bash
CR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/claude-report}/scripts/cli.py"
[ -f "$CR" ] || CR=$(ls -1 "$HOME"/.claude/{plugins,skills}/claude-report/scripts/cli.py "$HOME"/.claude/plugins/cache/*/claude-report/*/scripts/cli.py 2>/dev/null | head -1)
CRROOT=$(dirname "$(dirname "$CR")")
python3 "$CR" status reports_docs
```

The CLI prints the compact table: type, brief completeness, pages against the
`report.yaml` targets, blocking placeholders, empty brief fields, readable
documents in `reports_docs/sources/`, figures, citations, and one next action.
Show that output as-is. Do not reformat it into a longer essay.

If the next action is about gaps, add one concrete line naming **which document
would close the biggest one** — that is the thing the user can act on.

For the full list of what is still missing:

```bash
python3 "$CR" gaps reports_docs
```

If the command fails because `reports_docs/` is missing, tell the user to run
`/report:init` first.

Remember the endpoint when reporting progress: this pipeline ends at
`build/overleaf.zip`, which the user uploads to Overleaf. It never produces a
PDF locally.
