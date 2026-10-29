# Graphics text survey

Most on-screen text (dialogue, menus, item lists, name entry, intro crawl) is drawn at run time from the 12x11 font
(`text.md`): that is text work, not graphics. This file lists text stored as tiles.

## How the survey was done (phase 1)

- **Tour:** boot, attract mode (`work/qa/orig_attract`), title, NEW GAME, name entry, first scene, field menu and its
  submenus (`work/qa/menu1`).
- **Static sweep:** `python -X utf8 tools/gfx_sweep.py work/sweep/lz4` (and `--fmt snes2 work/sweep/lz2`) decompresses
  every LZ block behind every bank-start pointer table (972 blocks) and renders contact sheets; four read-only
  reviewer subagents read all 84 + 160 sheets. Skipped, with reasons printed by the tool: banks without a pointer
  table ($80-$89, $8B, $90, $91, $9F, $A4, $A6, $A7, $AE, $C8, $C9, $D2, $D9, $DA, $DF and the empty banks) and
  blocks that are not LZ or decompress to < 512 bytes. Raw (uncompressed) banks are noise as tiles. Not yet swept:
  RLE (A7:85ED) and the other decompressors (88:860D, 83:8D67, 83:BD91); sprites built at run time.
- **Phase-2 warp tour** (`python -X utf8 tools/debug/run_scenes.py`, shots in `work/qa/scenes/`): battle intro,
  battle HUD, shop menus and lists, parts view, Game Over, both THE END screens, Results, staff roll, save/load,
  Turbo File menu, psycho-dive scenes, field menu + submenus, every area's room 0. The Japanese text seen there
  looks like the 12x11 font (text work; guess by eye, the marker build confirms it); the tile-drawn titles on those screens are already English (`WARNING`,
  `Game Over`, `THE END`, `Results`, staff roll). No chapter/area title cards were seen (areas load straight in).
  Rows below still stand; the marker build tour (phase 5) is the final check.

## Japanese as graphics

| # | Screen | Source | Layer | State |
|---|---|---|---|---|
| G1 | Title: katakana subtitle `ソリッドランナー` under the English logo | LZ block D8_02 [2C1B78] (logo art; same block as the big letters) | BG | seen on screen; block from sweep (medium confidence), confirm with corrupt-and-boot |
| G2 | 8x8 kana + Latin font (2bpp and 4bpp copies) | AC_01 [1601BE], AC_05 [160EDC] | ? | font, users unknown: find which screens draw with it (battle HUD? shop?). If text uses it, it is text work with its own table |
| G3 | Debug-looking menu font and labels: katakana place/BGM names (`タオ シュウ カフェ まち … ホストセンタ クラブ … アジト CTI びょういん パーク … ドーム サイコ`), `フラグ`, `KIND`, `SOUND`, `LEVEL`, `END` | B3_10 [19CC4D], B3_11 [19D76F] | ? | probably a leftover debug / sound-test menu: lead for phase 2. Translate only if reachable in normal play |
| G4 | Small sprite tags at the bottom of an item/icon sheet: `…Eは`, `あけて` | A3_05 [11D474] last tile row | OBJ | read off the sheet only; find the screen |

## English already (no work, listed so nobody re-checks them)

Title `SOLID RUNNER`, `PUSH START`, `NEW GAME`, `CONTINUE`, `(c)1997 ASCII CORPORATION` (D8_00); intro staff credits
(`Character Background & Monster Design HAJIME OKI`) and `Story ORCA`; `LV:` `HP:` `G` in the menu; `PARTS SHOP`
(9D_00); HUD digits `HP 0-9 G` (9D_0C); `HIT!`, `no damage!` (CB_2E); `WARNING`, `ENEMY IS APPROACHING`,
`COMBAT MODE`, `STAND BY`, `READY GO!!`, `DETECTED` (AC_0E-AC_11); `Winner` (AC_13); `Game Over` (AC_1D); `Result`
(D8_13); `COMPLETE`, `ACCESS`, keypad (9C_0E, 9C_10); `TURBOFILE` (D8_04); ASCII fonts (DC_0E, DB_02/03).
