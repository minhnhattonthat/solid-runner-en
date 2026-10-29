"""Event-script disassembler (tools/events.py): reaches the map scripts cleanly and finds their inline texts."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Solid Runner (Japan).sfc"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")


@pytest.fixture(scope="module")
def dis():
    import events
    return events.disassemble(ROM.read_bytes())


@needs_rom
def test_no_bad_ops_and_no_overlaps(dis):
    assert dis.bad == []
    spans = sorted(dis.code.items())
    assert all(a + n <= b for (a, n), (b, _) in zip(spans, spans[1:]))


@needs_rom
def test_known_texts_found(dis):
    assert 0x9584CA in dis.texts  # Tao's first line (95:84C9 op 18), verified on screen in phase 1
    assert len(dis.texts) > 2800


@needs_rom
def test_texts_roundtrip(dis):
    import events
    from tbl import Table
    rom = ROM.read_bytes()
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    for s, (_, n) in dis.texts.items():
        o = events.off(s)
        text, used = t.decode(rom, o, n)
        assert used == n and t.encode(text) == rom[o:o + n], hex(s)
