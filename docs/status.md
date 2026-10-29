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
  15000 frames (English types ~2x longer; A doesn't skip typing). Rewordings to fit 2-cell items (full words, not
  abbreviations): Discard -> Drop (item_cmds), Normal -> Mid (message speed), Magazine -> Ammo (shop parts view).
  Heads fixed (`insert.HEADS`, slot starts at the real op-18 text): ev_959A59, ev_959C40, ev_A8C91E (full EN).
  Last build 2026-10-30 05:11, sha1 94b1a7b8..., smoke ok; `tools/check.py` 30 passed.
- **Phase 7 left (next session, in this order):**
  1. `script/engine_todo.txt` (20 known overflows the lint exempts): sliced menus show the bitmap in rows of N cells
     (setup labels 4, tune menu 4, data submenu 2; battle keys code-placed, unseen): find the window tilemap builder's
     row width and widen it (one routine for all?), move the setup part names right; tune_armor 54 px, slot labels
     36 px, results title 120 px; name buffers (D11): $1AC3/$1AC9/$1ACF (5/5/6 + FF, money at $1AD6) are read by
     F8 0C (handler 84:AB89), the name entry, save/load and the 8x8 save-slot line; defaults `default_names` are
     skipped by insert (kept JP) until then.
  2. Heads still JP: ev_93827B (real start 93:8267 `店のオヤジ「…`, after a `12` op, not a text op: find what reads
     it) and ev_97BA44 (news headline); garbage entries ev_91940D, ev_92DE77, ev_95A2AA, ev_96DB26, ev_96DBF8,
     ev_979F08, ev_A8D233, loose_93EED3, turbo_929F06, places2_93C015 (inserted as translated; check in game).
  3. In game: elevators (` | ` columns), A5 countdown, info_data submenu, battle key config, Riff's tune-up, name
     entry grid (charset in place, letters drawn proportional: cursor cells may not line up).
  4. `{c1C:xx}` slow-print timing; typing speed (English ~2x glyphs; maybe halve the per-glyph delay).
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
