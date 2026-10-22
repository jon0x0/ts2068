; TS2068 CP/M: COLOR lists schemes; COLOR 0..7 selects ink/paper.
; SCLD FF bits 3..5 select ink; FE border follows its complementary paper. CP/M BDOS function 9 prints messages.
    org $100
    ld a,$ff
    ld (border),a
    ld a,($80)
    or a
    jp z,help
    ld b,a
    ld hl,$81
.leading:
    ld a,(hl)
    inc hl
    cp ' '
    jr nz,.scheme
    djnz .leading
    jp help
.scheme:
    sub '0'
    cp 8
    jp nc,help
    ld (scheme),a
    dec b
    jr z,select
    ld a,(hl)
    cp ' '
    jp nz,help
.spaces:
    inc hl
    dec b
    jr z,select
    ld a,(hl)
    cp ' '
    jr z,.spaces
    sub '0'
    cp 8
    jp nc,help
    ld (border),a
    inc hl
    dec b
    jr z,select
.trailing:
    ld a,(hl)
    cp ' '
    jp nz,help
    inc hl
    djnz .trailing
select:
    ld a,(scheme)
    xor 7
    ld e,a
    ld a,(border)
    cp 8
    jr c,.border
    ld a,e
.border:
    out ($fe),a                  ; standard border = complementary paper
    ld a,(scheme)
    rlca
    rlca
    rlca
    ld e,a
    in a,($ff)
    and $c7
    or e
    out ($ff),a
    ld a,($eff7)
    or a
    jr z,selected
    ld a,($eff5)
    or a
    ld c,64
    jr z,.palette
    ld c,80
.palette:
    ld a,(border)
    ld b,a
    ld a,(scheme)
    call console_palette_with_border
selected:
    ld de,changed
    jr print
help:
    ld de,options
print:
    ld c,9
    call 5
    ret
border: db $ff
scheme: db 7
changed: db 'Color scheme selected.',13,10,'$'
options:
    db 'TS2068 console colors',13,10
    db 'Usage: COLOR n [border]   (both 0 to 7)',13,10
    db 'Number   Text on background',13,10
    db '  0      Black on white',13,10
    db '  1      Blue on yellow',13,10
    db '  2      Red on cyan',13,10
    db '  3      Magenta on green',13,10
    db '  4      Green on magenta',13,10
    db '  5      Cyan on red',13,10
    db '  6      Yellow on blue',13,10
    db '  7      White on black (default)',13,10
    db 'Border defaults to background; optional number overrides.',13,10
    db 'Border: 0 black, 1 blue, 2 red, 3 magenta,',13,10
    db '        4 green, 5 cyan, 6 yellow, 7 white.',13,10,'$'

    include "console_palette.asm"
