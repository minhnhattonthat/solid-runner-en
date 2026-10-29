"""release.py: build, verify and package the English patch. Stops at the first failure.

    python -X utf8 tools/release.py [--version 1.0] [--force]

Steps: build -> tests (check.py) -> smoke boot -> leftover Japanese in the script slots (jp_left.py) -> visual-QA gate
(qa_gate.py check, tour made from this exact build) -> debug tool off -> SNES checksum -> BPS patch (bps.py make
re-applies it) -> apply again to the clean original and compare -> zip (patch + README only).
Outputs: release/Solid_Runner_EN_v<ver>.{bps,zip}, release/README.txt, and the playable patched ROM in
build/Solid_Runner_EN_v<ver>.sfc. Publishing is the user's call; this script never uploads anything.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from coverage import TEXT_BANKS  # noqa: E402
from events import off  # noqa: E402
import insert  # noqa: E402

ORIG = ROOT / "rom" / "Solid Runner (Japan).sfc"
BUILT = ROOT / "build" / "solid_runner_en.sfc"
PY = [sys.executable, "-X", "utf8"]

README = """Solid Runner - English translation patch v{ver}
================================================

Unofficial fan translation of Solid Runner (ASCII, 1997, Super Famicom) into English.
No ROM is included and none will be provided: apply the patch to your own dump.

Base ROM (No-Intro: Solid Runner (Japan).sfc, headerless)
  Size:   {size} bytes
  CRC32:  {crc}
  MD5:    {md5}
  SHA-1:  {sha1}

Patched ROM
  CRC32:  {pcrc}
  SHA-1:  {psha1}

Applying
  Apply Solid_Runner_EN_v{ver}.bps with Flips, beat or RomPatcher.js (https://www.marcrobledo.com/RomPatcher.js/).
  A copier-headered (3,146,240-byte) dump must have its 512-byte header removed first.

Notes
  - Tested in Mesen 2.2.1 (MesenCE). Start from a cold boot: savestates made with the Japanese game won't work.
  - English text takes about twice as many letters as the Japanese: set Message Speed to Fast in the
    Config menu if text feels slow.
  - The katakana reading under the title logo was removed; the logo itself is unchanged.

Known issues
  - Not seen in testing: the A5 countdown, the Turbo File "No data" message, the add-armor yes/no prompt
    (needs a level-up) and the shop's sell-count screen. Please report anything odd at
    https://github.com/minhnhattonthat/solid-runner-en/issues (a save file helps).

Credits
  Translation, tools and font: the solid-runner-en project. Translated with AI assistance (Claude, Anthropic),
  checked in the emulator scene by scene. Font: drawn for this project (MIT).
  Solid Runner (c) 1997 ASCII. This patch is not affiliated with them.
"""


def run(step, cmd):
    print(f"== {step}", flush=True)
    rc = subprocess.call(cmd, cwd=ROOT)
    if rc:
        sys.exit(f"release: {step} failed (exit {rc})")


def sha1(p):
    return hashlib.sha1(Path(p).read_bytes()).hexdigest()


def slot_ranges():
    """Bytes the game reads as text: not NOT_TEXT, from a moved head on (before it = VM ops), and not the old copies of
    table-list names (the game reaches those through their repointed table word; tests/test_insert.py follows it)."""
    for f in sorted((ROOT / "script").rglob("*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            if e["id"] in insert.NOT_TEXT or e["id"].split("_")[0] in insert.TABLES:
                continue
            bank, lo = e["addr"].split(":")
            a = int(bank + lo, 16)
            yield off(insert.HEADS.get(e["id"], a)), off(a) + e["len"], e["id"]


def jp_left(skill, rom):
    """Japanese runs left unchanged inside a script slot = text the build never replaced."""
    print("== jp_left", flush=True)
    ranges = []
    for b in TEXT_BANKS:
        o = (b & 0x7F) * 0x8000
        ranges += ["--range", f"{o:X}-{o + 0x7FFF:X}"]
    out = subprocess.run(PY + [f"{skill}/scripts/jp_left.py", str(rom), "--orig", str(ORIG), "--tbl", "tbl/jp.tbl",
                               "--min", "2", "--limit", "1000000"] + ranges,
                         cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if out.returncode > 1:  # 1 = runs found; the code/data noise outside the slots always has some
        sys.exit(f"release: jp_left failed\n{out.stderr}")
    runs = [(int(m[1], 16), int(m[2]), m[3]) for m in re.finditer(r"^0x([0-9A-F]+)\s+(\d+)B\s+(.*)$", out.stdout, re.M)]
    slots = sorted(slot_ranges())
    left = [(o, t, i) for o, n, t in runs for a, z, i in slots if o < z and a < o + n]
    print(f"{len(runs)} unchanged runs in the text banks (code/data), {len(left)} inside script slots")
    for o, t, i in left[:40]:
        print(f"  {o:06X} {i}: {t}")
    if left:
        sys.exit("release: untranslated Japanese left in script slots")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    a = ap.parse_args()

    name = f"Solid_Runner_EN_v{a.version}"
    rel = ROOT / "release"
    bps, zpath, fixed = rel / f"{name}.bps", rel / f"{name}.zip", ROOT / "build" / f"{name}.sfc"
    if not a.force and (bps.exists() or zpath.exists()):
        sys.exit(f"release: {zpath.name} already exists; pass --force to overwrite v{a.version}")
    skill = subprocess.run(PY + ["tools/skill.py"], cwd=ROOT, capture_output=True, text=True).stdout.strip()

    run("build", PY + ["tools/build.py"])
    run("tests", PY + ["tools/check.py"])
    run("smoke", PY + [f"{skill}/scripts/emu.py", str(BUILT), "--out", "work/qa/smoke", "--route", "tools/routes/boot.txt",
                       "--smoke"])
    jp_left(skill, BUILT)

    print("== visual-QA gate", flush=True)
    tour = (ROOT / "work/qa/tour_rom.sha1").read_text().split()[0]
    if tour != sha1(BUILT):
        sys.exit("release: work/qa/tour was not made from this build; re-run the tour and the gate (docs/status.md)")
    run("qa_gate", PY + [f"{skill}/scripts/qa_gate.py", "check", "work/qa/manifest.tsv", "work/qa/verdicts"])

    # the debug tool (tools/debug/*.lua) runs in the emulator only; build.py has no debug switch, and the marker/QA
    # variants (--marker, --qa) are never passed here
    print("== debug tool: external Lua only, plain build", flush=True)

    rel.mkdir(exist_ok=True)
    run("checksum", PY + ["tools/bps.py", "snes-checksum", str(BUILT), "--out", str(fixed)])
    run("patch", PY + ["tools/bps.py", "make", str(ORIG), str(fixed), str(bps)])
    check = ROOT / "build" / "reapply_check.sfc"
    run("re-apply", PY + ["tools/bps.py", "apply", str(ORIG), str(bps), str(check)])
    if sha1(check) != sha1(fixed):
        sys.exit("release: re-applied patch differs from the build")
    check.unlink()

    o, p = ORIG.read_bytes(), fixed.read_bytes()
    (rel / "README.txt").write_text(README.format(
        ver=a.version, size=f"{len(o):,}", crc=f"{zlib.crc32(o):08X}", md5=hashlib.md5(o).hexdigest(),
        sha1=hashlib.sha1(o).hexdigest(), pcrc=f"{zlib.crc32(p):08X}", psha1=hashlib.sha1(p).hexdigest()),
        encoding="utf-8", newline="\r\n")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(bps, bps.name)
        z.write(rel / "README.txt", "README.txt")
    print(f"release ok: {zpath.relative_to(ROOT)} (patch sha1 {sha1(bps)}), playable ROM {fixed.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
