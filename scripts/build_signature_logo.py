#!/usr/bin/env python3
"""Genera atc_mail/static/atc-signature-logo.png (fondo blanco, ~300px)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT.parent / "atc-noc-suite" / "static" / "img" / "american-tower-watermark.png"
OUT = ROOT / "atc_mail" / "static" / "atc-signature-logo.png"


def main() -> int:
    try:
        from PIL import Image
    except ImportError:
        print("Instalá Pillow: pip install Pillow", file=sys.stderr)
        return 1
    if not SRC.is_file():
        print(f"No existe fuente: {SRC}", file=sys.stderr)
        return 1
    im = Image.open(SRC).convert("RGBA")
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    max_w = 300
    if im.width > max_w:
        ratio = max_w / im.width
        im = im.resize((max_w, int(im.height * ratio)), Image.Resampling.LANCZOS)
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bg.paste(im, mask=im.split()[3])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bg.save(OUT, "PNG", optimize=True)
    print(f"OK {OUT} ({OUT.stat().st_size} bytes, {bg.size[0]}x{bg.size[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
