"""Static graphics sweep: decompress every LZ block reached by a bank-start pointer table and render it as tiles.

    python -X utf8 tools/gfx_sweep.py OUT_DIR [--rom ROM] [--fmt snes4|snes2] [--height 1000]

Writes OUT_DIR/<bank>_<idx>.bin, contact sheets OUT_DIR/sheet_NN.png (several blocks per sheet, each labelled
with bank, index and file offset) and OUT_DIR/index.txt. Prints every bank and block it skipped, with the reason.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from lz import decompress  # noqa: E402


def tiles_img(data, fmt, cols=32):
    bpp = {"snes2": 2, "snes4": 4}[fmt]
    size = 8 * bpp
    n = len(data) // size
    rows = max(1, (n + cols - 1) // cols)
    im = Image.new("L", (cols * 8, rows * 8))
    px = im.load()
    for t in range(n):
        o = t * size
        for r in range(8):
            planes = [data[o + 2 * r], data[o + 2 * r + 1]]
            if bpp == 4:
                planes += [data[o + 16 + 2 * r], data[o + 16 + 2 * r + 1]]
            for x in range(8):
                v = sum(((planes[p] >> (7 - x)) & 1) << p for p in range(bpp))
                px[(t % cols) * 8 + x, (t // cols) * 8 + r] = v * (255 // ((1 << bpp) - 1))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--rom", default="rom/Solid Runner (Japan).sfc")
    ap.add_argument("--fmt", default="snes4", choices=["snes2", "snes4"])
    ap.add_argument("--height", type=int, default=1000, help="max sheet height in px")
    ap.add_argument("--min", type=int, default=512, help="skip outputs smaller than this")
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    blocks, index = [], []
    for b in range(len(rom) // 0x8000):
        s = b * 0x8000
        w = rom[s] | rom[s + 1] << 8
        if not 0x8002 <= w < 0x8400 or w & 1:
            print(f"skip bank {b | 0x80:02X}: no pointer table (first word {w:04X})")
            continue
        n = (w - 0x8000) // 2
        for i in range(n):
            p = rom[s + 2 * i] | rom[s + 2 * i + 1] << 8
            off = s + (p & 0x7FFF)
            if p < 0x8000:
                print(f"skip {b | 0x80:02X}_{i:02X}: pointer {p:04X} outside bank")
                continue
            try:
                data, used = decompress(rom, off)
            except (ValueError, IndexError) as e:
                print(f"skip {b | 0x80:02X}_{i:02X} @{off:06X}: not LZ ({e})")
                continue
            if len(data) < a.min:
                print(f"skip {b | 0x80:02X}_{i:02X} @{off:06X}: {len(data)} bytes out")
                continue
            name = f"{b | 0x80:02X}_{i:02X}"
            (out / f"{name}.bin").write_bytes(data)
            blocks.append((name, off, data))
            index.append(f"{name} off={off:06X} packed={used} size={len(data)}")
    (out / "index.txt").write_text("\n".join(index) + "\n", encoding="utf-8")
    groups, cur, h = [], [], 0  # pack blocks into sheets at most --height px tall (a big block gets its own)
    for name, off, d in blocks:
        im = tiles_img(d, a.fmt)
        im = im.resize((512, im.height * 2), Image.NEAREST)
        if cur and h + im.height + 14 > a.height:
            groups.append(cur)
            cur, h = [], 0
        cur.append((name, off, d, im))
        h += im.height + 14
    if cur:
        groups.append(cur)
    for k, group in enumerate(groups):
        sheet = Image.new("RGB", (512, sum(im.height + 14 for *_, im in group)), (60, 0, 60))
        dr = ImageDraw.Draw(sheet)
        y = 0
        for name, off, d, im in group:
            dr.text((2, y), f"{name} @{off:06X} {len(d)}B", fill=(255, 220, 0))
            sheet.paste(im.convert("RGB"), (0, y + 14))
            y += im.height + 14
        sheet.save(out / f"sheet_{k:03d}.png")
    print(f"{len(blocks)} blocks, {len(groups)} sheets in {out}")


if __name__ == "__main__":
    main()
