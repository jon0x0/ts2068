; Protected compositor with threaded row publication at $EB00 and a guarded
; changed-byte fallback at $F000. Only final differing display bytes are written.
render:
 xor a
 ld ($78ed),a
 exx
 ld hl,$eb00
 exx
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
 ld hl,$00ff
 ld ($78c0),hl
 ld ($78c2),hl
 ld ($78c4),hl
 ld bc,(oldface)
 ld a,(oldface+2)
 ld e,a
 ld d,52
 call union_rect
 call union_face_color
 ld bc,(newface)
 ld a,(newface+2)
 ld e,a
 ld d,52
 call union_rect
 call union_face_color
 ld hl,($78c0)
 ld ($78e0),hl
 ld hl,($78c2)
 ld ($78e2),hl
 ld bc,(oldxy)
 ld de,$0c03
 call union_rect
 call union_color
 ld bc,(newxy)
 ld de,$0c03
 call union_rect
 call union_color
 call separated_bounds
 ld ($78d6),a
 or a
 jr z,shared_bounds
 call select_relative_transition
 ld a,2
 ld ($78c6),a
 jp erase_start
shared_bounds:
 ld a,($78c1)
 ld hl,$78c0
 sub (hl)
 cp 11
 jr nc,slow_bounds
 ld a,($78c3)
 ld hl,$78c2
 sub (hl)
 cp 65
 jr nc,slow_bounds
 ld a,1
 ld ($78c6),a
 jr erase_start
slow_bounds:
 xor a
 ld ($78c6),a
 call rebuild_bounds
 jr erase_start
rebuild_bounds:
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
 ret
erase_start:
 ld bc,(oldface)
 ld a,(oldface+2)
 or a
 jr z,no_old_face
 call offset
 ld a,h
 or $a0
 ld h,a
 xor $60
 ld d,a
 ld e,l
 call erase_face
no_old_face:
 ld bc,(oldxy)
 ld de,$0c03
 call clear_rect
 call scene_stars_update
; Emit the twenty star cells separately; never stretch sprite rows to distant stars.
list_start:
 ld ix,$b900
 call emit_stars
 ld ix,$7e00
 call emit_stars
 ld a,($78c6)
 cp 2
 jp z,separated_list
 or a
 jp nz,fast_list
 ld a,($78c2)
 ld b,a
clear_row:
 ld a,($78c6)
 or a
 jr z,list_slow_row
 ld a,($78c0)
 ld c,a
 ld a,($78c1)
 sub c
 jr list_width
list_slow_row:
 ld l,b
 ld h,$79
 ld c,(hl)
 ld h,$7d
 ld a,(hl)
 sub c
 jr z,clear_next
 jr c,clear_next
list_width:
 ld hl,scan_table
 push af
 ld a,($78c4)
 cp b
 jr z,list_color
 jr nc,list_mono
 ld a,($78c5)
 cp b
 jr z,list_mono
 jr nc,list_color
list_mono:
 ld hl,mono_table
list_color:
 pop af
 call select_loop
 call offset
 ld a,h
 or $a0
 ld h,a
 call emit_row
clear_next:
 inc b
 ld a,($78c3)
 cp b
 jr nz,clear_row
list_done:
 exx
 ld ($78b4),hl
 ld de,publication_done
 ld (hl),e
 inc hl
 ld (hl),d
 exx
composition_start:
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
 ld ($78b6),sp
 ld a,($78d0)
 or a
 jr nz,publication_delta
 ld a,($78d6)
 or a
 call nz,$f000
 ld sp,$eb00
 ret
publication_delta:
 call $f000
publication_done:
 ld a,(sx+1)
 and 7
 ld ($78ee),a
 ld sp,($78b6)
 ei
 ld hl,(newxy)
 ld (oldxy),hl
 ld hl,(newface)
 ld (oldface),hl
 ld a,(newface+2)
 ld (oldface+2),a
 ret

union_rect:
 ld a,e
 or a
 ret z
 ld hl,$78c0
 ld a,c
 cp (hl)
 jr nc,ur_right
 ld (hl),a
ur_right:
 inc hl
 add a,e
 cp (hl)
 jr c,ur_y
 ld (hl),a
ur_y:
 inc hl
 ld a,b
 cp (hl)
 jr nc,ur_bottom
 ld (hl),a
ur_bottom:
 inc hl
 add a,d
 cp (hl)
 ret c
 ld (hl),a
 ret
union_face_color:
 ld a,e
 or a
 ret z
 push bc
 push de
 ld a,b
 add a,12
 ld b,a
 ld d,36
 call union_color
 pop de
 pop bc
 ret
union_color:
 ld hl,$78c4
 ld a,b
 cp (hl)
 jr nc,uc_bottom
 ld (hl),a
uc_bottom:
 inc hl
 add a,d
 cp (hl)
 ret c
 ld (hl),a
 ret

fast_list:
 ld a,($78c1)
 ld hl,$78c0
 sub (hl)
 push af
 ld hl,scan_table
 call select_loop
 ld ($78ca),de
 pop af
 ld hl,mono_table
 call select_loop
 ld ($78c8),de
 ld a,($78c0)
 ld c,a
 ld a,($78c2)
 ld b,a
 call offset
 ld a,h
 or $a0
 ld h,a
 ld a,($78c4)
 ld de,$78c2
 ex de,hl
 sub (hl)
 ex de,hl
 ld b,a
 call fl_rows
 ld de,($78ca)
 ld ($7b81),de
 ld a,($78c5)
 ld de,$78c4
 ex de,hl
 sub (hl)
 ex de,hl
 ld b,a
 call fl_rows
 ld de,($78c8)
 ld ($7b81),de
 ld a,($78c3)
 ld de,$78c5
 ex de,hl
 sub (hl)
 ex de,hl
 ld b,a
 call fl_rows
 jp list_done
fl_rows:
 ld a,b
 or a
 ret z
fl_row:
 push hl
 exx
 pop de
 ld bc,($7b81)
 ld (hl),c
 inc hl
 ld (hl),b
 inc hl
 ld (hl),e
 inc hl
 ld a,d
 xor $e0
 ld (hl),a
 inc hl
 ld (hl),e
 inc hl
 ld (hl),d
 inc hl
 exx
 inc h
 ld a,h
 and 7
 jr nz,fl_next
 ld a,l
 add a,32
 ld l,a
 jr c,fl_next
 ld a,h
 sub 8
 ld h,a
fl_next:
 djnz fl_row
 ret

clear_rect:
 ld a,e
 or a
 ret z
 push de
 ld hl,clear_table
 call select_loop
 pop de
cr_row:
 push de
 call offset
 ld a,h
 or $a0
 ld h,a
 xor $60
 ld d,a
 ld e,l
 ld a,7
 call $7b80
 pop de
 inc b
 dec d
 jr nz,cr_row
 ret

emit_stars:
 ld b,10
 ld hl,star_publish
 ld ($7b81),hl
es_loop:
 ld l,(ix+2)
 ld a,(ix+3)
 or $a0
 ld h,a
 call emit_row
 ld de,5
 add ix,de
 djnz es_loop
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
 ld a,($78d6)
 or a
 jr z,compile_shared
 call separated_attributes
 call separated_budget
 jr compile_selected
compile_shared:
 call check_budget
compile_selected:
 ld ($78d0),a
 or a
 ret z
 call rebuild_bounds
 ld iy,$b900
 call mark_stars
 ld iy,$7e00
 call mark_stars
 exx
 ld hl,$f000
 exx
 ld b,0
fallback_row:
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
 jr z,fallback_next
 jr c,fallback_next
 ld hl,delta_table
 call select_loop
 call offset
 ld a,h
 or $a0
 ld h,a
 xor $e0
 ld d,a
 ld e,l
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
fallback_next:
 inc b
 ld a,b
 cp 192
 jr nz,fallback_row
 exx
 ld (hl),$c9
 ld ($78d4),hl
 exx
 ret
fallback_byte:
 ld a,(hl)
 push de
 exx
 pop de
 ld (hl),$21
 inc hl
 ld (hl),e
 inc hl
 ld (hl),d
 inc hl
 ld (hl),$36
 inc hl
 ld (hl),a
 inc hl
 exx
 ret
mark_stars:
 ld b,10
ms_loop:
 push bc
 ld a,(iy+0)
 srl a
 srl a
 srl a
 ld c,a
 ld b,(iy+1)
 ld de,$0101
 call mark_rect
 ld de,5
 add iy,de
 pop bc
 djnz ms_loop
 ret

; Worst-case publication bound: 36 T per changed byte, 40/116 T row overhead,
; 2,000 T star/entry allowance, and a further 1,024 T margin before the beam.
check_budget:
 ld a,($78c6)
 or a
 jr z,budget_slow
 ld a,($78c1)
 ld hl,$78c0
 sub (hl)
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 ld de,row_costs
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 inc hl
 push hl
 ld a,($78c3)
 ld hl,$78c2
 sub (hl)
 ld b,a
 call scale_cost
 ld ($78d2),hl
 pop hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld a,($78c5)
 ld hl,$78c3
 cp (hl)
 jr c,budget_top
 ld a,(hl)
budget_top:
 ld b,a
 ld a,($78c4)
 ld hl,$78c2
 cp (hl)
 jr nc,budget_height
 ld a,(hl)
budget_height:
 ld c,a
 ld a,b
 sub c
 ld b,a
 call scale_cost
 ld de,($78d2)
 add hl,de
 ld de,3024
 add hl,de
 push hl
 ld a,($78c3)
 add a,39
 ld b,a
 ld de,224
 call scale_cost
 pop de
 or a
 sbc hl,de
 jr c,budget_slow
 xor a
 ret
budget_slow:
 ld a,1
 ret
scale_cost:
 ld hl,0
 ld a,b
 ld b,8
sc_loop:
 srl a
 jr nc,sc_skip
 add hl,de
sc_skip:
 sla e
 rl d
 djnz sc_loop
 ret
row_costs:
 INCLUDE "../build/scene-costs.asm"

; Threaded publication records: handler, display pointer, shadow pointer.
emit_row:
 push hl
 exx
 pop de
 ld bc,($7b81)
 ld (hl),c
 inc hl
 ld (hl),b
 inc hl
 ld (hl),e
 inc hl
 ld a,d
 xor $e0
 ld (hl),a
 inc hl
 ld (hl),e
 inc hl
 ld (hl),d
 inc hl
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

erase_face:
 push hl
 push de
 ld hl,erase_source
 ld a,(hl)
 inc hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld ($7b87),de
 ld ($7804),a
 out ($f4),a
 pop de
 pop hl
 call $7b86
 ld a,$10
 ld ($7804),a
 out ($f4),a
 ret
erase_source:
 INCLUDE "../build/erase-pointer.asm"
 INCLUDE "scene-relative.asm"
 INCLUDE "scene-separated.asm"
 INCLUDE "../build/scene-loops.asm"

 INCLUDE "scene-stars.asm"

scene_overflow:
 di
 ld a,2
 out ($fe),a
 halt
 jr scene_overflow
