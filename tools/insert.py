"""insert.py: script/*.json English -> ROM writes (called by tools/build.py; docs/re/insert.md).

Every entry with `en` is encoded with tbl/en.tbl and placed in free space. Its original slot keeps its length and
its terminator: `F8 20 lo hi bank` (jump, asm/vwf.asm), `01` fill, the original end byte. So the VM's text scanner
(81:C930) still finds the end of an inline text, and a reader that walks a list by its terminators still lands on
the next slot. Slots of 4-5 bytes get `F8 22 lo hi` (jump into bank $BA) instead. List entries that sit back to
back are placed back to back, so a reader that draws one string and goes on past its end finds the next one.
Slots under 4 bytes in a list with a pointer table get their table word repointed (the run is then placed in the
table's own bank); `IN_PLACE` lists are written over the slot (the code copies or indexes their bytes).

    python -X utf8 tools/insert.py      dry run: where everything goes, free space left
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import font  # noqa: E402
import freespace  # noqa: E402
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EN_TBL = ROOT / "tbl" / "en.tbl"
CELLS = ROOT / "cells.json"         # sliced menus: item columns (next to windows.json, outside the script globs)
TEXTBANK = 0xBA                     # F8 22 targets (asm/vwf.asm !textbank)
BANKS = [0xBA, 0xBB, 0xCD, 0xD3, 0xD4]  # whole banks of FF
TAILS = [0x86, 0xD7, 0xAF, 0x91, 0x94, 0xB9, 0xC7, 0xCB, 0xD2, 0xB3]  # bank tails of FF (freespace.py), after BANKS
MARGIN = 16                         # bytes left after the last data byte of a tail
TABLES = {"names": (0x87EEC4, 0x87EEEC), "runners": (0x82A17F, 0x82A1C9)}  # list -> its 16-bit pointer table
IN_PLACE = {"charset", "default_names"}  # name-entry grid (indexed by cell), defaults copied into name buffers
# the new game's default names, extracted with places2: copied byte for byte into $1AC3/$1AC9/$1ACF, so in place too
# (a jump slot there put F8 20 into the name buffer and {c0C:xx} printed other text)
NAME_DEFAULTS = {"places2_93C163", "places2_93C169", "places2_93C20B"}
TAB = "{tab:%02X}"


def off(addr):
    """CPU address (int or 'BB:AAAA') -> file offset."""
    if isinstance(addr, str):
        b, a = addr.split(":")
        addr = int(b, 16) << 16 | int(a, 16)
    return ((addr >> 16) & 0x7F) << 15 | (addr & 0x7FFF)


def cpu(o):
    return (0x80 | o >> 15) << 16 | 0x8000 | (o & 0x7FFF)


# Extractor blind spot: a byte pair inside these strings decodes as a text op, so the entry starts mid-string and
# the head bytes belong to no entry. The real text op is just before these addresses (op 18, checked by decoding);
# the slot starts there and the English covers the whole string.
HEADS = {"ev_959A59": 0x959A43, "ev_959C40": 0x959C2F, "ev_A8C91E": 0xA8C910,
         # no pointer or VM path reaches these two (dead copies?): started at the text anyway, in case one is shown
         "ev_93827B": 0x938267, "ev_97BA44": 0x97BA0F,
         "places2_93C015": 0x93C016,  # its "H" is the high byte of the last word of the table at 93:BFE8
         "ev_91940D": 0x91941A, "ev_95A2AA": 0x95A2B1, "ev_979F08": 0x979F1D,  # text after the VM's op 18
         "loose_93EED3": 0x93EED5, "turbo_929F06": 0x929F08}  # after PLX : RTL (FA 6B, read as 選)
# extracted entries that are code or VM data, not text: never written (92:DE77 is 65816 code, the others VM operands)
NOT_TEXT = {"ev_92DE77", "ev_96DB26", "ev_96DBF8", "ev_A8D233"}


def entries():
    """[(list name, entry)]: events (and loose VM texts) are 'events', lists by file stem. HEADS entries come with
    their slot moved to the real string start."""
    out, rom, jp_t = [], None, None
    for f in sorted((ROOT / "script").glob("*/*.json")):
        lst = "events" if f.parent.name == "events" else f.stem
        for e in json.loads(f.read_text(encoding="utf-8")):
            kind = "default_names" if e["id"] in NAME_DEFAULTS else lst
            if e["id"] in HEADS:
                h = HEADS[e["id"]]
                back = off(h) < off(e["addr"])  # a split head: the JP is the whole string from its real start
                e = dict(e, addr=f"{h >> 16:02X}:{h & 0xFFFF:04X}", len=e["len"] + off(e["addr"]) - off(h))
                if back:
                    rom = rom or (ROOT / "rom" / "Solid Runner (Japan).sfc").read_bytes()
                    jp_t = jp_t or Table.load(ROOT / "tbl" / "jp.tbl")
                    e["jp"] = jp_t.decode(rom, off(e["addr"]), e["len"])[0]
            out.append((kind, e))
    return out


def english(e, cells):
    """The entry's English as it is encoded: ' | ' cells -> tabs to their original columns (cells.json);
    other entries get the JP's layout blanks back (layout())."""
    en = e["en"]
    if e["id"] in cells:
        items = en.split(" | ")
        pre = cells[e["id"]]
        assert len(items) <= len(pre), e["id"]
        if all(isinstance(p, (int, list)) for p in pre):  # cells: blank the menu's whole run, then tab to each item
            return clear(e, pre) + "".join(TAB % cell(pre, i)[0] + x for i, x in enumerate(items))
        return "".join(p + x for p, x in zip(pre, items))
    import batches
    return layout(e["jp"], en, batches.box(e["id"], e["jp"])["px"])


def layout(jp, en, px=240):
    """Leading blanks of the JP lines, which the translation dropped: an indent of 1-2 cells (a choice cursor's
    room) is kept as it is; a deeper one centred the line, so the English line is centred on the same point.
    Trailing empty JP lines come back too. Lines are matched one to one; other entries are left alone."""
    import batches
    end = batches.END.search(en)
    tail = end.group(0) if end else ""
    jl = batches.END.sub("", jp).split("{br}")
    el = batches.END.sub("", en).split("{br}")
    while len(el) < len(jl) and all(x == "" for x in jl[len(el):]):
        el.append("")
    if len(jl) != len(el):
        return en
    out = []
    for j, x in zip(jl, el):
        k = len(j) - len(j.lstrip(" "))
        if " | " in x:  # columns: each ' | ' piece starts where the JP line's next blank-separated column does
            cols, col, gap = [], 0, True
            for t in re.findall(r"\{[^}]*\}| {2,}|.", j):
                if t.startswith("{"):
                    continue  # codes have no width
                if t.startswith("  ") or t == " " and not cols:
                    gap = True
                elif gap:
                    cols.append(col)
                    gap = False
                col += len(t)
            parts = x.split(" | ")
            assert len(parts) == len(cols), (jp, en)
            out.append("".join((TAB % c if c else "") + p for c, p in zip(cols, parts)))
            continue
        if k and x and not x.startswith((" ", "{blank}", "{tab:")):
            if k > 2:
                k = max(0, round(k + (len(batches.plain(j)) * 12 - batches.width(x)) / 24))
            x = "{blank}" * max(0, min(k, (px - batches.width(x)) // 12)) + x  # never out of the box
        out.append(x)
    return "{br}".join(out) + tail


def load_cells():
    return {k: v for k, v in json.loads(CELLS.read_text(encoding="utf-8")).items() if not k.startswith("#")}


def cell(pre, i):
    """(column, room in px) of item i of a sliced menu: cells.json gives n (room up to the next item's column, the
    last item as wide as the one before) or [n, px] (a window laid out for the English: tools/winmap.py)."""
    p = pre[i]
    if isinstance(p, list):
        return tuple(p)
    col = lambda j: pre[j][0] if isinstance(pre[j], list) else pre[j]  # noqa: E731
    nxt = col(i + 1) if i + 1 < len(pre) else p + (p - col(i - 1) if i else 99)
    return p, 12 * (nxt - p)


def clear(e, pre):
    """Blanks over every cell the menu's run covers, then back to column 0: the VWF draws only its glyphs' pixels,
    where the original's fixed cells and padding overwrote the whole run (menu_info showed the field menu's leftovers).
    A blank is 12 px in overwrite mode ($18B9 = 0)."""
    import batches
    jp = len(batches.CODE.sub("", batches.END.sub("", e["jp"])))
    end = max([c * 12 + room for c, room in (p for p in pre if isinstance(p, list))] or [0])  # English-only cells
    return "{blank}" * max(jp, -(-end // 12))


def sliced_errors(en, pre):
    """Items of a sliced menu (' | ' pieces): each must fit its cell room (cell())."""
    import batches
    errs = []
    for i, item in enumerate(batches.END.sub("", en).split(" | ")):
        room = cell(pre, i)[1]
        if batches.width(item) > room:
            errs.append(f"{item!r} {batches.width(item)}px > {room}px")
    return errs


def fit_errors(e, cells):
    """Width/line errors of entry e's English as it is encoded (tabs, restored indents): the phase 7 lint, also run
    by batches.py check on sliced menus. script/engine_todo.txt lists the known overflows; callers decide."""
    import batches
    b = batches.box(e["id"], e["jp"])
    text = batches.END.sub("", english(e, cells))
    if e["id"] in cells and all(isinstance(c, (int, list)) for c in cells[e["id"]]):
        errs = sliced_errors(e["en"], cells[e["id"]])
    elif e["id"] in cells:  # a menu laid out in lines: each label fits its column, no more lines than the JP
        jl = batches.END.sub("", e["jp"]).split("{br}")
        lines = text.split("{br}")
        errs = [s for ln in lines for s in re.split(r"\{tab:..\}", ln) if batches.width(s) > b["px"]]
        errs += ["lines"] if len(lines) > len(jl) else []
    else:
        lines = text.split("{br}")
        errs = [ln for ln in lines if batches.width(ln) > b["px"]] + (["lines"] if len(lines) > b["lines"] else [])
    if b.get("chars") and len(font.pack(batches.plain(e["en"]), b["chars"])) > b["chars"]:
        errs.append(f"{len(batches.plain(e['en']))} letters > name buffer {b['chars']} (font.DIGRAPHS)")
    if batches.codes(e["jp"]) != batches.codes(e["en"]):
        errs.append("control codes differ from the JP")
    return errs


class Space:
    """First-fit allocator over free ranges [start, end) of file offsets, one bank each."""

    def __init__(self, rom):
        tails = {b | 0x80: p for b, p, n, f in freespace.tails(rom) if f == 0xFF}
        self.free = []
        for b in BANKS:
            s = off(b << 16 | 0x8000)
            assert tails.get(b) == s, f"bank ${b:02X} is not all FF"
            self.free.append([s, s + 0x8000])
        for b in TAILS:
            self.free.append([tails[b] + MARGIN, off(b << 16 | 0xFFFF) + 1])
        for b in (0x82, 0x87):  # table lists only
            self.free.append([tails[b] + MARGIN, off(b << 16 | 0xFFFF) + 1])
        self.size = sum(e - s for s, e in self.free)

    def alloc(self, n, bank=None):
        for r in self.free:
            b = cpu(r[0]) >> 16
            if bank is not None and b != bank or bank is None and b in (0x82, 0x87):
                continue
            s = r[0]
            while (cpu(s) & 0xFF) >= 0xFD or (cpu(s) >> 8 & 0xFF) >= 0xFD:  # no end byte inside a pointer
                s += 1
            if s + n <= r[1]:
                r[0] = s + n
                return s
        raise SystemExit(f"free space: no room for {n} bytes" + (f" in bank ${bank:02X}" if bank else ""))

    def left(self):
        return sum(e - s for s, e in self.free)


def runs(items):
    """Group (kind, entry) of lists into runs of back-to-back slots; every event is its own run."""
    out = []
    for kind, e in sorted(items, key=lambda x: off(x[1]["addr"])):
        o = off(e["addr"])
        if out and kind != "events" and out[-1][-1][0] == kind and off(out[-1][-1][1]["addr"]) + out[-1][-1][1]["len"] == o:
            out[-1].append((kind, e))
        else:
            out.append([(kind, e)])
    return out


def table_slots(rom, kind, o):
    """File offsets of the 16-bit words in the list's pointer table that point at slot o."""
    a, b = TABLES[kind]
    want = (cpu(o) & 0xFFFF).to_bytes(2, "little")
    return [off(a) + i for i in range(0, off(b) - off(a) - 1, 2) if rom[off(a) + i:off(a) + i + 2] == want]


# The battle HUD (82:A170 LDA $A17F,y / 82:A175 LDA $A180,y, bank 82, 8x8 font at 8 px a letter) holds 9 letters;
# it reads a copy of the runners table where the longer names point at these short forms (D13). Dialogue ({c12},
# 84:ABF6) and 87:BA05 keep the full names.
HUD_OPS = (0x82A171, 0x82A176)
HUD_NAMES = {"runners_82A221": "N. Vague", "runners_82A24F": "G. Hunter", "runners_82A290": "P. Lizard",
             "runners_82A2AC": "Weissheit"}
HUD_MAX = 9


def hud_table(rom, writes, space, en_t):
    a, b = TABLES["runners"]
    t0 = off(a)
    tab = bytearray(rom[t0:off(b)])
    for o, d, who in writes:  # the table words plan() just repointed
        if who.startswith("table runners_"):
            tab[o - t0:o - t0 + 2] = d
    byid = {e["id"]: e for k, e in entries() if k == "runners"}
    for eid, name in HUD_NAMES.items():
        assert len(name) <= HUD_MAX, eid
        e = byid[eid]
        o = off(e["addr"])
        d = en_t.encode(name) + rom[o + e["len"] - 1:o + e["len"]]
        p = space.alloc(len(d), a >> 16)
        writes.append((p, d, "en hud " + eid))
        for w in table_slots(rom, "runners", o):
            tab[w - t0:w - t0 + 2] = (cpu(p) & 0xFFFF).to_bytes(2, "little")
    p = space.alloc(len(tab), a >> 16)
    writes.append((p, bytes(tab), "table runners_hud"))
    for i, op in enumerate(HUD_OPS):
        writes.append((off(op), ((cpu(p) + i) & 0xFFFF).to_bytes(2, "little"), "table runners_hud op"))


def plan(rom):
    """[(file offset, bytes, writer)] for the whole script, and a report."""
    en_t = Table.load(EN_TBL)
    cells = load_cells()
    space = Space(rom)
    writes, report = [], {"jump": 0, "jump16": 0, "table": 0, "in_place": 0, "skipped": []}
    todo = [(k, e) for k, e in entries() if e["en"] and e["id"] not in NOT_TEXT]
    rs = sorted(runs(todo), key=lambda r: all(e["len"] >= 6 for _, e in r))  # runs bound to a bank first
    for run in rs:
        data = []
        for kind, e in run:
            d = en_t.encode(english(e, cells))
            if kind == "default_names" and len(d) > e["len"]:  # D11: letter pairs in one code (font.DIGRAPHS)
                d = b"".join(bytes([font.DIGRAPHS[u]]) if u in font.DIGRAPHS else en_t.encode(u)
                             for u in font.pack(en_t.decode(d, length=len(d) - 1)[0], e["len"] - 1)) + d[-1:]
            assert d[-1] >= 0xFD, f"{e['id']}: English must end with its terminator"
            data.append(d)
        kind0, e0 = run[0]
        if kind0 in IN_PLACE:
            for (kind, e), d in zip(run, data):
                o = off(e["addr"])
                if len(d) > e["len"]:
                    report["skipped"].append((e["id"], f"{len(d)} bytes > slot {e['len']} (in place)"))
                    continue
                # grid rows keep their cells, and padded default names their 01s (the name entry's empty cell)
                if kind == "charset" or 0x01 in rom[o:o + e["len"]]:
                    d = d[:-1] + b"\x01" * (e["len"] - len(d)) + d[-1:]
                else:
                    d = d + b"\xff" * (e["len"] - len(d))
                writes.append((o, d, "text " + e["id"]))
                report["in_place"] += 1
            continue
        short = [e for _, e in run if e["len"] < 6]
        bank = None
        if kind0 in TABLES:  # every entry repointed: the battle HUD's 8x8 renderer reads names by table, no jumps
            bank = rom_bank = off(TABLES[kind0][0]) >> 15 | 0x80
        elif short:
            bank = TEXTBANK
        base = space.alloc(sum(map(len, data)), bank)
        p = base
        for (kind, e), d in zip(run, data):
            o, n = off(e["addr"]), e["len"]
            writes.append((p, d, "en " + e["id"]))
            a = cpu(p)
            end = rom[o + n - 1:o + n]
            slot = None
            if kind in TABLES:
                ws = table_slots(rom, kind, o)  # none: a string only reached through another one's wrap
                assert (ws or n >= 6) and a >> 16 == rom_bank, e["id"]
                for w in ws:
                    writes.append((w, (a & 0xFFFF).to_bytes(2, "little"), "table " + e["id"]))
                report["table"] += 1
            if n >= 6:  # table entries too, for any reader that has the slot's address rather than the table
                slot = bytes([0xF8, 0x20, a & 0xFF, a >> 8 & 0xFF, a >> 16]) + b"\x01" * (n - 6) + end
                report["jump"] += 1
            elif kind in TABLES:
                pass
            elif n >= 4 and kind != "events" or n == 5:
                assert a >> 16 == TEXTBANK
                slot = bytes([0xF8, 0x22, a & 0xFF, a >> 8 & 0xFF]) + (end if n == 5 else b"")
                report["jump16"] += 1
            else:
                raise SystemExit(f"{e['id']}: slot of {n} bytes, no way to reach the English")
            if slot:
                writes.append((o, slot, "slot " + e["id"]))
            p += len(d)
    hud_table(rom, writes, space, en_t)
    report["free_left"] = space.left()
    report["free_total"] = space.size
    return writes, report


ASM_SITES = [(0x00C942, 4), (0x022967, 3), (0x022993, 6), (0x022A2A, 3), (0x026000, 0x2000),  # asm/vwf.asm
             (0x012923, 1), (0x012A6B, 5), (0x012AF9, 4), (0x012A00, 1), (0x012F34, 3),  # asm/menus.asm
             (0x09A7A6, 1), (0x09AAAE, 1), (0x09AC24, 5), (0x09AA9E, 2), (0x09B2A1, 1),
             (0x03A817, 11)] + [  # 87:A817-A821 tab bar pointer (build.py bridges the short gaps)
    (0x09B2DA + 13 * i, 2) for i in range(6)]
FONT = (0x170000, 0x500 * 22)  # $AE:8000 glyphs (tools/font.py)


def allowed(rom):
    """File offsets a build may change: text slots, the pointer tables, free space, the font, asm sites, checksum."""
    ok = set()
    for kind, e in entries():
        ok.update(range(off(e["addr"]), off(e["addr"]) + e["len"]))
    for a, b in TABLES.values():
        ok.update(range(off(a), off(b)))
    for s, e in Space(rom).free:
        ok.update(range(s, e))
    for s, n in ASM_SITES + [FONT, (0x7FDC, 4)] + [(off(op), 2) for op in HUD_OPS]:
        ok.update(range(s, s + n))
    import gfx
    import winmap
    return ok | winmap.allowed(rom) | gfx.allowed(rom)


def main():
    rom = (ROOT / "rom" / "Solid Runner (Japan).sfc").read_bytes()
    writes, rep = plan(rom)
    skipped = rep.pop("skipped")
    print(len(writes), "writes;", rep)
    for eid, why in skipped:
        print("  skipped", eid, why)


if __name__ == "__main__":
    main()
