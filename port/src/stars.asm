; Common-camera star motion from SAM/IRQ.SRC, adapted to TS2068 bitmap.
; Rounded camera byte differences preserve fractional scrolling and reversals.
; Ten stars (SAM/SAMEQUAT NSTARS). White palette; deterministic toroidal wrap
; replaces the original first-wrap randomization and packed-nibble colors.
stars_init:
 ld hl,star_seeds
 ld de,$7d00
 ld bc,50
 ldir
 ret

stars_update:
 ld hl,($7880)
 ld de,128
 add hl,de
 ld a,($7886)
 ld b,a
 ld a,h
 ld ($7886),a
 sub b
 neg
 ld ($7888),a
 ld hl,($7883)
 add hl,de
 ld a,($7887)
 ld b,a
 ld a,h
 ld ($7887),a
 sub b
 ld ($7889),a
; Remove ALL old stars first, avoiding collisions with another new star.
 ld ix,$7d00
 ld iy,$7d80
 ld b,10
stars_erase:
 push bc
 ld l,(ix+2)
 ld h,(ix+3)
 ld (iy+0),l
 ld (iy+1),h
 inc iy
 inc iy
 ld a,h
 or $e0
 ld h,a
 ld a,(ix+4)
 cpl
 and (hl)
 ld (hl),a
; Mirrored background cell; sprite will be recomposed after all star changes.
 res 6,h
 ld (hl),a
 ld de,5
 add ix,de
 pop bc
 djnz stars_erase
; Update the ten coordinates, then add new pixels to both protected buffers.
 ld ix,$7d00
 ld b,10
stars_draw:
 push bc
 ld a,($7889)
 add a,(ix+0)
 ld (ix+0),a
 ld c,a
 ld a,($7888)
 add a,(ix+1)
 cp 192
 jr c,stars_y_ok
 ld b,a
 ld a,($7888)
 bit 7,a
 ld a,b
 jr z,stars_bottom
 add a,192
 jr stars_y_ok
stars_bottom:
 sub 192
stars_y_ok:
 ld (ix+1),a
 ld b,a
 ld a,c
 and 7
 ld e,a
 ld d,0
 ld hl,star_masks
 add hl,de
 ld a,(hl)
 ld (ix+4),a
 srl c
 srl c
 srl c
 call offset
 ld (ix+2),l
 ld (ix+3),h
 ld (iy+0),l
 ld (iy+1),h
 inc iy
 inc iy
 ld a,h
 or $e0
 ld h,a
 ld a,(ix+4)
 or (hl)
 ld (hl),a
 res 6,h
 ld (hl),a
 ld de,5
 add ix,de
 pop bc
 djnz stars_draw
 ret

stars_commit:
 ld ix,$7d80
 ld b,20
stars_commit_cell:
 ld l,(ix+0)
 ld h,(ix+1)
 ld a,h
 or $40
 ld d,a
 ld e,l
 ld a,h
 or $a0
 ld h,a
 ld a,(de)
 xor (hl)
 jr z,stars_unchanged
 ld a,(hl)
 ld (de),a
stars_unchanged:
 inc ix
 inc ix
 djnz stars_commit_cell
 ret

star_masks:
 DB 128,64,32,16,8,4,2,1
star_seeds:
 INCLUDE "../build/star-seeds.asm"
