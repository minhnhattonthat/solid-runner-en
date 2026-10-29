"""script/ against the original ROM: every entry re-encodes to its original bytes, and the dump is up to date."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Solid Runner (Japan).sfc"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")


def entries():
    for f in sorted((ROOT / "script").rglob("*.json")):
        yield from json.loads(f.read_text(encoding="utf-8"))


@needs_rom
def test_roundtrip():
    from events import off
    from tbl import Table
    rom = ROM.read_bytes()
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    n = 0
    for e in entries():
        bank, lo = e["addr"].split(":")
        o = off(int(bank + lo, 16))
        assert t.encode(e["jp"]) == rom[o:o + e["len"]], e["id"]
        n += 1
    assert n > 3000


def test_kanji_table():
    """Every kanji code the script uses decodes (no raw [F9]-[FC] lead byte left), and no two codes share a reading."""
    from tbl import Table
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    kanji = [v for k, v in t.dec.items() if len(k) == 2 and 0xF9 <= k[0] <= 0xFC]
    assert len(kanji) == len(set(kanji)) > 1000
    left = [e["id"] for e in entries() if any(f"[{p:02X}]" in e["jp"] for p in range(0xF9, 0xFD))]
    assert not left, left[:5]


def test_ids_unique():
    ids = [e["id"] for e in entries()]
    assert len(ids) == len(set(ids))


@needs_rom
def test_dump_up_to_date():
    r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/extract.py"), "--check"], capture_output=True,
                       text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
