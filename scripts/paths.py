#!/usr/bin/env python3
"""Locate the plugin installation root.

Commands must never call ``python3 scripts/...`` from the user's project —
those files live in the plugin. Prefer ``CLAUDE_PLUGIN_ROOT`` (set by Claude
Code when a plugin command runs); otherwise walk up from this file.
"""
from __future__ import annotations

import os
from pathlib import Path

_CANDIDATES = (
    Path.home() / ".claude" / "plugins" / "claude-report",
    Path.home() / ".claude" / "plugins" / "pfe-report-skeletons",
)


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
    return here


def cli_path() -> Path:
    return plugin_root() / "scripts" / "cli.py"


def assets_dir() -> Path:
    return plugin_root() / "assets"
