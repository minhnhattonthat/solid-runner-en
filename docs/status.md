# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) **done** 2026-10-30. **Next: phase 6 (translate).**
- **Next (phase 6):** copy `translator-brief.md` / `reviewer-brief.md` (and the style reference) from the skill's
  `assets/` into `docs/` (the `.claude/agents/` translator and reviewer types read them; they don't exist yet), fill
  `glossary.md` (characters, places, terms; register/SFX rows are `<set in phase 6>`), cut `work/tl/<batch>.tsv`
  batches with each entry's budget from `windows.json` (`fields` -> `variant` -> px/lines/sliced/centred), then
  dispatch translator agents per `references/translation.md`. Notes for translators: `{c0C:01}` = player name,
  `{c0C:02}` = runner name; `FAB1` ✕ is a censored word (`✕✕ババア`); ev_97BA44 `6功` is an original typo for `成功`;
  sliced entries (14) are menu cells, each piece within `px`.
- **Done (phase 5):**
  - VWF `asm/vwf.asm` (asar 1.91 in `tools/asar/`): hooks glyph draw 84:A993, pixel cursor in the $7E:2000 line
    bitmap, centring via 84:AA2A, 10-column wrap kept at string end (`docs/re/vwf.md`). Font `fonts/vwf.txt` ->
    `tools/font.py`, `tbl/en.tbl` (letters/digits/punctuation reuse the Latin/symbol codes). Tests `test_engine.py`.
  - Marker build: `python -X utf8 tools/build.py --marker --out build/marker.sfc` (tag = 3 base-36 chars,
    `python tools/marker.py TAG`); tour `run_scenes.py --rom build/marker.sfc --out work/qa/marker --script
    tools/lua/fields.lua` (~45 min) then `tools/fields.py` -> `windows.json`. Last tour + reruns: no missed text.
    Both builds smoke-boot (2026-10-30).
  - **Width gate:** all 4080 entries have a measured budget (`fields.VARIANTS`, 0 `guess`). This session: Riff's
    tune-up (`tune_menu` 54 sliced, `tune_armor` 54, `tune_desc` 240x2, `tune_labels` 40 sliced) and the request
    accept/cancel row (`info_choice` 78 sliced; phase 7: cancel must start at x 96).
  - **Kanji table:** all 1010 kanji cells `F901-FCF2` in `tbl/jp.tbl` (glyphs to 0x4F1, not 0x4C1 as once noted),
    read by eye off zoomed sheets, unsure cells checked in context, 6 reviewer look-alike scans of the whole script
    (24 readings fixed). `tools/kanji.py` (ctx/dump/table), `test_kanji_table`. Details `docs/re/text.md`.
  - Second renderer 84:B017: 0 hits in the full 92-scene tour (`work/qa/b017`, cpulog): its only caller 82:9024 is
    pointer-reached; treat as unused unless phase 8 `jp_left.py` or a shot shows otherwise.
  - Debug: scenes `tune_riff` (arena garage, area 15 room 00, $70:003D bit 0) and `info_choice` (request terminal
    with $70:0141+ bit 7 = requests offered). `tools/lua/pin.lua`: SET/CLR SRAM bits every frame, POKE once; e.g.
    point an NPC's resume script (thread x: $7E:B4C2+x lo / B4E7+x hi / B50C+x bank, op 49/4A at 81:D33F) at another
    VM script. Riff's tune-up: from `work/play/riff3/0001.mss`, POKE x=13 to 93:A5AE (`work/play/riff6`). The
    add-armor yes/no (`増やす/やめる`) needs a level-up and was not seen.
- **Phase 7 carry-overs:** tab-to-cell control code for the 14 sliced menus and a wider info>data submenu
  (`data_submenu` 22 px); `loose` VM texts need their roots found (watch $7E:B297 writes) before scripts are
  relocated; find users of the 8x8 kana font (AC_01/AC_05; the save slot's name/TIME/LV line is one).
- **Done (phases 1-4):** recon (`docs/re/`), debug warp tool (`tools/debug/`, `run_scenes.py`; 93 scenes + raw
  area:room), identity build (`tests/test_identity.py`), extraction (`tools/events.py`, `strings.py`, `extract.py`,
  `coverage.py`; 4080 entries in `script/`, roundtrip + coverage tests).
- **Gaps in the debug tool:** story flags per chapter not mapped (rooms show new-game state; force events by
  injecting VM scripts or poking resume pointers); no won battle (enemy HP not a plain 16-bit 9999); opening takes
  ~3460 mashed frames; spawning a thread over the opening thread gives a black screen.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the Mesen GUI's keyboard input was not hand-tested (headless session);
  emu.py wrote default key mappings to `tools/mesen/settings.json`.
