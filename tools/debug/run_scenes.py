"""Warp to scenes from a cold boot, one emulator run each (in parallel), and collect a proof shot per scene.

    python -X utf8 tools/debug/run_scenes.py                    every scene in tools/debug/scenes.lua
    python -X utf8 tools/debug/run_scenes.py title_menu shop_parts --frames 2600
    python -X utf8 tools/debug/run_scenes.py --raw 02:00 03:01  raw area:room (hex), for surveys
    python -X utf8 tools/debug/run_scenes.py --states            also save work/states/<scene>.mss (regen the library)
    python -X utf8 tools/debug/run_scenes.py --rom build/solid_runner_en.sfc

Shots land in work/qa/scenes/<name>.png plus a contact sheet work/qa/scenes/sheet*.png. Exit 1 if any run failed or
never logged its WARP line (warp.lua asserts the new-game map load happened).
"""
import argparse
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
SCRIPTS = None  # set in main(): importing skill exits when the skill is absent, and tests import this module

SCENES = ROOT / "tools/debug/scenes.lua"


def scene_entries():
    """(name, frames) for every scene in scenes.lua: a line `  name = ...` inside S.list, optional `frames = N`
    (for battle(...) entries, the 4th argument)."""
    out, inside = [], False
    for line in SCENES.read_text(encoding="utf-8").splitlines():
        inside = inside or line.startswith("S.list = {")
        if inside and line.startswith("}"):
            break
        m = inside and re.match(r"\s{2}(\w+)\s*=\s*", line)
        if m:
            f = re.search(r"\bframes\s*=\s*(\d+)", line) or re.search(r"battle\((?:[^,)]*,){3}\s*(\d+)\s*\)", line)
            out.append((m.group(1), int(f.group(1)) if f else 2600 if "battle(" in line else
                        15000 if "field(" in line else 15400 if "data(" in line else None))  # = scenes.lua
    return out


def run(rom, out_root, name, var, frames, state, extra=()):
    out = out_root / name
    shutil.rmtree(out, ignore_errors=True)
    cmd = [sys.executable, "-X", "utf8", str(Path(SCRIPTS) / "emu.py"), str(rom), "--out", str(out),
           "--script", str(SCENES), "--script", str(ROOT / "tools/debug/warp.lua"), "--frames", str(frames),
           "--shot-every", "300"] + sum((["--var", v] for v in var), []) + sum((["--script", s] for s in extra), [])
    if state:
        cmd += ["--state-out", str(ROOT / "work/states" / f"{name}.mss")]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    ok = r.returncode == 0 and "WARP f" in log and (out / "final.png").exists()
    if (out / "final.png").exists():
        shutil.copy(out / "final.png", out_root / f"{name}.png")
    return name, ok, (r.stdout + r.stderr).strip().splitlines()[-1:] if not ok else ""


def main():
    global SCRIPTS
    from skill import SCRIPTS
    ap =argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*")
    ap.add_argument("--raw", nargs="*", default=[], help="area:room in hex")
    ap.add_argument("--rom", default=str(ROOT / "rom/Solid Runner (Japan).sfc"))
    ap.add_argument("--out", default=str(ROOT / "work/qa/scenes"))
    ap.add_argument("--frames", type=int, default=2400, help="frames from power-on (the warp lands at ~f1560)")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--states", action="store_true")
    ap.add_argument("--script", action="append", default=[], help="extra Lua probe for every run (e.g. fields.lua)")
    ap.add_argument("--var", action="append", default=[], help="NAME=lua-value for every run (probe settings)")
    a = ap.parse_args()

    out_root = Path(a.out)
    out_root.mkdir(parents=True, exist_ok=True)
    jobs = []
    for spec in a.raw:
        ar, rm = (int(x, 16) for x in spec.split(":"))
        jobs.append((f"raw_{ar:02X}_{rm:02X}", [f"AREA=0x{ar:02X}", f"ROOM=0x{rm:02X}"], a.frames))
    if a.names or not a.raw:
        known = dict(scene_entries())
        for n in a.names or known:
            if n not in known:
                sys.exit(f"unknown scene {n}")
            jobs.append((n, [f"SCENE='{n}'"], known[n] or a.frames))
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda j: run(a.rom, out_root, j[0], j[1] + a.var, j[2], a.states, a.script), jobs))
    bad = [r for r in res if not r[1]]
    for name, ok, err in res:
        print(("ok  " if ok else "FAIL"), name, *err)
    shots = [str(out_root / f"{j[0]}.png") for j in jobs if (out_root / f"{j[0]}.png").exists()]
    if shots:
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SCRIPTS) / "sheet.py"), *shots, "--out",
                        str(out_root / "sheet.png")], cwd=ROOT)
    print(f"{len(res) - len(bad)}/{len(res)} scenes reached")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
