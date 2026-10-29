# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise. Prior work: none found (no fan patch or
community docs for Solid Runner as of 2026-10-29).

| File | Covers | State |
|---|---|---|
| [text.md](text.md) | encoding, control codes, font, text engine, where each text kind lives | encoding/font/engine verified; kanji table and some list locations pending |
| [events.md](events.md) | event-script VM, text opcodes, map loading (area/room), story state in SRAM, battles, map headers, insertion plan | dispatcher, text ops, map loading, battle op verified; ~40 opcode lengths to read; story flags unmapped |
| [rom-map.md](rom-map.md) | header, bank map, LZ/RLE compression, free space | LZ verified; bank map partly guessed |
| [vwf.md](vwf.md) | text bitmap layout (strips), typewriter upload, VWF hook, sliced strings, second renderer | verified by stress builds and marker tour |
| [graphics.md](graphics.md) | graphics-text survey | sweep done for LZ blocks; mid/late-game screens wait for the debug tool |

Tools: `tools/font_sheet.py` (font with codes), `tools/vm_oplen.py` (VM opcode lengths), `tools/lz.py` (LZ codec),
`tools/gfx_sweep.py` (decompress + render every LZ block), `tools/freespace.py`, `tools/lua/textlog.lua` (log every
string the text engine is given).
