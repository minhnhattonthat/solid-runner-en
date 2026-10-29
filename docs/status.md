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
- **Marker build + tour (93 scenes, no crash):** `python -X utf8 tools/build.py --marker --out build/marker.sfc`,
  then `python -X utf8 tools/debug/run_scenes.py --rom build/marker.sfc --out work/qa/marker --script
  tools/lua/fields.lua` (~45 min, run in the background), then `python -X utf8 tools/fields.py` -> `windows.json`.
  `fields.lua` logs every string start (instant draw 84:A87B, typewriter 84:A7E1); a logged ROM pointer that no
  entry covers is missed text (the last full tour + reruns: none left). Findings and fixes of 2026-10-30 are in
  `docs/re/text.md` "Phase 5 corrections": new lists `results`, `labels`, `default_names`; missions start 92:96A3;
  names table 87:EEC4 (adds the player's `name＝family`); database page-pointer prefixes are data (cut out); the
  missions report table 92:9719 and the Turbo File table 92:AE6E had been inside entries (split; orphan 92:AE42
  dropped; `test_no_pointer_table_inside_entries`). 4077 entries. `run_scenes.py --var` passes probe settings.
- **Width gate (`windows.json`, from `fields.VARIANTS`):** every entry has a budget through a box variant measured
  with `tools/ruler.py` on the tour shots (text start x to the window frame's inner edge; see each variant's `how`):
  dialogue 240x3 (last line 232), battle messages (bank $90) 240x2, database/people pages 212x3, requests 220x5,
  item names 94 / descriptions 222, part names 88, place names 240 centred, save slot 212 centred, names 58/66
  (5 glyphs), menu titles 74, shop labels, Turbo File, intro crawl, and 14 **sliced** menus (window rows of N
  cells: field menu 6, setup labels 4, info menu 5, info>data 2, ...; phase 7 needs a tab-to-cell control code and a
  wider info>data submenu). Scenes added for it: info_status/requests/data, data_info_list/page,
  data_people_list/page, requests_view, item_use, setup_slot (`ready_flags` = SRAM unlock bits written when the
  field is ready).
- **Left in phase 5:**
  1. 225 entries still use variants tagged `guess` (screens not reached): parts descriptions, config submenus
     (menu_config + A), Results labels/mission names (code-positioned: phase 7 reworks the line), runners list,
     info terminal (info list 87:8558 + runner_status: an object in some town room; find it with the object tables,
     `docs/re/events.md`), save-slot places (needs a save: save from the save menu in a scene first), equipment texts
     (93:B33D...), third name ($1ACF). Measure each with a scene + `tools/ruler.py` and change its `how`.
  2. Kanji table (925 codes, see phase 4 notes below): needed before phase 6.
  3. Second renderer 84:B017 (screen unknown, `docs/re/text.md`): a tour hook on 84:B017 over all scenes finds it.
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
