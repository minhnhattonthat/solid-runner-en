# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (QA in the emulator) **in progress** (2026-10-30). Phase 7 done (lint clean, codes matched, writes
  only in allowed ranges).
- **Phase 8 so far:** tour = `run_scenes.py --rom build/qa_tour.sfc --out work/qa/tour --jobs 7 --script
  tools/lua/textlog.lua` (~25 min, every scene now gets a `--sheet`); JP baseline `work/qa/tour_jp` (same ids);
  `tools/textscan.py` reads the tour's textlog lines and lists drawn strings that still hold kana/kanji (run it with
  the ROM the tour used). Gate: `qa_gate.py init work/qa/manifest.tsv work/qa/tour`, `todo ... --size 30 --out-dir
  work/qa/chunks`, 4 `visual-qa` agents (brief `docs/visual-qa-brief.md`), verdicts in `work/qa/verdicts/`.
  First review (116 sheets): ~25 issues, fixed and seen in game unless noted: battle HUD names (8x8 renderer reads
  the runners table: every table-list entry is now repointed, jump slot kept too), VWF full line + `{br}` stepped
  two lines (asm `vwf_pos`: a strip edge stays column 10), shop Buy/Sell submenu (string starts at column 2 where the
  main menu's wrap left it: cells [2, 8], Items/Weapons), request Cancel at cell 10, intro crawl (`intro` variant
  196 px `clipped`), parts view Hit/Ammo (glossary), news headline 2 lines, 411 one-word last lines
  (`batches.py dewidow`, test_dewidow), title logo katakana removed (`tools/gfx.py`, G1), 5 code-loaded labels
  extracted (request Client/Reward, shop Amount/Cost: `scene shop_buy_count`), heads ev_93827B/ev_97BA44 (dead copies
  as far as known, started at the real text anyway; `insert.entries` decodes a moved head's whole JP).
  New scenes: `shop_buy_count`, `vm_*` (`vmtext(op)`: 0E window + jump to a text op; elevators/keypad seen OK; the
  `vm_9194..` ones show garbage on the JP too = wrong entry, not a bug).
- **Phase 8 next (in this order):**
  1. Results screen (scene `results`): the reward/total count-up redraws its number with narrow VWF digits at
     shifting x and leaves old digits ("250G 500G"; before: a stray "!"). JP digits are fixed 12 px cells, right
     aligned by pad blanks. Find the number writer ({c04} or native, 92:95xx) and draw digits there at 12 px (or
     clear the field first). `Reward:` now has the JP's 3 trailing blanks.
  2. Teal/green pixels above "Status" in the info submenu header and list row (menu_info, info_status, info_data,
     data_people_*; zoom work/qa/zoom/c2/id_z2.png): not in JP. Topics selection bar in info_terminal_4 (DATA
     LIBRARY tabs) keeps the JP 2-glyph width: widen it or shorten the label (Topics/People/Enemies).
  3. Re-tour everything on the final build (copy to build/qa_tour.sfc first), `textscan.py`, `qa_gate.py init`
     (changed sheets lose their verdicts), `todo`, re-review, recheck files `verdicts/recheck_<n>.tsv` for fixed
     issues, until `qa_gate.py check` exits 0.
  4. Graphics rows: G3 (debug-menu font B3_10/11) not reachable in play; G4 (`EAは/あけて` tags, A3_05 tiles
     0x1D80+, not in area_01's VRAM): find the screen or record as unused. Game Over / THE END / credits already
     English (tour scenes game_over, ending_*, credits).
  Non-blocking: English types ~2x the JP's glyphs; the player can set Message Speed: Fast. `{c1C:xx}` slow print not
  timed.
- **Phase 7 done so far:** `tools/insert.py` (run by `build.py`): every English entry in free space, each slot a
  jump (`F8 20 p24` / `F8 22 p16` / table word) keeping its length and end byte; new control table at 84:E000 with
  jump, jump16 and `{tab:n}` (asm/vwf.asm); `01` = 12 px `{blank}`, English space = code 02; indents and column
  layouts restored (`cells.json` for sliced menus, ` | ` columns for elevators / Yes-No). Lint
  `tests/test_batches.py::test_inserted_text_fits` (final encoded layout, sliced items, name buffers) and
  `tests/test_insert.py` (romdiff write log + allowed ranges, every slot followed to its English). Seen in game:
  opening dialogue, field/config/item/shop menus, Turbo File. Notes `docs/re/insert.md`. Debug field scenes now
  15000 frames (English types ~2x longer; A doesn't skip typing). Rewordings to fit 2-cell items (full words, not
  abbreviations): Discard -> Drop (item_cmds), Normal -> Mid (message speed), Magazine -> Ammo (shop parts view).
  Heads fixed (`insert.HEADS`, slot starts at the real op-18 text): ev_959A59, ev_959C40, ev_A8C91E (full EN).
  Phase 6 review (`.harness/reviews/solid-runner-en-phase6.md`) fixed: -sama on the 4 dressing-room signs;
  `batches.py check` has an honorific check (`honorific_errors`, D1; katakana words that aren't names in
  `HON_COMMON`) and measures sliced menus with `insert.fit_errors` (the lint's own layout), only `engine_todo` ids
  are warnings (regression tests in `test_batches.py`); synopsis says Dark Dragon. `work/tl/b006`/`b036.out.tsv`
  synced with the script (all 36 batches check OK).
  Name bug fixed: places2_93C163/69/20B are the new game's default names (`insert.NAME_DEFAULTS`, in place); a jump
  slot there had put `F8 20` into the name buffer and `{c0C:xx}` printed other text. D11 done without relocating the
  buffers: default names pack letter pairs into one glyph (`font.DIGRAPHS` Er/sk/Gr, codes 03-05): "Erskine" in 5
  codes, "Grandil" in 6, seen in game (name entry, "Shu Erskine" in dialogue). Name-entry grid's first row
  (93:CC73, missed by extraction) added; grid = A-Z, a-z, punctuation, digits. Tao pilot seen in game
  (`work/qa/pilot`, scene `opening_talk`; docs/style-reference.md).
  Windows re-laid for the English (`tools/winmap.py` sheets in bank $9C + `asm/menus.asm`, seen in game): setup
  labels/slot header, data submenu, Riff's tune-up (menu, title, armor list, current armor), battle key config
  (labels in two columns, "Attack" dropped, keys moved), save slot (`=` blanked; 8x8 font AC_05 with Er/sk/Gr tiles
  -> "Shu Erskine"). Results line: each mission name holds `Mission '...' Complete` (pieces collided), label
  `Log:`, 帰らなかった男 = The Man Who Didn't Return (glossary). VWF clears a string's first cell from its first
  column (config key swap read K for X). Slots that started inside code/VM data fixed (`insert.HEADS`,
  `insert.NOT_TEXT`): places2_93C015 had overwritten its table's last byte (save slot place showed "ま狩B");
  92:DE77 (65816 code), 96:DB26/DBF8, A8:D233 no longer written; 93:EED3 / 92:9F06 keep their `PLX : RTL`.
  Last build 2026-10-30 07:09, sha1 8c88fb089d14..., smoke ok; `tools/check.py` 34 passed.
- **Still not seen in game:** A5 countdown, Turbo File "No data" (92:9F08), the load screen's slot (sheet DC_03 also
  has the `=`), add-armor yes/no (needs a level-up).
  Note: `run_scenes.py` defaults to the original ROM; pass `--rom build/solid_runner_en.sfc` for the English.
  Results with another mission: point table word 0 (92:9681) at the mission's name in a ROM copy (pin of
  $70:013E didn't take).
- **Phase 6 result:** all 4079 non-empty entries have `en` in `script/*.json` (wrapped with `{br}` by pixel width,
  end code copied from the JP; sliced menus keep ` | ` between cells). 36 batches, all `batches.py check` OK; 9
  reviewer passes, every Critical/Important fixed (no Critical found), most accuracy Minors applied in the same round.
  Tools: `tools/batches.py` (split/check/merge/fit/pairs/dump; box never smaller than the JP's own geometry),
  `script/engine_todo.txt` (15 full-term entries waiting for a wider box/buffer: warnings, not errors).
  Docs: `docs/translator-brief.md`, `docs/reviewer-brief.md`, `docs/style-reference.md` (pilot = opening Tao scene,
  not yet seen in-game), `docs/synopsis.md`, glossary (rulings D9-D11 + "Decisions from earlier batches"),
  `docs/translation-notes.md` (wave-1 phase 7 items), `docs/terms_proposed.tsv` (terms pass source).
  `work/tl/` is gitignored; `split` regenerates the batch inputs identically, outputs live only in `script/`.
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
- **Phase 7 carry-overs (from phase 5):** tab-to-cell control code for the 14 sliced menus and a wider info>data submenu
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
  emu.py wrote default key mappings to `tools/mesen/settings.json`. (non-blocking) Name spellings chosen by the
  controller with no official source: Weissheit, Raoel, Brundle, Lecter, Orbiselus, Bivisible, Dark Dragon (暗龍),
  Daemon, runner/weapon names in glossary.md; register/SFX/speech layout D9-D10. Owner may override; a rename is a
  glossary edit + `batches.py check` sweep.
