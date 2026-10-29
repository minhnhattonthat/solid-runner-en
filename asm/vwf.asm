; vwf.asm: variable-width font for the text engine (84:A91E). Assembled by tools/build.py with asar.
;
; The engine draws every glyph (12x11 1bpp, $AE:8000, 22 bytes) into a 2bpp bitmap at $7E:2000 at a fixed 12 px
; pitch: column $18BA (0-9) in a strip of 15 tiles, strip base $18BB*256, 2 strips per line (docs/re/text.md).
; This replaces the glyph draw at 84:A993 with one that keeps a pixel cursor and advances by a width per code.
; Strips stay as the engine laid them out: tile t of a line is in strip t/15, so text runs on into the next strip
; exactly where the original's 10-column wrap put it.
;
; Callers position text by writing $18BA/$18BB; when either differs from what the VWF last left there, or the
; engine has zeroed $18B8 (string or line start), the cursor restarts at column*12 from that strip. After each glyph the VWF leaves $18BB/$18BA in the original's form (strip
; and column 0-10 where the next glyph starts): the typewriter (84:A7E1) uploads the strip $18BB names before each
; character, so a glyph that straddles two strips shows its right part with the next character.
; Pixel colours follow the original's two modes ($18B9 = 0: overwrite, else merge), applied only inside the
; glyph's own advance (+1 shadow column), so neighbours are kept.

lorom

!px = $1D80        ; pixel cursor in the line (16-bit)
!col = $1D82       ; $18BA as the VWF last wrote it
!row = $1D83       ; $18BB where the cursor was last placed: the line's first strip, px counts from there
!rowout = $1DA0    ; $18BB as the VWF last wrote it
!w = $1D84         ; advance of this glyph
!sh = $1D85        ; px & 7
!tmp = $1D87
!fp = $1D88        ; glyph index, then font offset of the current row (16-bit)
!ro = $1D8A        ; scratch / row offset in the bitmap (16-bit)
!G = $1D8C         ; 3 bytes: glyph row, shifted
!S = $1D8F         ; 3 bytes: shadow (G >> 1)
!M = $1D92         ; 3 bytes: merge mask, w+1 px from sh
!MC = $1D95        ; 3 bytes: overwrite clear mask, w px from sh+1
!B = $1D98         ; 3 words: bitmap offsets of the 3 tiles the glyph touches
!lp = $1D9E        ; pixel width of the line since the engine last zeroed $18B8 (16-bit)
!ocol = $1DA1      ; the original's column ($18BA as it would be, 0-9), for its wrap at the end of a string
!lpc = $1DA2       ; lp in 12 px columns, rounded up: the line width the centring code reads
!ysave = $1DA3     ; Y on entry: index of the glyph's (last) byte in [$50]

org $84A993
    JML vwf_draw
    NOP #2

org $84AA2A
    LDA !lpc                ; line lengths for centring (84:A8FA, 20 columns) in 12 px columns, not glyphs

org $84F000
vwf_draw:
    ; in: A = code (single byte) or kanji low byte, $3C = kanji page (0 for single-byte codes); M/X 8-bit
    PHX
    PHY
    PHA
    STY !ysave
    LDA $18B8               ; 0 at each string/line start (84:A87B, A8C6, A983): the redraw after A skips the
    BEQ .moved              ; typewriter (84:A71C) restarts at the same $18BA/$18BB the VWF left
    LDA $18BA
    CMP !col
    BNE .moved
    LDA $18BB
    CMP !rowout
    BEQ .same
.moved:
    LDA $18BB
    STA !row
    STA !rowout
    LDA $18BA
    STA !ocol
    STA $4202
    LDA #12
    STA $4203
    NOP #4
    REP #$20
    LDA $4216
    STA !px
    SEP #$20
.same:
    LDA $18B8               ; the engine zeroes it at each string/line start
    BNE +
    STZ !lpc
    STZ !lp
    STZ !lp+1
+   PLA
    STA !fp
    TAX
    LDA.l vwf_widths,x
    LDY $3C
    BEQ +
    LDA #12                 ; kanji keep the 12 px pitch
+   STA !w
    LDA $3C
    STA !fp+1
    REP #$20
    DEC !fp                 ; glyph index = code - 1
    LDA !fp                 ; font offset = index * 22
    ASL
    STA !ro
    ASL
    ASL
    ADC !ro
    ASL
    ADC !ro
    STA !fp
    SEP #$20
    LDA $18B0
    BIT #$10                ; engine's count-only mode: advance without drawing
    BNE .advance
    JSR vwf_plot
.advance:
    INC $18B8               ; glyph count, as the original: its field padding (84:A897) counts glyphs
    REP #$21                ; lp += w, lpc = lp in 12 px columns rounded up (centring, see 84:AA2A above)
    LDA !w
    AND #$00FF
    ADC !lp
    STA !lp
    STA $4204
    SEP #$20
    LDA #12
    STA $4206
    NOP #8
    LDA $4214
    LDX $4216
    BEQ +
    INC
+   STA !lpc
    REP #$21
    LDA !w
    AND #$00FF
    ADC !px
    STA !px
    SEP #$20
    ; The original wraps to the next strip when its column reaches 10. Mid-string the VWF wraps by pixels instead,
    ; but at the end of a string it keeps the original's wrap: list rows (item name at column 0, count at 8) rely
    ; on it to step down a row.
    INC !ocol
    LDA !ocol
    CMP #10
    BNE .pos
    STZ !ocol
    LDY !ysave
    INY
    LDA [$50],y
    CMP #$FD
    BCC .pos
    REP #$20                ; px = start of the strip after the one holding the last pixel drawn
    LDA !px
    DEC
    STA $4204
    SEP #$20
    LDA #120
    STA $4206
    NOP #8
    LDA $4214
    INC
    STA $4202
    LDA #120
    STA $4203
    NOP #4
    REP #$20
    LDA $4216
    STA !px
    SEP #$20
.pos:
    JSR vwf_pos
    LDA #$00                ; B = 0 on return, as the original draw leaves it: the typewriter's next
    XBA                     ; JSL $809DB2 (84:A856) takes its DMA size from 16-bit A
    PLY
    PLX
    JML $84AA16             ; CLC : RTS, as after the original draw

vwf_pos:
    ; $18BA/$18BB (and the VWF's copies) from px: the strip and column where the next glyph starts. M/X 8-bit
    REP #$20
    LDA !px
    STA $4204
    SEP #$20
    LDA #12
    STA $4206
    NOP #8
    LDA $4214               ; q = px / 12: strip q / 10, column q % 10 (+1 if px is inside a cell)
    LDX #$00
-   CMP #10
    BCC +
    SBC #10
    INX
    INX
    BRA -
+   LDY $4216
    BEQ .edge
    INC
    BRA .set
.edge:                      ; px on a strip edge: column 10 of the strip before, as the original leaves a full
    CMP #$00                ; strip (a full line then {br} stepped down two lines: battle_A5CDF0)
    BNE .set
    CPX #$00
    BEQ .set
    LDA #10
    DEX
    DEX
.set:
    STA $18BA
    STA !col
    TXA
    CLC
    ADC !row
    STA $18BB
    STA !rowout
    SEP #$30
    RTS

; ---- control codes ----
; The engine's F8 cc table (84:AA39: handler, argc per even cc) ends at cc 1E with code right after it, so both
; readers (the draw dispatch 84:A967 and the VM's text scanner 81:C942, which skips argc bytes) move to a copy
; with three new codes:
;   F8 20 lo hi bank   jump: read on at that address (the English in free space; a slot keeps its original length)
;   F8 22 lo hi        jump into bank !textbank (slots of 4-5 bytes)
;   F8 24 n            tab: move to the original's column n of this line (sliced menu cells, column layouts)
!textbank = $BA

org $84A967
    JSR (ctl_table,x)
org $81C942
    LDA.l ctl_table+2,x

org $84E000
ctl_table:
    !i = 0
    while !i < 16
        dw read2($84AA39+(!i*4)), read2($84AA3B+(!i*4))
        !i #= !i+1
    endwhile
    dw ctl_jump, 3
    dw ctl_jump16, 2
    dw ctl_tab, 1

ctl_jump:
    ; in: Y = index of the first argument in [$50]; out: Y = index of the next byte to read (the engine's form)
    LDA [$50],y
    PHA
    INY
    LDA [$50],y
    PHA
    INY
    LDA [$50],y
    STA $52
    PLA
    STA $51
    PLA
    STA $50
    LDY #$00
    RTS

ctl_jump16:
    LDA [$50],y
    PHA
    INY
    LDA [$50],y
    STA $51
    PLA
    STA $50
    LDA #!textbank
    STA $52
    LDY #$00
    RTS

ctl_tab:
    LDA [$50],y
    INY
    PHY
    PHA
    LDA $18B8               ; no glyph yet in this line: px counts from the line's strip, as vwf_draw's restart
    BNE +
    LDA $18BB
    STA !row
    STZ !lp
    STZ !lp+1
    STZ !lpc
+   PLA
    STA $4202
    LDX #12
    STX $4203
    NOP #4
    REP #$20
    LDX $4216
    STX !px
    LDX $4217
    STX !px+1
    SEP #$20
-   CMP #10                 ; the original's column for its end-of-string wrap
    BCC +
    SBC #10
    BRA -
+   STA !ocol
    JSR vwf_pos
    INC $18B8               ; not a line start any more: the next glyph goes on from px
    PLY
    RTS

macro plot(j)
    REP #$21
    LDA !B+(<j>*2)
    ADC !ro
    TAX
    SEP #$20
    LDA $18B9
    BEQ ?over
    LDA !G+<j>
    EOR #$FF
    AND !S+<j>
    EOR $7E2000,x
    ORA !G+<j>
    STA !tmp                ; new plane 0
    EOR $7E2000,x
    AND !M+<j>
    EOR $7E2000,x
    STA $7E2000,x
    LDA !tmp
    EOR #$FF
    ORA !G+<j>
    EOR $7E2001,x
    AND !M+<j>
    EOR $7E2001,x
    STA $7E2001,x
    BRA ?done
?over:
    LDA !MC+<j>
    EOR #$FF
    AND $7E2000,x
    ORA !G+<j>
    STA $7E2000,x
    LDA !MC+<j>
    EOR #$FF
    AND $7E2001,x
    ORA !G+<j>
    ORA !S+<j>
    STA $7E2001,x
?done:
endmacro

vwf_plot:
    ; M = w+1 ones from bit 23, shifted right by sh; MC = M & (M >> 1)
    REP #$20
    LDA !px
    AND #$0007
    STA !sh                 ; 16-bit store: $1D86 = 0, so 16-bit LDX !sh below reads sh
    SEP #$20
    STZ !M
    STZ !M+1
    STZ !M+2
    LDX !w
    LDA $18B8               ; first glyph of a string/line in overwrite mode: clear its whole 12 px cell from its
    ORA $18B9               ; first column, as the original's fixed pitch did (config: a key letter redrawn
    STA !tmp                ; over another left the old one's stem, X + A read as K)
    BNE +
    LDX #11
+   INX
-   SEC
    ROR !M
    ROR !M+1
    ROR !M+2
    DEX
    BNE -
    LDX !sh
    BEQ +
-   LSR !M
    ROR !M+1
    ROR !M+2
    DEX
    BNE -
+   LDA !M
    LSR
    AND !M
    STA !MC
    LDA !M
    LSR
    LDA !M+1
    ROR
    AND !M+1
    STA !MC+1
    LDA !M+1
    LSR
    LDA !M+2
    ROR
    AND !M+2
    STA !MC+2
    LDA !tmp
    BNE +
    LDA !M                  ; first glyph: MC = M (12 px from sh)
    STA !MC
    LDA !M+1
    STA !MC+1
    LDA !M+2
    STA !MC+2
+
    ; the three tile offsets: tile t = px/8 .. t+2 through vwf_tiles, plus the line's first strip * 256
    REP #$30
    LDA !row
    AND #$00FF
    XBA
    STA !ro
    LDA !px
    LSR
    LSR
    LSR
    ASL
    TAX
    CLC
    LDA.l vwf_tiles,x
    ADC !ro
    STA !B
    CLC
    LDA.l vwf_tiles+2,x
    ADC !ro
    STA !B+2
    CLC
    LDA.l vwf_tiles+4,x
    ADC !ro
    STA !B+4
    LDY #$0000              ; Y = row * 2
.row:
    LDX !fp
    LDA.l $AE8000,x         ; glyph row, bit 15 = leftmost pixel
    INX
    INX
    STX !fp
    SEP #$20
    STA !G+1
    XBA
    STA !G
    STZ !G+2
    LDX !sh
    BEQ +
-   LSR !G
    ROR !G+1
    ROR !G+2
    DEX
    BNE -
+   LDA !G
    LSR
    STA !S
    LDA !G+1
    ROR
    STA !S+1
    LDA !G+2
    ROR
    STA !S+2
    REP #$20
    TYX
    LDA.l vwf_rows,x
    STA !ro
    PHY
    %plot(0)
    %plot(1)
    %plot(2)
    REP #$30
    PLY
    INY
    INY
    CPY.w #22
    BEQ +
    JMP .row
+
    SEP #$30
    LDA $18B9               ; overwrite mode: also clear the cell's rows above and below the glyph (0-2, 14-15),
    BEQ +                   ; which held another screen's pixels (teal marks over the info menu's "Status")
    RTS
+
    STZ !G
    STZ !G+1
    STZ !G+2
    STZ !S
    STZ !S+1
    STZ !S+2
    REP #$30
    LDY #$0000
-   PHY
    TYX
    LDA.l vwf_edge,x
    STA !ro
    %plot(0)
    %plot(1)
    %plot(2)
    REP #$30
    PLY
    INY
    INY
    CPY.w #10
    BEQ +
    JMP -
+   SEP #$30
    RTS

vwf_edge:                   ; bitmap rows 0-2 (top tile) and 14-15 (bottom tile) of a line
    dw $0000, $0002, $0004, $010C, $010E

; glyph row r -> bitmap row r+3 of a 2-tile-high line
vwf_rows:
    dw $0006, $0008, $000A, $000C, $000E, $0100, $0102, $0104, $0106, $0108, $010A
; tile t of a line -> strip t/15 (+$200 each), tile t%15 (+$10 each)
vwf_tiles:                  ; 8 strips: sliced menus run up to ~34 cells (408 px) in one string
    !s = 0
    while !s < 8
        !t = 0
        while !t < 15
            dw (!s*$200)+(!t*$10)
            !t #= !t+1
        endwhile
        !s #= !s+1
    endwhile
    dw $1000, $1010, $1020   ; a glyph straddling the last strip's end

assert pc() <= $84F000
org $84FF00
vwf_widths:             ; 256 advance widths by code, written by tools/build.py from the font
