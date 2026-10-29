"""build.py: original ROM -> build/solid_runner_en.sfc + build/writes.txt.

Checks the dump against rom.sha1 first. Every byte change goes through put(), which logs it with the original
bytes it replaces, so `python tools/romdiff.py ORIG BUILT --writes build/writes.txt` audits the build.
No edits yet (phase 3): tests/test_identity.py asserts the build is byte-identical to the original.

    python -X utf8 tools/build.py [--out FILE]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_rom  # noqa: E402
from bps import snes_checksum  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / "rom" / "Solid Runner (Japan).sfc"
OUT = ROOT / "build" / "solid_runner_en.sfc"


def build(orig):
    """Return (built ROM, write log lines) for the original ROM bytes."""
    rom, writes = bytearray(orig), []

    def put(off, data, by):
        writes.append("%06X %s %s %s" % (off, orig[off:off + len(data)].ljust(len(data), b"\xff").hex(), data.hex(), by))
        rom[off:off + len(data)] = data

    # Text, font and graphics edits go here (phases 5+), each through put().
    fixed, _ = snes_checksum(rom)
    put(0x7FDC, fixed[0x7FDC:0x7FE0], "checksum")
    return bytes(rom), writes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    check_rom.check()
    rom, writes = build(ORIG.read_bytes())
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(rom)
    a.out.with_name("writes.txt").write_text("\n".join(writes) + "\n", encoding="utf-8")
    print(f"{a.out}: {len(rom)} bytes, {len(writes)} writes")


if __name__ == "__main__":
    main()
