"""Event-script disassembler: every inline dialogue text reachable from the maps (docs/re/events.md).

Walks area table A7:F000 -> room scripts (interpreter 80:C900) -> map headers (room ops 08/0A) -> the three thread
entries at header +0x17/+0x1A/+0x1D, then disassembles the VM (81:BDFF, table 81:BE4C) by recursive descent,
following jumps, branches, calls, thread spawns and battle callbacks. Text ops 17/18/19/1A carry inline text that
runs to the first FD/FE/FF by the scanner rule of 81:C930.

    python -X utf8 tools/events.py [--stats] [--texts]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Solid Runner (Japan).sfc"
AREA_TABLE = 0xA7F000
NAREAS = 0x20
NOT_MAPS = {0x18}  # area $18 points at code (87:8000)
ARGC = 0x84AA3B  # text control-code argument counts, word per cc (cc even)


def off(a):
    return ((a & 0x7F0000) >> 1) | (a & 0x7FFF)


def w16(rom, a):
    o = off(a)
    return rom[o] | rom[o + 1] << 8


def p24(rom, a):
    o = off(a)
    return rom[o] | rom[o + 1] << 8 | rom[o + 2] << 16


def near(a, lo16):
    return (a & 0xFF0000) | lo16


# Room-script ops (80:C918, even opcodes): total length incl. the opcode. 08/0A = map header ptr16, 1A = call ptr24,
# 1C = branch (addr24 val target16 cond), 1E = goto ptr16, 16 = native call ptr24. FF ends.
ROOM_LEN = {0x00: 7, 0x02: 6, 0x04: 3, 0x06: 4, 0x08: 3, 0x0A: 3, 0x0C: 9, 0x0E: 3, 0x10: 4, 0x12: 4, 0x14: 8,
            0x16: 4, 0x18: 7, 0x1A: 4, 0x1C: 8, 0x1E: 3, 0x20: 3, 0x22: 9, 0x24: 4, 0x26: 4, 0x28: 4, 0x2A: 3,
            0x2C: 3, 0x2E: 1, 0x5C: 9, 0x5E: 4, 0x60: 3}
ROOM_LEN.update({op: 3 for op in range(0x30, 0x5C, 2)})
# map header ptr16 (mode 00/FF/01 to $52, 80:CD39). Mode 00 (op 08) clears the thread banks (80:CE8E); FF and 01 start
# the threads at header +0x17 (80:CEA3). 5E = goto ptr24.
ROOM_HEADER = {0x0A, 0x60}


def room_scripts(rom):
    """{(area, room): room-script address}."""
    out = {}
    for area in range(NAREAS):
        if area in NOT_MAPS:
            continue
        p = p24(rom, AREA_TABLE + 3 * area)
        n = (w16(rom, p) - (p & 0xFFFF) - 2) // 2
        for room in range(n):
            rs = w16(rom, p + 2 + 2 * room)
            if rs >= 0x8000:  # area 0 ends its list with a 0000
                out[area, room] = near(p, rs)
    return out


def map_headers(rom, start, headers=None, seen=None, tables=None):
    """Walk one room script; returns {header address} it can select. `tables` collects room op 0C's tile/object
    record tables ($1757, 7-byte records, see object_scripts)."""
    headers = set() if headers is None else headers
    seen = set() if seen is None else seen
    tables = set() if tables is None else tables
    work = [start]
    while work:
        a = work.pop()
        while a not in seen:
            seen.add(a)
            op = rom[off(a)]
            if op == 0xFF:
                break
            if op not in ROOM_LEN:
                raise ValueError(f"room op {op:02X} at {a:06X}")
            if op in ROOM_HEADER:
                headers.add(near(a, w16(rom, a + 1)))
            elif op == 0x5E:
                work.append(p24(rom, a + 1))
                break
            elif op == 0x1A:
                map_headers(rom, p24(rom, a + 1), headers, seen, tables)
            elif op == 0x0C:
                tables.add(p24(rom, a + 1))
            elif op == 0x1C:
                work.append(near(a, w16(rom, a + 5)))
            elif op == 0x1E:
                work.append(near(a, w16(rom, a + 1)))
                break
            a += ROOM_LEN[op]
    return headers


def header_threads(rom, h):
    """The thread entry pointers of a map header (bank byte 0 = no thread)."""
    return [t for t in (p24(rom, h + k) for k in (0x17, 0x1A, 0x1D)) if t & 0xFF0000]


# VM opcode lengths incl. the opcode (vm_oplen.py, read by hand where it says dyn). Waits ("0,n") count as n.
VM_LEN = {
    0x01: 1, 0x02: 2, 0x03: 3, 0x04: 3, 0x05: 4, 0x06: 1, 0x07: 4, 0x08: 4, 0x09: 4, 0x0A: 1, 0x0B: 1, 0x0C: 1,
    0x0D: 1, 0x0E: 3, 0x0F: 3, 0x10: 1, 0x11: 1, 0x12: 1, 0x13: 1, 0x14: 3, 0x15: 1, 0x16: 1, 0x1B: 1, 0x1C: 4,
    0x1D: 4, 0x1E: 4, 0x1F: 4, 0x20: 4, 0x21: 4, 0x22: 4, 0x23: 2, 0x24: 1, 0x25: 5, 0x26: 6, 0x27: 7, 0x28: 7,
    0x29: 4, 0x2A: 5, 0x2B: 6, 0x2C: 6, 0x2D: 6, 0x2E: 6, 0x2F: 6, 0x30: 8, 0x31: 10, 0x32: 7, 0x33: 9, 0x34: 6,
    0x35: 6, 0x36: 6, 0x37: 6, 0x3A: 4, 0x3B: 4, 0x3C: 4, 0x3D: 4, 0x3E: 4, 0x3F: 4, 0x40: 4, 0x44: 2, 0x46: 4,
    0x47: 4, 0x48: 1, 0x49: 3, 0x4A: 4, 0x4B: 3, 0x4C: 7, 0x4D: 3, 0x4E: 7, 0x4F: 1, 0x50: 4, 0x51: 4, 0x52: 1,
    0x53: 1, 0x6C: 5, 0x6D: 2, 0x6E: 4, 0x6F: 4, 0x70: 4, 0x71: 5, 0x72: 7, 0x73: 5, 0x74: 7, 0x75: 5, 0x76: 5,
    0x77: 1, 0x78: 1, 0x79: 1, 0x7A: 1, 0x7B: 1, 0x7C: 1, 0x7D: 4, 0x7E: 2, 0x7F: 2, 0x80: 3, 0x81: 3, 0x82: 2,
    0x83: 3, 0x84: 3, 0x85: 1, 0x86: 1, 0x87: 1, 0x88: 2, 0x93: 1, 0x94: 2, 0x95: 2, 0x96: 2, 0x97: 2, 0x98: 2,
    0x99: 2, 0x9A: 2, 0x9B: 2, 0x9C: 2, 0x9D: 2, 0x9E: 1, 0x9F: 1, 0xA0: 1, 0xA1: 4, 0xA2: 4,
}
VM_LEN.update({op: 2 for op in range(0x89, 0x93)})
# 38/39 addr16 val: wait for an SRAM bit (81:CFB9 runs the 34-37 test; when it would branch it parks the thread
# instead, else continues with Y-2 = 4)
VM_LEN.update({0x38: 4, 0x39: 4})
# movement ops 54-6B: 1 arg byte (Y=2, via 81:D634) or none (Y=1, 81:D63C) + a data block of n bytes (handler LDA #n)
VM_LEN.update(dict(zip(range(0x54, 0x6C), [n for n in (2, 3, 7, 4, 3, 6, 2, 8, 7, 7, 3, 2) for _ in (0, 1)])))
BRANCH_AT = {0x30: 5, 0x31: 7, 0x32: 4, 0x33: 6, 0x34: 4, 0x35: 4, 0x36: 4, 0x37: 4}  # target16 offset
# ptr24 to another script, then continue: 07-09/51 start a thread, 4A sets the resume script (81:D33F, restored by
# 81:DA29); 49 is 4A with a ptr16 in this bank. 46/47 (81:D2E7) point at native object code (22 of 25 decode as
# 65816), not scripts.
SPAWN = {0x07, 0x08, 0x09, 0x51, 0x4A}
TEXT_HEAD = {0x17: 2, 0x18: 1, 0x19: 1, 0x1A: 4}  # bytes before the inline text


# table entries where the heuristic overruns: 929BE6's 5th word is native code `DA A2`, 94889F's 4th is `43 AE A5 93`
SWITCH_COUNT = {0x929BE6: 4, 0x94889F: 3}
# Branch targets in the game's own scripts that land on garbage (dead code): A9:9AC9 `35 47 00 08 26 9B` jumps to
# 06 / 0E 00 06 / then "カーク「..." without its 18 opcode (the live copy is at A9:9AD7).
DEAD = {0xA99B26}


def is_op(op):
    return op in VM_LEN or op in TEXT_HEAD or op in (0x00, 0x01, 0x41, 0x42, 0x43, 0x45)


def text_len(rom, a):
    """Length of inline text at a by the 81:C930 scanner (through the FD/FE/FF terminator)."""
    p = off(a)
    s = p
    while True:
        b = rom[p]
        p += 1
        if b < 0xF8:
            continue
        if b == 0xF8:
            cc = rom[p]
            p += 1 + (w16(rom, ARGC + cc * 2) & 0xFF)
            continue
        if b < 0xFD:
            p += 1
            continue
        return p - s


class Disasm:
    def __init__(self, rom):
        self.rom = rom
        self.code = {}  # addr -> length
        self.texts = {}  # text start -> (op addr, length)
        self.bad = []  # (addr, why)
        self.entries = {}  # entry -> origin

    def add(self, a, why):
        if not (a & 0x8000 and off(a) < len(self.rom)):
            self.bad.append((a, f"not ROM ({why})"))
        elif a not in self.code and a not in self.entries:
            self.entries[a] = why
            self.work.append(a)

    def run(self, entries):
        self.work = []
        for a, why in entries:
            self.add(a, why)
        while self.work:
            self.thread(self.work.pop())
        return self

    def thread(self, a):
        rom, self.cur = self.rom, a
        while a not in self.code:
            op = rom[off(a)]
            if op in (0x00, 0x01, 0x41):  # end thread / park (81:C500) / return from call
                self.code[a] = 1
                return
            if op == 0x42:
                self.code[a] = 3
                a = near(a, w16(rom, a + 1))
                continue
            if op == 0x43:
                self.code[a] = 4
                self.add(p24(rom, a + 1), f"jump {a:06X}")
                return
            if op in TEXT_HEAD:
                t = a + TEXT_HEAD[op]
                n = text_len(rom, t)
                self.texts[t] = (a, n)
                self.code[a] = TEXT_HEAD[op] + n
                a += TEXT_HEAD[op] + n
                continue
            if op == 0x45:  # switch: 45 addr24, then a table of 16-bit targets
                self.code[a] = 4
                self.switch(a)
                return
            n = VM_LEN.get(op)
            if n is None:
                if self.cur not in DEAD:
                    self.bad.append((a, f"op {op:02X} in thread {self.cur:06X} ({self.entries.get(self.cur)})"))
                return
            self.code[a] = n
            if op in BRANCH_AT:
                self.add(near(a, w16(rom, a + BRANCH_AT[op])), f"branch {a:06X}")
            elif op in SPAWN and rom[off(a) + 3]:  # 46/47 with bank 00 clear the talk script
                self.add(p24(rom, a + 1), f"spawn {a:06X}")
            elif op == 0x49:
                self.add(near(a, w16(rom, a + 1)), f"resume {a:06X}")
            elif op == 0x40:
                self.add(p24(rom, a + 1), f"call {a:06X}")
            a += n  # 7D's battle record callback (flag + ptr24) is native code (A9:EDDF), not a script

    def switch(self, a):
        """Targets follow the 4-byte head; the table ends where the first target starts (at most 64 entries)."""
        t, end, n = a + 4, None, 0
        while n < SWITCH_COUNT.get(a, 64) and (end is None or t < end):
            dst = near(a, w16(self.rom, t))
            if dst & 0x8000 == 0 or not is_op(self.rom[off(dst)]):  # 929BE6: 4 targets, then native code
                break
            end = dst if end is None else min(end, dst)
            self.add(dst, f"switch {a:06X}")
            t += 2
            n += 1
        self.code[a] = t - a



def object_scripts(rom, table):
    """Room op 0C's record table: 7 bytes {type, ...}. Types 00-06 are tile events with a native routine at +1
    (80:D289); types 08/0A place an object (NPC) whose VM script is the ptr24 at +4 (copied to $7E:A009 by 81:A2F3).
    The table has no count: walk while the type and pointers are valid."""
    out = []
    while True:
        t = rom[off(table)]
        ptr = p24(rom, table + (4 if t >= 8 else 1))
        if t > 0x0A or t & 1 or not (ptr & 0x8000 and 0x80 <= ptr >> 16 < 0xE0):
            return out
        if t >= 8 and not rom[off(table) + 1] & 2:  # flags 07: the pointer is native object code (decodes as 65816)
            out.append(ptr)
        elif t < 8 and ptr in TILE_SCRIPT:
            out.append(p24(rom, table + 4))
        table += 7


TILE_SCRIPT = {0xA7F10F, 0xA7F11E}  # tile-event routines that run the VM script at record +4 (A7:F151 -> 81:D443)


def map_entries(rom):
    """[(thread entry, origin)] for every map header and object record reached from every room."""
    out = []
    for (area, room), rs in room_scripts(rom).items():
        tables = set()
        for h in sorted(map_headers(rom, rs, tables=tables)):
            for t in header_threads(rom, h):
                out.append((t, f"map {area:02X}/{room:02X} hdr {h:06X}"))
        for tb in sorted(tables):
            for t in object_scripts(rom, tb):
                out.append((t, f"map {area:02X}/{room:02X} objects {tb:06X}"))
    return out


STORE_LEN = {0x85: 1, 0x8D: 2, 0x8F: 3}  # STA dp / abs / long


def immediates(rom, target):
    """[(code address, 24-bit value, next 24 code bytes)] for native `LDA #b0 / STA t / LDA #b1 / STA t+1 / LDA #b2 / STA t+2` runs
    (8-bit A) storing a pointer to `target`. Thread starts use $3E-$40 (A7:F1AC, or 80:D813 with handler 81:D443),
    native text calls $18B2-$18B4 (the text engine's pointer, then JSL 84:A873)."""
    out = []
    for p in range(len(rom) - 15):
        if rom[p] != 0xA9:
            continue
        vals, q = [], p
        for k in range(3):
            if rom[q] != 0xA9 or rom[q + 2] not in STORE_LEN:
                break
            n = STORE_LEN[rom[q + 2]]
            if int.from_bytes(rom[q + 3:q + 3 + n], "little") != target + k:
                break
            vals.append(rom[q + 1])
            q += 3 + n
        if len(vals) == 3:
            cpu = 0x800000 | (p & 0x3F8000) << 1 | 0x8000 | p & 0x7FFF
            out.append((cpu, vals[2] << 16 | vals[1] << 8 | vals[0], rom[q:q + 24]))
    return out


SCRIPT_BANKS = set(range(0x92, 0xA0)) | {0xA5, 0xA8, 0xA9, 0xAD}


def native_entries(rom):
    """Thread starts set up by native code: $3E-$40 immediates followed by JSL A7:F1AC, or by handler 81:D443 for
    80:D813 (`LDA #$43 / STA $3B / LDA #$D4`). $3E alone is also a data pointer (sprites, A7:F49D)."""
    out = [(v, f"native {a:06X}") for a, v, nxt in immediates(rom, 0x3E)
           if b"\x22\xac\xf1\xa7" in nxt or b"\xa9\x43\x85\x3b\xa9\xd4" in nxt]
    # $3B-$3D then JSL/JML 81:C266 (spawn the object record there: script at +4 unless flags & 2, as in
    # object_scripts) or 81:C13C/C14A (thread on slot A at $3B, 81:C15E)
    for a, v, nxt in immediates(rom, 0x3B):
        i = min((k for k in (nxt.find(b"\x22"), nxt.find(b"\x5c")) if k >= 0), default=-1)
        call = nxt[i + 1:i + 4] if i >= 0 else b""
        if call == b"\x66\xc2\x81" and not rom[off(v) + 1] & 2:
            out.append((p24(rom, v + 4), f"native {a:06X} object {v:06X}"))
        elif call in (b"\x3c\xc1\x81", b"\x4a\xc1\x81"):
            out.append((v, f"native {a:06X}"))
    return out


PROSE = set(range(0x02, 0x52)) | {0xAD, 0xAE, 0xAF, 0xB1, 0xB2, 0xB7, 0xB8}  # hiragana, ー？！「」、。


def prose(rom, a, n):
    """Share of hiragana/punctuation in a text: dialogue scores ~0.6, data decoded as text ~0.3."""
    o, units, hits, brs = off(a), 0, 0, 0
    p = o
    while p < o + n - 1:
        b = rom[p]
        if b == 0xF8:
            if rom[p + 1] & 1 or rom[p + 1] > 0x1E:
                return 0  # no such control code
            p += 2 + (w16(rom, ARGC + rom[p + 1] * 2) & 0xFF)
            continue
        if b == 0xFC and rom[p + 1] > 0xC2:
            return 0  # past the last kanji
        units += 1
        hits += b in PROSE or 0xF9 <= b <= 0xFC  # kanji count as prose
        brs += b == 0x00
        p += 2 if 0xF9 <= b <= 0xFC else 1
    if units < 6 or brs * 8 > units:  # dialogue breaks a line every ~20 characters; map data is mostly 00
        return 0
    return hits / units


def no_latin(rom, a):
    """No latin letter (B9-EC) in the text at a, kanji pairs and control codes skipped."""
    p = off(a)
    end = p + text_len(rom, a) - 1
    while p < end:
        b = rom[p]
        if b == 0xF8:
            p += 2 + (w16(rom, ARGC + rom[p + 1] * 2) & 0xFF)
            continue
        if 0xB9 <= b <= 0xEC:
            return False
        p += 2 if 0xF9 <= b <= 0xFC else 1
    return True


def sync(rom, a, ends):
    """Start of the op run that leads to the text op at a: the nearest point in the 48 bytes before it (after a text
    terminator or a known instruction) whose op-by-op decode lands exactly on a. (Taking RTS/RTL as boundaries too
    misaligned bank 91, where 60 is a common argument.) None if there is none, so a text op
    byte inside a text or an argument (`ソあぐす{br}フぬ「` = 5F 02 30 0E 00 2A 18) is not taken as a root."""
    for s in range(a, a - 48, -1):
        if not (rom[off(s) - 1] >= 0xFD or s in ends):
            continue
        p = s
        while p < a:
            op = rom[off(p)]
            if op in TEXT_HEAD:
                p += TEXT_HEAD[op] + text_len(rom, p + TEXT_HEAD[op])
            elif op in VM_LEN:
                p += VM_LEN[op]
            else:
                break
        if p == a:
            return s
    return None


def chain(rom, a, code):
    """Fall-through decode from a until an end op or known code: (texts, prose texts) or None if invalid."""
    texts = good = 0
    for _ in range(300):
        if a in code:
            return texts, good
        op = rom[off(a)]
        if op in (0x00, 0x01, 0x41, 0x42, 0x43, 0x45):
            return texts, good
        if op in TEXT_HEAD:
            s = a + TEXT_HEAD[op]
            n = text_len(rom, s)
            if n > 500:
                return None
            texts += 1
            good += prose(rom, s, n) >= 0.5 and any(b in rom[off(s):off(s) + n] for b in b"\xb1\xb7\xb8")  # 「、。
            a = s + n
            continue
        if op not in VM_LEN:
            return None
        a += VM_LEN[op]
    return None


# banks whose scripts the roots reach, plus 87/90/91 (psycho-dive, battle and info scripts reached from native
# tables); 98-9D and 9F hold no reachable script, and data there passes the chain test.
ORPHAN_BANKS = {0x83, 0x87, 0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x9E, 0xA5, 0xA8, 0xA9, 0xAD}
# text-op roots that pass the orphan test but are data or start inside a real text (checked by hand)
LATE_SKIP = {0x90BF33, 0x90BF3A, 0x90BF41, 0x90BF50, 0x90BF5F, 0x90BF6E, 0x90BF7D,  # table rows `ぬュさ、ゅフザぬビあ6`
             0x919E06}  # op byte in the bytes before the real op at 919E0D


def orphan_entries(rom, d):
    """Scripts with no root found yet: addresses some 16-bit word in the same bank or some 24-bit triple points at,
    not yet decoded, whose fall-through chain is valid and whose texts all read as dialogue (prose >= 0.5)."""
    covered = set()
    for a, n in d.code.items():
        covered.update(range(a, a + n))
    cand = set()
    for bank in ORPHAN_BANKS:
        base = off(bank << 16 | 0x8000)
        blk = rom[base:base + 0x8000]
        for i in range(0x7FFF):
            w = blk[i] | blk[i + 1] << 8
            if w >= 0x8000:
                cand.add(bank << 16 | w)
    # scripts are laid out back to back: the byte after an end/jump of known code often starts the next one
    cand.update(a + n for a, n in d.code.items() if rom[off(a)] in (0x00, 0x01, 0x41, 0x42, 0x43))
    # last resort, after the pointer candidates: a text op itself (scripts inline after native code, e.g. 90:83E7)
    # The first text must hold no latin, which data decoded as text is full of; LATE_SKIP drops the rest.
    late = sorted({bank << 16 | 0x8000 | i for bank in ORPHAN_BANKS for i in range(0x8000)
                   if rom[off(bank << 16 | 0x8000) + i] in TEXT_HEAD} - cand - LATE_SKIP)
    ends = {a + n for a, n in d.code.items()}
    late_set = {s for a in late if no_latin(rom, a + TEXT_HEAD[rom[off(a)]]) for s in [sync(rom, a, ends)] if s}
    out = []
    for a in sorted((cand | late_set) - LATE_SKIP):
        if a in covered:
            continue
        r = chain(rom, a, d.code)
        # a pointer root needs every text to read as prose; a text-op root a majority (shouts like うおおお！ fail)
        if not (r and r[0] and (r[1] * 2 > r[0] if a in late_set else r[0] == r[1])):
            continue
        # trial descent: everything it reaches must decode and must not overlap code already known
        trial = Disasm(rom)
        trial.code = dict(d.code)
        trial.run([(a, "orphan")])
        new = {x: n for x, n in trial.code.items() if x not in d.code}
        if not trial.bad and not any(x + k in covered for x, n in new.items() for k in range(n)):
            out.append((a, "orphan"))
            d.code.update(new)
            d.texts.update(trial.texts)
            d.entries.update({x: w for x, w in trial.entries.items() if x not in d.entries})
            covered.update(x + k for x, n in new.items() for k in range(n))
    return out


def disassemble(rom, orphans=True):
    d = Disasm(rom).run(map_entries(rom) + native_entries(rom))
    if orphans:
        d.orphans = []
        while True:  # an accepted orphan adds end-of-block candidates after it
            more = orphan_entries(rom, d)
            if not more:
                return d
            d.orphans += more
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", action="store_true")
    ap.add_argument("--list", type=lambda s: int(s, 16), help="print the decoded instructions from ADDR")
    ap.add_argument("--count", type=int, default=60)
    a = ap.parse_args()
    rom = ROM.read_bytes()
    d = disassemble(rom)
    if a.list:
        for x in [x for x in sorted(d.code) if x >= a.list][:a.count]:
            print(f"{x:06X} {rom[off(x):off(x) + min(d.code[x], 12)].hex(' ')}{' ..' if d.code[x] > 12 else ''}"
                  f"{'   <- ' + d.entries[x] if x in d.entries else ''}")
        return
    print(f"entries {len(d.entries)}  instructions {len(d.code)}  texts {len(d.texts)}  bad {len(d.bad)}")
    for addr, why in d.bad[:40]:
        print(f"  bad {addr:06X} {why}")
    if a.texts:
        sys.path.insert(0, str(ROOT / "tools"))
        from tbl import Table
        t = Table.load(ROOT / "tbl" / "jp.tbl")
        for s, (op, n) in sorted(d.texts.items()):
            print(f"{s:06X} {t.decode(rom, off(s), n)[0][:60]}")


if __name__ == "__main__":
    main()
