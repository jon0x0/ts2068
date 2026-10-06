; General dirty-row compositor. Final stores are compiled into HOME $EB00.
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
 ld hl,clear_table
 call select_loop
 call offset
 ld a,h
 or $a0
 ld h,a
 xor $60
 ld d,a
 ld e,l
 ld a,7
 call $7b80
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
 ld a,(hl)
 inc hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld ($7b87),de
 ld ($7804),a
 out ($f4),a
 ld bc,(newface)
 call offset
 ld a,h
 or $a0
 ld h,a
 xor $60
 ld d,a
 ld e,l
 call $7b86
 ld a,$10
 ld ($7804),a
 out ($f4),a
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
 call $eb00
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
 exx
 ld hl,$eb00
 exx
 call scan_scene
 exx
 ld (hl),$c9
 ld ($78b4),hl
 exx
 ret

; Choose an unrolled row tail; A=width, HL=33-word table. BC preserved.
select_loop:
 add a,a
 ld e,a
 ld d,0
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld ($7b81),de
 ret

next_face_row:
 ld a,l
 sub 7
 ld l,a
 inc h
 ld a,h
 and 7
 jr nz,nfr_attributes
 ld a,l
 add a,32
 ld l,a
 jr c,nfr_attributes
 ld a,h
 sub 8
 ld h,a
nfr_attributes:
 ld a,h
 xor $60
 ld d,a
 ld e,l
 ret

scan_scene:
 ld b,0
scan_row:
; Reserve a full two-plane row before emitting (maximum 320 bytes).
 exx
 ld a,h
 cp $fe
 exx
 jp nc,scene_overflow
 ld l,b
 ld h,$79
 ld c,(hl)
 ld h,$7d
 ld a,(hl)
 sub c
 jr c,scan_next
 jr z,scan_next
 ld hl,scan_table
 call select_loop
 call offset
 ld a,h
 or $40
 ld d,a
 ld e,l
 ld a,h
 or $a0
 ld h,a
 push hl
 push de
 call $7b80
 pop de
 pop hl
 ld a,h
 xor $60
 ld h,a
 ld a,d
 xor $20
 ld d,a
 call $7b80
scan_next:
 inc b
 ld a,b
 cp 192
 jr nz,scan_row
 ret

 INCLUDE "../build/scene-loops.asm"

 INCLUDE "scene-stars.asm"

scene_overflow:
 di
 ld a,2
 out ($fe),a
 halt
 jr scene_overflow
