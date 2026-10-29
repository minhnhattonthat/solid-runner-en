# VWF and the text bitmap (phase 5)

Source: `asm/vwf.asm` (asar, run by `tools/build.py`). Font: `fonts/vwf.txt` -> `tools/font.py`. Table: `tbl/en.tbl`.

## The engine's bitmap (verified: disassembly of 84:A993-AA17, ADBF, AED6, A7E1; stress shots)

- Glyph draw at 84:A993 (code - 1 -> glyph, $3C = kanji page). Original: 12 px cells, column $18BA 0-9 in a
  **strip** of 15 tiles (2 tile rows, $200 bytes) at $7E:2000 + $18BB*256; column offsets table 84:B00D; glyph rows
  0-10 go to bitmap rows 3-13 of the strip. After column 9 the original moves to the next strip ($18BB += 2, $18BA = 0)
  unless the next byte is `00`; `00` sets $18BB = ($18BB & $FC) + 4 (next line). A dialogue line = 2 strips side by
  side (240 px, x 8-247 on screen).
- Two colour modes: $18B9 = 0 overwrite (plane0 = ink, plane1 = ink | shadow), else merge (formula in vwf.asm). $18B9
  is also the pad character for field padding (84:A897 pads with it to $18B7 glyphs).
- Count-only mode: $18B0 bit $10 (measure pass for centring); line glyph counts stored by 84:AA26 into $18C4,y;
  84:A8FA centres each line at (20 - count)/2 columns.
- Typewriter (84:A7E1): pushes $18BB, draws one glyph (JSR 84:A91E), uploads the strip it pushed (VRAM $6000 +
  $18BB*128 words, $200 bytes) through JSL 80:9DB2 with a 16-bit A size: the draw routine must return with B = 0.
- Pressing A mid-text redraws the whole text at once from 84:A71C (STZ $18BA, $18BB unchanged) then uploads
  `(($18BB - $18BC) & $FC) + 4` lines: a wrong $18BB at the end of that redraw uploads tens of KB over the BG tiles.
- List menus rely on the original's wrap at column 10 at the **end** of a string to step down a row (item menu:
  name at column 0, count at column 8, next row = the count's wrap), not on setting $18BB per row.

## The VWF (verified by the stress builds and the marker tour)

- Pixel cursor; the glyph is shifted into 3 bytes per row and written with masks, so neighbours keep their pixels.
- Advance = ink width + 2 (shadow + gap) for English glyphs; kana, kanji and symbols keep 12.
- After each glyph $18BA/$18BB are left in the original form (strip and column where the next glyph starts), so
  the typewriter uploads the right strip. A glyph that straddles two strips shows its right part with the next glyph
  (only a straddling *last* glyph of a text could stay half-drawn: the lint keeps lines inside the box anyway).
- Cursor restarts (column*12 in the caller's strip) when $18B8 = 0 (string/line start) or $18BA/$18BB differ from
  what the VWF left.
- $18B8 stays a glyph count (padding); centring gets the width in 12 px columns through a patch at 84:AA2A.
- At the end of a string (next byte FD-FF) the original's column-10 wrap is replayed from a mirrored glyph column.
- WRAM $1D80-$1DA3 (unused in the opening, menus, shop and a battle: RAM dumps every 200 frames, and a write watch
  over the opening): **guess** for other screens until the full tours pass.

## Not covered

- Second renderer 84:B017 / 84:B055: writes tilemap entries for an 8x16 VRAM tile font (code -> tile
  `((c-1) & $0F) | ((c-1) & $FFF0) * 2 + $180`), fixed pitch; one caller 82:9024. Screen not identified yet.
- Strings the code slices into fixed-length fields (no terminator between them): menu_82C4A9 (title + use/discard),
  setup slot labels, equipment labels (93:B248...). `windows.json` marks them `sliced`.
