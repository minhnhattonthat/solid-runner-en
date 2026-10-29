# Visual-QA reviewer brief - Solid Runner (SNES)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- The original ROM's sheets: `work/qa/tour_jp/` (same scene folder names) and `glossary.md`.

Each sheet is one scene warped to from a cold boot by the debug tool, a shot every 300 frames. The first frames are
the boot logos and the warp; the scene itself comes last.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 "$(python tools/skill.py)/scripts/sheet.py" SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png`
  (scratch = a file under `work/qa/zoom/`) and read that. Single frames: `work/qa/tour/<scene>/f*.png`.
- When something looks wrong, open the same scene from `work/qa/tour_jp/` (`sheet.py EN.png --compare JP.png`).
  If the original shows the same thing, it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok`:
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- The boot frames before the warp (logos, the intro text crawl in English, the title screen) repeat on every sheet:
  judge them once, on the sheet where they are the scene.
- The title logo's dark bar right of "SOLID" is empty on purpose (its katakana reading was removed).
- Pair glyphs: "Er", "sk", "Gr" are one glyph each in the default names ("Shu Erskine"); slightly tight kerning
  inside them is expected.
- English text types out about twice as long as the Japanese did; a box caught half-typed is fine.
- Short labels are deliberate rewordings to fit their cells (glossary.md): Drop, Mid (field menu), Hit and Ammo
  (shop parts view), Items / Weapons (shop Buy/Sell submenu), Cost (shop count window); battle HUD enemy names
  N. Vague, G. Hunter, P. Lizard, Weissheit (for Neo Weissheit): the HUD holds 9 letters.
- The `credits` scene is the boot intro crawl (area 17 room 08); the staff roll is `staff_intro`.
- The boot intro crawl lines are centred in a narrow band (x 30-226); the original clips its own long lines there.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
