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
    "battle_msg": {"px": 240, "lines": 2, "prefixes": ["ev_90"],
                   "how": "measured: battle_fight message bar x 8-247, y 192-224 (2 lines); bank $90 = battle "
                          "messages (59 of 60 one line)"},
    "database": {"px": 212, "lines": 3, "lists": ["database"],
                 "how": "measured: data_info_page / data_people_page boxes x 24 to frame 238; title box 2 lines, "
                        "page box 3 lines (FE pages)"},
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
    "parts_name": {"px": 88, "lines": 1, "ranges": [("parts", 0x83A642, 0x83A8D8)],
                   "ids": ["labels_82C13F", "labels_839A66"],
                   "how": "measured: setup_slot header x 150 to frame 240 (menu_setup x 72-164, slot list x 118-236, "
                          "shop_parts_view x 8-247)"},
    "parts_desc": {"px": 182, "lines": 1, "ranges": [("parts", 0x83A8D8, 0x83AE5F)],
                   "how": "measured: shop weapon list (work/play/shop/0003.png) bottom box line 1 from x 8, the weapon "
                          "sprite from x 192; the JP {br} is not honoured there (one line): write none"},
    "slot_label": {"px": 80, "lines": 1, "ranges": [("labels", 0x82AB25, 0x82AB39)],
                   "how": "phase 7 layout (tools/winmap.py setup_slot): the header has two lines, the label has the "
                          "first (10 tiles of strip $14), the part name the second (was: label x 112, name at 150)"},
    "remove": {"px": 116, "lines": 1, "ids": ["labels_82C1DB"], "how": "measured: setup_slot list x 118 to 236"},
    "setup_labels": {"sliced": True, "cells": 4, "px": 72, "ids": ["menu_82C4DD"],
                     "how": "phase 7 layout (tools/winmap.py setup): labels 72 px (the arms 48), part names from x "
                            "104; per-item rooms in cells.json (was rows of 4 cells x 24-70, part names from x 72)"},
    "setup_stats": {"sliced": True, "cells": 6, "px": 68, "ids": ["menu_82C4FA"],
                    "how": "measured: setup_slot left panel rows x 24 to frame 95"},
    "info_menu": {"sliced": True, "cells": 5, "px": 58, "ids": ["menu_82C515"],
                  "how": "measured: menu_info / info_data rows of 5 cells x 24-86, frame 95"},
    "place_name": {"px": 240, "lines": 1, "lists": ["places"], "centred": True,
                   "how": "measured: area_14 banner x 8-247 (work/qa/place f1780); JP centres with leading spaces"},
    "people": {"px": 212, "lines": 1, "lists": ["names"], "how": "measured: data_people_list x 24 to frame 238"},
    "intro": {"px": 240, "lines": 2, "lists": ["intro"], "centred": True,
              "how": "measured: boot crawl (area_01 f900) lines centred, no frame, x 8-247"},
    "turbo": {"px": 240, "lines": 1, "lists": ["turbo"], "how": "measured: turbofile_menu frameless rows from x 8"},
    "shop_left": {"px": 66, "lines": 1, "ids": ["labels_938AFB", "labels_938B02"],
                  "how": "measured: shop_buy_items left window labels x 24, values at x 92 / 88"},
    "shop_menu_left": {"sliced": True, "cells": 5, "px": 54, "ids": ["equip_938D8A", "equip_938D9B"],
                       "how": "measured: shop_buy left window rows x 24 to frame 79"},
    "shop_menu_right": {"sliced": True, "cells": 5, "px": 62, "ids": ["equip_938D77"],
                        "how": "measured: shop_buy right window rows x 118 to frame 182"},
    "item_cmds": {"sliced": True, "cells": 4, "px": 44, "ids": ["menu_82C4A9"],
                  "how": "measured: menu_item use/discard x 32 to frame 79 (title part: menu_title 74)"},
    "requests_title": {"px": 74, "lines": 1, "ids": ["menu_82C4D3"], "how": "measured: title box as menu_title"},
    "config": {"sliced": True, "px": 100, "ids": ["menu_82C529"],
               "how": "measured: menu_config rows x 24 to frame 128 (work/play/config/0000.png)"},
    "config_sub": {"sliced": True, "px": 54, "ids": ["menu_82C540", "menu_82C549"],
                   "how": "measured: sound / message speed submenu x 171 to frame 226 (work/play/config/0001, 0004)"},
    "config_keys": {"sliced": True, "px": 152, "ids": ["menu_82C554"],
                    "how": "measured: area map key config labels x 38 to the key letter at 192 (config/0005)"},
    "battle_keys": {"sliced": True, "px": 50, "ids": ["menu_82C574"],
                    "items": [50, 50, 55, 55, 104, 55, 104],
                    "how": "measured: battle key config (config/0006), labels code-placed in two columns: left x 38 "
                           "to key at 90, right x 166 to key at 223; overboost / item menu x 38 to key at 144"},
    "mission_report": {"px": 160, "lines": 2, "ranges": [("missions", 0x92973B, 0x9299C7)],
                       "how": "measured: results (original) report lines x 80-247 after the `report:` label; phase 7 "
                              "rework of the code-positioned fields may widen it"},
    "results_labels": {"px": 80, "lines": 1, "ids": ["results_92960A", "results_929611", "results_92961B"],
                       "how": "measured: results (work/play/results/0000.png) labels x 40, value right-aligned to "
                              "x 195 (6-cell value from x 123)"},
    "results": {"px": 120, "lines": 1, "lists": ["results", "missions"],
                "how": "measured: results line `Mission 'name' complete` x 8-247 shared by prefix, mission name and "
                       "suffix (code-placed: phase 7 makes it one string); 120 for the name, the rest for the two"},
    "runners": {"px": 120, "lines": 1, "lists": ["runners"],
                "how": "measured (derived): {c12} inserts it into the dialogue line `{c0C:02} VS {c12}.` (91.json): "
                       "240 - runner name field 90 - ' VS ' 24 - '.' 6. 87:BA05 also loads it for a screen not seen"},
    "info_terminal": {"px": 240, "lines": 2, "ids": ["info_878562", "info_87857A", "info_878593", "info_8785B0",
                                                     "info_8785D6"],
                      "how": "measured: info_terminal help box x 8-247, 2 rows"},
    "info_status": {"px": 184, "lines": 1, "lists": ["info"],
                    "how": "measured: info_terminal_1..4 list box top row x 8 to the price at x 194"},
    "info_menu_en": {"px": 144, "lines": 5, "ids": ["info_8787B8"],
                     "how": "measured: info_terminal menu x 96 to the bar end at 240 (Latin in the original)"},
    "info_price": {"px": 56, "lines": 1, "ids": ["info_8791FE"],
                   "how": "measured: info_terminal_1 price x 196 to frame 252"},
    "data_tabs": {"sliced": True, "px": 62, "ids": ["info_87A920"],
                  "how": "measured: info_terminal_4 column heads at x 24, 88, 152"},
    "info_choice": {"sliced": True, "px": 78, "ids": ["info_879681"],
                    "how": "measured: scene info_choice (request terminal, $70:0141+ bit 7) accept x 16, cancel x 96, "
                           "frame 248: each word to 78 px (phase 7: cancel must start at x 96)"},
    "runner_data": {"px": 164, "lines": 4, "ids": ["runner_status_87B2F9"],
                    "how": "measured: runner_status data box x 78 to frame 244, 4 rows"},
    "people_stats": {"px": 212, "lines": 1, "lists": ["runner_status"],
                     "how": "measured: people page box (data_people_page x 24 to 238); 87:B1DE draws these after a "
                            "people page"},
    "save_places": {"px": 154, "lines": 1, "lists": ["places2"],
                    "how": "measured: save_game slot (work/qa/savegame) place x 80 to frame 236, left-aligned; the "
                           "slot's name/TIME/LV line is the 8x8 font (name x 72 to TIME at 152: 10 cells)"},
    # Riff's tune-up (scene tune_riff + tools/lua/pin.lua POKE of his resume script, work/play/riff6 0002-0006)
    "tune_menu": {"sliced": True, "cells": 4, "px": 54, "ids": ["equip_93B248"],
                  "how": "measured: tune-up menu x 24 to frame 80 (the picked row repeats as a title, x 26-88)"},
    "tune_armor": {"px": 54, "lines": 1, "ids": ["equip_93B33D", "equip_93B346", "equip_93B34F", "equip_93B358",
                                                 "equip_93B361"],
                   "how": "measured: armor exchange 'current' box value x 58 to frame 112 (the list itself x 138-240)"},
    "tune_desc": {"px": 240, "lines": 2, "ids": ["equip_93B376", "equip_93B38F", "equip_93B3AB", "equip_93B3C9",
                                                 "equip_93B3E7", "equip_93B403"],
                  "how": "measured: armor exchange description in the dialogue box x 8-247"},
    "tune_labels": {"sliced": True, "px": 40, "ids": ["equip_93B274", "equip_93B291"],
                    "how": "measured: 'current' label x 18 to its value at 58, cost label x 138 to the number at 194; "
                           "the add-armor yes/no (増やす/やめる) needs a level-up, not seen: take the smaller box"},    "third_name": {"px": 90, "lines": 1, "chars": 6, "ids": ["default_names_93CB38", "places2_93C20B"],
                   "how": "measured: runner name ($1ACF, 6 glyphs + FF) in name_entry_a x 144 to frame 236"},
    "data_submenu": {"sliced": True, "cells": 6, "px": 72, "ids": ["labels_82AEF4"],
                     "how": "phase 7 layout (tools/winmap.py data_submenu): window 12 wide, per-item rooms in "
                            "cells.json (was rows of 2 cells x 118, frame 143)"},
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
            single = [v for v, d in VARIANTS.items() if e["id"] in d.get("ids", ())]  # an id beats its list's rule
            if single:
                out[e["id"]] = single[0]
                continue
            for v, d in VARIANTS.items():
                if name in d.get("lists", ()) or (name, i % 2) in d.get("pairs", ()) or e["id"] in d.get("ids", ()) \
                        or e["id"].startswith(tuple(d.get("prefixes", ()))) \
                        or any(n == name and lo <= int(e["addr"].replace(":", ""), 16) < hi
                               for n, lo, hi in d.get("ranges", ())):
                    out[e["id"]] = v
                    break
    return out


def merge(fields, variants):
    """Each entry's budget: its variant's measured px, else the logged geometry. The variant wins: windows map
    strip cells to screen rows in their own way, so logged columns can disagree with the pixels (slot labels:
    2 columns in the log, 38 px on screen)."""
    out = {}
    for eid in sorted(set(fields) | set(variants)):
        f, v = fields.get(eid), variants.get(eid)
        if v:
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
    variants = {k: {x: y for x, y in v.items() if x not in ("lists", "pairs", "ids", "prefixes", "ranges")}
                for k, v in VARIANTS.items()}
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
