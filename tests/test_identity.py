"""Identity build (phase 3): unpack + repack with no edits gives the original ROM byte for byte."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Solid Runner (Japan).sfc"
pytestmark = pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")


@pytest.fixture(scope="module")
def rom():
    return ROM.read_bytes()


def test_build_is_byte_identical(rom):
    import romdiff
    from build import build
    built, writes = build(rom)
    assert built == rom
    log = ROOT / "work" / "test_identity_writes.txt"  # romdiff reads the log from a file
    log.parent.mkdir(exist_ok=True)
    log.write_text("\n".join(writes) + "\n", encoding="utf-8")
    errs, _ = romdiff.check(rom, built, [], romdiff.load_writes(log))
    assert not errs


def test_checksum_matches_header(rom):
    from bps import snes_checksum
    assert snes_checksum(rom)[0] == rom  # 3 MiB: mirrored-sum rule


def test_lz_blocks_repack(rom):
    """Every LZ block recompresses to a stream that decodes to the same bytes and is no bigger (fits in place).
    The original encoder isn't plain greedy: 1004 of 1361 blocks come out byte-identical, so the build repacks
    only blocks it edits."""
    from lz import blocks, compress, decompress
    n = 0
    for name, off in blocks(rom):
        try:
            data, used = decompress(rom, off)
        except (ValueError, IndexError):
            continue  # pointer-table entry that isn't LZ (code/data banks)
        packed = compress(data)
        assert decompress(packed, 0)[0] == data, name
        assert len(packed) <= used, name
        n += 1
    assert n > 1300
