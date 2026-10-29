; menus.asm: window descriptors and code bytes for the English menu layouts (tools/winmap.py rewrites the sheets).
; A descriptor is {dx, dy, sx, sy, w, h, $20}: the rect at (sx, sy) of the screen's sheet goes to the BG3 tilemap at
; (dx, dy) (copied by 82:B704).

lorom

; Field menu > Setup (sheet 9C_03): labels 9 tiles + part names, 20 -> 25 tiles wide
org $82A923
    db 25

; Setup > a slot (sheet 9C_00): header + list rect, header two lines high, 2 rows higher on screen
org $82AA6B
    db 6, 0, 32, 19, 16

; the slot header's part name: column 0 of strip $1E (line 2 of the header) instead of column 2 of strip $14, the
; slot label's strip (82:AB1B), so the label keeps a whole line
org $82AAF9
    LDX.b #$00
    LDY.b #$1E

; Information > Data submenu (sheet 9C_00): rows 68-73, 12 wide (Information, People on one strip)
org $82AF34
    db 0, 68, 12

; the slot screen's text upload at entry (DMA param 82:A9FC, $7E:3400 -> VRAM $6A00): strips $14-$1D -> $14-$1F, so
; it carries strip $1E
org $82AA00
    db $0C
