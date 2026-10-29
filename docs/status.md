# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0 (repo setup) done; next is phase 1 (research and recon). No build yet.
- **Done:**
  - Template in place; `tools/skill.py`, `tools/{tbl,bps,romdiff}.py` copied from the skill.
  - MesenCE 2.2.1 in `tools/mesen/` (settings copy in `tools/emu-config/settings.json`). Original ROM boots under `emu.py --smoke` (exit 0); a Start press on the title changes the screen; a `--script` probe's `L.log` reached `log.txt`.
  - Plugin guard hook active (blocks `sed -i` canary and heredocs). Pre-commit runs `tools/check.py`; a failing test was rejected.
  - `rom.sha1` pinned; tests check the hash and the LoROM/FastROM header (title `ｿﾘｯﾄﾞﾗﾝﾅｰ`, map `$30`, size byte `$0C`, 8 KiB SRAM).
  - Owner's standing answers recorded as D1-D8 in `docs/decisions.md` and in `glossary.md`.
- **Next:** phase 1 recon: earlier patches/docs, text encoding (intro crawl at ~f1290 shows kana/kanji text), pointer tables, compression, free space, graphics-text survey. Write `docs/re/`.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) the Mesen GUI's keyboard input was not hand-tested (headless session); emu.py wrote default key mappings to `tools/mesen/settings.json`.
