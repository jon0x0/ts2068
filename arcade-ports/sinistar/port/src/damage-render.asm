; Erase removed source-piece rectangles in shadow before composing actors.
; HOME 7F45 column, 7F46 row count, 7F47 piece count, 7F50..53 masks.
damage_render:
 ld a,(bs_hits)
 or a
 ret z
 cp 13
 ret nc
 ld ($7f47),a
 ld a,(rects+22)
 or a
 ret z
 ld ix,damage_pieces
dr_piece:
 ld a,(face_x+1)
 ld l,a
 ld a,($7cba)
 neg
 ld h,a
 ld e,(ix+0)
 ld d,0
 add hl,de
 ld a,l
 and 7
 ld c,a
 sra h
 rr l
 sra h
 rr l
 sra h
 rr l
 ld a,l
 ld ($7f45),a
 ld hl,$7f50
 ld (hl),255
 inc hl
 ld (hl),255
 inc hl
 ld (hl),255
 ld hl,$7f50
 ld a,$80
 inc c
dr_phase:
 dec c
 jr z,dr_mask_ready
 srl a
 jr dr_phase
dr_mask_ready:
 ld e,a
 ld b,(ix+2)
dr_mask:
 ld a,e
 cpl
 and (hl)
 ld (hl),a
 srl e
 jr nz,dr_mask_next
 inc hl
 ld e,$80
dr_mask_next:
 djnz dr_mask
 ld a,(face_y+1)
 ld l,a
 ld a,($7cbb)
 neg
 ld h,a
 ld e,(ix+1)
 ld d,0
 add hl,de
 ld a,(ix+3)
 ld ($7f46),a
 ; Clip the vertical run once; then clear columns with scanline stepping.
 ld a,h
 or a
 jp nz,dr_next_piece
 ld a,l
 cp 176
 jp nc,dr_next_piece
 cp 64
 jr nc,dr_bottom
 ld a,($7f46)
 add a,l
 sub 64
 jp c,dr_next_piece
 jp z,dr_next_piece
 ld ($7f46),a
 ld l,64
dr_bottom:
 ld a,176
 sub l
 ld b,a
 ld a,($7f46)
 cp b
 jr c,dr_height
 ld a,b
 ld ($7f46),a
dr_height:
 ld b,l
 ld a,($7f45)
 ld c,a
 ld iy,$7f50
 ld a,3
 ld ($7f48),a
dr_column:
 ld a,c
 cp 32
 jr nc,dr_next_column
 ld a,(iy+0)
 cp 255
 jr z,dr_next_column
 push bc
 ld e,a
 call offset
 ld a,h
 or $a0
 ld h,a
 ld a,($7f46)
 ld d,a
dr_pixels:
 ld a,(hl)
 and e
 ld (hl),a
 jr nz,dr_step
 ld a,h
 xor $60
 ld h,a
 ld (hl),7
 xor $60
 ld h,a
dr_step:
 inc h
 ld a,h
 and 7
 jr nz,dr_scanline
 ld a,l
 add a,32
 ld l,a
 jr c,dr_scanline
 ld a,h
 sub 8
 ld h,a
dr_scanline:
 dec d
 jr nz,dr_pixels
 pop bc
dr_next_column:
 inc c
 inc iy
 ld a,($7f48)
 dec a
 ld ($7f48),a
 jr nz,dr_column
dr_next_piece:
 ld de,4
 add ix,de
 ld a,($7f47)
 dec a
 ld ($7f47),a
 jp nz,dr_piece
 ret
