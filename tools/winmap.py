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


def window(w, lines, frame=0x2800, blank=0, lead=1):
    """Rows of a framed text window w wide: lines = [(strip, first tile, tiles)] one per text line, `lead` blank
    columns before the text (the cursor's room). frame: the sheet's frame tiles are frame + 1..$C (right side
    mirrored, + $4000); blank: its empty text cell."""
    f = lambda n, mirror=False: frame + n + (0x4000 if mirror else 0)  # noqa: E731
    rows = [[f(1), f(2), f(3)] + [f(4)] * (w - 6) + [f(3, True), f(2, True), f(1, True)]]
    last = 2 * len(lines) - 1
    for k in range(last + 1):
        strip, t0, n = lines[k // 2]
        side = 8 if k == last else 5 + min(k, 2)  # frame sides: first row, second, middle rows, last row
        rows.append([f(side)] + [blank] * lead + [text(strip, t0 + t, k % 2) for t in range(n)]
                    + [blank] * (w - 2 - lead - n) + [f(side, True)])
    return rows + [[f(9), f(0xA), f(0xB)] + [f(0xC)] * (w - 6) + [f(0xB, True), f(0xA, True), f(9, True)]]


def put(rows, r0, c0, rect):
    for i, r in enumerate(rect):
        rows[r0 + i][c0:c0 + len(r)] = r


def data_submenu(rows):
    """Information > Data submenu (82:AF32, was rows 56-61 cols 6-11, 6 wide): one strip ($18), Information at px 0
    (tiles 0-8), People at cell 6 = px 72 (tiles 9-14); window 12 wide at rows 68-73 (new rows, cols 0-11)."""
    new = window(12, [(0x18, 0, 9), (0x18, 9, 6)])
    rows += [r + [0] * (32 - len(r)) for r in new]
    return rows


def tune(rows):
    """Riff's tune-up (sheet 9C_02, loaded at $7F:9000 beside a bank $9D sheet; descriptors in bank 93, src rows
    relative to this sheet). Frame tiles $28C1-$28CC, blank cell $20C0.
    Menu (93:A7A2, rows 0-9): 9 -> 11 wide; its string (equip_93B248) puts Add Armor / Upgrade at px 0 / 72 of strip
    $10 and Swap Armor / Quit at px 120 / 192 (strip $12), as the setup labels.
    Title (93:AAAA, rows 10-13, the picked row: strip $0E): 10 -> 11 wide, 8 tiles.
    Armor list (93:AC1C, rows 14-28): each name (one strip each, $10-$16) 6 -> 12 tiles.
    Current armor (93:AC23): 13x4 at rows 17-20 -> 14x6 at rows 3-8 cols 16-29 ("Current:" = strip $18 tiles 3-8,
    the name = strip $1A on a line of its own: records 93:B2DA.., asm/menus.asm); the add-armor yes/no window
    (93:AA9C) that sat there moves to rows 32-37 cols 19-26 (free)."""
    kw = dict(frame=0x28C0, blank=0x20C0)
    put(rows, 32, 19, [r[16:24] for r in rows[3:9]])
    put(rows, 0, 0, window(11, [(0x10, 0, 8), (0x12, 0, 8), (0x10, 9, 6), (0x12, 9, 6)], **kw))
    put(rows, 10, 0, window(11, [(0x0E, 0, 8)], **kw))
    for line in range(4):
        for half in (0, 1):
            rows[15 + 2 * line + half][2:14] = [text(0x10 + 2 * line, t, half) for t in range(12)]
    put(rows, 3, 16, window(14, [(0x18, 3, 6), (0x1A, 0, 12)], lead=0, **kw))
    return rows


def battle_keys(rows):
    """Config > battle key config (sheet 9C_01 rows 26-42, 28 wide). Labels (menu_82C574, one run over strips
    $14-$1A, run tile T = strip $14 + 2 * (T // 15), tile T % 15) were 4-cell slices; the English run puts them at
    px 0 / 72 / 120 / 216 / 264 / 336 / 384 (cells.json). Left column labels at cols 2-11, their keys (strips $1C/$1E,
    drawn at cells 0, 2, 4, 6 / 0, 2) move from cols 9 / 15 to 13; right column labels from col 18, keys at 25 as
    before. Guard stays at col 21 (its cursor)."""
    run = lambda t, half: text(0x14 + 2 * (t // 15), t % 15, half)  # noqa: E731
    lines = [((0, 9), (0x1C, 0), (9, 6), 18, (0x1C, 3)), ((15, 10), (0x1C, 6), (27, 6), 18, (0x1C, 9)),
             ((33, 9), (0x1C, 12), (42, 4), 21, (0x1E, 0)), ((48, 9), (0x1E, 3), None, 0, None)]
    for k, (left, lkey, right, rcol, rkey) in enumerate(lines):
        for half in (0, 1):
            r = rows[29 + 3 * k + half]
            r[1:27] = [BLANK] * 26
            r[2:2 + left[1]] = [run(left[0] + t, half) for t in range(left[1])]
            r[13:15] = [text(lkey[0], lkey[1] + t, half) for t in range(2)]
            if right:
                r[rcol:rcol + right[1]] = [run(right[0] + t, half) for t in range(right[1])]
                r[25:27] = [text(rkey[0], rkey[1] + t, half) for t in range(2)]
    return rows


EDITS = {3: [setup], 0: [setup_slot, data_submenu], 1: [battle_keys], 2: [tune]}


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
