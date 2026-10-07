; Foreground only. HL=78 indices, DE=triple dictionary, C=pixel phase.
; Decode three source cells plus a transparent spill cell per row.
explosion_unpack:
 ld a,c
 ld ($7f44),a
 push de
 pop iy
 push hl
 pop ix
 ld de,$b800
 ld b,26
eu_row:
 push bc
 ld b,3
eu_cell:
 push bc
 ld a,(ix+0)
 inc ix
 ld l,a
 ld h,0
 ld c,a
 ld b,0
 add hl,hl
 add hl,bc
 push iy
 pop bc
 add hl,bc
 ldi
 ldi
 ldi
 pop bc
 djnz eu_cell
 ld a,255
 ld (de),a
 inc de
 xor a
 ld (de),a
 inc de
 inc a
 ld (de),a
 inc de
 pop bc
 djnz eu_row
 ld a,($7f44)
 or a
 ret z
 call eu_phase_four
 or a
 jr z,eu_colors
eu_shift:
 ld ix,$b800
 ld de,12
 ld b,26
eu_shift_row:
 scf
 rr (ix+0)
 rr (ix+3)
 rr (ix+6)
 rr (ix+9)
 or a
 rr (ix+1)
 rr (ix+4)
 rr (ix+7)
 rr (ix+10)
 add ix,de
 djnz eu_shift_row
 dec c
 jr nz,eu_shift
eu_colors:
 ; Propagate the preceding cell palette into transparent spill cells.
 ld ix,$b800
 ld de,3
 ld b,26
eu_color_row:
 push bc
 ld b,4
 ld c,7
eu_color:
 ld a,(ix+0)
 cp 255
 jr z,eu_color_next
 ld a,(ix+2)
 cp 1
 jr nz,eu_color_keep
 ld a,c
 ld (ix+2),a
eu_color_keep:
 ld c,a
eu_color_next:
 add ix,de
 djnz eu_color
 pop bc
 djnz eu_color_row
 ret

worker_impact_origin:
 ld a,(worker_x)
 sub 5
 ld (worker_x),a
 ld a,($7c98)
 sbc a,0
 and 1
 ld ($7c98),a
 ld a,(worker_y)
 sub 7
 ld (worker_y),a
 ld a,($7c99)
 sbc a,0
 and 1
 ld ($7c99),a
 ret
