; Byte-exact four-pixel right shift, avoiding four indexed bit-shift passes.
; Runs after explosion unpack, before remaining 0..3 bit shifts and colors.
eu_phase_four:
 ld c,a
 cp 4
 ret c
 push bc
 ld hl,$b800
 ld b,26
eu_nibble_row:
 push hl
 ld a,15
 DUP 4
 rrd
 inc hl
 inc hl
 inc hl
 EDUP
 pop hl
 inc hl
 xor a
 DUP 4
 rrd
 inc hl
 inc hl
 inc hl
 EDUP
 dec hl
 djnz eu_nibble_row
 pop bc
 ld a,c
 and 3
 ld c,a
 ret
