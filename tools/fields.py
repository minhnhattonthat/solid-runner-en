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
# Box variants measured on marker-tour shots with tools/ruler.py (text start x to the window frame's inner edge, or
# to the next thing drawn on the row). `lists` = list files whose every entry uses the box, `pairs` = (list, parity)
# for name/description lists (entry index % 2), `ids` = single entries. `sliced`: the code shows a linear run of
# cells cut into rows of `cells` 12-px cells (field menu, setup labels...): English needs a tab-to-cell control
# (phase 7); each item's budget is the slice.
VARIANTS = {
    "dialogue": dict(DIALOGUE, lists=["events", "loose", "item_use"],
                     note="field, cutscene and shop typewriter box (opening, shop_greeting: x 8-247)"),
    "item_name": {"px": 94, "lines": 1, "pairs": [("items", 0)],
                  "how": "measured: count at col 8 in menu_item; shop_buy_items list x 144-240 (96)"},
    "item_desc": {"px": 222, "lines": 1, "pairs": [("items", 1)],
                  "how": "measured: menu_item bottom box x 16 to frame 238 (shop_buy_items: x 8-247)"},
    "requests": {"px": 220, "lines": 5, "lists": ["requests"],
                 "how": "measured: requests_view box x 16 to frame 236, 5 text rows"},
    "menu_title": {"px": 74, "lines": 1, "ids": ["menu_82C4B8", "menu_82C4BF", "menu_82C4C7", "menu_82C4CD"],
                   "how": "measured: menu/menu_item title box x 24 to frame 100"},
    "save_slot": {"px": 212, "lines": 1, "ids": ["equip_93B63C", "equip_93B646"], "centred": True,
                  "how": "measured: save_load slot frame x 28-240, text centred"},
    "save_title": {"px": 240, "lines": 1, "ids": ["equip_93B62E", "equip_93B635"], "centred": True,
                   "how": "measured: save_load title centred over x 8-247"},
    "help_line": {"px": 240, "lines": 1, "lists": ["help"], "how": "measured: name_entry bottom box x 8-247"},
    "given_name": {"px": 58, "lines": 1, "chars": 5, "ids": ["default_names_838F1D", "default_names_93CB2C",
                                                             "places2_93C163"],
                   "how": "measured: name_entry first name x 88 to '=' at 148; buffer $1AC3 holds 5 + FF"},
    "family_name": {"px": 66, "lines": 1, "chars": 5, "ids": ["default_names_838F21", "default_names_93CB32",
                                                              "places2_93C169"],
                    "how": "measured: name_entry second name x 168 to frame 236; buffer 5 + FF"},
    "charset": {"px": 11, "lines": 1, "lists": ["charset"], "how": "measured: name_entry grid, one glyph per cell"},
    "parts_view_name": {"px": 240, "lines": 1, "pairs": [("parts", 0)],
                        "how": "measured: shop_parts_view bottom box x 8-247 (setup lists: see fields)"},
    "field_menu": {"sliced": True, "cells": 6, "px": 70, "ids": ["menu_82C48F"],
                   "how": "measured: menu shows the run in rows of 6 cells (x 24-96)"},
    "parts_labels": {"sliced": True, "cells": 4, "px": 44, "ids": ["status_93951C"],
                     "how": "measured: shop_parts_view labels x 8 / 92, values at x 56 / 138"},
    "turbo_menu": {"sliced": True, "cells": 7, "px": 80, "ids": ["turbo_92AF0B"],
                   "how": "measured: turbofile_menu rows x 8, cursor at 84"},
}


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


def variant_of():
    """{id: variant name} from VARIANTS."""
    out = {}
    for f in sorted((ROOT / "script").glob("*/*.json")):
        name = "events" if f.parent.name == "events" else f.stem
        for i, e in enumerate(json.loads(f.read_text(encoding="utf-8"))):
            for v, d in VARIANTS.items():
                if name in d.get("lists", ()) or (name, i % 2) in d.get("pairs", ()) or e["id"] in d.get("ids", ()):
                    out[e["id"]] = v
                    break
    return out


def merge(fields, variants):
    """Each entry's budget: its variant's measured px, or the logged next field when that is closer."""
    out = {}
    for eid in sorted(set(fields) | set(variants)):
        f, v = fields.get(eid), variants.get(eid)
        if v and not (f and f["how"] == "next-field" and f["px"] < VARIANTS[v]["px"]):
            out[eid] = {"px": VARIANTS[v]["px"], "how": "variant", "variant": v}
            if f:
                out[eid]["scene"] = f["scene"]
        else:
            out[eid] = dict(f)
        if f and "sliced" in f:
            out[eid]["sliced"] = f["sliced"]
    return out


def main():
    logdir = sys.argv[1] if len(sys.argv) > 1 else ROOT / "work" / "qa" / "marker"
    fields = merge(budgets(logdir), variant_of())
    variants = {k: {x: y for x, y in v.items() if x not in ("lists", "pairs", "ids")} for k, v in VARIANTS.items()}
    OUT.write_text(json.dumps({"variants": variants, "fields": fields}, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    hows = {}
    for v in fields.values():
        hows[v["how"]] = hows.get(v["how"], 0) + 1
    total = len(marker.entries())
    print(f"{OUT}: {len(fields)}/{total} entries with a budget", hows,
          "sliced:", sum("sliced" in v for v in fields.values()))


if __name__ == "__main__":
    main()
