"""Render the 12x11 text font (bank $AE, 22 bytes/glyph, 11 rows of 16-bit words) as labelled sheets.

    python tools/font_sheet.py OUT_DIR [--rom ROM] [--first 0] [--count 1280] [--zoom 3]

Each cell is labelled with its table code (single byte c = glyph c-1; F9..FC xx = glyph (p-F8)*256 + xx-1).
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

FONT_OFF = 0x170000  # $AE:8000 LoROM
GLYPH = 22


def code_of(i):
    """Table code for glyph index i (inverse of the 84A98B decode)."""
    c = i + 1
    return "%02X" % c if c < 0xF8 else "%02X%02X" % (0xF8 + (c >> 8), c & 0xFF)


def glyph(rom, i):
    """11 rows of 16 pixels (1 = ink); each row is a little-endian word, bit 15 = leftmost (read by 84ADEA)."""
    o = FONT_OFF + i * GLYPH
    return [[(int.from_bytes(rom[o + 2 * r:o + 2 * r + 2], "little") >> (15 - x)) & 1 for x in range(16)] for r in range(11)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--rom", default="rom/Solid Runner (Japan).sfc")
    ap.add_argument("--first", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--count", type=lambda s: int(s, 0), default=1280)
    ap.add_argument("--cols", type=int, default=16)
    ap.add_argument("--per", type=int, default=256, help="glyphs per sheet")
    ap.add_argument("--zoom", type=int, default=3)
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    z, cw, ch = a.zoom, 16 * a.zoom + 4, 11 * a.zoom + 14
    for s0 in range(a.first, a.first + a.count, a.per):
        n = min(a.per, a.first + a.count - s0)
        rows = (n + a.cols - 1) // a.cols
        im = Image.new("RGB", (a.cols * cw, rows * ch), (40, 40, 60))
        d = ImageDraw.Draw(im)
        for k in range(n):
            i = s0 + k
            x0, y0 = (k % a.cols) * cw, (k // a.cols) * ch
            d.text((x0 + 1, y0), code_of(i), fill=(255, 200, 0))
            d.rectangle([x0 + 2, y0 + 12, x0 + 2 + 16 * z - 1, y0 + 12 + 11 * z - 1], fill=(0, 0, 0))
            for r, row in enumerate(glyph(rom, i)):
                for x, b in enumerate(row):
                    if b:
                        d.rectangle([x0 + 2 + x * z, y0 + 12 + r * z, x0 + 2 + x * z + z - 1, y0 + 12 + r * z + z - 1], fill=(255, 255, 255))
        p = out / ("font_%04X.png" % s0)
        im.save(p)
        print(p)


if __name__ == "__main__":
    main()
