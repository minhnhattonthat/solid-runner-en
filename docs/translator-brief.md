# Translator brief - Solid Runner (Super Famicom, 1997)

You translate part of the Japanese script of Solid Runner into English for a fan patch. Near-future cyberpunk RPG:
the player, Shu Erskine (name can be changed), is a "cyber detective" in Solid City who pilots a mech called a
runner, takes jobs from terminals, and gets pulled into a war between crime syndicates after his wedding goes wrong.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before
the next. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - speech layout, character voices, approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table in `glossary.md` if you need more).
3. `docs/synopsis.md` - plot, who is who, the late reveals (marked SPOILER). Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese` - form is dlg | text | menu | name | narration; ` / ` separates the
lines of one box (translate the box as one utterance); limit is the box (`240px x 3` = 3 lines of 240 px; `(last
232)` = the last line leaves room for the more-arrow). Lines are in script order: use neighbours for context. A box
without a speaker bracket usually continues the previous speaker. For context beyond your batch, grep
`work/tl/script_dump.txt` (whole script, `id<TAB>jp`).

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `-`; no tabs inside
the English, no Japanese or fullwidth characters, no `\uXXXX`, no `\n`.
- Write each box as ONE paragraph: the tool word-wraps it by pixel width into the box's lines. The font is
  proportional (~5-6 px a letter), so a 240px x 3 box holds about 120 characters.
- ` / ` (space slash space) forces a line break: use it only where the JP layout matters (intro crawl, a list of
  options on separate lines). A blank line is two breaks with nothing between: `line one /  / line three`.
- ` | ` separates the cells of a sliced menu (only in batches the controller tells you about).

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.
Dry-run one line: `python -X utf8 tools/batches.py fit "English text" --box dialogue` (box names: windows.json
`variants`). Characters the font has: A-Z a-z 0-9 space and `- ? ! : " ' ; ... ( ) , . + * = & % / $`. No `#`, `@`,
`[`, `_`, `~` (write "-" or rephrase).

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Speech layout per `docs/style-reference.md`: `Name「` -> `Name: ` (no quotes); a box starting `「` -> `"..."`
  closed in that box; no bracket -> plain text.
- Use names and terms exactly as in the glossary. Never abbreviate a name or term to fit; the boxes are roomy. If a
  line can't fit without losing meaning, keep the meaning and report it as `LONG: id`.
- Honorifics kept, hyphenated, where the JP has them (Kirk-san, Shu-kun); name order Western (given name first).
  Titles like シスター stay as the English title ("Sister Rachel", "Sister").
- Punctuation: 「」 -> per layout above, 『』 -> '...', ・・・/… -> `...`, ！？ -> `?!`, 〜 (drawn-out speech) -> repeat
  a letter or drop. Em dash -> ` - ` or `--`.
- Placeholders/control codes: copy every `{...}` code exactly, same count. `{c0C:01}` = player's given name,
  `{c0C:00}` = player's family name, `{c0C:02}` = the player's runner (mech) name; `{c04:...}` = a number the game
  prints (money, counts); `{c18}`, `{c1A:..}`, `{c1C:..}` = item/part names the game inserts. No suffixes glued to a
  code ("No. {c04:..}" not "{c04:..}th"), no a/an right before a code, no possessive 's on a name code if it would
  read wrong for names ending in s - "{c0C:01}'s" is fine.
- Money: `{c04:..}G` stays `{c04:..}G` (G = the currency).
- `FAB1`-style ✕ in JP (`✕✕ババア`) is a censored swear: write `**` in its place (`you old **-hag`).
- Original typo: ev_97BA44 `6功` means `成功` (success).
- SFX/onomatopoeia (ドカーン, バキッ): English comic-style words in caps-first ("Kaboom!", "Crack!").

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Notes from earlier batches
- (none yet)

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
