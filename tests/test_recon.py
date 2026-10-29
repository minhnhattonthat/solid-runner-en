"""Phase 1 findings as tests: the table decodes known on-screen strings, the LZ codec reads the first map's tiles."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Solid Runner (Japan).sfc"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")


@pytest.fixture(scope="module")
def rom():
    return ROM.read_bytes()


@pytest.fixture(scope="module")
def table():
    from tbl import Table
    return Table.load(ROOT / "tbl" / "jp.tbl")


@needs_rom
def test_intro_crawl_decodes(rom, table):
    text, _ = table.decode(rom, 0x090F1F, 4)  # "２１ＸＸ年。" on screen at ~f1250; 年 = FA 62
    assert text == "21XX" and rom[0x090F23:0x090F26] == b"\xfa\x62\xb8"


@needs_rom
def test_tao_line_decodes_and_roundtrips(rom, table):
    start, end = 0x0A84CA, rom.index(b"\xfd", 0x0A84CA) + 1  # op 18 text after 95:84C9, ends FD (more follows)
    assert table.decode(rom, start, 3)[0] == "タオ「" and rom[start + 3:start + 5] == b"\xf9\xc9"  # …
    text, _ = table.decode(rom, start + 5, end - start - 5)
    assert text.startswith("とにかくだ。{br}アイリーンは、わしの") and text.endswith("。{endFD}")
    assert table.encode(table.decode(rom, start, end - start)[0]) == rom[start:end]


@needs_rom
def test_lz_first_map_tiles(rom):
    from lz import decompress
    out, used = decompress(rom, 0x118000 + ((rom[0x118002] | rom[0x118003] << 8) & 0x7FFF))  # A3 table entry 1
    assert len(out) >= 0x2000 and used < len(out)
