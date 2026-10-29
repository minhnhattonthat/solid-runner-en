# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4 (extract) done; next is phase 5 (engine spike + marker build).
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
