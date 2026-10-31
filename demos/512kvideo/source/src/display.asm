; Standalone 32x24 text renderer, direct HOME screen writes, own 8x8 font.
screen_clear:
        ld hl,$4000
        ld de,$4001
        ld bc,6143
        ld (hl),0
        ldir
        ld hl,$5800
        ld de,$5801
        ld bc,767
        ld (hl),$47
        ldir
        ld hl,$5800
        ld b,64
.header:ld (hl),$4f
        inc hl
        djnz .header
        xor a
        ld (CURSOR_ROW),a
        ld (CURSOR_COL),a
        ret

; D=row E=column, subsequent characters advance to next row automatically.
screen_at:
        ld a,d
        ld (CURSOR_ROW),a
        ld a,e
        ld (CURSOR_COL),a
        ret

screen_puts:
        ld a,(hl)
        or a
        ret z
        inc hl
        call screen_char
        jr screen_puts

screen_char:
        push af
        push bc
        push de
        push hl
        cp 13
        jr z,.newline
        cp 32
        jr c,.replace
        cp 127
        jr c,.valid
.replace:
        ld a,'.'
.valid: sub 32
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,font
        add hl,de
        ex de,hl
        ld a,(CURSOR_ROW)
        cp 24
        jr nc,.done
        ld b,a
        and $18
        add a,$40
        ld h,a
        ld a,b
        and 7
        rrca
        rrca
        rrca
        ld l,a
        ld a,(CURSOR_COL)
        or l
        ld l,a
        ld b,8
.glyph: ld a,(de)
        ld (hl),a
        inc de
        inc h
        djnz .glyph
        ld a,(CURSOR_COL)
        inc a
        cp 32
        jr c,.col
.newline:
        ld a,(CURSOR_ROW)
        inc a
        ld (CURSOR_ROW),a
        xor a
.col:   ld (CURSOR_COL),a
.done:  pop hl
        pop de
        pop bc
        pop af
        ret

screen_hex:
        push af
        rrca
        rrca
        rrca
        rrca
        call .nibble
        pop af
.nibble:and 15
        add a,'0'
        cp '9'+1
        jr c,.out
        add a,7
.out:   jp screen_char

; Highlight B rows beginning at row D, attribute A.
screen_band:
        push bc
        ld c,a
        ld l,d
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,$5800
        add hl,de
        pop de                         ; D=number of rows
.row:   ld b,32
.cell:  ld (hl),c
        inc hl
        djnz .cell
        dec d
        jr nz,.row
        ret

; Active-low matrix. No keyboard ROM, interrupts or system variables.
key_scan:
        ld hl,key_rows
        ld b,8
.row:   ld a,(hl)
        inc hl
        in a,($fe)
        ld c,a
        ld e,5
.bit:   rr c
        jr nc,.found
        inc hl
        dec e
        jr nz,.bit
        djnz .row
        xor a
        ret
.found: ld a,(hl)
        cp 1
        jr z,.modifier
        cp 2
        jr z,.modifier
        cp '0'
        jr z,.delete
        cp ' '
        jr z,.escape
        cp 'M'
        jr z,.period
        ret
.period:ld a,$7f
        in a,($fe)
        bit 1,a
        ld a,'M'
        ret nz
        ld a,'.'
        ret
.modifier:inc hl
        dec e
        jr nz,.bit
        djnz .row
        xor a
        ret
.delete:ld a,$fe
        in a,($fe)
        bit 0,a
        ld a,'0'
        ret nz
        ld a,8
        ret
.escape:ld a,$fe
        in a,($fe)
        bit 0,a
        ld a,' '
        ret nz
        ld a,27
        ret

key_get:
.release:call key_scan
        or a
        jr nz,.release
.press: call key_scan
        or a
        jr z,.press
        ret

key_rows:
        db $fe,1,'Z','X','C','V'
        db $fd,'A','S','D','F','G'
        db $fb,'Q','W','E','R','T'
        db $f7,'1','2','3','4','5'
        db $ef,'0','9','8','7','6'
        db $df,'P','O','I','U','Y'
        db $bf,13,'L','K','J','H'
        db $7f,' ',2,'M','N','B'
