"""batches.py: width model, wrap, whole-run term match, and every merged English entry still fits its box."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402
import insert  # noqa: E402


def test_width_and_wrap():
    b = {"px": 60, "lines": 3}
    assert batches.width(" ") == 4
    lines = batches.wrap("one two three four five six", b)
    assert all(batches.width(x) <= 60 for x in lines) and " ".join(lines) == "one two three four five six"
    assert batches.wrap("a /  / b", b) == ["a", "", "b"]


def test_term_match_whole_runs():
    assert batches.has_term("リフ「よう", "リフ")
    assert not batches.has_term("リフトに乗る", "リフ")
    assert not batches.has_term("タイミング", "ミン")


def sliced_errors(text, cols, b):
    """Items of a sliced menu as laid out by insert.english(): each must end before the next item's column."""
    errs, items = [], re.split(r"\{tab:([0-9A-F]{2})\}", text)
    starts = [cols[0] if isinstance(cols[0], int) else 0] + [int(c, 16) for c in items[1::2]]
    for i, item in enumerate(items[0::2]):
        room = 12 * ((starts[i + 1] if i + 1 < len(starts) else starts[i] + (starts[i] - starts[i - 1] if i else 99))
                     - starts[i])
        if batches.width(item) > room:
            errs.append(f"{item!r} {batches.width(item)}px > {room}px")
    return errs


def test_inserted_text_fits():
    """Every English entry, as tools/insert.py encodes it (tabs, restored indents), fits its box: the phase 7 lint.
    engine_todo ids are known overflows waiting for a wider box (script/engine_todo.txt)."""
    cells = {k: v for k, v in json.loads(insert.CELLS.read_text(encoding="utf-8")).items() if not k.startswith("#")}
    todo, bad = batches.engine_todo(), []
    for _, e in insert.entries():
        if not e["en"]:
            continue
        b = batches.box(e["id"], e["jp"])
        text = batches.END.sub("", insert.english(e, cells))
        if e["id"] in cells and all(isinstance(c, int) for c in cells[e["id"]]):
            errs = sliced_errors(text, cells[e["id"]], b)
        elif e["id"] in cells:  # a menu laid out in lines: each label fits its column, no more lines than the JP
            jl = batches.END.sub("", e["jp"]).split("{br}")
            lines = text.split("{br}")
            errs = [s for ln in lines for s in re.split(r"\{tab:..\}", ln) if batches.width(s) > b["px"]]
            errs += ["lines"] if len(lines) > len(jl) else []
        else:
            lines = text.split("{br}")
            errs = [ln for ln in lines if batches.width(ln) > b["px"]] + (["lines"] if len(lines) > b["lines"] else [])
        if b.get("chars") and len(batches.plain(e["en"])) > b["chars"]:
            errs.append(f"{len(batches.plain(e['en']))} letters > name buffer {b['chars']}")
        if batches.codes(e["jp"]) != batches.codes(e["en"]):
            errs.append("control codes differ from the JP")
        if errs and e["id"] not in todo:
            bad.append((e["id"], errs))
        if not errs and e["id"] in todo:
            bad.append((e["id"], "fits now: delete it from script/engine_todo.txt"))
    assert not bad, f"{len(bad)} entries: {bad[:40]}"
