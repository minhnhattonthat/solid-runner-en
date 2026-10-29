"""Dump the Japanese script to script/ (JSON, one file per source and bank).

    python -X utf8 tools/extract.py            # write missing files, refresh `jp` in existing ones, keep `en`
    python -X utf8 tools/extract.py --check    # exit 1 if script/ is out of date with the ROM and table

Sources:
  events/BB.json   inline texts of the event-script VM (tools/events.py), id `ev_BBAAAA` = text start address
  lists/NAME.json  string lists read by native code (tools/strings.py), id `NAME_AAAAAA`

Entry fields: id, addr (CPU address of the text), op (event: address of the text opcode), len (original bytes incl.
the terminator), jp (decoded with tbl/jp.tbl), en (the translation; "" = untranslated), notes.
A dump never drops an `en`: an id that disappears while it has English stops the dump (rerun with --force to drop).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import events  # noqa: E402
from tbl import Table  # noqa: E402

SCRIPT = ROOT / "script"


def event_entries(rom, table):
    """{relative file: [entry]} for the event texts."""
    d = events.disassemble(rom)
    files = {}
    for s, (op, n) in sorted(d.texts.items()):
        jp, used = table.decode(rom, events.off(s), n)
        assert used == n
        files.setdefault(f"events/{s >> 16:02X}.json", []).append(
            {"id": f"ev_{s:06X}", "addr": f"{s >> 16:02X}:{s & 0xFFFF:04X}", "op": f"{op:06X}", "len": n, "jp": jp,
             "en": "", "notes": ""})
    return files


def all_entries(rom, table):
    files = event_entries(rom, table)
    try:
        import strings
    except ImportError:
        return files
    files.update(strings.list_entries(rom, table))
    return files


def merge(path, fresh, force):
    """Fresh entries with en/notes carried over from the file on disk."""
    if not path.exists():
        return fresh, []
    old = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))}
    ids = {e["id"] for e in fresh}
    lost = [i for i, e in old.items() if i not in ids and (e.get("en") or e.get("notes"))]
    if lost and not force:
        raise SystemExit(f"{path}: {len(lost)} translated ids would be dropped (e.g. {lost[:3]}); use --force")
    for e in fresh:
        o = old.get(e["id"])
        if o:
            e["en"], e["notes"] = o.get("en", ""), o.get("notes", "")
    return fresh, lost


def dumps(entries):
    return json.dumps(entries, ensure_ascii=False, indent=1) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--rom", default=str(events.ROM))
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    table = Table.load(ROOT / "tbl" / "jp.tbl")
    files = all_entries(rom, table)
    stale = []
    for rel, fresh in sorted(files.items()):
        path = SCRIPT / rel
        entries, _ = merge(path, fresh, a.force)
        text = dumps(entries)
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            stale.append(rel)
            if not a.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
    n = sum(len(v) for v in files.values())
    print(f"{n} strings in {len(files)} files; {'stale' if a.check else 'written'}: {len(stale)}")
    if a.check and stale:
        print("\n".join(stale[:20]))
        sys.exit(1)


if __name__ == "__main__":
    main()
