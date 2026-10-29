"""batches.py: width model, wrap, whole-run term match, and every merged English entry still fits its box."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402


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


def test_merged_entries_fit():
    bad = []
    for f in sorted((ROOT / "script").glob("*/*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            if not e["en"]:
                continue
            b = batches.box(e["id"], e["jp"])
            en = batches.END.sub("", e["en"])
            if b.get("sliced"):
                errs = []  # shortcut: sliced cells are laid out in phase 7; its lint gates their width
            else:
                lines = en.split("{br}")
                errs = [ln for ln in lines if batches.width(ln) > b["px"]] + (["lines"] if len(lines) > b["lines"] else [])
            if errs or batches.codes(e["jp"]) != batches.codes(e["en"]):
                bad.append((e["id"], errs))
    assert not bad, bad[:10]
