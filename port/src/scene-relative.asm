; Relative color-cell transition lists for dx/dy in -1..1, all eight phases.
; Only used when BOTH old/new envelopes are separate from the player.
select_relative_transition:
 ld a,(oldface+2)
 or a
 ret z
 ld a,(newface+2)
 or a
 ret z
 ld a,(newface)
 ld hl,oldface
 sub (hl)
 add a,a
 add a,a
 add a,a
 ld c,a
 ld a,(sx+1)
 and 7
 add a,c
 ld hl,$78ee
 sub (hl)
 inc a
 cp 3
 jr nc,rf_miss
 ld c,a
 ld a,(newface+1)
 ld hl,oldface+1
 sub (hl)
 inc a
 cp 3
 jr nc,rf_miss
 ld e,a
 add a,a
 add a,e
 add a,c
 ld c,a
 ld a,($78ee)
 ld e,a
 add a,a
 add a,a
 add a,a
 add a,e
 add a,c
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 ld de,relative_pointers
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 inc hl
 ld ($78f0),de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld ($78f2),de
 ld a,(oldface)
 ld c,a
 ld a,(newface)
 cp c
 jr nc,rt_base
 ld c,a
rt_base:
 ld a,c
 ld ($78f4),a
 ld a,(oldface+1)
 dec a
 ld ($78f5),a
 ld a,1
 ld ($78ed),a
 ret
rf_miss:
 xor a
 ret

relative_face_attributes:
 ld a,($78ed)
 or a
 ret z
 ld iy,($78f0)
 ld b,(iy+0)
 inc iy
 ld a,b
 or a
 jr z,rf_done
rf_row:
 push bc
 ld a,(oldface+1)
 add a,(iy+0)
 ld b,a
 ld a,(oldface)
 ld c,a
 call offset
 ld a,h
 or $c0
 ld h,a
 xor $a0
 ld d,a
 ld e,l
 ld c,(iy+1)
 inc iy
 inc iy
 ld b,8
rf_cell:
 srl c
 call c,fallback_byte
 inc l
 inc e
 djnz rf_cell
 pop bc
 djnz rf_row
rf_done:
 ld a,1
 ret

; RLE rows of precomputed bitmap-change spans, relocated from the old origin.
; Stars are already in the publication list and repair changing background holes.
relative_bitmap_list:
 ld iy,($78f2)
 ld b,(iy+0)
 inc iy
rb_run:
 push bc
 ld a,(iy+0)
 ld ($78f6),a
 ld a,(iy+1)
 or a
 jr z,rb_advance
 and 15
 ld c,a
 ld a,($78f4)
 add a,c
 ld c,a
 ld a,($78f5)
 ld b,a
 ld a,(iy+1)
 rrca
 rrca
 rrca
 rrca
 and 15
 ld hl,mono_table
 call select_loop
 call offset
 ld a,h
 or $a0
 ld h,a
 ld a,($78f6)
 ld b,a
 call fl_rows
rb_advance:
 ld a,($78f6)
 ld hl,$78f5
 add a,(hl)
 ld (hl),a
 inc iy
 inc iy
 pop bc
 djnz rb_run
 ret
relative_pointers:
 INCLUDE "../build/relative-pointers.asm"
