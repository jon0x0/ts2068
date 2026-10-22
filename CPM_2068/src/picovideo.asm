; PicoVideo 4.2 extension: 80x24 character RAM at HOME 4000,
; 1920 attributes at HOME 4780. Do not use its disabled text-port parser.
video_init:
    xor a
    ld ($eff5),a
    ld ($eff7),a
    ld a,64
    ld (columns),a
    ld bc,$bf3b
    in a,(c)
    push af
    ld a,$7f
    out (c),a
    ex (sp),hl
    ex (sp),hl ; preserve HL; let the Pico finish register selection
    ld b,$ff
    in a,(c)
    cp $42
    jr nz,video_absent
    ld bc,$bf3b
    ld a,$41
    out (c),a
    ex (sp),hl
    ex (sp),hl
    in a,(c)
    cp $41
    jr nz,video_absent
    ; Only enable the inspected 4.2 layout, not an arbitrary ULA+ device.
    ld de,$4300
    call video_reg
    ld de,$0792
    call video_reg
    ld de,$0800
    call video_reg
    ld de,$4105
    call video_reg
    ld de,$4001
    call video_reg
    ld a,80
    ld (columns),a
    ld hl,$eff5
    inc (hl)
    inc hl
    inc hl
    inc (hl)
video_absent:
    pop af
    ld bc,$bf3b
    out (c),a
    ret
video_reg:
    ld bc,$bf3b
    out (c),d
    ld b,16
.wait: djnz .wait
    ld b,$ff
    out (c),e
    ret
video_clear:
    ld a,3
    out ($f4),a
    ld hl,$4000
    ld de,$4001
    ld bc,1919
    ld (hl),' '
    ldir
    ld hl,$4780
    ld de,$4781
    ld bc,1919
    ld (hl),7
    ldir
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
video_put:
    ld a,(row)
    ld l,a
    ld h,0
    ld e,a
    ld d,0
    add hl,hl
    add hl,hl
    add hl,de
    DUP 4
    add hl,hl
    EDUP
    ld de,$4000
    add hl,de
    ld a,(col)
    ld e,a
    ld d,0
    add hl,de
    ld a,3
    out ($f4),a
    ld (hl),c
    ld a,15
    out ($f4),a
    ld hl,col
    inc (hl)
    ld a,(hl)
    cp 80
    ret c
    xor a
    ld (hl),a
    ; fall through for automatic line wrap
video_lf:
    ld hl,row
    inc (hl)
    ld a,(hl)
    cp 24
    ret c
    ld (hl),23
    call keypoll
    ld de,$4000
    ld hl,$4050
    ld bc,1840
    IF BUILD_TERMINAL
    ld a,(scroll_top)
    or a
    jr z,video_scroll
    ld de,$4050
    ld hl,$40a0
    ld bc,1760
    ENDIF
video_scroll:
    ld a,3
    out ($f4),a
    ldir
    ex de,hl
    ld (hl),' '
    ld d,h
    ld e,l
    inc de
    ld bc,79
    ldir
    ld a,15
    out ($f4),a
    ret
columns: db 64
video_notice:
    ld hl,video_64_message
    ld a,($eff5)
    or a
    jr z,.print
    ld hl,video_80_message
.print:
    jp puts
video_64_message: db 'TS2068 64 columns',13,10,0
video_80_message: db 'PicoVideo 80 columns',13,10,0
