; User-requested console width. BIOS descriptor leaves future renderers possible.
    org $100
    ld hl,$effa
    ld de,signature
    ld b,4
.signature:
    ld a,(de)
    cp (hl)
    jp nz,old_bios
    inc de
    inc hl
    djnz .signature
    ld a,($80)
    ld b,a
    ld hl,$81
    or a
    jp z,status
.spaces:
    ld a,(hl)
    cp ' '
    jr nz,.argument
    inc hl
    djnz .spaces
    jp status
.argument:
    ld a,b
    cp 2
    jp c,usage
    ld a,(hl)
    inc hl
    cp '6'
    jr z,.sixty
    cp '8'
    jp nz,usage
    ld a,(hl)
    cp '0'
    jp nz,usage
    ld a,80
    jr .parsed
.sixty:
    ld a,(hl)
    cp '4'
    jp nz,usage
    ld a,64
.parsed:
    ld (requested),a
    inc hl
    dec b
    dec b
    jr z,.change
.trailing:
    ld a,(hl)
    cp ' '
    jp nz,usage
    inc hl
    djnz .trailing
.change:
    ld a,(requested)
    cp 80
    jr nz,.hardware
    ld a,($eff7)
    or a
    call z,probe_video
    ld a,($eff7)
    or a
    jp z,unavailable
.hardware:
    ld bc,$bf3b
    in a,(c)
    ld (selector),a
    ld a,($eff7)
    or a
    jr z,.normal
    in a,($ff)
    rrca
    rrca
    rrca
    and 7
    ld (scheme),a
    ld a,(requested)
    ld c,a
    ld a,(scheme)
    call console_palette
.normal:
    ld a,($eff7)
    or a
    jr nz,.scld
    ld a,(requested)
    cp 64
    jr nz,.scld
    in a,($ff)
    rrca
    rrca
    rrca
    and 7
    xor 7
    out ($fe),a
.scld:
    in a,($ff)
    and $f8
    or 6
    out ($ff),a
    ld hl,($eff8)
    ld a,(requested)
    ld (hl),a
    cp 80
    ld a,0
    jr nz,.flag
    inc a
.flag:
    ld ($eff5),a
    ld a,(selector)
    ld bc,$bf3b
    out (c),a
    ld e,12
    ld c,2
    call 5                       ; clear/reset cursor through the active BIOS
status:
    ld de,current64
    ld hl,($eff8)
    ld a,(hl)
    cp 80
    jr nz,.print
    ld de,current80
.print:
    ld c,9
    call 5
usage:
    ld de,help
print:
    ld c,9
    jp 5
old_bios:
    ld de,need_bios
    jr print
unavailable:
    ld de,no80
    jr print
probe_video:
    ld bc,$bf3b
    in a,(c)
    ld (probe_selector),a
    ld a,$7f
    out (c),a
    call probe_delay
    ld b,$ff
    in a,(c)
    cp $42
    jr nz,.restore
    ld bc,$bf3b
    in a,(c)
    cp $7f
    jr nz,.restore
    ld a,1
    ld ($eff7),a
.restore:
    ld a,(probe_selector)
    ld bc,$bf3b
    out (c),a
    ret
probe_delay:
    push bc
    ld b,64
.wait: djnz .wait
    pop bc
    ret
probe_selector: db 0
signature: db 'COLS'
requested: db 64
selector: db 0
scheme: db 7
current64: db 'Console: 64 columns.',13,10,'$'
current80: db 'Console: 80 columns.',13,10,'$'
help: db 'COLUMNS 64 or COLUMNS 80 selects the console width.',13,10
    db '80 needs a supported renderer (currently PicoVideo).',13,10
    db 'Screen clears; disk files stay unchanged. Restart apps',13,10
    db 'after changing width. Cold boot selects the default.',13,10,'$'
no80: db '80 columns unavailable; current mode kept.',13,10,'$'
need_bios: db 'COLUMNS needs the updated CP/M cartridge.',13,10,'$'

    include "console_palette.asm"
