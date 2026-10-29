"""font.py: fonts/vwf.txt -> English glyphs (12x11 font format) and the VWF advance table (asm/vwf.asm).

Each glyph is drawn at the code tbl/en.tbl gives its character, replacing the Latin/symbol glyph there. Codes not
in the font keep their glyph and the 12 px pitch.

    python -X utf8 tools/font.py     selftest + width summary
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FONT_TXT = ROOT / "fonts" / "vwf.txt"
EN_TBL = ROOT / "tbl" / "en.tbl"
FONT_OFF = 0x170000  # $AE:8000, 22 bytes per glyph, glyph = code - 1
GLYPH = 22
ADV_EXTRA = 2        # 1 shadow column (the engine draws ink >> 1) + 1 gap
JP_ADV = 12          # original pitch, kept for kana, kanji and symbols
MAX_INK = 11         # 12 px cell minus the shadow column


def load(path=FONT_TXT):
    """{char: rows} (rows from glyph row 1 down, '#' = ink)."""
    glyphs, cur = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if cur is None and line.startswith("#"):  # comments only above the first glyph: rows start with '#'
            continue
        if line.startswith("== "):
            cur = glyphs.setdefault(" " if line[3:] == "space" else line[3:], [])
        elif line and cur is not None:
            cur.append(line)
    return glyphs


def width(rows):
    return max(len(r) for r in rows)


def encode_glyph(rows):
    """22 bytes: 11 little-endian words, bit 15 = leftmost pixel; row 0 blank."""
    out = bytearray(GLYPH)
    for r, row in enumerate(rows, 1):
        word = sum(1 << (15 - x) for x, c in enumerate(row) if c == "#")
        out[2 * r:2 * r + 2] = word.to_bytes(2, "little")
    return bytes(out)


# D11: default names longer than their name buffer (Erskine in 5 bytes, Grandil in 6) keep every letter by packing
# letter pairs into one code; tools/insert.py packs only those names. Codes = unused hiragana (02 is the space).
DIGRAPHS = {"Er": 0x03, "sk": 0x04, "Gr": 0x05}


def pair(a, b):
    """One glyph of two letters, spaced as the VWF spaces them (shadow + gap = 2 blank columns)."""
    wa = width(a)
    return [(a[r] if r < len(a) else "").ljust(wa + 2, ".") + (b[r] if r < len(b) else "") for r in range(max(len(a), len(b)))]


def pack(text, n):
    """Text as units (letters, DIGRAPHS pairs), pairs taken in order until it is at most n units."""
    units = list(text)
    for p in DIGRAPHS:
        for i in range(len(units) - 1):
            if len(units) > n and units[i] + units[i + 1] == p:
                units[i:i + 2] = [p]
                break
    return units


def build(table=None, glyphs=None):
    """(list of (code, 22 glyph bytes), 256-byte advance table)."""
    table = table or Table.load(EN_TBL)
    glyphs = dict(glyphs or load())
    adv = bytearray([JP_ADV] * 256)
    out = []
    for p, code in DIGRAPHS.items():
        glyphs[p] = pair(glyphs[p[0]], glyphs[p[1]])
    for ch, rows in glyphs.items():
        code = [DIGRAPHS[ch]] if ch in DIGRAPHS else table.enc[ch]
        assert len(code) == 1, (ch, code)
        assert len(rows) <= 10 and width(rows) <= MAX_INK, f"glyph {ch!r} is over 11x10"
        out.append((code[0], encode_glyph(rows)))
        adv[code[0]] = width(rows) + ADV_EXTRA
    return out, bytes(adv)


def selftest():
    t = Table.load(EN_TBL)
    g = load()
    printable = [v for v in t.enc if len(v) == 1 and v not in "○▲▼≡"]
    missing = [c for c in printable if c not in g]
    assert not missing, f"no glyph for {missing}"
    _, adv = build(t, g)
    assert adv[t.enc[" "][0]] == 4 and adv[0x01] == JP_ADV  # 01: the JP's 12 px blank, kept for indents
    assert encode_glyph(["#"])[2:4] == b"\x00\x80"
    assert pack("Erskine", 5) == ["Er", "sk", "i", "n", "e"] and pack("Grandil", 6)[0] == "Gr" and pack("Shu", 5) == list("Shu")
    assert adv[DIGRAPHS["Er"]] == adv[t.enc["E"][0]] + adv[t.enc["r"][0]]  # same width as the two letters
    assert not set(DIGRAPHS.values()) & {c[0] for c in t.enc.values() if len(c) == 1}


if __name__ == "__main__":
    selftest()
    _, adv = build()
    t = Table.load(EN_TBL)
    print("selftest ok;", " ".join(f"{ch}{adv[t.enc[ch][0]]}" for ch in sorted(load())))
