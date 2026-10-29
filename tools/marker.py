"""marker.py: marker text for every extracted string, in place (same byte length, same controls and line breaks).

Each run of glyphs becomes English filler of the same byte count; the first run starts with the string's short tag
(3 base-36 characters, in id order), so a shot shows which entry each box comes from. Text stays in place because
event texts are inline in VM code (phase 7 relocates them), so the marker can't be longer than the Japanese.

    python -X utf8 tools/marker.py TAG..     tag -> id, address, Japanese
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FILLER = "The quick brown fox jumps over the lazy dog. "
DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def entries():
    """Every script entry (events then lists), sorted by id."""
    out = []
    for f in sorted((ROOT / "script").glob("*/*.json")):
        out += json.loads(f.read_text(encoding="utf-8"))
    return sorted(out, key=lambda e: e["id"])


def tag(i):
    return DIGITS[i // 1296 % 36] + DIGITS[i // 36 % 36] + DIGITS[i % 36]


def offset(addr):
    bank, lo = addr.split(":")
    return ((int(bank, 16) & 0x7F) << 15) | (int(lo, 16) & 0x7FFF)


def runs(data):
    """Split encoded Japanese into ('text', nbytes) and ('raw', bytes) pieces (controls, breaks, ends)."""
    out, i = [], 0
    while i < len(data):
        b = data[i]
        if b == 0x00 or b >= 0xFD:
            n = 1
        elif b == 0xF8:
            n = 2 + {0x02: 2, 0x04: 4, 0x06: 3, 0x08: 3, 0x0A: 1, 0x0C: 1, 0x10: 1, 0x16: 1, 0x1A: 1, 0x1C: 1}.get(
                data[i + 1], 0)
        else:
            n = 2 if b >= 0xF9 else 1
            if out and out[-1][0] == "text":
                out[-1] = ("text", out[-1][1] + n)
            else:
                out.append(("text", n))
            i += n
            continue
        out.append(("raw", data[i:i + n]))
        i += n
    return out


def marker(data, t, en):
    """Marker bytes for the encoded Japanese `data`, starting with tag `t`; same length."""
    out, fill = bytearray(), t + " " + FILLER * 20
    for kind, v in runs(data):
        if kind == "raw":
            out += v
        else:
            out += en.encode(fill[:v])
            fill = fill[v:]
    assert len(out) == len(data)
    return bytes(out)


def build_markers(rom):
    """[(file offset, marker bytes, id)] for every entry; checks each entry's Japanese against the ROM."""
    jp, en = Table.load(ROOT / "tbl" / "jp.tbl"), Table.load(ROOT / "tbl" / "en.tbl")
    out = []
    for i, e in enumerate(entries()):
        off = offset(e["addr"])
        data = rom[off:off + e["len"]]
        assert jp.encode(e["jp"]) == data, e["id"]
        out.append((off, marker(data, tag(i), en), e["id"]))
    return out


if __name__ == "__main__":
    es = entries()
    for t in sys.argv[1:]:
        i = int(t, 36)
        print(t, es[i]["id"], es[i]["addr"], es[i]["jp"])
