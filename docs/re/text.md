# Text: encoding, font, engine, where the text lives

Addresses are CPU (LoROM, `$80+` mirror) with file offsets in brackets. Dump: `rom.sha1`.

## Encoding (verified)

One table for all text seen so far (`tbl/jp.tbl`). **Verified** by decoding the intro crawl at [090F1F]
(`２１ＸＸ年。政治や経済、人口など…`) and Tao's first line at [0A84CA] (`タオ「…とにかくだ。アイリーンは、…`) against
screenshots, and by the font: glyph index = code - 1 (decode at 84:A98B).

| Code | Meaning |
|---|---|
| `00` | line break |
| `01` | full-width space (glyph 0, blank) |
| `02-51` | hiragana in gojuon order, then dakuten/handakuten, then small kana (`あ`=02, `ん`=2F, `が`=30, `ぁ`=49, `っ`=4E, `ょ`=51) |
| `52-A2` | katakana, same order (`ア`=52, `ン`=7F, `ガ`=80, `ァ`=99, `ッ`=9E, `ョ`=A1, `ヴ`=A2) |
| `A3-B8` | `0-9`, `ー？！・「」『』（）、。` |
| `B9-EC` | `A-Z a-z` (full-width-looking glyphs, 12 px cells) |
| `ED-F7` | `＋−＝＆％／＄○▲▼` and a `≡`-like icon (F7) |
| `F8 cc args` | control code, see below |
| `F9-FC xx` | kanji: glyph `(p-F8)*256 + xx - 1`; used up to `FC C2` (glyph 0x4C1). Kanji are in first-use order, not JIS |
| `FD` `FE` `FF` | end of text (three variants; `FF` is the common one). Intro engine: FD calls 80:D938 with 84:B2EF, FE clears $18B0 bit 1, FF plain end. In scripts FD ends a page that the next text opcode continues (Tao's line [0A84CA] ends FD at [0A84FF]; op 18 at [0A8500] starts the next page). Exact box effects are a **guess** until the marker build |

`tbl/jp.tbl` has the kana, latin, symbols and controls. **Kanji are not in it yet**: they decode as `[F9][xx]`, which
round-trips. Reading the ~960 kanji cells off the font (`python tools/font_sheet.py work/font`) is phase 4 work (skill:
template guess + reviewer subagents with script context).

### Control codes `F8 cc` (verified table, meanings guessed)

Handler + argument-count table at 84:AA39: word pairs `(handler, argc)` indexed by `cc` (even values 00-1E;
`JSR ($AA39,x)` with x = cc*2). The dialogue scanner 81:C930 uses the argc word (84:AA3B+cc*2) to skip arguments, so
the counts are what the engine itself uses:

| cc | args | handler | cc | args | handler |
|---|---|---|---|---|---|
| 00 | 0 | 84:AA79 | 10 | 1 | 84:ABE7 |
| 02 | 2 | 84:AA88 | 12 | 0 | 84:ABE1 |
| 04 | 4 | 84:AAD4 | 14 | 0 | 84:AB7F |
| 06 | 3 | 84:AA98 | 16 | 1 | 84:AC97 |
| 08 | 3 | 84:AAAD | 18 | 0 | 84:AC4C |
| 0A | 1 | 84:AACD | 1A | 1 | 84:AD06 (84:A96C returns from the call after cc 1A) |
| 0C | 1 | 84:AB89 | 1C | 1 | 84:AD20 |
| 0E | 0 | 84:AB84 | 1E | 0 | 84:AD32 |

Seen in script: `F8 0C 01` at the start of a line where a speaker name would go (`{c0C:01}「…`: probably prints the
player's name, which is entered at the name screen), `F8 04` with 4 bytes. Meanings are guesses until the marker
build.

## Font (verified)

12x11 1bpp glyphs, 22 bytes each (11 rows x 16-bit little-endian word, bit 15 = leftmost pixel) at **$AE:8000
[170000]**, 0x4C2 glyphs (to [176E00]; rest of bank $AE is FF). Read by 84:ADEA (`LDA $8000,y` with Y = glyph*22,
data bank $AE) and drawn with a shadow/outline into a WRAM bitmap at $7E:2000+ (84:ADBF / 84:AED6, two shift paths),
then DMA'd as 2bpp BG3 tiles. So all font text is rendered at run time into a bitmap: a VWF needs only the renderer
and advance logic, not tile allocation. Cell pitch on screen is 12 px wide, 16 px line height in menus/dialogue.

`tools/font_sheet.py` renders the font with codes.

## Text engine (verified by breakpoint logs)

`84:A91E` reads one character per call from `[$50],y` (DP $50-$52 = 24-bit string pointer), dispatches
`<F8` glyph / `F8` control / `F9-FC` kanji / `FD-FF` end. Every text kind below goes through it (`tools/lua/textlog.lua`
logs each distinct pointer it is given).

Dialogue box: 3 lines, about 22 full-width characters per line (screenshots `work/play/ng/0005.sheet1.png`); ▼ at
bottom right when more follows. Width gate is phase 5.

## Where the text is

| Kind | Where | Format | State |
|---|---|---|---|
| Event dialogue | event-script banks (see `events.md`) | inline after VM opcode `17 xx` / `18` / `19`, runs to the first `FD/FE/FF` (scanner 81:C930); no pointers to the text itself | verified (Tao scene, 95:84CA) |
| Intro crawl | bank $92 [090F1F]... | strings inline in the intro code bank, pointer loaded by code | verified (first page) |
| Menus | bank $82 [01448F-01463B] (`アイテム セットアップ 情報 コンフィグ`, `ステータス`, `サウンド メッセージ…`) | FF-terminated, padded with `01` | verified (textlog on menu open) |
| Runner/mech names | bank $82 [0121DE-0122B9] (`ラヴィアン マッドキャット …`) | FF-terminated list | guess (decoded, not yet seen on screen) |
| Items + descriptions | bank $83 [0196AD-019A63] (`リペアキット…` / `HPを150ポイント回復する`) | name/description pairs, FF-terminated | verified (item menu textlog) |
| Parts, weapons + descriptions | bank $83 [01A642-01AFEB] (`ニーメイヤRY1`, `ショットガン` texts) | FF-terminated | verified for [01A642],[01A7A1],[01A841] (setup menu textlog) |
| Location names | bank $83 [01B4C2-01B98E] (`ホストセンター B1F`, `テロリストのアジト B2F`) | FF-terminated, left-padded with spaces | guess |
| Name entry | defaults `シュウ` `アースキン` at [018F28]; screen builds strings in WRAM ($17F4, $1AC3) | FF-terminated | partly verified |
| Character names | bank $87 [03EEF4-] (`アイリーン リフ タオ シスターレイチェル カーク イオン ミネルバ…`) | FF-terminated list | guess |
| Info/database and other long texts | bank $87 [03C3B4-03F59F] | FF-terminated; some preceded by 2-3 bytes of another script format (`たぬ「…`) | guess |
| Battle(?) dialogue | bank $91 [088BBA-08A5D5] (`イオン「ミネルバ、サイコダイブ…`) | text with a short non-text prefix per line (different VM?) | guess |

Phase 4 (verified by roundtrip and `tests/test_coverage.py`): the event texts come from the VM disassembler
(`events.py`, `script/events/`); everything else is in `tools/strings.py` -> `script/lists/<name>.json`, one entry
per FD/FE/FF-terminated string in hand-checked ranges. Bank $91 "battle dialogue" turned out to be the same VM
(psycho-dive scenes). Pointer tables found so far (16-bit, same bank): runners 82:A17F, requests 82:C8B6, locations
83:B41E (74), info menu 87:8558, names 87:EEC6 (19), database records 87:C76F/C771/C773 (stride 7) and 87:C968
(stride 4), missions 92:9683, Turbo File 92:AE6E, equipment 93:B32A/93:B36A, help 93:C365. Other lists (status
labels, "N件の情報があります" counters, robot battle messages) are loaded by code immediates, often right after an
RTS/RTL (`60`/`6B`) with the string inline in the code bank. Phase 7 needs the reader of every list that is not
relocated in place. Some ranges are guesses at the edges (equipment labels at 93:B248/B274/B291 have no terminator
between labels; database records start with 2-6 bytes such as `RゆRエ{br}` that may be data): the marker build
checks them on screen. Banks $80-$93 hold code and tables mixed with these lists: never treat a whole bank as text.
