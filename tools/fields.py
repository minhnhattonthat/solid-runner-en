"""fields.py: field logs (tools/lua/fields.lua) -> windows.json, the width budget of every string seen.

The engine draws each string at column $18BA (12 px cells) of strip $18BB (15 tiles; a dialogue line is 2 strips).
A field's budget is the distance to the next field that starts later on the same strip within the same burst of
drawing (`next-field`), else to the strip end (`strip-end`: text past 120 px wraps to strip+2, which in menus is
usually the next row; a guess until a shot shows the window frame doesn't clip earlier), or to the line end
(`line-end`, 2 strips) when the Japanese itself already runs past the strip end, so strip+2 continues it on screen. Typewriter strings (event
dialogue) take the measured dialogue box. Budgets keep 2 px (shadow + gap) inside the next field.

    python -X utf8 tools/run_scenes.py ... --script tools/lua/fields.lua   (logs in work/qa/<dir>/<scene>/log.txt)
    python -X utf8 tools/fields.py [work/qa/marker]
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import marker  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "windows.json"  # not under script/: the extract and coverage tools read every script/**.json
LINE = re.compile(r"FIELD f(\d+) pc=(\w+) ptr=(\w+) col=(\d+) row=(\d+)")
BURST = 30  # frames: fields drawn closer together than this belong to one screen
# Measured in-game (docs/status.md, shots work/qa/stress, work/qa/stress2): 3 lines x 240 px; the last line of a
# page stops at 232 px when the page prompt shows.
DIALOGUE = {"px": 240, "lines": 3, "last_px": 232, "how": "measured: 40-digit stress lines, work/qa/stress2"}


def entry_index():
    """[(cpu start, cpu end, id)] sorted, for pointer lookup."""
    out = []
    for e in marker.entries():
        bank, lo = e["addr"].split(":")
        a = int(bank, 16) << 16 | int(lo, 16)
        out.append((a, a + e["len"], e["id"]))
    return sorted(out)


def lookup(index, ptr):
    for a, b, eid in index:
        if a <= ptr < b:
            return eid, ptr - a
    return None, None


def jp_cells():
    """{id: longest line of the Japanese in 12 px cells} (controls take none, a kanji pair takes one)."""
    out = {}
    for e in marker.entries():
        text = re.sub(r"\{[^}]*\}(?<!\{br\})", "", e["jp"]).replace("[F9]", "").replace("[FA]", "")
        text = text.replace("[FB]", "").replace("[FC]", "")
        out[e["id"]] = max(len(re.sub(r"\[[0-9A-F]{2}\]", "x", line)) for line in text.split("{br}"))
    return out


def budgets(logdir):
    index, cells = entry_index(), jp_cells()
    fields = {}
    for log in sorted(Path(logdir).glob("*/log.txt")):
        rows = [(int(f), pc, int(p, 16), int(c), int(r)) for f, pc, p, c, r in LINE.findall(log.read_text("utf-8"))]
        bursts, cur = [], []
        for x in rows:
            if cur and x[0] - cur[-1][0] > BURST:
                bursts.append(cur)
                cur = []
            cur.append(x)
        bursts += [cur] if cur else []
        for b in bursts:
            for f, pc, ptr, col, row in b:
                eid, off = lookup(index, ptr)
                if eid is None:
                    continue
                if pc.upper().endswith("A7E1"):
                    fields.setdefault(eid, []).append((DIALOGUE["px"], "dialogue", log.parent.name, off))
                    continue
                later = [c for _, _, _, c, r in b if r == row and c > col]
                if later:
                    px, how = (min(later) - col) * 12 - 2, "next-field"
                elif cells.get(eid, 0) > 10 - col:  # the Japanese already runs on into strip+2: it is the line
                    px, how = (20 - col) * 12, "line-end"
                else:
                    px, how = (10 - col) * 12, "strip-end"
                fields.setdefault(eid, []).append((px, how, log.parent.name, off))
    out = {}
    for eid, obs in sorted(fields.items()):
        px, how, scene, off = min(obs)
        out[eid] = {"px": px, "how": how, "scene": scene}
        if any(o[3] for o in obs):
            out[eid]["sliced"] = sorted({o[3] for o in obs})  # drawn from inside the string: fixed-length fields
    return out


def main():
    logdir = sys.argv[1] if len(sys.argv) > 1 else ROOT / "work" / "qa" / "marker"
    fields = budgets(logdir)
    OUT.write_text(json.dumps({"dialogue": DIALOGUE, "fields": fields}, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    hows = {}
    for v in fields.values():
        hows[v["how"]] = hows.get(v["how"], 0) + 1
    print(f"{OUT}: {len(fields)} entries seen", hows, "sliced:", sum("sliced" in v for v in fields.values()))


if __name__ == "__main__":
    main()
