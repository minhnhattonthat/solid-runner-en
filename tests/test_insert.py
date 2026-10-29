"""Phase 7: the English build (tools/insert.py through tools/build.py), audited at ROM level."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Solid Runner (Japan).sfc"
pytestmark = [pytest.mark.skipif(not ROM.is_file(), reason="ROM absent"),
              pytest.mark.skipif(not (ROOT / "tools" / "asar" / "asar.exe").is_file(), reason="asar absent")]


@pytest.fixture(scope="module")
def built():
    from build import build
    rom = ROM.read_bytes()
    out, writes = build(rom)
    return rom, out, writes


def test_writes_audit_clean(built, tmp_path):
    """romdiff: every change has a write with the right original bytes, no overlaps, all inside allowed ranges."""
    import insert
    import romdiff
    rom, out, writes = built
    log = tmp_path / "writes.txt"
    log.write_text("\n".join(writes) + "\n", encoding="utf-8")
    ws = romdiff.load_writes(log)
    errs, _ = romdiff.check(rom, out, [], ws)
    assert not errs, errs[:10]
    ok = insert.allowed(rom)
    outside = [(hex(o), by) for o, a, _, by in ws if not set(range(o, o + len(a))) <= ok]
    assert not outside, outside[:10]


def test_every_slot_reaches_its_english(built):
    """Follow each slot the way the engine does (jump, jump16, table word) and decode the English found there."""
    import insert
    from tbl import Table
    rom, out, _ = built
    en = Table.load(insert.EN_TBL)
    cells = {k: v for k, v in json.loads(insert.CELLS.read_text(encoding="utf-8")).items() if not k.startswith("#")}
    seen, bad = 0, []
    for kind, e in insert.entries():
        if not e["en"] or kind in insert.IN_PLACE:
            continue
        o = insert.off(e["addr"])
        s = out[o:o + e["len"]]
        if s[:2] == b"\xf8\x20":
            p = insert.off(int.from_bytes(s[2:5], "little"))
            assert s[-1] == rom[o + e["len"] - 1] and set(s[5:-1]) <= {1}, e["id"]  # scanner still finds the end
        elif s[:2] == b"\xf8\x22":
            p = insert.off(insert.TEXTBANK << 16 | int.from_bytes(s[2:4], "little"))
        else:
            ws = insert.table_slots(rom, kind, o)
            assert ws, e["id"]
            p = insert.off((ws[0] >> 15 | 0x80) << 16 | int.from_bytes(out[ws[0]:ws[0] + 2], "little"))
        want = en.encode(insert.english(e, cells))
        if out[p:p + len(want)] != want:
            bad.append((e["id"], en.decode(out, p, len(want))[0]))
        seen += 1
    assert not bad, bad[:5]
    assert seen > 4000


def test_jump_codes_in_the_control_table(built):
    """The engine's F8 table moved to 84:E000 with cc 20/22/24; both readers point at it."""
    _, out, _ = built
    assert out[0x022967:0x02296A] == bytes.fromhex("FC00E0")  # JSR (ctl_table,x)
    assert out[0x00C942:0x00C946] == bytes.fromhex("BF02E084")  # LDA ctl_table+2,x
    assert out[0x026040 + 2:0x026040 + 4] == b"\x03\x00" and out[0x026048 + 2] == 1  # argc of cc 20 / cc 24
