"""Phase 2: every scene in tools/debug/scenes.lua names a real map (area/room inside the ROM's area table)."""
import re
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "debug"))
ROM = ROOT / "rom" / "Solid Runner (Japan).sfc"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")


def off(a):
    return ((a & 0x7F0000) >> 1) | (a & 0x7FFF)


def room_count(rom, area):
    """Area table A7:F000: 24-bit pointer to a block whose first word points past its room-pointer list."""
    o = off(0xA7F000) + 3 * area
    p = rom[o] | rom[o + 1] << 8 | rom[o + 2] << 16
    return (struct.unpack_from("<H", rom, off(p))[0] - (p & 0xFFFF) - 2) // 2


@needs_rom
def test_scenes_point_at_real_rooms():
    import run_scenes
    rom = ROM.read_bytes()
    src = (ROOT / "tools/debug/scenes.lua").read_text(encoding="utf-8")
    names = [n for n, _ in run_scenes.scene_entries()]
    assert len(names) == len(set(names)) and len(names) > 60
    for line in src.splitlines():
        m = re.search(r"area = 0x(\w\w), room = 0x(\w\w)", line)
        if m:
            area, room = int(m.group(1), 16), int(m.group(2), 16)
            assert area != 0x18 and room < room_count(rom, area), line


@needs_rom
def test_room_counts():
    rom = ROM.read_bytes()
    assert [room_count(rom, a) for a in (0x01, 0x16, 0x17)] == [15, 10, 9]
