# Event-script VM (dialogue lives inside it)

## Interpreter (verified by breakpoint logs, Tao scene after NEW GAME)

- Threads: up to 0x25, X = thread index. Script pointer per thread in `$7E:B297,x` (lo) / `B2BC,x` (hi) /
  `B2E1,x` (bank); copied to DP `$32-$34` by 81:BDBA.
- Dispatch 81:BDCF: `LDY #0; LDA [$32],y; INY` then `JMP (table,opcode*2)` with the table at **81:BE4C** (2-byte
  handlers in bank $81; opcodes 00-A2 are real, the table runs into code after A2). Handlers run with 8-bit A/X/Y and
  return by RTS to 81:BE26, which adds Y to the thread pointer: **instruction length = Y on return**. Y = 0 means
  "run this instruction again next frame" (waits).
- `python -X utf8 tools/vm_oplen.py` walks every handler and prints the possible lengths. Fixed-length results are
  reliable; rows flagged `dyn` need reading by hand (list below).

## Text opcodes (verified)

| Op | Handler | Form |
|---|---|---|
| `17 xx` | 81:C90E | 1 arg (box mode, stored to $4D), then inline text |
| `18` | 81:C8FA | inline text, mode 00 |
| `19` | 81:C904 | inline text, mode 80 |

The handler stores the text start in `$18B2-$18B4`, then scans to the end (81:C930): bytes `<F8` one byte,
`F8 cc` + argc from 84:AA3B, `F9-FC xx` two bytes, `FD/FE/FF` end. So text length changes move every later byte of
the script: **script code after a text must stay where it is, or every jump into it breaks**. Insertion plan (phase
5): leave scripts in place and replace each inline text with a new control `F8 <new cc> <24-bit ptr>` that sends the
text engine to the English in free space, keeping the original bytes after it so 81:C930 still finds the old
terminator (pad to a character boundary first: a kanji's second byte can be F8-FF).

Other ops seen around a dialogue: `0E aa bb` (open window with portraits aa-1 / bb-1; 81:E860), `12` (set $18D0),
`94-9D xx` (store xx to $0209-$0212: variables).

## Opcode lengths still to read by hand (`dyn` in vm_oplen.py)

03, 05 (indirect), 0A, 0B, 17-1A (text: computed by the scanner rule above; 1A is text-like with 4 bytes before it),
1E, 29-2F, 38, 39, 3E, 3F, 45, 7B, 7C, 80, 81, 83, 84, and 54-6B: movement commands, `op aa` + a data block whose size
is set per opcode by `LDA #n` before `JMP 81:D634` (54/55: 0, 56/57: 2, 58/59: 4, 5A/5B: 6, 5C/5D: 8, ...): length
2 + n. Ops reporting `0,n` are waits or conditional jumps; find which by reading them before trusting a disassembly.

## Map loading, story state, battles (verified by the phase-2 warp tool, `tools/debug/`)

- **Map = area + room.** Area id `$7E:1AA8`, room `$7E:1AA9`. Loader 80:C546: area table **A7:F000** (32 x 24-bit
  pointers, one per area; entry $18 = 87:8000 is code, not a map). Each points to a bank-start block: word 0 points
  past the room list, then one 16-bit room-script pointer per room (same bank). Room scripts run on a small
  interpreter 80:C900 (pointer `$2F-$31`, table 80:C918, `FF` ends): e.g. `1A ptr24` call, `1C addr24 val ptr16
  cond` branch on a byte test (81:CE3E: cond 0 eq, 2 ne, ... 0C/0E bit set/clear), `1E ptr16` goto, `0A ptr16` map
  header. Verified: every area's room 0 loads (`run_scenes.py --raw`).
- **Areas seen:** $00 battle arena (rooms = backgrounds), $01-$15 and $19-$1F story maps, $16 system (rooms 0-2
  psycho-dive scenes, 3 title, 4/5 name entry, 6 save/load, 7 shop greeting, 8 parts view, 9 shop buy/sell menu),
  $17 (0 staff roll, 1/2 THE END, 3-5 cutscenes, 6 Turbo File menu, 7 Results, 8 intro credits). New game: title
  $16/03, name entry $16/05, first map $01/00 (opening event thread 95:84BC).
- **Map change:** queue task 80:D2C3 in the 8-slot task list (`$06BF/$06C7/$06CF,y` = 24-bit callback, bank 0 =
  free; added by 80:D938) after setting area/room; VM op `4D aa rr` (81:D355) does exactly this. Tasks don't run in
  every mode (a queued change stalled in the battle arena), so the warp tool redirects the new game's first load
  instead (one cold boot per scene).
- **Story state is in SRAM** (`$70:0000-$70:01FF` working area; save slots further up, e.g. continue reads
  `$70:07BC/07BD` = saved area/room). Event flags are bits tested by room-script op 1C and set by VM ops 25/26
  (`25 addr24 val`). Which flags mark which story point is **not mapped yet**.
- **Battles:** VM op `7D ptr24` (81:C82A) starts a scripted battle from a record `{id, formation, callback24 or 00}`
  (`id` -> `$70:01CB`, beaten flag = bit 7 of `$70:01CB+id`), via 90:BE20: saves the return map in `$7E:D05C/D05D`,
  loads area $00, task 80:D4BC. Random battles enter at 90:BE16 (called from 90:ECB7). Battle end 90:BEA8 runs the
  callback and returns. 12 records found by scanning the event banks for `7D` + record shape (`scenes.lua`).
- **Party:** Shu max HP `$7E:1896`, current `$7E:189A` (16-bit), money `$7E:1AD6` (16-bit). HP 0 in battle -> Game
  Over -> back to the title.
- VM op `05 ptr24` calls native code; `07/08/09 ptr24` start a script thread on object slot 0/1/2 (spawning one over
  the first map's opening thread gave a black screen); `10` opens the in-dialogue name keyboard; `00` ends a thread.

## Where scripts live (partly verified)

- A map header (first map after NEW GAME: 95:83D1 [0A83D1]) holds three 24-bit thread entry pointers at +0x17,
  +0x1A, +0x1D (95:84BC, 95:83F4, none); 80:CEA3 copies the bank bytes, 85:96D1 starts the threads.
- The header is picked from a list at 95:837D [0A837D] (`[$2F],y` at 80:CD40); that list is entry 0x0A of the 16-word
  pointer table at the start of bank $95. Most data banks start with such a table of 16-bit pointers to their blocks.
- Banks holding inline dialogue by the heuristic scan (an opcode 17/18/19 followed by plausible text; counts are
  noisy): $94-$97 (densest), $92-$93, $98-$9E, $A5, $A8, $A9, $AD. Phase 4: enumerate every map header from the bank
  tables, disassemble each thread from its entry with the opcode lengths above, follow jumps/calls, and list every
  text; then compare with the heuristic scan to catch scripts reached some other way (battle events, intro, ending).
- A second, different script format carries dialogue in banks $87 [03C3B4-] and $91 [088BBA-] (2-3 bytes before
  each `name「…` line). Unknown VM: find its reader with `textlog.lua` in a scene that uses it (battle?).
