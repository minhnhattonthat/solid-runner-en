# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) in progress.
- **Done (phase 5 so far):** VWF `asm/vwf.asm` (asar 1.91 in `tools/asar/`, URL in `tools/build.py`): hooks the glyph
  draw at 84:A993, pixel cursor into the same $7E:2000 line bitmap; keeps $18BA/$18BB in the original strip form
  (typewriter uploads the strip $18BB names, 84:A7E1), $18B8 = glyph count (pad loop 84:A897), centring line widths in
  12 px columns via a patch at 84:AA2A, the original's 10-column wrap kept at the end of a string (list rows: item
  name col 0 + count col 8 step down a row by it), B=0 on return (84:A856 DMA size is 16-bit A). Font
  `fonts/vwf.txt` (drawn for the project) -> `tools/font.py`, `tbl/en.tbl` (letters/digits/punctuation reuse the
  Latin/symbol codes; kana/kanji keep their glyphs, 12 px). `tools/marker.py` + `build.py --marker` (tag = 3 base-36
  chars, `python tools/marker.py TAG` looks it up), `build.py --qa ID=TEXT` for width tests. Torture line and the
  dialogue box measured: 3 lines x 240 px (x 8-247; past 240 px text wraps mid-glyph into the next line), last line
  232 px when the page prompt shows (stress shots work/qa/stress, work/qa/stress2). Tests: `tests/test_engine.py`.
  Debug probes: `tools/lua/cpulog.lua` (registers/RAM/stack at PCs), `tools/lua/pcwrites.lua`.
- **Found by the marker build:** some menu strings are sliced into fixed-length fields by code, not terminated:
  menu_82C4A9 (`アイテム` title + `使用`/`廃棄` commands), the setup labels (`左肩：`... tag 2ss), equipment labels
  (93:B248...). English there needs the drawing code changed (phase 7). Second renderer 84:B017/B055 (tilemap
  writer, 8x16 VRAM tile font, fixed pitch; one caller 82:9024): which screen uses it is not known yet.
- **Marker tour (73/73 scenes, no crash, no data broken by markers):** `python -X utf8 tools/debug/run_scenes.py
  --rom build/marker.sfc --out work/qa/marker --script tools/lua/fields.lua`, then `python -X utf8 tools/fields.py`
  writes `windows.json` (dialogue variant + per-entry px budgets: `next-field` from the logged column of the
  next string on the row, `line-end`/`strip-end` geometric; see the docstring). 32 entries seen so far.
- **Session 2026-10-30 (phase 5):** new lists `results` (92:95FD), `labels` (setup slot labels 82:AB25, info>data
  submenu 82:AEF4, empty-slot dashes 82:C13F/83:9A66 - EE is `*` in en.tbl so English must use `-`, はずす 82:C1DB,
  shop item labels 93:8AFB/8B02), `default_names` (copies at 83:8F1D/21 and 93:CB2C/32/38; 93:CB20 is a {RAM dest,
  src} table into the name buffers $1AC3/$1AC9/$1ACF, 5 glyphs + FF each); missions list starts at 92:96A3 (table
  92:9681; `母と娘` was missed). Database descriptions start with **big-endian page-pointer lists** + 00 (49 of
  them; `strings.page_ptrs`): data, now cut out of the entries (the marker build had overwritten them). Missed
  strings are found precisely by `fields.lua` logs: any logged ROM pointer no entry covers (scratch check: grep the
  logs, `fields.lookup`). `fields.lua` now also hooks the typewriter (84:A7E1, string starts) - before, no
  dialogue was logged. New scenes: info_status/requests/data, data_info_list/page, data_people_list/page (unlock
  bits set when the field is ready: `ready_flags`; info $70:0154+x bit 6, people $70:018F+x bit 7, 82:D08D/D0A5),
  requests_view ($70:013B = request index, $70:0141+i bit 6; 82:ADC7), item_use, setup_slot. `run_scenes.py --var`
  passes probe settings. `tools/ruler.py` overlays a pixel ruler on shots (budget measuring). `fields.py` now has
  `VARIANTS` (measured box widths per list/entry, see its comments) merged with logged next-field budgets into
  `windows.json` (3461/4078 entries have a budget).
- **Left in phase 5 (width gate):**
  1. Measure the remaining variants with `tools/ruler.py` on the marker tour shots (`work/qa/marker`, rerun
     `run_scenes.py --rom build/marker.sfc --out work/qa/marker --script tools/lua/fields.lua` after
     `build.py --marker --out build/marker.sfc`) and add them to `fields.VARIANTS`: battle message box
     (battle_fight; are battle event texts narrower than 240?), database list titles / info page title (2 lines) /
     page body (3 lines x ~240) / people pages (data_* scenes), setup parts list + はずす (setup_slot), info and data
     submenus (sliced, 2 cells per row), place names (area HUD, `places` are space-padded), intro crawl, Results
     fields (code-positioned: needs a phase-7 rework into one line), runner_status/runners/names/missions (screens
     not found yet: the info terminal (info list 87:8558) is an object in some town room).
  2. Unassigned so far: database (264), parts descriptions, places/places2, runners, names, missions, info, turbo,
     equip, menu, runner_status, intro, results, labels. `python -X utf8 tools/fields.py` prints the count.
  3. Identify the screen of the second renderer (84:B017).
  4. Before phase 6: kanji table (925 codes, see phase 4 notes below).
- **Done (phase 4):** `tools/events.py` VM disassembler (`docs/re/events.md` "Disassembler": every opcode, room
  scripts, NPC/tile record tables, native roots, orphan roots incl. text-op roots synced to op boundaries; 3172
  inline texts, 0 bad ops, 0 overlaps). "Second script format" in $87/$91 is the same VM. `tools/strings.py`: 20
  native lists (menus, runner/character names, items, parts, places, info menus + database, intro crawl, missions,
  Turbo File, equipment, help, name-entry charset, status labels) plus `loose` VM texts no root reaches, by address
  (`docs/re/text.md` "Where the text is" lists the pointer tables). `tools/extract.py` dumps `script/events/BB.json`
  and `script/lists/NAME.json` (4057 strings; id `ev_<addr>` / `<list>_<addr>`; never drops an `en`, `--check`).
  `tools/coverage.py`: uncovered terminated runs whose character-bigram score (model of the event script) passes
  `GATE`; 0 left, data runs listed in `script/not_text.txt`. Tests: `test_events.py`, `test_extract.py` (roundtrip
  of every entry, dump current), `test_coverage.py` (no uncovered prose, no overlaps, gate sanity).
- **Next (phase 5):** marker build per skill; it will show which list starts are wrong (some ranges are guesses at
  the edges, see `text.md`) and which on-screen text is still Japanese (short menus below the coverage gate:
  `coverage.py` with `GATE=-5.6` lists ~70 more runs, nearly all data). Kanji: 925 distinct codes used, `jp` shows
  them as `[F9]x`; template-match the font cells against a system font, then reviewer subagents
  (`references/pipeline.md` §Recon 4) - needed before phase 6 (translation). `loose` texts still need their roots
  found (watch $7E:B297 writes) before phase 7 relocates scripts.
- **Done (phase 3):** `tools/build.py` (dump check, logged `put()` writes, checksum, build/writes.txt; no edits yet),
  `lz.compress` + `lz.blocks`, 3 MiB checksum fix in `tools/bps.py`. `tests/test_identity.py`: build byte-identical
  and romdiff-clean, checksum reproduces the header, all 1361 LZ blocks repack (same data, never bigger). Smoke ok.
- **Done (phase 1):** encoding (`tbl/jp.tbl`, kanji not read yet), 12x11 font $AE:8000, text engine 84:A91E, event
  VM (`docs/re/events.md`), text locations (`docs/re/text.md`), LZ codec, free space (`docs/re/rom-map.md`),
  graphics survey (`docs/re/graphics.md`). Tests in `tests/test_recon.py`.
- **Done (phase 2):** `tools/debug/warp.lua` + `scenes.lua` + `run_scenes.py` (commands in AGENTS.md). Cold boot,
  mash Start through NEW GAME, rewrite area/room ($7E:1AA8/1AA9) at the new game's first map load (80:C546); scenes
  can also inject event-VM bytes over the opening thread (scripted battles via op 7D), press keys, wait on RAM
  flags, mash, pin HP (`GOD`). `run_scenes.py --states` reached all scenes from cold boots with a shot each
  (`work/qa/scenes/`, sheets `sheet*.png`) and saved `work/states/<scene>.mss`. Covered: title, name entry,
  save/load, Turbo File menu, psycho-dive scenes, shop (greeting, buy/sell, item and weapon lists, parts view), 12
  scripted battles + one fought with HP pinned, Game Over, both THE END screens, Results, staff roll/credits, cutscenes $17/03-05, opening,
  field menu + item/setup/info/config, every story area's room 0 (27). RE notes: `events.md` "Map loading, story
  state, battles". Test: `tests/test_debug.py` (every scene names a real room).
- **Gaps in the debug tool (fill when a phase needs them):** story flags per chapter are not mapped (state is bit
  flags in SRAM $70:00xx, tested by room-script op 1C), so rooms show their new-game state; to see a later event's
  text, phase 5/8 should force it (screen tour: hook the text engine or inject the event's script) rather than set
  flags. Rooms other than 0 are reachable with `--raw AA:RR` (room counts: `tests/test_debug.py:room_count`). A won
  battle is not in the list (the scripted battles tried show enemy HP 9999; enemy HP is not a plain 16-bit 9999 in
  WRAM). The opening takes ~3460 frames of mashed A; menu scenes wait on `$70:0013=1`/`$7E:1745=0` (pressing A after
  that talks to Tao again). Spawning a script thread (op 07-09)
  over the opening thread gave a black screen; ending that thread early leaves the player without control.
- **Phase 4 carry-overs left:** find users of the 8x8 kana font (AC_01/AC_05).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the Mesen GUI's keyboard input was not hand-tested (headless session);
  emu.py wrote default key mappings to `tools/mesen/settings.json`.
