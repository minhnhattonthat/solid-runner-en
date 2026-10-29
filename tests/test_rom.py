import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Solid Runner (Japan).sfc"


@pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")
def test_rom_matches_sha1():
    import check_rom
    check_rom.check()  # sys.exit on mismatch fails the test


@pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")
def test_header_is_fastrom_lorom():
    hdr = ROM.read_bytes()[0x7FC0:0x7FE0]
    assert hdr[:9].decode("cp932") == "ｿﾘｯﾄﾞﾗﾝﾅｰ"
    assert hdr[0x15] == 0x30  # LoROM, FastROM
