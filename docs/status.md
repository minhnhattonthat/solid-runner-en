# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7 (insert, fit, check) **in progress** (2026-10-30).
- **Phase 7 done so far:** `tools/insert.py` (run by `build.py`): every English entry in free space, each slot a
  jump (`F8 20 p24` / `F8 22 p16` / table word) keeping its length and end byte; new control table at 84:E000 with
  jump, jump16 and `{tab:n}` (asm/vwf.asm); `01` = 12 px `{blank}`, English space = code 02; indents and column
  layouts restored (`cells.json` for sliced menus, ` | ` columns for elevators / Yes-No). Lint
  `tests/test_batches.py::test_inserted_text_fits` (final encoded layout, sliced items, name buffers) and
  `tests/test_insert.py` (romdiff write log + allowed ranges, every slot followed to its English). Seen in game:
  opening dialogue, field/config/item/shop menus, Turbo File. Notes `docs/re/insert.md`. Debug field scenes now
  15000 frames (English types ~2x longer; A doesn't skip typing).
- **Phase 7 left:** `script/engine_todo.txt` (20 known overflows: name buffers D11, sliced rows of N cells for setup
  labels / tune menu / data submenu / battle keys, tune_armor, slot labels, results title); extractor blind spots
  (below); `{c1C}` timing; check elevator/turbo/countdown layouts in game; typing speed (phase 8 polish).
- **Phase 6 result:** all 4079 non-empty entries have `en` in `script/*.json` (wrapped with `{br}` by pixel width,
  end code copied from the JP; sliced menus keep ` | ` between cells). 36 batches, all `batches.py check` OK; 9
  reviewer passes, every Critical/Important fixed (no Critical found), most accuracy Minors applied in the same round.
  Tools: `tools/batches.py` (split/check/merge/fit/pairs/dump; box never smaller than the JP's own geometry),
  `script/engine_todo.txt` (15 full-term entries waiting for a wider box/buffer: warnings, not errors).
  Docs: `docs/translator-brief.md`, `docs/reviewer-brief.md`, `docs/style-reference.md` (pilot = opening Tao scene,
  not yet seen in-game), `docs/synopsis.md`, glossary (rulings D9-D11 + "Decisions from earlier batches"),
  `docs/translation-notes.md` (wave-1 phase 7 items), `docs/terms_proposed.tsv` (terms pass source).
  `work/tl/` is gitignored; `split` regenerates the batch inputs identically, outputs live only in `script/`.
- **Phase 7 must do (from phase 6, details in `docs/translation-notes.md`):**
  - insert `en` (encode with `tbl/en.tbl`; ` | ` cells -> tab-to-cell code); lint = `test_batches` fit + romdiff.
  - layout blanks dropped by translators: restore the JP's leading indent per line (choice cursor, 12 px per JP
    blank) and a pad-to-x for column menus (elevators, keypad, turbo Yes/No) and centring (places_*, turbo_*).
  - `engine_todo.txt`: widen name buffers (Erskine/Grandil, D11), tune_armor 54 px, slot labels 36 px, results
    120 px; sliced menus in full words (`batches.py check b036` warnings, needs `split` first).
  - extractor blind spot: 5 entries start mid-string (fake op inside a string; head bytes uncovered, stay JP):
    ev_93827B, ev_959A59, ev_959C40, ev_97BA44, ev_A8C91E; garbage-prefixed/garbage entries: ev_91940D, ev_92DE77,
    ev_95A2AA, ev_96DB26, ev_96DBF8, ev_979F08, ev_A8D233, loose_93EED3, turbo_929F06, places2_93C015. Sweep the
    whole ROM for the form, fix extraction, re-translate the changed entries (full-string EN drafts in the notes).
  - `{c1C:xx}` slow-print codes were moved off name interiors (Weissheit, Riff) to keep names whole: check timing.
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
