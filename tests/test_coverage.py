"""Coverage of the original ROM's text: no prose left outside script/, no two entries overlap, and the gate keeps
script strings in and data out."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Solid Runner (Japan).sfc"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")


def spans():
    for f in sorted((ROOT / "script").rglob("*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            bank, lo = e["addr"].split(":")
            a = int(bank + lo, 16)
            yield a, a + e["len"], e["id"]


def test_no_overlap():
    s = sorted(spans())
    bad = [(x[2], y[2]) for x, y in zip(s, s[1:]) if y[0] < x[1]]
    assert not bad, bad[:5]


@needs_rom
def test_no_pointer_table_inside_entries():
    """3+ consecutive 16-bit words (LE or BE) that point at entry starts are a pointer table, not text: the marker
    build overwrote two (missions reports 92:9719, Turbo File 92:AE6E) before the ranges were split."""
    from events import off
    rom = ROM.read_bytes()
    es = sorted(spans())
    starts = {a for a, _, _ in es}
    bad = []
    for a, b, eid in es:
        o, n = off(a), b - a
        for k in range(n - 5):
            for be in (False, True):
                ws = [(rom[p] << 8 | rom[p + 1]) if be else (rom[p] | rom[p + 1] << 8)
                      for p in range(o + k, o + k + 6, 2)]
                if all(w >= 0x8000 and (a & 0xFF0000) | w in starts for w in ws):
                    bad.append((eid, hex(a + k)))
    assert not bad, bad[:5]


@needs_rom
def test_no_uncovered_prose():
    import coverage
    rom = ROM.read_bytes()
    nt = coverage.not_text()
    left = [f"{s:06X}" for s, n in coverage.sentences(rom, coverage.covered_bytes(rom)) if s not in nt]
    assert not left, left[:10]


@needs_rom
def test_gate_separates():
    import coverage
    from events import off
    rom = ROM.read_bytes()
    m = coverage.Bigrams(rom, None)
    # Tao's first line scores as text; map data decoded as text (not_text.txt) does not
    tao = coverage.units(rom, off(0x9584CA), off(0x9584FF))
    assert m.score(tao) > coverage.GATE
    noise = coverage.units(rom, off(0x87B33B), off(0x87B33B + 60))  # native code
    assert m.score(noise) < coverage.GATE
