"""winmap.py: the menu window sheets and the edits the English menus need (run by tools/build.py; docs/re/insert.md).

A menu screen's windows come from one sheet: an LZ block behind bank $9C's pointer table (tools/lz.py), decoded to
$7F:8000, 32 tilemap words a row. A window descriptor {dx, dy, sx, sy, w, h, $20} (82:B704 copies the rect row by
row) puts the rect at (sx, sy) of the sheet on the BG3 tilemap at (dx, dy). Text tiles in a rect are the text
bitmap's tiles: strip s, tile t (0-14) = tile s*16 + t (top half), + 16 (bottom half). Descriptors and code bytes
are patched in asm/menus.asm; this module rewrites the sheets. An edited sheet re-encodes bigger than its slot, so the
bank's blocks are re-packed one after another into the bank (its FF tail absorbs the growth) and the table rewritten
(the decompressor reads the table word and the block within bank $9C; callers point $3E at a table entry).

    python -X utf8 tools/winmap.py BLOCK [ROW ROWS]     print a sheet (patched) as hex words
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lz  # noqa: E402

BANK = 0x9C
BASE = (BANK & 0x7F) * 0x8000
MARGIN = 16
BLANK = 0x2000  # text window background tile


def off(bank, addr):
    return (bank & 0x7F) * 0x8000 + (addr & 0x7FFF)


def slot(rom, i):
    """(file offset of table word, file offset of the block, compressed length) of block i."""
    p = rom[BASE + 2 * i] | rom[BASE + 2 * i + 1] << 8
    return BASE + 2 * i, BASE + p - 0x8000, lz.decompress(rom, BASE + p - 0x8000)[1]


def sheet(rom, i):
    out, _ = lz.decompress(rom, slot(rom, i)[1])
    return [[out[r * 64 + 2 * c] | out[r * 64 + 2 * c + 1] << 8 for c in range(32)] for r in range(len(out) // 64)]


def pack(rows):
    return b"".join(w.to_bytes(2, "little") for row in rows for w in row)


def text(strip, t, bottom=False):
    return 0x2000 | (strip * 16 + t + (16 if bottom else 0))


def setup(rows):
    """Field menu > Setup (82:A91F, sheet rows 12-21): labels 9 tiles + gap + part names 12 tiles, window 25 wide.
    The labels string (menu_82C4DD) holds its four items in two strips at px 0 / 72 (strip $14) and 120 / 192
    (strip $16): line 0 = $14 tiles 0-8, line 1 = $16 tiles 0-8, line 2 = $14 tiles 9-14, line 3 = $16 tiles 9-14.
    Part names: strip $18 + 2 * line, tiles 0-11 (as the original)."""
    w = 25
    top, bottom = rows[12][:20], rows[21][:20]
    rows[12][:w] = top[:3] + [0x2804] * (w - 5) + top[-2:]
    rows[21][:w] = bottom[:18] + [0x280C] * 4 + [0x680C] + bottom[-2:]
    for line in range(4):
        strip, t0 = (0x14, 0x16)[line & 1], (0, 9)[line >> 1]
        for half in (0, 1):
            r = rows[13 + 2 * line + half]
            labels = [text(strip, t0 + t, half) for t in range(9 if t0 == 0 else 6)]
            names = [text(0x18 + 2 * line, t, half) for t in range(12)]
            r[:w] = [r[0], BLANK] + labels + [BLANK] * (9 - len(labels)) + [BLANK] + names + [r[19]]
    return rows


def setup_slot(rows):
    """Setup > a slot (sheet 9C_00). Stats panel (82:AA63): the Accuracy row showed tile 15 of strip $10, which the
    VWF never draws (a strip holds 120 px), between its two halves: map strip $10 tiles 12-14 then strip $12 0-2.
    Header + list (82:AA6A, was rows 34-47, now 32-47): the header two lines high (the window moves up 2 rows into
    free screen rows 6-7): slot label on strip $14, the part name on strip $1E (82:AAF9, asm/menus.asm). Rows 32-33
    held the last rows of a frameless copy of the setup labels at rows 26-33 that no copy reads (read watch over
    $7F:8680-887F through setup, a slot, back, item, info, config: only the decompressor)."""
    rows[19][23:29] = [0x210C, 0x210D, 0x210E, 0x2120, 0x2121, 0x2122]
    rows[20][23:29] = [0x211C, 0x211D, 0x211E, 0x2130, 0x2131, 0x2132]
    top, bottom = rows[34][:19], rows[37][:19]
    head = [top]
    for strip, n, (left, right) in zip((0x14, 0x14, 0x1E, 0x1E), (10, 10, 11, 11),
                                       ((0x2805, 0x6805), (0x2806, 0x6806), (0x2807, 0x6807), (0x2808, 0x6808))):
        half = len(head) % 2 == 0  # label <= 80 px (slot_label), part name <= 88 (parts_name): the rest packs as 0s
        head.append([left] + [text(strip, t, half) for t in range(n)] + [0] * (17 - n) + [right])
    for r, new in zip(range(32, 38), head + [bottom]):
        rows[r][:19] = new
    return rows


def window(w, lines, left=(0x2805, 0x2806, 0x2807, 0x2808), right=(0x6805, 0x6806, 0x6807, 0x6808)):
    """Rows of a framed text window w wide: lines = [(strip, first tile, tiles)] one per text line, a blank column
    before the text (the cursor's room)."""
    rows = [[0x2801, 0x2802, 0x2803] + [0x2804] * (w - 5) + [0x6802, 0x6801]]
    last = 2 * len(lines) - 1
    for k in range(last + 1):
        strip, t0, n = lines[k // 2]
        side = 3 if k == last else min(k, 2)  # frame sides: first row, second, middle rows, last row
        rows.append([left[side], 0] + [text(strip, t0 + t, k % 2) for t in range(n)] + [0] * (w - 3 - n)
                    + [right[side]])
    return rows + [[0x2809, 0x280A, 0x280B] + [0x280C] * (w - 5) + [0x680A, 0x6809]]


def data_submenu(rows):
    """Information > Data submenu (82:AF32, was rows 56-61 cols 6-11, 6 wide): one strip ($18), Information at px 0
    (tiles 0-8), People at cell 6 = px 72 (tiles 9-14); window 12 wide at rows 68-73 (new rows, cols 0-11)."""
    new = window(12, [(0x18, 0, 9), (0x18, 9, 6)])
    rows += [r + [0] * (32 - len(r)) for r in new]
    return rows


EDITS = {3: [setup], 0: [setup_slot, data_submenu]}


def plan(rom):
    """[(file offset, bytes, writer)]: the bank's blocks re-packed from its first block on (an edited sheet is
    usually bigger than its slot; the others keep their bytes), and the pointer table."""
    word0, first, _ = slot(rom, 0)
    count = (rom[BASE] | rom[BASE + 1] << 8) - 0x8000 >> 1
    table, region = bytearray(), bytearray()
    for i in range(count):
        word, o, n = slot(rom, i)
        data = rom[o:o + n]
        if i in EDITS:
            rows = sheet(rom, i)
            for edit in EDITS[i]:
                rows = edit(rows)
            data = lz.compress(pack(rows))
            if len(data) > n:
                data = lz.compress_min(pack(rows))
        table += ((first + len(region)) & 0x7FFF | 0x8000).to_bytes(2, "little")
        region += data
    assert first + len(region) <= BASE + 0x8000 - MARGIN, "bank $9C full"
    return [(BASE, bytes(table), "sheet table 9C"), (first, bytes(region), "sheets 9C (re-packed)")]


def allowed(rom):
    """File offsets plan() may write: all of bank $9C (its table, blocks and FF tail)."""
    return set(range(BASE, BASE + 0x8000))


def main():
    rom = (Path(__file__).resolve().parents[1] / "rom" / "Solid Runner (Japan).sfc").read_bytes()
    i = int(sys.argv[1])
    rows = sheet(rom, i)
    for edit in EDITS.get(i, []):
        rows = edit(rows)
    r0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    n = int(sys.argv[3]) if len(sys.argv) > 3 else len(rows)
    for r in range(r0, min(r0 + n, len(rows))):
        print(f"{r:2d}", " ".join(f"{w:04X}" for w in rows[r]))


if __name__ == "__main__":
    main()
