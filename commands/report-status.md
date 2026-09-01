---
description: Show report progress — pages against budget, brief completeness, blocking placeholders, figures outstanding
allowed-tools: Read, Glob, Bash
---

Report the current state of the report. Read-only — change nothing.

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
python3 "$ROOT/scripts/cli.py" status reports_docs
```

The CLI already prints the compact table (type, brief completeness, pages vs
`report.yaml` targets, blocking placeholders, figures fournies vs placeholder,
citations, one next action). Show that output to the user. Do not reformat it
into a longer essay.

If the command fails because `reports_docs/` is missing, tell the user to run
`/report:init` first.
