 INCLUDE "../build/world-equ.asm"
 ORG render_extension
 jp inc_prepare
 jp inc_mark_eyes
 jp inc_draw
 jp inc_restore
 jp inc_border
 jp inc_flash
 jp damage_render
 ret
 nop
 nop
 jp inc_assembly_draw
 jp inc_ship
 jp inc_cached_face
 jp inc_mouth_four
 jp inc_speaking_face
inc_prepare:
 ld hl,effects_origin+3
 call inc_effect_call
 xor a
 ld ($7ba1),a
 ld a,(bs_hits)
 or a
 ret nz
 ld a,($78f6)
 ld hl,$78f7
 or (hl)
 ret nz
 ld a,(awake_done)
 or a
 ret z
 ld a,(awake_mouth)
 ld hl,awake_previous
 or (hl)
 ret nz
 ld a,(assembly_count)
 ld hl,assembly_previous
 cp (hl)
 ret nz
 ld a,(rects+22)
 cp 7
 ret nz
 ld a,(rects+23)
 cp 52
 ret nz
 ld a,(face_x+1)
 ld hl,face_oldx
 cp (hl)
 ret nz
 ld a,(face_y+1)
 ld hl,face_oldy
 cp (hl)
 ret nz
 ld a,1
 ld ($7ba1),a
 ret
inc_mark_eyes:
 ; Called only when image identity changed; stationary shut-mouth images
 ; differ solely on these preverified eye rows across every fine X phase.
 push iy
 ld hl,(rects+20)
 ld a,h
 add a,12
 ld h,a
 ld ($7ba2),hl
 ld hl,14*256+7
 ld ($7ba4),hl
 ld iy,$7ba2
 call mark_object
 pop iy
 ret
inc_draw:
 push de
 pop ix
 ld bc,(rects+20)
 ld a,52
 ld ($78e0),a
inc_row:
 push bc
 ld a,c
 add a,7
 ld e,a
 ld l,b
 ld h,$79
 ld a,(hl)
 cp c
 jr c,inc_left
 ld c,a
inc_left:
 ld h,$7d
 ld a,(hl)
 cp e
 jr c,inc_right
 ld a,e
inc_right:
 sub c
 jr c,inc_next
 jr z,inc_next
 ld ($7ba6),a
 call offset
 ld a,h
 or $a0
 ld h,a
 push hl
 ld a,c
 ld hl,rects+20
 sub (hl)
 inc a
 ld e,a
 ld d,0
 ld l,(ix+0)
 ld h,(ix+1)
 add hl,de
 pop de
 push de
 ld a,($7ba6)
 ld c,a
 ld b,0
 ldir
 ld a,($7ba6)
 neg
 add a,9
 ld c,a
 add hl,bc
 pop de
 ld a,d
 xor $60
 ld d,a
 ld a,($7ba6)
 ld c,a
 ldir
inc_next:
 inc ix
 inc ix
 pop bc
 inc b
 ld hl,$78e0
 dec (hl)
 jr nz,inc_row
 ret
; Subtract the new face rectangle once per old object, not per pixel/row.
; Retain dirty bounds for overlap repair, then erase at most four strips.
inc_restore:
 ld a,(iy+2)
 or a
 ret z
 ld a,(rects+20)
 ld c,a
 ld a,(rects+22)
 ld d,a
 ld a,(iy+0)
 ld b,(iy+2)
 call inc_intersection
 jp c,clear_plain
 ld ($7ba8),a
 ld a,e
 ld ($7ba9),a
 ld a,(rects+21)
 ld c,a
 ld a,(rects+23)
 ld d,a
 ld a,(iy+1)
 ld b,(iy+3)
 call inc_intersection
 jp c,clear_plain
 ld ($7baa),a
 ld a,e
 ld ($7bab),a
 call mark_object
 ld a,(iy+0)
 ld ($7ba2),a
 ld a,(iy+2)
 ld ($7ba4),a
 ld a,(iy+1)
 ld ($7ba3),a
 ld c,a
 ld a,($7bab)
 sub c
 ld ($7ba5),a
 call inc_erase
 ld a,($7baa)
 ld ($7ba3),a
 ld c,a
 ld a,(iy+1)
 add a,(iy+3)
 sub c
 ld ($7ba5),a
 call inc_erase
 ld a,($7bab)
 ld ($7ba3),a
 ld c,a
 ld a,($7baa)
 sub c
 ld ($7ba5),a
 ld a,(iy+0)
 ld c,a
 ld a,($7ba9)
 sub c
 ld ($7ba4),a
 call inc_erase
 ld a,($7ba8)
 ld ($7ba2),a
 ld c,a
 ld a,(iy+0)
 add a,(iy+2)
 sub c
 ld ($7ba4),a
 jp inc_erase
inc_erase:
 ld a,($7ba4)
 or a
 ret z
 ld a,($7ba5)
 or a
 ret z
 push iy
 ld iy,$7ba2
 call clear_plain
 pop iy
 ret
; A/B=old start/length, C/D=new start/length. E=max start, A=min end.
inc_intersection:
 ld e,a
 add a,b
 ld b,a
 ld a,c
 cp e
 jr c,inc_start
 ld e,a
inc_start:
 ld a,c
 add a,d
 cp b
 jr c,inc_end
 ld a,b
inc_end:
 cp e
 ret c
 jr nz,inc_valid
 scf
 ret
inc_valid:
 or a
 ret


 ; Refresh-clock effects; HOME 783F is boot-cleared, single-byte timer.
 ; IRQ calls only while active. Final tick restores black, then costs stop.
inc_border:
 ld hl,$783f
 dec (hl)
 ld a,(hl)
 or a
 jr z,ib_write
 ld b,a
 ld a,(game_status)
 cp 1
 ld a,2
 jr nz,ib_write
 bit 3,b
 jr z,ib_write
 ld a,6
ib_write:
 out ($fe),a
 ret

inc_flash:
 ld hl,effects_origin
inc_effect_call:
 ld a,($78df)
 push af
 ; DOCK7 effects code, HOME2 settings and HOME6 record buffer visible.
 ld a,$94
 ld ($78df),a
 out ($f4),a
 call world_dispatch
 pop af
 ld ($78df),a
 out ($f4),a
 ret

 INCLUDE "damage-render.asm"

inc_assembly_draw:
 ld a,(game_mode)
 or a
 ret z
 ld a,(sinistar_built)
 or a
 ret nz
 ld a,(rects+22)
 or a
 ret z
 jp $dfbe

inc_ship:
 ld a,(rects+14)
 cp 3
 jr nz,inc_ship_clip
 ld a,(rects+15)
 cp 12
 jr nz,inc_ship_clip
 ld a,12
 jp draw_ship_raw
inc_ship_clip:
 jp $dfef

 INCLUDE "cached-face.asm"

; Four-pixel mouth shift, exactly equivalent to four carry-fed bit passes.
; Only mouth rows 33..45 need shifting; the body is already pre-shifted.
inc_mouth_four:
 ld hl,$bab5
 ld e,13
im4_row:
 ld d,2
 ld a,15
im4_plane:
 push hl
 ld b,7
im4_cell:
 rrd
 inc hl
 inc hl
 inc hl
 djnz im4_cell
 pop hl
 inc hl
 xor a
 dec d
 jr nz,im4_plane
 ld bc,19
 add hl,bc
 dec e
 jr nz,im4_row
 ret

; Shifted awake poses have one masked left edge, then opaque cells.
; Keep the attribute pointer in alternate HL instead of switching planes
; twice per cell. Other sprites retain the general transparency compositor.
inc_speaking_face:
 ld a,(rects+23)
 ld iyh,a
 ld ixl,e
 ld de,$b800
isf_row:
 call offset
 ld a,h
 or $a0
 ld h,a
 push bc
 push hl
 exx
 pop hl
 ld a,h
 xor $60
 ld h,a
 exx
 ld b,ixl
 ; Only the first cell can preserve pixels from the previous background.
 ld a,(de)
 inc de
 and (hl)
 ld c,a
 ld a,(de)
 or c
 jr isf_store
isf_cell:
 inc de
 ld a,(de)
isf_store:
 ld (hl),a
 inc de
 ld a,(de)
 exx
 ld (hl),a
 inc l
 exx
 inc de
 inc l
 djnz isf_cell
 pop bc
 inc b
 dec iyh
 jr nz,isf_row
 ret
