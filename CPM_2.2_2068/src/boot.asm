; AROS entry in DOCK chunk 4. Copy loader into HOME before changing mapping.
    include "../build/disk-layout.inc"
    org $8000
    db 2,2
    dw entry
    db $ef,1,0,0
entry:
    di
    ld sp,$7fff
    xor a
    out ($ff),a
    ld a,$10
    out ($f4),a
    ld hl,loader_image
    ld de,$5b00
    ld bc,loader_end-loader_image
    ldir
    jp $5b00
loader_image:
    disp $5b00
loader:
    jp loader_start
    IF BUILD_DUAL
    jp boot_modern
    ENDIF
loader_start:
    xor a
    ld ($eff4),a
    IF BUILD_OLIGER
    ld a,(8)             ; release Board B before writing/testing low DOCK RAM
    ENDIF
    ld a,$23             ; low RAM and source chunk 5, destination stays HOME
    out ($f4),a
    ld hl,$a000
    ld de,$d000
    ld bc,$2000
    ldir
    ld a,$43
    out ($f4),a
    ld hl,$c000
    ld de,$f000
    ld bc,$1000
    ldir
    IF BUILD_BANKED
    ld a,$80
    out ($f4),a
    ld hl,$e000
    ld de,$8000
    ld bc,$2000
    ldir
    ld a,3
    out ($f4),a
    ENDIF
    ; Exhaustive address-derived patterns in both low RAM pages.
    ld hl,0
fill:
    ld a,h
    xor l
    xor $a5
    ld (hl),a
    inc hl
    bit 6,h
    jr z,fill
    ld hl,0
check:
    ld a,h
    xor l
    xor $a5
    cp (hl)
    jp nz,fail
    inc hl
    bit 6,h
    jr z,check
    ld a,$03             ; BIOS maps screen shadows after leaving loader
    out ($f4),a
    ld a,$a5
    ld ($eff0),a
    jp $e600
fail:
    ld ($eff2),hl
    ld a,2
    out ($fe),a
    halt
    jr fail
    IF BUILD_DUAL
; Fixed $5B03 entry. Copy the modern BIOS from immutable cartridge ROM,
; not the TPA: it must survive programs and subsequent cartridge restarts.
boot_modern:
    ld sp,$7f00
    ld a,$13
    out ($f4),a
    ld hl,$8400
    ld de,$e600
    ld bc,$1a00
    ldir
    ld a,$a5
    ld ($eff0),a
    ld a,2
    ld ($eff3),a
    xor a
    ld ($eff4),a
    jp $e600
    ENDIF
    ent
loader_end:
