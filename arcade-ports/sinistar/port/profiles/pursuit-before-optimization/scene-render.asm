; General dirty-row compositor. Final stores are compiled into HOME $E000.
render:
 ld hl,$7900
 ld de,$7901
 ld bc,191
 ld (hl),32
 ldir
 ld hl,$7d00
 ld de,$7d01
 ld bc,191
 ld (hl),0
 ldir
 xor a
 ld (newface+2),a
 ld a,(sx+1)
 sub 24
 jr c,face_hidden
 cp 200
 jr nc,face_hidden
 srl a
 srl a
 srl a
 ld (newface),a
 ld a,126
 ld hl,sy+1
 sub (hl)
 jr c,face_hidden
 cp 40
 jr c,face_hidden
 cp 133
 jr nc,face_hidden
 ld (newface+1),a
 ld a,7
 ld (newface+2),a
face_hidden:
 ld bc,(oldface)
 ld a,(oldface+2)
 ld e,a
 ld d,52
 call mark_rect
 ld bc,(newface)
 ld a,(newface+2)
 ld e,a
 ld d,52
 call mark_rect
 ld bc,(oldxy)
 ld de,$0c03
 call mark_rect
 ld bc,(newxy)
 ld de,$0c03
 call mark_rect
 call scene_stars_update
; Clear dirty rows only, in protected RAM.
 ld b,0
clear_row:
 ld l,b
 ld h,$79
 ld c,(hl)
 ld h,$7d
 ld a,(hl)
 sub c
 jr z,clear_next
 jr c,clear_next
 push af
 call offset
 ld a,h
 or $a0
 ld h,a
 pop af
clear_cell:
 ld (hl),0
 ld d,a
 ld a,h
 xor $60
 ld h,a
 ld (hl),7
 ld a,h
 xor $60
 ld h,a
 ld a,d
 inc l
 dec a
 jr nz,clear_cell
clear_next:
 inc b
 ld a,b
 cp 192
 jr nz,clear_row
; Stars first, then Sinistar, then player. Overlap priority is explicit.
 ld ix,$7e00
 ld b,10
scene_star_pixels:
 ld l,(ix+2)
 ld h,(ix+3)
 ld a,h
 or $a0
 ld h,a
 ld a,(ix+4)
 or (hl)
 ld (hl),a
 ld de,5
 add ix,de
 djnz scene_star_pixels
 ld a,(newface+2)
 or a
 jr z,scene_player
 ld a,(sx+1)
 and 7
 ld l,a
 ld h,0
 ld e,l
 ld d,h
 add hl,hl
 add hl,de
 ld de,faces
 add hl,de
 ld bc,1092
 call stage_sprite
 ld bc,(newface)
 ld a,52
 ld e,7
 call scene_sprite
scene_player:
 ld a,(angle)
 add a,4
 and $f8
 ld e,a
 ld a,(posx+1)
 and 7
 or e
 ld l,a
 ld h,0
 ld e,l
 ld d,h
 add hl,hl
 add hl,de
 ld de,sprites
 add hl,de
 ld bc,108
 call stage_sprite
 ld bc,(newxy)
 ld a,12
 ld e,3
 call scene_sprite
 call compile_scene
ready:
 halt
publish:
 call $e000
 ld hl,(newxy)
 ld (oldxy),hl
 ld hl,(newface)
 ld (oldface),hl
 ld a,(newface+2)
 ld (oldface+2),a
 ret

; BC=(y,xbyte), D=height, E=width; no clipping here, caller validates.
mark_rect:
 ld a,e
 or a
 ret z
mark_row:
 ld l,b
 ld h,$79
 ld a,c
 cp (hl)
 jr nc,mark_max
 ld (hl),a
mark_max:
 ld h,$7d
 ld a,c
 add a,e
 cp (hl)
 jr c,mark_next
 ld (hl),a
mark_next:
 inc b
 dec d
 jr nz,mark_row
 ret

stage_sprite:
 ld a,(hl)
 inc hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ex de,hl
 ld ($7804),a
 out ($f4),a
 ld de,$b800
 cp $30
 jr nz,stage_copy
 ld de,$7c00
stage_copy:
 ldir
 ld a,($7804)
 push af
 ld a,$10
 ld ($7804),a
 out ($f4),a
 pop af
 cp $30
 ret nz
 ld hl,$7c00
 ld de,$b800
 ld bc,108
 ldir
 ret

scene_sprite:
 ld ($78b1),a
 ld a,e
 ld ($78b0),a
 ld de,$b800
ss_row:
 call offset
 ld a,h
 or $a0
 ld h,a
 push bc
 ld a,($78b0)
 ld b,a
ss_cell:
 ld a,(de)
 inc de
 cp 255
 jr z,ss_transparent
 and (hl)
 ld (hl),a
 ld a,(de)
 or (hl)
 ld (hl),a
 inc de
 ld a,h
 xor $60
 ld h,a
 ld a,(de)
 ld (hl),a
 ld a,h
 xor $60
 ld h,a
 jr ss_next
ss_transparent:
 inc de
ss_next:
 inc de
 inc l
 djnz ss_cell
 pop bc
 inc b
 ld a,($78b1)
 dec a
 ld ($78b1),a
 jr nz,ss_row
 ret

compile_scene:
 ld ix,$e000
 ld b,0
compile_row:
 ld l,b
 ld h,$79
 ld c,(hl)
 ld h,$7d
 ld a,(hl)
 sub c
 jr c,compile_next
 jr z,compile_next
 ld ($78b2),a
 call offset
 ld a,h
 or $a0
 ld h,a
compile_cell:
 call emit_bitmap
 ld a,h
 xor $60
 ld h,a
 call emit_attr
 ld a,h
 xor $60
 ld h,a
 inc l
 ld a,($78b2)
 dec a
 ld ($78b2),a
 jr nz,compile_cell
compile_next:
 inc b
 ld a,b
 cp 192
 jr nz,compile_row
 ld (ix+0),$c9
 ld ($78b4),ix
 ret
emit_bitmap:
 ld a,h
 xor $e0
 ld d,a
 jr emit_common
emit_attr:
 ld a,h
 xor $a0
 ld d,a
emit_common:
 ld e,l
 ld a,(de)
 xor (hl)
 ret z
 ld a,ixh
 cp $ff
 jr nz,emit_safe
 ld a,ixl
 cp $fa
 jp nc,scene_overflow
emit_safe:
 ld (ix+0),$21
 ld (ix+1),e
 ld (ix+2),d
 ld (ix+3),$36
 ld a,(hl)
 ld (ix+4),a
 inc ix
 inc ix
 inc ix
 inc ix
 inc ix
 ret
scene_overflow:
 di
 ld a,2
 out ($fe),a
 halt
 jr scene_overflow

 INCLUDE "scene-stars.asm"
