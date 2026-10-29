# ROM map, compression, free space

## Header (verified, tests/test_rom.py)

3 MiB LoROM, map mode `$30` (FastROM), size byte `$0C`, 8 KiB SRAM, title `ｿﾘｯﾄﾞﾗﾝﾅｰ`. 96 banks of 32 KiB
(`$80-$DF`). Code runs in the `$80+` mirror. File offset = `((addr & 0x7F0000) >> 1) | (addr & 0x7FFF)`.

## Rough bank map (entropy + table survey; guess unless noted)

| Banks | Contents |
|---|---|
| $80-$87 | code + tables; menu/item/name strings in $82, $83, $87 (`text.md`); text engine $84 (verified); event VM $81 (verified) |
| $88-$91 | data (maps/tables), $91 battle-ish dialogue |
| $92-$9E | event scripts, map headers (verified for $95), intro crawl in $92 (verified) |
| $A0-$A3, $A5, $AA-$AC, $AF-$C7, $CA-$DE | LZ graphics blocks behind bank-start pointer tables (verified for $A2/$A3 map tiles by `vramfind.py`) |
| $A8, $A9, $AD | more script/text (heuristic) |
| $AE | 12x11 font [170000-176DFF] (verified) |
| $A4, $A6, $A7, $D2, $D9, $DA, $DF | no bank table; other formats ($A7:85ED RLE for boot logos) |

## Compression (verified)

- **LZ** (`tools/lz.py`, decompressor 80:935E, loop 80:93A8): ops `01-7F n` = n literals, `80-FF d` = copy
  `(op&7F)+3` bytes from `d+1` back, `00` = end. Callers pass a pointer to a 16-bit table entry (`$3E-$40`), the
  table being the one at the start of the bank. Verified: first-map tiles in VRAM match blocks A3_01-A3_03.
  A compressor is needed only for edited graphics (phase 8 graphics work).
- **RLE** at A7:85ED (boot logos): `01 n b` byte run, `02 n w` word run, `FE n ...`, `FF` end (read, not fully
  decoded).
- Other decompressors seen writing the 7E:2000 buffer: 88:860D, 83:8D67, 83:BD91 (not analysed).
- Text is not compressed.

## Free space (candidates; trap-test before use)

Trailing 0xFF runs at bank ends, ~470 KiB in all. Whole banks of FF: **$BA, $BB, $CD, $D3, $D4** (160 KiB). Large
tails: $86 [0319D0-037FFF] 26 KiB, $D7 [2B8CAD-] 29 KiB, $AF [17AE2E-] 21 KiB, $84 [02389F-] 18 KiB (the text-engine
bank: room for VWF code), $91 [08B789-] 18 KiB, $94 [0A3CE1-] 17 KiB, $B9 [1CC5CB-] 15 KiB, $C7 [23C756-] 14 KiB,
$82 [015349-] 11 KiB. Full list: `python tools/freespace.py`. Expanding to 4 MiB (size byte `$0C` already covers 4 MiB) adds 32 more banks.
