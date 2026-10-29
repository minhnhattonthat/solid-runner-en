# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (research and recon) done; next is phase 2 (debug tool). No build yet.
- **Done (phase 1):**
  - No prior fan patch or community docs found.
  - Encoding verified (`tbl/jp.tbl`: kana, latin, symbols, `F8` controls with engine arg counts; kanji `F9-FC xx` not
    yet read). 12x11 font at $AE:8000 (`tools/font_sheet.py`). Text engine 84:A91E; all text goes through it.
  - Event-script VM mapped (`docs/re/events.md`): dispatcher 81:BDCF, table 81:BE4C, inline text after ops 17/18/19,
    `tools/vm_oplen.py` gives lengths for most opcodes. Insertion plan: in-place `F8` jump control to free space.
  - Text locations (`docs/re/text.md`), LZ codec + bank tables + free space (`docs/re/rom-map.md`,
    `tools/lz.py`, `tools/freespace.py`), graphics survey via LZ sweep + 4 reviewer subagents
    (`docs/re/graphics.md`, `tools/gfx_sweep.py`). Tests in `tests/test_recon.py`.
- **Next:** phase 2 debug tool (`tools/debug/warp.lua` + `scenes.lua`). Leads: map header lists at the start of
  bank $95 etc. (`events.md`), thread pointers $7E:B297/B2BC/B2E1, possible leftover debug menu (font/labels in
  LZ block B3_10: `フラグ KIND SOUND LEVEL`, place names). Savestates from the recon tour: `work/play/ng/` (0002 title,
  0003 first map, 0006 after the opening dialogue; work/ is gitignored, recreate with the boot route + NEW GAME).
  New game: title Start at ~f1100, NEW GAME Start, wait ~600 frames, name screen Start accepts the default name.
- **Phase 4 carry-overs:** read the ~960 kanji cells; finish the dyn opcode lengths and write the VM disassembler;
  pin the pointer tables behind each FF-list (`text.md` table); find the second script format in banks $87/$91; find
  users of the 8x8 kana font (AC_01/AC_05).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the Mesen GUI's keyboard input was not hand-tested (headless session);
  emu.py wrote default key mappings to `tools/mesen/settings.json`.
