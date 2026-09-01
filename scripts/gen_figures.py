#!/usr/bin/env python3
"""Generate grey placeholder PNGs so the report compiles before any real image exists.

    python3 scripts/gen_figures.py reports_docs figures

Existing files are never overwritten: drop your real image in with the same
filename and it survives every rebuild.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from placeholders import scan_tree  # noqa: E402

BASE_W = 1600  # px at width=1.0
BG = (238, 238, 238)
BORDER = (176, 176, 176)
SLUG_C = (90, 90, 90)
CAP_C = (130, 130, 130)


def _font(size: int):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass
    return ImageFont.load_default()


def make_placeholder(path: Path, slug: str, caption: str, width_frac: float) -> None:
    w = max(480, int(BASE_W * width_frac))
    h = int(w * 0.6)
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([4, 4, w - 5, h - 5], outline=BORDER, width=3)

    # diagonal hatch so it is unmistakably a placeholder in print
    for x in range(-h, w, 48):
        d.line([(x, h), (x + h, 0)], fill=(228, 228, 228), width=2)

    f_slug = _font(max(22, w // 26))
    f_cap = _font(max(16, w // 42))

    lines = [("PLACEHOLDER", f_cap, CAP_C), (slug, f_slug, SLUG_C)]
    for chunk in textwrap.wrap(caption, width=48)[:3]:
        lines.append((chunk, f_cap, CAP_C))
    lines.append((f"figures/{slug}.png", f_cap, CAP_C))

    heights = [d.textbbox((0, 0), t, font=f)[3] for t, f, _ in lines]
    total = sum(heights) + 14 * (len(lines) - 1)
    y = (h - total) // 2
    for (text, font, colour), th in zip(lines, heights):
        tw = d.textbbox((0, 0), text, font=font)[2]
        d.text(((w - tw) // 2, y), text, font=font, fill=colour)
        y += th + 14

    img.save(path)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "reports_docs")
    outdir = Path(sys.argv[2] if len(sys.argv) > 2 else "figures")
    outdir.mkdir(parents=True, exist_ok=True)

    figs = [p for p in scan_tree(root) if p.kind == "FIG"]
    seen, created, kept = set(), 0, 0

    for p in figs:
        if p.slug in seen:
            continue
        seen.add(p.slug)
        dest = outdir / f"{p.slug}.png"
        if dest.exists():
            kept += 1
            continue
        make_placeholder(dest, p.slug, p.caption, float(p.options.get("width", 0.8)))
        created += 1

    manifest = outdir / "MANIFEST.md"
    rows = ["# Figures attendues", "", "| Slug | Légende | Chapitre | Largeur min. | État |", "|---|---|---|---|---|"]
    for p in figs:
        if p.slug not in seen:
            continue
        seen.discard(p.slug)
        dest = outdir / f"{p.slug}.png"
        real = dest.exists() and dest.stat().st_size > 0
        # a generated placeholder is ~identical size every time; flag by mtime heuristic
        state = "à fournir" if real is False else "placeholder ou fourni"
        minw = int(1600 * float(p.options.get("width", 0.8)))
        rows.append(f"| `{p.slug}` | {p.caption} | {p.file} | {minw} px | {state} |")
    manifest.write_text("\n".join(rows) + "\n", encoding="utf-8")

    print(f"figures: {created} placeholder(s) créé(s), {kept} fichier(s) existant(s) conservé(s)")
    print(f"manifeste: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
