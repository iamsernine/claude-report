#!/usr/bin/env bash
# Rebuild the skill's bundled references from the canonical repo content.
# Run from the repo root or from anywhere: ./skills/build.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_REFS="$REPO_ROOT/skills/rapport-pfe/references"

rm -rf "$SKILL_REFS"
mkdir -p "$SKILL_REFS"

cp -r "$REPO_ROOT/skeletons"  "$SKILL_REFS/skeletons"
cp -r "$REPO_ROOT/templates"  "$SKILL_REFS/templates"
cp "$REPO_ROOT/reference/"*.md "$SKILL_REFS/"

echo "Rebuilt $SKILL_REFS"
find "$SKILL_REFS" -name '*.md' | wc -l | xargs echo "files:"
