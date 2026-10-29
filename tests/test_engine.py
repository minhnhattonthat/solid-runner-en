"""Phase 5: VWF engine + English font + marker build."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Solid Runner (Japan).sfc"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")
needs_asar = pytest.mark.skipif(not (ROOT / "tools" / "asar" / "asar.exe").is_file(), reason="asar absent")


def test_font():
    import font
    font.selftest()
    glyphs, adv = font.build()
    assert len(glyphs) == 82 + len(font.DIGRAPHS) and max(adv) == font.JP_ADV


def test_marker_runs_keep_controls():
    import marker
    from tbl import Table
    en = Table.load(ROOT / "tbl" / "en.tbl")
    data = bytes.fromhex("52F80C01F9300000FF")  # ア {c0C:01} kanji {br}{br} {end}
    m = marker.marker(data, "abc", en)
    assert m[1:4] == data[1:4] and m[-3:] == data[-3:] and len(m) == len(data)


@needs_rom
@needs_asar
def test_marker_build_audits_clean():
    import romdiff
    from build import build
    rom = ROM.read_bytes()
    built, writes = build(rom, markers=True)
    log = ROOT / "work" / "test_engine_writes.txt"
    log.parent.mkdir(exist_ok=True)
    log.write_text("\n".join(writes) + "\n", encoding="utf-8")
    errs, _ = romdiff.check(rom, built, [], romdiff.load_writes(log))
    assert not errs
    assert built[0x022993:0x022997] == bytes.fromhex("5C00F084")  # JML vwf_draw
