; Fletcher-16 of BC bytes at HL; result DE, sums modulo 255.
; An end-around carry permits FF as zero internally; normalize at the end.
page_checksum:
    ld de,0
.byte:
    ld a,(hl)
    add a,e
    adc a,0
    ld e,a
    add a,d
    adc a,0
    ld d,a
    inc hl
    dec bc
    ld a,b
    or c
    jr nz,.byte
    ld a,e
    inc a
    jr nz,.high
    ld e,0
.high:
    ld a,d
    inc a
    ret nz
    ld d,0
    ret
