"""build.py: original ROM -> build/solid_runner_en.sfc + build/writes.txt.

Checks the dump against rom.sha1 first. Every byte change goes through put(), which logs it with the original
bytes it replaces, so `python tools/romdiff.py ORIG BUILT --writes build/writes.txt` audits the build.
Engine: English glyphs + VWF advance table (tools/font.py), then asm/*.asm through asar (tools/asar/, gitignored:
https://github.com/RPGHacker/asar/releases/download/v1.91/asar191.zip); asar's changes are logged as put() writes.

    python -X utf8 tools/build.py [--out FILE] [--marker] [--qa ID=TEXT ...]

--marker replaces every extracted string with its marker text in place (tools/marker.py); --qa ID=TEXT puts English
TEXT (tbl/en.tbl, padded with spaces to the entry's length) into one entry, for width tests.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_rom  # noqa: E402
import font  # noqa: E402
from bps import snes_checksum  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / "rom" / "Solid Runner (Japan).sfc"
OUT = ROOT / "build" / "solid_runner_en.sfc"
ASAR = ROOT / "tools" / "asar" / "asar.exe"
ASM = [ROOT / "asm" / "vwf.asm", ROOT / "asm" / "menus.asm"]
WIDTHS = 0x027F00  # $84:FF00, vwf_widths in asm/vwf.asm


def assemble(rom):
    """Run every asm file over rom; return the patched bytes."""
    tmp = ROOT / "build" / "asar_tmp.sfc"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_bytes(rom)
    for asm in ASM:
        r = subprocess.run([str(ASAR), "--fix-checksum=off", str(asm), str(tmp)], capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f"asar {asm.name}:\n{r.stdout}{r.stderr}")
    out = tmp.read_bytes()
    tmp.unlink()
    return out


def qa_text(entries, spec):
    """--qa ID=TEXT -> (file offset, bytes padded with spaces before the entry's last byte (its terminator), id)."""
    import marker
    from tbl import Table
    en = Table.load(ROOT / "tbl" / "en.tbl")
    eid, _, text = spec.partition("=")
    e = next(e for e in entries if e["id"] == eid)
    data = en.encode(text)
    if len(data) > e["len"] - 1:
        raise SystemExit(f"--qa {eid}: {len(data)} bytes, entry holds {e['len'] - 1} + terminator")
    off = marker.offset(e["addr"])
    return off, data + en.encode(" ") * (e["len"] - 1 - len(data)), eid


def build(orig, engine=True, markers=False, qa=()):
    """Return (built ROM, write log lines) for the original ROM bytes. engine=False: no edits (identity build)."""
    rom, writes = bytearray(orig), []

    def put(off, data, by):
        writes.append("%06X %s %s %s" % (off, orig[off:off + len(data)].ljust(len(data), b"\xff").hex(), data.hex(), by))
        rom[off:off + len(data)] = data

    if engine:
        glyphs, adv = font.build()
        for code, g in glyphs:
            put(font.FONT_OFF + (code - 1) * font.GLYPH, g, "font %02X" % code)
        put(WIDTHS, adv, "vwf widths")
        patched = assemble(bytes(rom))
        i = 0
        while i < len(rom):
            if patched[i] != rom[i]:
                j = i
                while j < len(rom) and patched[j:j + 8] != rom[j:j + 8]:  # bridge short unchanged gaps
                    j += 1
                while patched[j - 1] == rom[j - 1]:
                    j -= 1
                put(i, patched[i:j], "asm")
                i = j
            i += 1
    if engine and not (markers or qa):
        import gfx
        import insert
        import winmap
        for off, data, by in insert.plan(orig)[0] + winmap.plan(orig) + gfx.plan(orig):
            put(off, data, by)
    if markers or qa:
        import marker
        ms = marker.build_markers(orig) if markers else []
        for off, data, eid in ms:
            put(off, data, "marker " + eid)
        es = marker.entries()
        for spec in qa:
            off, data, eid = qa_text(es, spec)
            put(off, data, "qa " + eid)
    fixed, _ = snes_checksum(rom)
    put(0x7FDC, fixed[0x7FDC:0x7FE0], "checksum")
    return bytes(rom), writes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--marker", action="store_true")
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT")
    a = ap.parse_args()
    check_rom.check()
    rom, writes = build(ORIG.read_bytes(), markers=a.marker, qa=a.qa)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(rom)
    a.out.with_name(a.out.stem + ".writes.txt" if a.out != OUT else "writes.txt").write_text(
        "\n".join(writes) + "\n", encoding="utf-8")
    print(f"{a.out}: {len(rom)} bytes, {len(writes)} writes")


if __name__ == "__main__":
    main()
