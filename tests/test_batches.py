"""batches.py: width model, wrap, whole-run term match, and every merged English entry still fits its box."""
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


def test_honorifics():
    sign = "『アンナ＝ケリー様 ひかえ室』"
    assert batches.honorific_errors(sign, "Anna Kelly - Dressing Room")
    assert not batches.honorific_errors(sign, "Anna Kelly-sama - Dressing Room")
    assert batches.honorific_errors("「{c0C:01}さん、{c0C:01}さん…", "{c0C:01}-san, {c0C:01}...")
    for jp in ("貴様！", "皆さん", "探偵さん", "イオン姉ちゃん", "タレントさん"):  # words, not name + honorific
        assert not batches.honorific_errors(jp, "x"), jp


def test_oversized_sliced_item_fails_check(monkeypatch):
    """A sliced menu item wider than its column is an error in check (and so refused by merge), not a warning."""
    eid = "equip_938D8A"
    e = next(e for _, e in insert.entries() if e["id"] == eid)
    assert eid not in batches.engine_todo()
    jp = batches.END.sub("", e["jp"]).replace("{br}", " / ")
    en = batches.END.sub("", e["en"]) + "W" * 200
    rows = {"x.tsv": [[eid, "-", "menu", "-", jp]], "x.out.tsv": [[eid, en]]}
    monkeypatch.setattr(batches, "read_tsv", lambda path, cols: rows[path.name])
    monkeypatch.setattr(batches, "TL", type("P", (), {"__truediv__": lambda s, n: type(
        "F", (), {"name": n, "exists": lambda s: True, "relative_to": lambda s, r: n})()})())
    errs, _ = batches.check("x")
    assert any(eid in x and "px" in x for x in errs), errs


def test_inserted_text_fits():
    """Every English entry, as tools/insert.py encodes it (tabs, restored indents), fits its box and keeps its
    honorifics: the phase 7 lint. engine_todo ids are known overflows waiting for a wider box."""
    cells = insert.load_cells()
    todo, bad = batches.engine_todo(), []
    for _, e in insert.entries():
        if not e["en"]:
            continue
        errs = insert.fit_errors(e, cells)
        hon = batches.honorific_errors(e["jp"], e["en"])
        if errs and e["id"] not in todo or hon:
            bad.append((e["id"], errs + hon))
        if not errs and e["id"] in todo:
            bad.append((e["id"], "fits now: delete it from script/engine_todo.txt"))
    assert not bad, f"{len(bad)} entries: {bad[:40]}"
