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

; Riff's tune-up (sheet 9C_02, tools/winmap.py tune): menu and title 11 wide; current armor box two lines high at
; rows 6-11 (src rows 3-8); the add-armor yes/no window's rect moved to rows 32-37 to make room
org $93A7A6
    db 11
org $93AAAE
    db 11
org $93AC24
    db 6, 16, 3, 14, 6
org $93AA9E
    db 19, 32
; strip $18 upload (DMA param 93:B29D, $7E:3800 -> VRAM $6C00): $200 -> $400, so strip $1A comes along
org $93B2A1
    db $04
; current armor name records {column, strip, 0, 0}: column 6 of strip $18 -> column 0 of strip $1A (its own line)
org $93B2DA
    db 0, $1A
org $93B2E7
    db 0, $1A
org $93B2F4
    db 0, $1A
org $93B301
    db 0, $1A
org $93B30E
    db 0, $1A
org $93B31B
    db 0, $1A

; the slot screen's text upload at entry (DMA param 82:A9FC, $7E:3400 -> VRAM $6A00): strips $14-$1D -> $14-$1F, so
; it carries strip $1E
org $82AA00
    db $0C

; DATA LIBRARY tab highlight (object 87:A80E): its metasprite 87:A83F is two 16 px sprites at x -8, 0 (24 px, the
; JP's two glyphs); the English tabs (Topics, People, Enemies) get three (-8, 8, 16: 40 px)
org $87A817
    db tab_bar
org $87A81C
    db tab_bar>>8
org $87A821
    db tab_bar>>16
org $84FE00
tab_bar:
    db $01 : dw -8, -8 : db $EE, $28
    db $01 : dw -8, 8 : db $EE, $28
    db $01 : dw -8, 16 : db $EE, $28
    db $FF
