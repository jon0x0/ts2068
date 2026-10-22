; ROM-independent 64x24 console. CPU chunks 2/3 are private DOCK RAM.
; Temporarily expose HOME screen only while drawing; preserve all BIOS regs.
puts:
    ld a,(hl)
    or a
    ret z
    inc hl
    push hl
    ld c,a
    call conout
    pop hl
    jr puts
cls:
    ld a,($eff5)
    or a
    jp nz,video_clear
    ld a,3
    out ($f4),a
    IF BUILD_OLIGER
    ld hl,$4000
    ld bc,$1800
    xor a
    call fill_screen_span
    ld hl,$6000
    ld bc,$1800
    xor a
    call fill_screen_span
    ld hl,$5800
    ld bc,768
    ld a,7
    call fill_screen_span
    ELSE
    ld hl,$4000
    ld de,$4001
    ld bc,$17ff
    ld (hl),0
    ldir
    ld hl,$6000
    ld de,$6001
    ld bc,$17ff
    ld (hl),0
    ldir
    ld hl,$5800
    ld de,$5801
    ld bc,767
    ld (hl),7
    ldir
    ENDIF
    ld a,15
    out ($f4),a
    xor a
    ld (row),a
    ld (col),a
    IF BUILD_TERMINAL
    ld (escape_state),a
    ld (scroll_top),a
    ENDIF
    ret
conout:
    push af
    push bc
    push de
    push hl
    call keypoll
    ld a,c
    ; An inspectable transcript ring in BIOS-owned memory, no host I/O trap.
    ld hl,(logptr)
    ld (hl),a
    inc hl
    ld a,h
    cp $fe
    jr nz,logok
    ld hl,$f800
logok:
    ld (logptr),hl
    IF BUILD_TERMINAL
    ld a,(escape_state)
    or a
    jp nz,terminal_byte
    ld a,c
    cp 27
    jr nz,not_escape
    ld a,1
    ld (escape_state),a
    jp outdone
not_escape:
    cp 26
    jp z,clear
    cp 30
    jr nz,not_home
    xor a
    ld (row),a
    ld (col),a
    jp outdone
not_home:
    ENDIF
    ld a,c
    cp 13
    jp z,cr
    cp 10
    jp z,lf
    cp 8
    jp z,bs
    cp 12
    jp z,clear
    cp 32
    jp c,outdone
    cp 127
    jp nc,outdone
    ld a,($eff5)
    or a
    jr z,bitmap_char
    call video_put
    jp outdone
bitmap_char:
    ld a,c
    sub 32
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,font
    add hl,de
    ex de,hl
    ld a,(row)
    ld c,a
    and $18
    or $40
    ld h,a
    ld a,c
    and 7
    rrca
    rrca
    rrca
    ld l,a
    ld a,(col)
    srl a
    or l
    ld l,a
    ld a,(col)
    and 1
    jr z,evenchar
    set 5,h
evenchar:
    ld a,$13
    out ($f4),a
draw:
    IF BUILD_OLIGER
    DUP 7
    ld a,(de)
    ld (hl),a
    inc de
    inc h
    EDUP
    ld a,(de)
    ld (hl),a
    ELSE
    ld b,8
draw_compact:
    ld a,(de)
    ld (hl),a
    inc de
    inc h
    djnz draw_compact
    ENDIF
    ld a,15
    out ($f4),a
    ld hl,col
    inc (hl)
    ld a,(columns)
    cp (hl)
    jp nz,outdone
    xor a
    ld (col),a
    jp lf
cr:
    xor a
    ld (col),a
    jp outdone
bs:
    ld hl,col
    ld a,(hl)
    or a
    jp z,outdone
    dec (hl)
    jp outdone
clear:
    call cls
    jp outdone
lf:
    ld a,($eff5)
    or a
    jr z,bitmap_lf
    call video_lf
    jp outdone
bitmap_lf:
    ld hl,row
    inc (hl)
    ld a,(hl)
    cp 24
    jp c,outdone
    ; Scroll by character rows using bitmap-aware line copies.
    ld a,3
    out ($f4),a
    xor a
    ld (plane),a
    call scrollplane
    ld a,$20
    ld (plane),a
    call scrollplane
    ld a,15
    out ($f4),a
    ld a,23
    ld (row),a
    jp outdone
    IF BUILD_TERMINAL
; ADM-3A ESC '=' row+32 col+32, with clamped coordinates.
terminal_byte:
    cp 1
    jr nz,terminal_coordinate
    ld a,c
    cp '='
    ld a,0
    jr nz,terminal_state
    ld a,1
    ld (scroll_top),a
    inc a
    jr terminal_state
terminal_coordinate:
    cp 2
    ld a,c
    jr nz,terminal_col
    sub 32
    cp 24
    jr c,terminal_row_ok
    ld a,23
terminal_row_ok:
    ld (row),a
    ld a,3
    jr terminal_state
terminal_col:
    ld a,(columns)
    ld b,a
    ld a,c
    sub 32
    cp b
    jr c,terminal_col_ok
    ld a,b
    dec a
terminal_col_ok:
    ld (col),a
    xor a
terminal_state:
    ld (escape_state),a
    jp outdone
    ENDIF
scrollplane:
    ; Each raster is three 256-byte strips. Copy seven rows as one
    ; contiguous span, then bridge the third boundary explicitly.
    ld a,(plane)
    or $40
    ld h,a
    ld l,0
scroll_raster:
    push hl
    call keypoll
    ld d,h
    ld e,0
    ld bc,224
    IF BUILD_TERMINAL
    ld a,(scroll_top)
    or a
    jr z,scroll_first
    ld e,32
    ld bc,192
scroll_first:
    ENDIF
    ld l,e
    ld a,l
    add a,32
    ld l,a
    call copy_screen_span
    ; DE is the last row of this third. HL advanced to H+1,L=0;
    ; H+7 selects the corresponding raster in the following third.
    ld a,h
    add a,7
    ld h,a
    ld bc,32
    call copy_screen_span
    ld d,h
    ld e,0
    ld bc,224
    call copy_screen_span
    ld a,h
    add a,7
    ld h,a
    ld bc,32
    call copy_screen_span
    ld d,h
    ld e,0
    ld bc,224
    call copy_screen_span
    ; Clear the last 32-byte row; overlapping copies propagate zero.
    ld h,d
    ld l,e
    xor a
    ld (hl),a
    inc de
    ld bc,31
    ldir
    pop hl
    inc h
    ld a,h
    and 7
    jr nz,scroll_raster
    ret
; BC is a positive multiple of 32. LDI takes 16 T states per byte,
; versus 21 for repeating LDIR. Final LDI exposes BC!=0 in P/V.
copy_screen_span:
    DUP 32
    ldi
    EDUP
    jp pe,copy_screen_span
    ret
; Fill a positive multiple of 32 bytes with A, retaining the same fast
; copy body as scrolling. The first group includes the explicitly seeded byte.
    IF BUILD_OLIGER
fill_screen_span:
    ld (hl),a
    ld d,h
    ld e,l
    inc de
    dec bc
    DUP 31
    ldi
    EDUP
    ret po
    jp copy_screen_span
    ENDIF
outdone:
    pop hl
    pop de
    pop bc
    pop af
    ret
; Poll during output/scrolling as well as input; retain typeahead in a FIFO.
const:
    call keypoll
    push hl
    ld a,(qhead)
    ld hl,qtail
    cp (hl)
    pop hl
    ld a,0
    ret z
    dec a
    ret
keypoll:
    push af
    push bc
    push de
    push hl
    call scan
    ld b,a
    ld a,(scanned_id)
    ld hl,held
    cp (hl)
    jr z,nokey
    ld (hl),a
    ld a,b
    or a
    jr z,nokey
    ld a,(qhead)
    ld e,a
    inc a
    and 31
    ld c,a
    ld hl,qtail
    cp (hl)
    jr z,nokey
    ld d,0
    ld hl,keyqueue
    add hl,de
    ld (hl),b
    ld a,c
    ld (qhead),a
nokey:
    pop hl
    pop de
    pop bc
    pop af
    ret
conin:
    call const
    or a
    jr z,conin
    IF BUILD_OLIGER
    ; Disk-change prompts precede console input; discard retained media data.
    call ol_invalidate
    ENDIF
    push hl
    push de
    ld a,(qtail)
    ld e,a
    inc a
    and 31
    ld (qtail),a
    ld d,0
    ld hl,keyqueue
    add hl,de
    ld a,(hl)
    pop de
    pop hl
    ret
scan:
    xor a
    ld (scanned_id),a
    ld bc,$7ffe
    in a,(c)
    and 2
    ld (symbol),a
    ld bc,$fefe
    in a,(c)
    and 1
    ld (shift),a
    ld hl,keymap
    ld d,8
keyrow:
    in a,(c)
    cpl
    and 31
    ld e,a
    ld a,b
    cp $fe
    ld a,e
    jr nz,notcapsrow
    and 30
notcapsrow:
    ld e,a
    ld a,b
    cp $7f
    ld a,e
    jr nz,notsymrow
    and 29
notsymrow:
    or a
    jr nz,keyrow_active
    DUP 5
    inc hl
    EDUP
    jr nextkeyrow
keyrow_active:
    ld e,5
keybit:
    rra
    jr c,found
    inc hl
    dec e
    jr nz,keybit
nextkeyrow:
    rlc b
    dec d
    jr nz,keyrow
    xor a
    ret
found:
    ; A host key event can land between the modifier and character reads
    ; (Fuse Backspace presses Caps+0 together). Discard a torn scan so that
    ; the first queued character is Delete, rather than an unshifted zero.
    ld bc,$fefe
    in a,(c)
    and 1
    ld e,a
    ld a,(shift)
    cp e
    jr nz,scan_changed
    ld bc,$7ffe
    in a,(c)
    and 2
    ld e,a
    ld a,(symbol)
    cp e
    jr nz,scan_changed
    push hl
    ld de,keymap
    or a
    sbc hl,de
    ld a,l
    inc a
    ld (scanned_id),a
    pop hl
    ld bc,$7ffe
    in a,(c)
    and 2
    or a
    jr nz,normalkey
    ld de,symmap-keymap
    add hl,de
    ld a,(hl)
    ret
normalkey:
    ld a,(hl)
    or a
    ret z
    ld e,a
    ld a,(shift)
    or a
    ld a,e
    ret nz
    cp '0'
    jr nz,notdelete
    ld a,8
    ret
notdelete:
    cp 'C'
    ret nz
    ld a,3
    ret
scan_changed:
    xor a
    ret
keymap:
    db 0,"ZXCV","ASDFG","QWERT","12345","09876","POIUY",13,"LKJH"," ",0,"MNB"
symmap:
    db 0,':',96,'?','/','~','|',92,'{','}','Q','W','E','<','>','!','@','#','$','%','_',')','(',39, '&',34,59,'I','U','Y',13,'=','+','-','^',' ',0,'.',',','*'
row: db 0
col: db 0
qhead: db 0
qtail: db 0
keyqueue: ds 32
held: db 0
scanned_id: db 0
shift: db 1
symbol: db 2
plane: db 0
logptr: dw $f800
    IF BUILD_TERMINAL
escape_state: db 0
scroll_top: db 0
    ENDIF
font EQU $8100
    include "picovideo.asm"
