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

org $84A993
    JML vwf_draw
    NOP #2

org $84F000
vwf_draw:
    ; in: A = code (single byte) or kanji low byte, $3C = kanji page (0 for single-byte codes); M/X 8-bit
    PHX
    PHY
    PHA
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
    REP #$21
    LDA !w
    AND #$00FF
    ADC !px
    STA !px
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
    BEQ +
    INC
+   STA $18BA
    STA !col
    TXA
    CLC
    ADC !row
    STA $18BB
    STA !rowout
    ; $18B8 = the line's width so far in 12 px columns, rounded up: the engine centres lines (84:A8FA, from 20
    ; columns) and pads fields to $18B7 columns (84:A897) with it, both by the original's 12 px count
    REP #$21
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
+   STA $18B8
    SEP #$30
    LDA #$00                ; B = 0 on return, as the original draw leaves it: the typewriter's next
    XBA                     ; JSL $809DB2 (84:A856) takes its DMA size from 16-bit A
    PLY
    PLX
    JML $84AA16             ; CLC : RTS, as after the original draw

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
    INX
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
    RTS

; glyph row r -> bitmap row r+3 of a 2-tile-high line
vwf_rows:
    dw $0006, $0008, $000A, $000C, $000E, $0100, $0102, $0104, $0106, $0108, $010A
; tile t of a line -> strip t/15 (+$200 each), tile t%15 (+$10 each)
vwf_tiles:
    dw $0000, $0010, $0020, $0030, $0040, $0050, $0060, $0070, $0080, $0090, $00A0, $00B0
    dw $00C0, $00D0, $00E0, $0200, $0210, $0220, $0230, $0240, $0250, $0260, $0270, $0280
    dw $0290, $02A0, $02B0, $02C0, $02D0, $02E0, $0400, $0410, $0420, $0430, $0440, $0450
    dw $0460, $0470, $0480, $0490, $04A0, $04B0, $04C0, $04D0, $04E0, $0600, $0610, $0620

assert pc() <= $84FF00
org $84FF00
vwf_widths:             ; 256 advance widths by code, written by tools/build.py from the font
