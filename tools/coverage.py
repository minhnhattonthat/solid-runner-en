"""Coverage: Japanese prose in the ROM that no extracted string covers.

Scans the text banks for terminated strings (FD/FE/FF) that read as sentences: >= 8 characters, >= 50% hiragana or
punctuation (events.prose) and at least one of 「、。. Everything found must be covered by script/ or listed with a
reason in script/not_text.txt (`AAAAAA reason`). Menus and names are too short to gate here; the marker build checks
them on screen.

    python -X utf8 tools/coverage.py [--all]     # list uncovered prose; exit 1 if any
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import events  # noqa: E402
from events import off  # noqa: E402

# banks that hold text; the rest are LZ graphics, maps, the font or code with no strings (docs/re/rom-map.md)
TEXT_BANKS = [0x82, 0x83, 0x87, 0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x9E, 0xA5, 0xA8, 0xA9, 0xAD]


def cpu(p):
    return 0x800000 | (p & 0x3F8000) << 1 | 0x8000 | p & 0x7FFF


def covered_bytes(rom):
    cov = bytearray(len(rom))
    for f in sorted((ROOT / "script").rglob("*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            bank, lo = e["addr"].split(":")
            o = off(int(bank + lo, 16))
            cov[o:o + e["len"]] = b"\x01" * e["len"]
    return cov


def sentences(rom, cov):
    """Uncovered prose strings: [(cpu address, length)]. A string starts after a terminator or covered byte."""
    out = []
    for bank in TEXT_BANKS:
        base = off(bank << 16 | 0x8000)
        p = base
        while p < base + 0x8000:
            q = p
            while q < base + 0x8000 and rom[q] < 0xFD and not cov[q] and q - p < 400:
                q += 2 if 0xF9 <= rom[q] <= 0xFC else 1
            if q < base + 0x8000 and rom[q] >= 0xFD and not cov[q] and q > p:
                n = q + 1 - p
                # the sentence may start anywhere in the run: take the longest prose suffix start
                for s in range(p, q):
                    if events.prose(rom, cpu(s), q + 1 - s) >= 0.5 and \
                            any(b in rom[s:q] for b in b"\xb1\xb7\xb8") and q - s >= 8:
                        out.append((cpu(s), q + 1 - s))
                        break
            p = q + 1 if q > p else p + 1
    return out


def not_text():
    f = ROOT / "script" / "not_text.txt"
    if not f.exists():
        return {}
    return {int(line.split()[0], 16): line for line in f.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    rom = events.ROM.read_bytes()
    from tbl import Table
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    left = [(s, n) for s, n in sentences(rom, covered_bytes(rom)) if s not in not_text()]
    for s, n in left if a.all else left[:60]:
        print(f"{s:06X} {n:4d} {t.decode(rom, off(s), n)[0][:70]}")
    print(f"{len(left)} uncovered sentences")
    sys.exit(1 if left else 0)


if __name__ == "__main__":
    main()
