"""Strings read by native code (menus, names, item and database texts, system messages), for tools/extract.py.

Each list is a set of CPU ranges [start, end): every FD/FE/FF-terminated string in a range is one entry; a range
with end None is the single string at start. Starts come from the pointer table behind a list where one is known
(noted per list) or from the code that loads them; bytes between lists are data (coverage.py checks nothing
prose-like is left out). `loose` holds event-VM texts no disassembler root reaches yet (start = after the text op).

    python -X utf8 tools/strings.py [NAME]    # print the entries
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from events import off, ROM  # noqa: E402

LISTS = {
    "runners": [(0x82A1C9, 0x82A2C1)],  # runner/mech names, table 82:A17F
    "menu": [(0x82C48F, 0x82C5A9)],  # field menu, setup, config
    "requests": [(0x82C8D8, 0x82CBE5), (0x82AE32, None), (0x82D06F, None), (0x82D082, None)],  # table 82:C8B6
    "items": [(0x8396AD, 0x839A64)],  # name/description pairs
    "item_use": [(a, None) for a in (0x839B79, 0x839B89, 0x839B9A, 0x839BA9, 0x839BB8, 0x839BCE, 0x839BE4,
                                     0x839BF8, 0x839C0C)],  # VM-style records `9A 1A 9E 18 text FE`
    "parts": [(0x83A642, 0x83AE5F)],  # runner parts and weapons
    "places": [(0x83B4B2, 0x83B9AF)],  # location names, table 83:B41E
    "info": [(0x878562, 0x8785ED),  # info terminal menu, table 87:8558
             (0x878FB4, None), (0x879147, None), (0x87915A, None), (0x8794E8, None), (0x879681, None),
             (0x879A3F, None), (0x879A52, None), (0x879FBD, None), (0x87A111, None), (0x87A124, None),
             (0x87A968, None), (0x87A97A, None)],
    "runner_status": [(0x87B1ED, 0x87B227), (0x87B2F9, None)],  # stat labels with a number code, model/memory
    "database": [(0x87CA07, 0x87EEC4), (0x87EF56, 0x87F616)],  # info database: requests, news, runners, monsters
    "names": [(0x87EEEC, 0x87EF56)],  # character names, table 87:EEC4 (first: the player's `name＝family`)
    "intro": [(0x928F1F, 0x9290A5)],  # opening text crawl
    # mission names (table 92:9681, first entry 96A3) and reports (table 92:9719, between the two: data)
    "missions": [(0x9296A3, 0x929719), (0x92973B, 0x9299C7)],
    # Turbo File menu and errors, table 92:AE6E (19 words), then the not-connected message
    "turbo": [(0x92AE94, 0x92B2CE), (0x929F06, None)],
    "equip": [(0x93B33D, 0x93B36A), (0x93B376, 0x93B430),  # tables 93:B32A, 93:B36A
              (0x93B62E, 0x93B64E),
              (0x93B248, None), (0x93B274, None), (0x93B291, None),  # menu labels, no terminator between them
              (0x938D77, 0x938DAC)],  # item menu
    "places2": [(0x93C015, 0x93C109), (0x93C163, None), (0x93C169, None), (0x93C20B, None)],  # + default names
    # more copies of the default names: 93:CB20 is a {RAM dest, source} table into the name buffers $1AC3/$1AC9/$1ACF
    "default_names": [(0x838F1D, None), (0x838F21, None), (0x93CB2C, None), (0x93CB32, None), (0x93CB38, None)],
    "results": [(0x9295FD, 0x929628)],  # Results screen labels, loaded by the code just before them
    # labels loaded by immediates in the code around them (found by fields.lua logs of the marker tour)
    "labels": [(0x82AB25, 0x82AB39),  # setup slots: left/right shoulder, left/right arm
               (0x82AEF4, None),  # info > data submenu (two rows)
               (0x82C13F, None), (0x839A66, None),  # empty slot dashes (EE is '*' in en.tbl: re-encode as '-')
               (0x82C1DB, None),  # setup slot: remove
               (0x938AFB, None), (0x938B02, None)],  # shop item list
    "help": [(0x93C36F, 0x93C3BE)],  # table 93:C365
    "status": [(0x93951C, None)],  # status screen labels
    "charset": [(0x93CC7E, 0x93CD23)],  # name entry grid
    "loose": [(a, None) for a in (
        0x908366, 0x9083EB, 0x908409, 0x908499, 0x90DD15, 0x90DD76, 0x90DDF4, 0x90DFF0, 0x90E020, 0x90E05A,
        0x90E07A, 0x90E08F, 0x90E0BD, 0x90E15C, 0x90E22C, 0x90E46D, 0x90E47E, 0x90E733, 0x918BAD, 0x918BBF, 0x918BDA, 0x919653,
        0x9196F1, 0x9198D4, 0x938374, 0x93E92A, 0x93E944, 0x93EED3, 0x94A435, 0x9583F7, 0x97B8AE, 0x97B90A,
        0x97B933, 0xA99B2A, 0xA9FEEC, 0xA9FF0E, 0xA9FF4F, 0xA9FF71)],
}


def page_ptrs(rom, p):
    """Bytes of the page-pointer prefix at p (database descriptions: k big-endian 16-bit pointers to the pages, then
    00, the first page right after), else 0. The pointers are data; the pages are the strings."""
    o = off(p)
    for k in range(1, 9):
        if rom[o + 2 * k] == 0 and rom[o] << 8 | rom[o + 1] == (p + 2 * k + 1) & 0xFFFF:
            return 2 * k + 1
    return 0


def strings(rom, start, end, pages=False):
    """[(cpu address, length incl. terminator)] in [start, end), or the one string at start if end is None.
    pages: skip page-pointer prefixes (page_ptrs)."""
    out, p = [], start
    while end is None and not out or end is not None and p < end:
        p += page_ptrs(rom, p) if pages else 0
        q = off(p)
        while rom[q] < 0xFD:
            q += 2 if 0xF9 <= rom[q] <= 0xFC else 1
        n = q + 1 - off(p)
        out.append((p, n))
        p += n
    return out


def list_entries(rom, table):
    """{relative file: [entry]} for script/lists/."""
    files = {}
    for name, ranges in LISTS.items():
        es = files.setdefault(f"lists/{name}.json", [])
        for start, end in ranges:
            for a, n in strings(rom, start, end, pages=name == "database"):
                jp, used = table.decode(rom, off(a), n)
                assert used == n
                es.append({"id": f"{name}_{a:06X}", "addr": f"{a >> 16:02X}:{a & 0xFFFF:04X}", "len": n, "jp": jp,
                           "en": "", "notes": ""})
    return files


def main():
    from tbl import Table
    rom = ROM.read_bytes()
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    for rel, es in list_entries(rom, t).items():
        if len(sys.argv) > 1 and rel != f"lists/{sys.argv[1]}.json":
            continue
        for e in es:
            print(f"{e['id']:18} {e['len']:4d} {e['jp'][:70]}")


if __name__ == "__main__":
    main()
