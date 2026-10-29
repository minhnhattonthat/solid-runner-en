"""textscan.py: which strings the game drew in a tour still hold Japanese (phase 8 runtime check).

Reads the textlog.lua lines (`pc=.. ptr=.. y=.. off=.. <24 bytes>`) from every <tour>/<scene>/log.txt, follows the
string in the built ROM through the jump codes (`F8 20 p24`, `F8 22 p16` into bank TEXTBANK) and decodes it with
tbl/jp.tbl. A string is Japanese when a kana/kanji char comes before its end code; the English codes that reuse
kana cells (02 space, AD -, B0 :) don't count. Prints one line per such string with the scenes that drew it.

    python -X utf8 tools/textscan.py [work/qa/tour] [--rom build/qa_tour.sfc]
Exit 1 when any string is Japanese.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from insert import TEXTBANK, off  # noqa: E402
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LINE = re.compile(r"pc=(\w+) ptr=(\w+) y=(\w+) off=(\w+)")
JP = re.compile(r"[぀-ヿ一-鿿]")
EN_KANA = {0x02, 0xAD, 0xB0}


def follow(rom, a, hops=4):
    """CPU address of the text after any leading jump codes."""
    for _ in range(hops):
        o = off(a)
        if rom[o:o + 2] == b"\xf8\x20":
            a = rom[o + 2] | rom[o + 3] << 8 | rom[o + 4] << 16
        elif rom[o:o + 2] == b"\xf8\x22":
            a = TEXTBANK << 16 | rom[o + 2] | rom[o + 3] << 8
        else:
            break
    return a


def japanese(rom, t, a, n=96):
    """The decoded string at CPU address a if it holds Japanese before its end, else None."""
    o = off(follow(rom, a))
    data = bytearray(rom[o:o + n])
    i = 0
    while i < len(data):  # blank the English codes that reuse kana cells (one-byte codes only)
        b = data[i]
        if b in EN_KANA:
            data[i] = 0x01
        i += 2 if 0xF9 <= b <= 0xFC else 1
    try:
        s = t.decode(bytes(data), 0, maxlen=n)[0]
    except ValueError:
        s = t.decode(bytes(data), 0, length=n)[0]
    s = re.split(r"\{end[^}]*\}|\{goto[^}]*\}", s)[0]
    return s if JP.search(s) else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tour", nargs="?", default=str(ROOT / "work/qa/tour"))
    ap.add_argument("--rom", default=str(ROOT / "build/qa_tour.sfc"))
    a = ap.parse_args()
    lines = (ROOT / "tbl/jp.tbl").read_text(encoding="utf-8").splitlines()
    lines += [ln for ln in (ROOT / "tbl/en.tbl").read_text(encoding="utf-8").splitlines() if ln[:4] in
              ("F820", "F822", "F824")]  # the English build's own control codes
    rom, t = Path(a.rom).read_bytes(), Table(lines)
    hits = {}
    for log in sorted(Path(a.tour).glob("*/log.txt")):
        for ln in log.read_text(encoding="utf-8", errors="replace").splitlines():
            m = LINE.search(ln)
            if m:
                addr = (int(m.group(2), 16) + int(m.group(3), 16)) & 0xFFFFFF
                bank = addr >> 16
                if bank not in (0x7E, 0x7F) and (addr & 0x8000 or bank & 0x7F >= 0x40):  # ROM text only
                    hits.setdefault(addr, set()).add(log.parent.name)
    bad = 0
    for addr in sorted(hits):
        s = japanese(rom, t, addr)
        if s:
            bad += 1
            print(f"{addr >> 16:02X}:{addr & 0xFFFF:04X}  {s[:60]}  [{', '.join(sorted(hits[addr]))}]")
    print(f"{len(hits)} strings drawn, {bad} Japanese")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
