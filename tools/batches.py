"""batches.py: phase 6 translation batches (cut, check, merge) and the English width model.

    python -X utf8 tools/batches.py dump OUT.txt          whole script as `id<TAB>jp` (synopsis / terms reading)
    python -X utf8 tools/batches.py split                 cut work/tl/bNNN.tsv + build/terms_bNNN.txt (refuses to overwrite)
    python -X utf8 tools/batches.py check bNNN [..]        validate work/tl/bNNN.out.tsv; prints OK or the errors
    python -X utf8 tools/batches.py merge bNNN [..]        check, then write the wrapped English into script/*.json
    python -X utf8 tools/batches.py fit "text" [--box dialogue]   width per wrapped line (dry run for translators)
    python -X utf8 tools/batches.py pairs bNNN [..]        work/tl/bNNN.pairs.txt for the reviewer

Input row: `id<TAB>speaker<TAB>form<TAB>limit<TAB>jp`; ` / ` = a JP line break. Output row: `id<TAB>EN`.
English is written as one paragraph per box; the tool wraps it by pixel width into the box's lines. ` / ` in the
English forces a break (lists, menus, the intro); ` | ` separates the cells of a sliced menu (one cell per piece).
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import font  # noqa: E402
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work" / "tl"
TERMS = ROOT / "build"
GLOSSARY = ROOT / "glossary.md"
MAX_CHARS = 3500     # JP characters per batch (one Read)
MAX_ENTRIES = 130
CODE = re.compile(r"\{[^}]*\}")
END = re.compile(r"\{end(?:FD|FE)?\}$")
# player given/family name and runner name, as the widest name the 5/6-letter buffers allow (Wwwww)
NAME_PX = {"{c0C:00}": None, "{c0C:01}": None, "{c0C:02}": None}
SPEAKER = re.compile(r"^((?:\{c0C:0[0-2]\})|[^「{\s]{1,12})「")

_adv = None


def adv():
    global _adv
    if _adv is None:
        t = Table.load(font.EN_TBL)
        _, table = font.build(t)
        _adv = {ch: table[code[0]] for ch, code in t.enc.items() if len(code) == 1 and not ch.startswith("{")}
        w = max(_adv[c] for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ") + 5 * max(_adv[c] for c in "abcdefghijklmnopqrstuvwxyz")
        for k in NAME_PX:
            NAME_PX[k] = w  # shortcut: one capital + 5 lowercase for every name; tighten when the buffers are known
    return _adv


def width(text):
    """Pixel width of one line of English (control codes: names at NAME_PX, others 0)."""
    a = adv()
    px = 0
    for tok in re.split(r"(\{[^}]*\})", text):
        if tok.startswith("{tab:"):
            px = int(tok[5:-1], 16) * font.JP_ADV  # the original's column n (asm/vwf.asm ctl_tab)
        elif tok == "{blank}":
            px += font.JP_ADV
        elif tok.startswith("{"):
            px += NAME_PX.get(tok, 0)
        else:
            px += sum(a.get(c, font.JP_ADV) for c in tok)
    return px


def entries():
    """[(list name, entry)] in script order, events first."""
    out = []
    for f in sorted((ROOT / "script" / "events").glob("*.json")):
        out += [("events", e) for e in json.loads(f.read_text(encoding="utf-8"))]
    for f in sorted((ROOT / "script" / "lists").glob("*.json")):
        out += [(f.stem, e) for e in json.loads(f.read_text(encoding="utf-8"))]
    return out


def budgets():
    w = json.loads((ROOT / "windows.json").read_text(encoding="utf-8"))
    return w["variants"], w["fields"]


def box(eid, jp=None):
    """The entry's box: {px, lines, last_px, sliced, cells, items, centred, variant}. With jp, never smaller than
    the Japanese itself (12 px a glyph, its own line count): the original shows it, so the box holds it."""
    global _budgets
    if _budgets is None:
        _budgets = budgets()
    variants, fields = _budgets
    v = fields[eid]["variant"]
    b = dict(variants[v], variant=v)
    b.setdefault("lines", 1)
    if jp and not b.get("sliced"):
        jl = END.sub("", jp).split("{br}")
        b["lines"] = max(b["lines"], len(jl))
        b["px"] = max(b["px"], max(len(plain(x)) * font.JP_ADV for x in jl))
    return b


_budgets = None


def engine_todo():
    """{id: reason} from script/engine_todo.txt: full-term English waiting for a wider box (phase 7)."""
    p = ROOT / "script" / "engine_todo.txt"
    rows = [ln.split("\t", 1) for ln in p.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return {r[0]: r[1] for r in rows}


def plain(jp):
    return CODE.sub("", jp).strip("　 ")


def form_of(lst, b):
    if b.get("sliced"):
        return "menu"
    if lst in ("names", "default_names", "runners", "places", "places2", "charset") or b["variant"].endswith("_name"):
        return "name"
    if lst == "intro":
        return "narration"
    if lst != "events" and lst != "loose":
        return "text" if b["lines"] > 1 or b["px"] >= 150 else "menu"
    return "dlg"


def limit_of(b):
    if b.get("sliced"):
        n = b.get("cells")
        return f"{n or '?'}cells x {b['px']}px"
    s = f"{b['px']}px x {b['lines']}"
    if b.get("last_px"):
        s += f" (last {b['last_px']})"
    return s


def jp_cell(jp):
    return END.sub("", jp).replace("{br}", " / ")


def dump(out):
    lines = [f"{e['id']}\t{jp_cell(e['jp'])}" for _, e in entries()]
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(len(lines), "entries ->", out)


# ---- glossary ----

def glossary():
    """[(jp, en, avoid)] from every table row of glossary.md."""
    rows = []
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(cells) < 2 or cells[0] in ("JP", "") or set(cells[0]) <= set("-"):
            continue
        rows.append((cells[0], cells[1], [a.strip() for a in (cells[4] if len(cells) > 4 else "").split(",")
                                         if a.strip()]))
    return rows


KANA_RUN = re.compile(r"[゠-ヿ－−]+|[一-鿿々]+|[぀-ゟ]+")


def has_term(jp, term):
    """Whole-run match: the term must start and end on a script-run boundary (ミン never matches inside タイミング)."""
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        kind = lambda c: (c and ("k" if "゠" <= c <= "ヿ" else "h" if "぀" <= c <= "ゟ" else
                                 "c" if "一" <= c <= "鿿" else "o"))
        before = jp[a - 1] if a else ""
        after = jp[b] if b < len(jp) else ""
        if kind(before) != kind(term[0]) and kind(after) != kind(term[-1]):
            return True
        if kind(term[0]) == "c":  # kanji compounds sit inside longer kanji runs; accept them
            return True
    return False


# ---- split ----

def split():
    TL.mkdir(parents=True, exist_ok=True)
    TERMS.mkdir(exist_ok=True)
    if list(TL.glob("b[0-9][0-9][0-9].tsv")):
        sys.exit("work/tl already has batches; delete them first (split numbers from b001 and never overwrites)")
    gl = glossary()
    batches, cur, chars, last, sliced = [], [], 0, None, []
    for lst, e in entries():
        if not plain(e["jp"]):
            continue
        if box(e["id"]).get("sliced"):  # fixed-length menu cells: one last batch, translated by the controller
            sliced.append((lst, e))
            continue
        group = lst if lst != "events" else e["id"][3:5]  # a list, or an event bank
        n = len(plain(e["jp"]))
        full = chars + n > MAX_CHARS or len(cur) >= MAX_ENTRIES
        kind_change = last and (lst == "events") != (last[0] == "events")
        nice_cut = last and group != last[1] and chars > 0.7 * MAX_CHARS  # end a near-full batch on a bank/list edge
        if cur and (full or kind_change or nice_cut):
            batches.append(cur)
            cur, chars = [], 0
        cur.append((lst, e))
        chars += n
        last = (lst, group)
    batches += [cur, sliced]
    for i, b in enumerate(batches, 1):
        name = f"b{i:03d}"
        rows = []
        for lst, e in b:
            bx = box(e["id"], e["jp"])
            m = SPEAKER.match(e["jp"])
            rows.append("\t".join([e["id"], m.group(1) if m else "-", form_of(lst, bx), limit_of(bx), jp_cell(e["jp"])]))
        (TL / f"{name}.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jp_all = "\n".join(e["jp"] for _, e in b)
        terms = [f"{j} = {en}" + (f"  (avoid: {', '.join(av)})" if av else "") for j, en, av in gl if has_term(jp_all, j)]
        (TERMS / f"terms_{name}.txt").write_text("\n".join(terms) + "\n", encoding="utf-8", newline="\n")
        print(name, len(b), "entries", sum(len(plain(e["jp"])) for _, e in b), "chars", len(terms), "terms")


# ---- wrap / check ----

def wrap(en, b):
    """English paragraph -> list of lines for box b (greedy by pixel width; ' / ' forces a break)."""
    lines = []
    for para in en.split(" / "):
        words, line = para.split(" "), ""
        for wd in words:
            trial = wd if not line else line + " " + wd
            limit = b["px"]
            if line and width(trial) > limit:
                lines.append(line)
                line = wd
            else:
                line = trial
        lines.append(line)
    return lines


def fit_errors(en, b):
    """Width/line errors for one English entry in box b."""
    errs = []
    if b.get("sliced"):
        cells = en.split(" | ")
        # no cell-count check: the logged slice counts include blank padding cells; phase 7 lays the cells out
        items = b.get("items") or [b["px"]] * len(cells)
        for i, c in enumerate(cells):
            lim = items[i] if i < len(items) else b["px"]
            if width(c) > lim:
                errs.append(f"cell {i + 1} {c!r} is {width(c)}px > {lim}px")
        return errs
    lines = wrap(en, b)
    if b.get("chars") and len(en) > b["chars"] and not CODE.search(en):
        errs.append(f"{len(en)} letters > name buffer {b['chars']} (report LONG; phase 7 widens the buffer)")
    if len(lines) > b["lines"]:
        errs.append(f"{len(lines)} lines > {b['lines']} at {b['px']}px: {lines}")
    for ln in lines:
        if width(ln) > b["px"]:
            errs.append(f"line {ln!r} is {width(ln)}px > {b['px']}px")
    if b.get("last_px") and len(lines) == b["lines"] and width(lines[-1]) > b["last_px"]:
        errs.append(f"last line {lines[-1]!r} is {width(lines[-1])}px > {b['last_px']}px (the more-arrow)")
    return errs


def read_tsv(path, cols):
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != cols:
            rows.append((None, f"line {n}: {len(parts)} tab-separated fields, expected {cols}"))
            continue
        rows.append(parts)
    return rows


def codes(s):
    """Control codes of a text, without line breaks and layout ({tab:n}, {blank}: tools/insert.py)."""
    return sorted(c for c in CODE.findall(s) if c != "{br}" and c != "{blank}" and not c.startswith("{tab:"))


def check(name, quiet=False):
    src = read_tsv(TL / f"{name}.tsv", 5)
    outp = TL / f"{name}.out.tsv"
    if not outp.exists():
        return [f"{outp.relative_to(ROOT)} missing"], {}
    out = read_tsv(outp, 2)
    errs = [r[1] for r in out if r[0] is None]
    out = [r for r in out if r[0] is not None]
    ids = [r[0] for r in src]
    got = {}
    for eid, en in out:
        if eid in got:
            errs.append(f"{eid}: duplicate id")
        got[eid] = en
    for eid in ids:
        if eid not in got:
            errs.append(f"{eid}: missing")
    for eid in got:
        if eid not in ids:
            errs.append(f"{eid}: not in this batch")
    enc = adv()
    gl = glossary()
    jp_of = {r[0]: r[4] for r in src}
    for eid, en in got.items():
        if eid not in jp_of:
            continue
        jp = jp_of[eid]
        e = []
        bare = CODE.sub("", en).replace(" | ", "")
        bad = sorted({c for c in bare if c not in enc})
        if bad:
            e.append(f"characters not in the English font: {''.join(bad)!r}")
        if "\\u" in en or "\\t" in en or "\\n" in en:
            e.append("escape sequence in the English (write plain text; ' / ' for a forced break)")
        if codes(jp) != codes(en):
            e.append(f"control codes {codes(en)} differ from the JP {codes(jp)}")
        if re.search(r"\}(st|nd|rd|th)\b", en):
            e.append("ordinal suffix glued to a variable")
        if re.search(r"\b(a|an|A|An)\s+\{c0C", en):
            e.append("a/an right before a name variable")
        if en != en.strip() or "  " in en.replace(" / ", "/"):
            e.append("leading/trailing or double spaces")
        for j, t, avoid in gl:
            if t and t != "-" and has_term(jp, j) and t.lower() not in en.lower():
                e.append(f"glossary: {j} -> {t!r} missing")
            for a in avoid:
                if re.search(r"\b" + re.escape(a) + r"\b", en):
                    e.append(f"glossary: avoid {a!r} (use {t!r})")
        b = box(eid, jp.replace(" / ", "{br}"))
        # sliced cell widths are the JP layout (phase 7 relays the cells); engine_todo ids wait for a wider box
        if b.get("sliced") or eid in engine_todo():
            for x in fit_errors(en, b):
                print(f"  warning {eid}: {x} (phase 7 layout)")
        else:
            e += fit_errors(en, b)
        errs += [f"{eid}: {x}" for x in e]
    return errs, got


def cmd_check(names):
    bad = 0
    for name in names:
        errs, _ = check(name)
        if errs:
            bad += 1
            print(f"{name}: {len(errs)} error(s)")
            for x in errs:
                print("  " + x)
        else:
            print(f"{name}: OK")
    return 1 if bad else 0


def merge(names):
    if cmd_check(names):
        sys.exit("merge refused: fix the errors above")
    en = {}
    for name in names:
        en.update(check(name)[1])
    files = sorted((ROOT / "script").glob("*/*.json"))
    n = 0
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        changed = False
        for e in data:
            if e["id"] in en:
                b = box(e["id"], e["jp"])
                text = en[e["id"]] if b.get("sliced") else "{br}".join(wrap(en[e["id"]], b))
                e["en"] = text + END.search(e["jp"]).group(0) if END.search(e["jp"]) else text
                changed = True
                n += 1
        if changed:
            f.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"merged {n} entries")


def pairs(names):
    """work/tl/bNNN.pairs.txt for the reviewer: `>> id | speaker | JP` then the English, in script order."""
    for name in names:
        src = read_tsv(TL / f"{name}.tsv", 5)
        got = dict(r for r in read_tsv(TL / f"{name}.out.tsv", 2) if r[0] is not None)
        out = [f">> {eid} | {sp} | {jp}\n   {got.get(eid, '(missing)')}" for eid, sp, _, _, jp in src]
        (TL / f"{name}.pairs.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
        print(f"work/tl/{name}.pairs.txt", len(out), "entries")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["dump", "split", "check", "merge", "fit", "pairs"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--box", default="dialogue", help="variant name for fit (see windows.json)")
    a = ap.parse_args()
    if a.cmd == "dump":
        dump(a.args[0])
    elif a.cmd == "split":
        split()
    elif a.cmd == "check":
        sys.exit(cmd_check(a.args))
    elif a.cmd == "merge":
        merge(a.args)
    elif a.cmd == "pairs":
        pairs(a.args)
    else:
        variants, _ = budgets()
        b = dict(variants[a.box], variant=a.box)
        b.setdefault("lines", 1)
        for text in a.args:
            for ln in (text.split(" | ") if b.get("sliced") else wrap(text, b)):
                print(f"{width(ln):4d}px  {ln}")
            errs = fit_errors(text, b)
            print("\n".join(errs) if errs else f"fits {limit_of(b)}")


if __name__ == "__main__":
    main()
