#!/usr/bin/env python3
"""Locate the plugin installation root.

Commands must never call ``python3 scripts/...`` from the user's project —
those files live in the plugin. Prefer ``CLAUDE_PLUGIN_ROOT`` (set by Claude
Code when a plugin command runs); otherwise walk up from this file.
"""
from __future__ import annotations

import os
from pathlib import Path

_CLAUDE = Path.home() / ".claude"

# Ordered fallbacks, used only when CLAUDE_PLUGIN_ROOT is unset and this file
# has been copied somewhere unusual. A properly installed plugin never gets
# here: Claude Code exports CLAUDE_PLUGIN_ROOT for plugin commands, and this
# module otherwise resolves itself from __file__.
_CANDIDATES = (
    _CLAUDE / "plugins" / "claude-report",
    _CLAUDE / "skills" / "claude-report",
    # 0.1.x layout, when the repo was named pfe-report-skeletons
    _CLAUDE / "plugins" / "pfe-report-skeletons",
    _CLAUDE / "skills" / "pfe-report-skeletons",
)


def _marketplace_candidates():
    """Plugins installed from a marketplace live under a versioned cache dir."""
    cache = _CLAUDE / "plugins" / "cache"
    if not cache.is_dir():
        return
    for marketplace in sorted(cache.iterdir()):
        plugin = marketplace / "claude-report"
        if not plugin.is_dir():
            continue
        for version in sorted(plugin.iterdir(), reverse=True):
            yield version


def plugin_root() -> Path:
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        root = Path(env).expanduser().resolve()
        if (root / "scripts" / "cli.py").is_file():
            return root
    here = Path(__file__).resolve().parent.parent
    if (here / "scripts" / "cli.py").is_file():
        return here
    for cand in _CANDIDATES:
        if (cand / "scripts" / "cli.py").is_file():
            return cand
    for cand in _marketplace_candidates():
        if (cand / "scripts" / "cli.py").is_file():
            return cand
    return here


def cli_path() -> Path:
    return plugin_root() / "scripts" / "cli.py"


def assets_dir() -> Path:
    return plugin_root() / "assets"


# ---------------------------------------------------------------------------
# What counts as report content
# ---------------------------------------------------------------------------
#
# `reports_docs/` holds three different things: the report itself, the working
# material that produced it (BRIEF.md, sources/), and generated output
# (figures/, .extracted/). Only the first is drafted, reviewed, counted and
# compiled. Defined once here because every tree walker needs the same answer —
# a supplied source document leaking into main.tex is exactly the bug this
# prevents.

NON_CONTENT_DIRS = frozenset({
    "sources",        # documents the student supplied to fill gaps
    ".extracted",     # text pulled out of those documents
    "figures",        # generated placeholders
    "build",          # generated output
})

NON_CONTENT_FILES = frozenset({
    "BRIEF.md", "MANIFEST.md", "citations-needed.md",
    "report.yaml", "cover.yaml",
})


def is_report_content(path, root) -> bool:
    """True if `path` is part of the report, not working material or output."""
    path, root = Path(path), Path(root)
    if path.name in NON_CONTENT_FILES or path.name.endswith(".generated"):
        return False
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    return not any(part in NON_CONTENT_DIRS for part in rel.parts)
