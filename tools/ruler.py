"""ruler.py: overlay an x/y pixel ruler on emulator shots, to read text starts and window frame edges (width gate).

    python -X utf8 tools/ruler.py SHOT.png [SHOT2.png ...] [--crop x,y,w,h] [--zoom 3] [--out OUT.png]

Ticks every 4 px, labelled every 16 px (screen pixels, before zoom), along the top and left of each crop; shots are
stacked vertically into one image (default: work/qa/ruler.png).
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def ruled(path, crop, zoom):
    im = Image.open(path).convert("RGB")
    x0, y0 = 0, 0
    if crop:
        x0, y0, w, h = crop
        im = im.crop((x0, y0, x0 + w, y0 + h))
    im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    pad = 14
    out = Image.new("RGB", (im.width + pad, im.height + pad + 12), (40, 0, 60))
    out.paste(im, (pad, pad))
    d = ImageDraw.Draw(out)
    d.text((pad, im.height + pad), Path(path).parent.name + "/" + Path(path).name, fill=(255, 255, 0))
    for x in range(x0 - x0 % 4, x0 + im.width // zoom + 1, 4):
        px = pad + (x - x0) * zoom
        if px < pad:
            continue
        major = x % 16 == 0
        d.line((px, pad - (8 if major else 3), px, pad - 1), fill=(255, 80, 80) if major else (200, 200, 200))
        if major:
            d.line((px, pad, px, pad + im.height), fill=(255, 80, 80))
            d.text((px + 1, 0), str(x), fill=(255, 255, 255))
    for y in range(y0 - y0 % 4, y0 + im.height // zoom + 1, 4):
        py = pad + (y - y0) * zoom
        if py < pad:
            continue
        major = y % 16 == 0
        d.line((pad - (8 if major else 3), py, pad - 1, py), fill=(255, 80, 80) if major else (200, 200, 200))
        if major:
            d.text((0, py + 1), str(y // 16), fill=(255, 255, 255))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shots", nargs="+")
    ap.add_argument("--crop", type=lambda s: tuple(int(v) for v in s.split(",")))
    ap.add_argument("--zoom", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "ruler.png"))
    a = ap.parse_args()
    ims = [ruled(p, a.crop, a.zoom) for p in a.shots]
    sheet = Image.new("RGB", (max(i.width for i in ims), sum(i.height for i in ims)), (40, 0, 60))
    y = 0
    for i in ims:
        sheet.paste(i, (0, y))
        y += i.height
    sheet.save(a.out)
    print(a.out, sheet.size)


if __name__ == "__main__":
    main()
