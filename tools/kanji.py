"""Read the kanji cells of the 12x11 font (codes F9xx-FCxx) off the font.

    python -X utf8 tools/kanji.py guess [--out work/kanji]     template-match every used cell against MS Gothic
    python -X utf8 tools/kanji.py sheets N [--out work/kanji]   N reviewer batches: sheet PNGs + context text
    python -X utf8 tools/kanji.py table READINGS.tsv           check readings (code<TAB>kanji) and print tbl lines

Used codes come from the extracted script (raw bytes re-encoded from each entry's `jp`, walked the way the engine
walks them: F8 = control + its args, F9-FC = kanji pair). Candidates: every JIS X 0208 kanji, rendered with MS Gothic's
12 px bitmaps (the game font is the same family of 12-dot design), scored by Dice overlap over +-1 px shifts.
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from font_sheet import glyph  # noqa: E402
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom/Solid Runner (Japan).sfc"
FONT = "C:/Windows/Fonts/msgothic.ttc"


def entries():
    for f in sorted((ROOT / "script").rglob("*.json")):
        yield from json.loads(f.read_text(encoding="utf-8"))


def walk(raw, argc):
    """Yield (pos, kanji code or None) per unit: F8 cc + argc[cc] args, F9-FC xx kanji pair, else one byte."""
    p = 0
    while p < len(raw):
        b = raw[p]
        if b == 0xF8 and p + 1 < len(raw):
            p += 2 + argc.get(raw[p + 1], 0)
        elif 0xF9 <= b <= 0xFC and p + 1 < len(raw):
            yield p, raw[p] << 8 | raw[p + 1]
            p += 2
        else:
            p += 1


def used():
    """{code: [entry ids]} for every kanji code the script uses, and {id: raw bytes}."""
    t = Table.load(ROOT / "tbl/jp.tbl")
    argc = {c[1]: n for c, (_, n) in t.ctrl.items() if len(c) == 2 and c[0] == 0xF8}
    uses, raws = defaultdict(list), {}
    for e in entries():
        raw = t.encode(e["jp"])
        raws[e["id"]] = raw
        for _, k in walk(raw, argc):
            uses[k].append(e["id"])
    return uses, raws


def cell(rom, code):
    g = (code >> 8) - 0xF8 << 8 | (code & 0xFF)
    return np.array(glyph(rom, g - 1), dtype=np.uint8)[:, :12]


def candidates():
    out = []
    for hi in range(0x88, 0xEB):
        for lo in range(0x40, 0xFD):
            try:
                ch = bytes([hi, lo]).decode("cp932")
            except UnicodeDecodeError:
                continue
            if "\u4e00" <= ch <= "\u9fff" or ch == "々":
                out.append(ch)
    return out


def render(ch, size=12):
    im = Image.new("L", (16, 14), 0)
    ImageDraw.Draw(im).text((0, 0), ch, font=ImageFont.truetype(FONT, size), fill=255)
    a = (np.array(im) > 127).astype(np.uint8)
    ys, xs = np.nonzero(a)
    return a, (ys.min(), xs.min()) if len(ys) else (0, 0)


def boxed(a):
    """Crop to the ink box and pad into 13x13 at the top-left (alignment is then searched by shifts)."""
    ys, xs = np.nonzero(a)
    out = np.zeros((13, 13), np.uint8)
    if len(ys):
        c = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1][:13, :13]
        out[:c.shape[0], :c.shape[1]] = c
    return out


def shifts(a):
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            yield np.roll(np.roll(a, dy, 0), dx, 1)


def guess(out):
    rom = ROM.read_bytes()
    uses, _ = used()
    cands = candidates()
    C = np.stack([boxed(render(ch)[0]).ravel() for ch in cands]).astype(np.float32)
    csum = C.sum(1)
    res = {}
    for code in sorted(uses):
        best = np.zeros(len(cands), np.float32)
        a = boxed(cell(rom, code))
        for s in shifts(a):
            v = s.ravel().astype(np.float32)
            best = np.maximum(best, 2 * (C @ v) / (csum + v.sum() + 1e-6))
        top = np.argsort(-best)[:6]
        res["%04X" % code] = {"top": [cands[i] for i in top], "score": [round(float(best[i]), 3) for i in top],
                              "uses": len(uses[code]), "ids": uses[code][:3]}
    out.mkdir(parents=True, exist_ok=True)
    (out / "guess.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    sc = [v["score"][0] for v in res.values()]
    print(f"{len(res)} codes, top-1 score median {np.median(sc):.3f}, <0.8: {sum(s < 0.8 for s in sc)}")


def context(t, raw, code, guesses):
    """The entry text with every kanji shown as its guess and the target as 【guess】."""
    s = t.decode(raw, 0, len(raw))[0]
    for k, v in guesses.items():
        hi, lo = bytes.fromhex(k)
        tok = f"[{hi:02X}]" + t.decode(bytes([lo]), 0, 1)[0]
        s = s.replace(tok, f"【{v}】" if k == code else v)
    return s.replace("{br}", " / ")


def sheets(out, n):
    rom = ROM.read_bytes()
    g = json.loads((out / "guess.json").read_text(encoding="utf-8"))
    _, raws = used()
    t = Table.load(ROOT / "tbl/jp.tbl")
    top1 = {k: v["top"][0] for k, v in g.items()}
    codes = sorted(g)
    per = -(-len(codes) // n)
    big = ImageFont.truetype(FONT, 24)
    lab = ImageFont.truetype(FONT, 14)
    for b in range(n):
        part = codes[b * per:(b + 1) * per]
        lines = []
        for i0 in range(0, len(part), 40):
            chunk = part[i0:i0 + 40]
            z, rh, cw = 4, 60, 330
            im = Image.new("RGB", (cw * 2, rh * ((len(chunk) + 1) // 2)), (30, 30, 45))
            d = ImageDraw.Draw(im)
            for j, code in enumerate(chunk):
                x0, y0 = (j % 2) * cw, (j // 2) * rh
                d.text((x0 + 2, y0 + 2), code, font=lab, fill=(255, 200, 0))
                d.rectangle([x0 + 2, y0 + 16, x0 + 2 + 12 * z + 3, y0 + 16 + 11 * z + 3], fill=(0, 0, 0))
                for (r, x) in zip(*np.nonzero(cell(rom, code))):
                    d.rectangle([x0 + 4 + x * z, y0 + 18 + r * z, x0 + 4 + x * z + z - 1, y0 + 18 + r * z + z - 1], fill=(255, 255, 255))
                for c, ch in enumerate(g[code]["top"][:5]):
                    d.text((x0 + 62 + c * 52, y0 + 16), ch, font=big, fill=(200, 230, 255))
                    d.text((x0 + 62 + c * 52, y0 + 44), str(c + 1), font=lab, fill=(150, 150, 150))
            im.save(out / f"batch{b + 1}_{i0 // 40 + 1}.png")
        for code in part:
            v = g[code]
            lines.append(f"{code}  candidates: {' '.join(v['top'][:5])}  (uses: {v['uses']})")
            for eid in v["ids"]:
                lines.append(f"    {eid}: {context(t, raws[eid], code, top1)}")
        (out / f"batch{b + 1}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(out / f"batch{b + 1}.txt", len(part))


def table(path):
    rows = [l.split("\t") for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    uses, _ = used()
    seen = Counter(r[1] for r in rows)
    bad = [r for r in rows if len(r) < 2 or len(r[1]) != 1]
    dup = sorted(k for k, c in seen.items() if c > 1)
    missing = sorted("%04X" % c for c in uses if "%04X" % c not in {r[0] for r in rows})
    print(f"# {len(rows)} readings, bad {len(bad)}, duplicate values {dup}, used codes missing {missing}", file=sys.stderr)
    for r in sorted(rows):
        print(f"{r[0]}={r[1]}")


def ctx(path, codes, n=4):
    """Print up to n script lines per code, decoded with the readings in `path`, the code itself as 【reading】."""
    rows = dict(l.split("\t") for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip())
    uses, raws = used()
    base = (ROOT / "tbl/jp.tbl").read_text(encoding="utf-8").splitlines()
    for code in codes:
        code = code.upper()
        t = Table(base + [f"{k}={'【%s】' % v if k == code else v}" for k, v in rows.items()])
        print(f"{code} {rows.get(code, '?')} ({len(uses[int(code, 16)])} uses)")
        for eid in uses[int(code, 16)][:n]:
            s = t.decode(raws[eid], 0, len(raws[eid]))[0].replace("{br}", "/")
            i = s.find("【")
            print("   ", eid, s[max(0, i - 30):i + 30])


def dump(out, n):
    """Every distinct `jp` with kanji, split into n files for look-alike readers (id<TAB>text, {br} as /)."""
    seen, rows = set(), []
    for e in entries():
        j = e["jp"]
        if any("一" <= c <= "鿿" for c in j) and j not in seen:
            seen.add(j)
            rows.append(f"{e['id']}\t{j.replace('{br}', '/')}")
    per = -(-len(rows) // n)
    for b in range(n):
        (out / f"read{b + 1}.txt").write_text("\n".join(rows[b * per:(b + 1) * per]) + "\n", encoding="utf-8")
    print(len(rows), "lines,", sum(map(len, rows)), "chars")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["guess", "sheets", "table", "ctx", "dump"])
    ap.add_argument("arg", nargs="?")
    ap.add_argument("codes", nargs="*")
    ap.add_argument("--out", type=Path, default=ROOT / "work/kanji")
    a = ap.parse_args()
    if a.cmd == "guess":
        guess(a.out)
    elif a.cmd == "sheets":
        sheets(a.out, int(a.arg or 6))
    elif a.cmd == "dump":
        dump(a.out, int(a.arg or 6))
    elif a.cmd == "ctx":
        ctx(a.arg, a.codes)
    else:
        table(a.arg)


if __name__ == "__main__":
    main()
