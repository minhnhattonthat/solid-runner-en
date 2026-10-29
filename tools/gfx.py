"""gfx.py: graphics-text edits (docs/re/graphics.md), run by tools/build.py.

G1: the title logo's katakana reading ソリッドランナー sits on a dark gradient bar in the logo block D8_02 (BG2,
8x8 4bpp, VRAM tiles 100+). The English logo keeps the bar and drops the reading: each run of letter pixels (colours
E/F) inside the bar's tiles is filled with the gradient around it.

    python -X utf8 tools/gfx.py      print the edited tiles as colour indices
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lz  # noqa: E402

LOGO = 0xD8, 2                       # bank, block
KATAKANA = range(0x7A, 0x82)         # block tiles of the bar's letter row (VRAM 17A-181); 179/182 are its edges


def slot(rom, bank, i):
    """(file offset of the block, compressed length)."""
    base = (bank & 0x7F) * 0x8000
    o = base + (rom[base + 2 * i] | rom[base + 2 * i + 1] << 8) - 0x8000
    return o, lz.decompress(rom, o)[1]


def pixels(data, t):
    o = t * 32
    return [[sum(((data[o + (0, 1, 16, 17)[k] + 2 * r] >> (7 - x)) & 1) << k for k in range(4)) for x in range(8)]
            for r in range(8)]


def put_pixels(data, t, g):
    o = t * 32
    for r in range(8):
        for k in range(4):
            data[o + (0, 1, 16, 17)[k] + 2 * r] = sum(((g[r][x] >> k) & 1) << (7 - x) for x in range(8))


def unletter(data, tiles):
    """Fill each run of E/F pixels on a line across `tiles` (side by side) with the colours left and right of it."""
    rows = [sum((pixels(data, t)[y] for t in tiles), []) for y in range(8)]
    for line in rows:
        x = 0
        while x < len(line):
            if line[x] < 0xE:
                x += 1
                continue
            end = x
            while end < len(line) and line[end] >= 0xE:
                end += 1
            left, right = line[x - 1] if x else line[end], line[end] if end < len(line) else line[x - 1]
            for k in range(x, end):
                line[k] = left if k - x < (end - x + 1) // 2 else right
            x = end
    for i, t in enumerate(tiles):
        put_pixels(data, t, [line[8 * i:8 * i + 8] for line in rows])


def plan(rom):
    """[(file offset, bytes, writer)]: the logo block without the katakana, in its own slot."""
    o, n = slot(rom, *LOGO)
    data = bytearray(lz.decompress(rom, o)[0])
    unletter(data, list(KATAKANA))
    new = lz.compress(bytes(data))
    if len(new) > n:
        new = lz.compress_min(bytes(data))
    assert len(new) <= n, f"logo block {len(new)} > slot {n}"
    return [(o, new, "gfx G1 title logo (no katakana)")]


def allowed(rom):
    o, n = slot(rom, *LOGO)
    return set(range(o, o + n))


def main():
    rom = (Path(__file__).resolve().parents[1] / "rom" / "Solid Runner (Japan).sfc").read_bytes()
    o, _ = slot(rom, *LOGO)
    data = bytearray(lz.decompress(rom, o)[0])
    unletter(data, list(KATAKANA))
    for y in range(8):
        print(" ".join("".join("%X" % p for p in pixels(data, t)[y]) for t in range(0x79, 0x83)))


if __name__ == "__main__":
    main()
