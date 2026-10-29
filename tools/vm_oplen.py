"""Static length analysis of the event-script VM opcodes (dispatcher 81:BDFF, handler table 81:BE4C).

Each handler is entered with Y = 1 (opcode byte consumed) and returns by RTS with Y = instruction length (81:BE27
adds Y to the script pointer $32). This walks every handler path, tracking Y through INY/DEY/LDY #/PHY/PLY and JSRs,
and prints the set of lengths per opcode plus flags:
  dyn    Y set from data (TAY, LDY mem, loops): variable length, read the handler by hand
  ptr    writes $32-$34 (the script pointer): a jump/call opcode
  ind    indirect jump (JMP/JSR (abs,x)): not followed
  rtl    hits RTL/RTI at handler level

    python -X utf8 tools/vm_oplen.py [--rom ROM] [--op 18]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from skill import SKILL  # noqa: E402

sys.path.insert(0, str(Path(SKILL) / "scripts"))
from dis65816 import OPS, SIZE  # noqa: E402

TABLE = 0x81BE4C
NOPS = 0xA3  # entries past A2 are not code addresses (table runs into data)


def off(a):
    return ((a & 0x7F0000) >> 1) | (a & 0x7FFF)


class Walk:
    def __init__(self, rom):
        self.rom = rom

    def run(self, addr, y, m8=True, x8=True):
        """Return (set of end Y values, flags) for code at addr reached with Y=y until RTS at depth 0."""
        ends, flags = set(), set()
        seen = set()
        work = [(addr, y, m8, x8, ())]
        steps = 0
        while work:
            a, y, m8, x8, stack = work.pop()
            while True:
                steps += 1
                if steps > 20000:
                    flags.add("dyn")
                    return ends, flags
                key = (a, y, m8, x8, stack)
                if key in seen:
                    break
                seen.add(key)
                if y is not None and y > 80:
                    flags.add("dyn")
                    y = None
                rom = self.rom
                p = off(a)
                op = rom[p]
                mn, mode = OPS[op]
                if mode in ("immM", "immX"):
                    size = 2 if (m8 if mode == "immM" else x8) else 3
                else:
                    size = SIZE.get(mode, 2)
                val = int.from_bytes(rom[p + 1:p + size], "little")
                nxt = (a & 0xFF0000) | ((a + size) & 0xFFFF)
                if mn == "REP":
                    m8, x8 = m8 and not val & 0x20, x8 and not val & 0x10
                elif mn == "SEP":
                    m8, x8 = m8 or bool(val & 0x20), x8 or bool(val & 0x10)
                elif mn == "INY":
                    y = None if y is None else y + 1
                elif mn == "DEY":
                    y = None if y is None else y - 1
                elif mn == "LDY" and mode == "immX":
                    y = val
                elif mn in ("LDY", "TAY", "TXY") or (mn == "PLY" and (not stack or stack[-1][0] != "Y")):
                    if mn == "PLY":
                        stack = stack[:-1]
                    flags.add("dyn")
                    y = None
                elif mn == "PLY":
                    y, stack = stack[-1][1], stack[:-1]
                elif mn == "PHY":
                    stack = stack + (("Y", y),)
                elif mn == "PHP":
                    stack = stack + (("P", (m8, x8)),)
                elif mn == "PLP":
                    if stack and stack[-1][0] == "P":
                        m8, x8 = stack[-1][1]
                    stack = stack[:-1]
                elif mn in ("PHA", "PHX", "PHB", "PHD", "PHK"):
                    stack = stack + (("o", 0),)
                elif mn in ("PLA", "PLX", "PLB", "PLD"):
                    stack = stack[:-1]
                elif mn in ("PEA", "PEI", "PER"):
                    stack = stack + (("o", 0), ("o", 0))
                if mn in ("STA", "STZ", "STX", "STY", "INC", "DEC") and mode in ("dp",) and 0x32 <= val <= 0x34:
                    flags.add("ptr")
                if mn == "RTS":
                    if stack:  # unbalanced pushes: treat as return anyway
                        flags.add("stack")
                    if y is None:
                        flags.add("dyn")
                    else:
                        ends.add(y)
                    break
                if mn in ("RTL", "RTI", "BRK", "STP", "COP"):
                    flags.add("rtl")
                    break
                if mn == "JSR" and mode == "abs":
                    sub_ends, sub_flags = self.run((a & 0xFF0000) | val, y, m8, x8)
                    flags |= sub_flags - {"stack"}
                    if not sub_ends:
                        break
                    for e in sorted(sub_ends, key=lambda v: -1 if v is None else v)[1:]:
                        work.append((nxt, e, m8, x8, stack))
                    y = sorted(sub_ends, key=lambda v: -1 if v is None else v)[0]
                    a = nxt
                    continue
                if mode == "iabsx" or (mn == "JMP" and mode in ("iabs", "ilabs")) or mn == "JML" and mode == "ilabs":
                    flags.add("ind")
                    break
                if mn == "JMP" and mode == "abs":
                    a = (a & 0xFF0000) | val
                    continue
                if mn in ("JML",) and mode == "long":
                    a = val
                    continue
                if mn == "BRA" or mn == "BRL":
                    rel = val - 256 if (mn == "BRA" and val > 127) else (val - 65536 if mn == "BRL" and val > 32767 else val)
                    a = (a & 0xFF0000) | ((a + size + rel) & 0xFFFF)
                    continue
                if mode == "rel":
                    rel = val - 256 if val > 127 else val
                    work.append(((a & 0xFF0000) | ((a + 2 + rel) & 0xFFFF), y, m8, x8, stack))
                a = nxt
        return ends, flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default="rom/Solid Runner (Japan).sfc")
    ap.add_argument("--op", type=lambda s: int(s, 16))
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    w = Walk(rom)
    ops = [a.op] if a.op is not None else range(NOPS)
    for op in ops:
        t = off(TABLE) + 2 * op
        h = 0x810000 | rom[t] | rom[t + 1] << 8
        ends, flags = w.run(h, 1)
        print("%02X %06X len=%s %s" % (op, h, ",".join(str(e) for e in sorted(ends)) or "-", " ".join(sorted(flags))))


if __name__ == "__main__":
    main()
