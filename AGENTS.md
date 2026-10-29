# Solid Runner (SNES) English translation

Skill: translate-retro-game; `python tools/skill.py` prints its folder. Read its SKILL.md before ROM, text or QA work. `"$(python tools/skill.py)"` works in bash and PowerShell; never paste a `plugins/cache/<hash>` path.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py` -> build/solid_runner_en.sfc (checks the dump against `rom.sha1` first; every change via `put()`, logged to build/writes.txt for `tools/romdiff.py --writes`)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/solid_runner_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/solid_runner_en.sfc --out work/qa/warp --script tools/debug/scenes.lua --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 2400 --sheet` (cold boot; warp lands ~f1560; scenes and options in `tools/debug/scenes.lua`/`warp.lua`; never ask the user to play to a scene)
- All scenes: `python -X utf8 tools/debug/run_scenes.py [names] [--raw AA:RR] [--states] [--rom R]` (parallel cold boots, shots in work/qa/scenes/, `--states` regenerates work/states/<scene>.mss)
- Release:  `python -X utf8 tools/release.py` [--version X.Y] (build, tests, smoke, jp_left, QA gate on a tour of this exact ROM, BPS + re-apply, zip in release/; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Solid Runner (Japan).sfc` (gitignored; 3 MiB LoROM FastROM, SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own copy in `tools/mesen/` (MesenCE 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/` (format chosen in phase 4). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.
- Copied from the skill so a clone builds without it: `tools/tbl.py`, `tools/bps.py`, `tools/romdiff.py`. QA tools (`emu.py`, `play.py`, `qa_gate.py`, `jp_left.py`) run from the skill.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- `fetch_emu.py` fails here with an SSL issuer error (Python urllib); `curl -L` the URL it prints with `--dry-run` and unzip into `tools/<emu>/`.
- Boot timing (original): logos to ~f600, intro text crawl, title "PUSH START" at ~f1050, then an attract story if left idle.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
