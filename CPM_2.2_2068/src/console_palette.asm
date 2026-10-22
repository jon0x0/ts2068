; Transient-only PicoVideo palette setup. A=scheme, C=64 or 80.
; Requires the inspected extension capability. Does not change BIOS width flags.
console_palette:
    ld b,$ff
console_palette_with_border:
    ld (pal_scheme),a
    ld a,b
    ld (pal_border),a
    ld a,c
    cp 64
    ld a,5
    jr nz,.mode
    inc a
.mode:
    ld (pal_mode),a
    ld bc,$bf3b
    in a,(c)
    ld (pal_selector),a
    ld a,(pal_scheme)
    call pal_rgb
    ld d,7
    ld a,(pal_mode)
    cp 6
    jr nz,.ink
    ld a,(pal_scheme)
    ld d,a
.ink:
    call pal_write
    ld a,(pal_mode)
    cp 6
    jr nz,.paper
    ; Cover both the erroneous mode-bit ink OR and a corrected firmware.
    ld a,(pal_scheme)
    or 1
    ld d,a
    call pal_write
.paper:
    ld a,(pal_scheme)
    xor 7
    call pal_rgb
    ld d,8
    ld a,(pal_mode)
    cp 6
    jr nz,.paper_write
    ld a,(pal_scheme)
    xor 7
    or 8
    ld d,a
.paper_write:
    call pal_write
    ld a,(pal_border)
    cp 8
    jr nc,.border_rgb
    call pal_rgb
.border_rgb:
    ld d,0
    ld a,(pal_mode)
    cp 6
    jr nz,.border
    ld a,(pal_scheme)
    or a
    jr nz,.border
    ld d,2                       ; ink entries 0/1 are black for scheme 0
.border:
    call pal_write               ; E still contains paper RGB
    ld a,d
    out ($fe),a
    ld de,$4300
    call pal_write
    ld a,(pal_mode)
    ld e,a
    ld d,$41
    call pal_write
    ld de,$4001
    call pal_write
    ld a,(pal_selector)
    ld bc,$bf3b
    out (c),a
    ret
pal_rgb:
    ld l,a
    ld h,0
    ld de,pal_colors
    add hl,de
    ld e,(hl)
    ret
pal_write:
    ld bc,$bf3b
    out (c),d
    ld b,32
.wait: djnz .wait
    ld b,$ff
    out (c),e
    ret
pal_border: db $ff
pal_scheme: db 7
pal_mode: db 5
pal_selector: db 0
pal_colors: db 0,2,$10,$12,$80,$82,$90,$92
