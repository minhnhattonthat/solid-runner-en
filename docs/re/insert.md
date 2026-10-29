# Insertion (phase 7)

`tools/insert.py` (run by `tools/build.py`) puts every English entry in free space and turns its original slot into
a jump. Verified: `tests/test_insert.py` (write log, allowed ranges, every slot followed to its English) and the
English build in game (opening dialogue, field/config/item/shop menus, Turbo File; `work/qa/en1`-`en3`, 2026-10-30).

## Control codes (asm/vwf.asm)

The engine's `F8 cc` table (84:AA39, `{handler, argc}` per even cc) ends at cc 1E with code after it, so the build
copies it to **84:E000** (`ctl_table`, built with asar `read2()` from the original) and points both readers at it:
the draw dispatch 84:A967 `JSR (ctl_table,x)` and the VM text scanner 81:C942 `LDA ctl_table+2,x` (it skips argc
bytes after `F8 cc`). New codes:

| Code | tbl | Does |
|---|---|---|
| `F8 20 lo hi bank` | `{jump:3}` | `$50-$52` = the address, Y = 0: the engine reads on there |
| `F8 22 lo hi` | `{jump16:2}` | same into bank $BA (slots of 4-5 bytes) |
| `F8 24 n` | `{tab:n}` | cursor to the original's column n of this line (12 px cells; n >= 10 runs on into the next strips as the original's wrap did) |

The typewriter (84:A7E1) stores `$18B2 = $50 + Y + 1` and keeps `$52` as the bank after each glyph, so after a jump it
types from the English; the A-press redraw (84:A873) and centring pass start from `$18B2` and follow the jump again.
English strings stay inside one bank (the typewriter never carries into the bank byte). Y is 8-bit in the engine:
every English string is < 250 bytes.

## Slots

- `n >= 6`: `F8 20 p24`, `01` fill, the original end byte. The VM scanner (81:C930) still finds the end at the same
  place, and a raw walker over a list still lands on the next slot. Allocated addresses never have FD-FF in their
  low or high byte (a raw walker would stop there).
- `n` 4-5 (no pointer table): `F8 22 p16` (+ end byte if 5); the English is in bank $BA.
- Lists with a 16-bit pointer table (`names` 87:EEC4, `runners` 82:A17F) and a slot under 6 bytes: the table word is
  repointed and the whole run goes in the table's bank tail.
- `charset` (name-entry grid, indexed by cell) and `default_names` (copied into the name buffers) are written in place.
- List entries that sit back to back are placed back to back (a reader may draw one and go on past its end).

Free space (`insert.Space`): whole FF banks $BA $BB $CD $D3 $D4, then FF tails of $86 $D7 $AF $91 $94 $B9 $C7 $CB $D2
$B3 (16 bytes after the last data byte), $82/$87 tails only for table runs. 349 KB, ~120 KB left after the script.

## Layout (insert.english)

- `01` stays the JP's 12 px blank (`{blank}` in en.tbl); the English space is a 4 px glyph at code 02.
- Leading JP blanks the translation dropped come back: 1-2 cells (choice cursor) as they are, deeper indents centre
  the line on the JP line's centre; never past the box.
- `' | '` in an entry: sliced menus (`cells.json`, item columns) or a JP line laid out in columns (elevators, Yes/No):
  each piece starts at the JP column's cell.
- Sliced menus: the window shows the text bitmap in rows of N cells of one linear string (verified on menu_setup:
  "Left Shoulder:" clipped at 48 px, the next row's tab overwrote the rest). An item can't pass its row without a
  wider row in the window's tilemap builder: `script/engine_todo.txt`.

## Not covered yet

Typing speed: English pages have ~2x the glyphs and A doesn't skip typing (1 glyph / 2 frames in the opening), so
scenes take ~2x as long; the debug scenes' field budget is 15000 frames.
