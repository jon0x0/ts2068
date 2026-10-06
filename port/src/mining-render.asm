; Seven native objects, composed in HOME before changed-byte publication.
; All sprites stay at y>=64. Publication timing is checked against the raster.
render:
 ld hl,world_extension+51
 call world_call
 call world_project
 ld a,(rock_y)
 ld b,a
 ld c,5
 ld a,(rock_alive)
 or a
 jr nz,mr_rock
 ld c,0
mr_rock:
 ld a,(rock_x)
 ld d,28
 ld hl,rects
 call make_rect
 ld hl,rects+4
 ld a,(crystal_alive)
 or a
 ld c,2
 jr nz,mr_crystal
 ld c,0
mr_crystal:
 ld a,(cy+1)
 ld b,a
 ld a,(cx+1)
 ld d,4
 call make_rect
 ld a,(bullet_alive)
 or a
 ld c,2
 jr nz,mr_bullet
 ld c,0
mr_bullet:
 ld a,(by+1)
 ld b,a
 ld a,(bx+1)
 ld d,2
 call make_rect
 ld a,(py+1)
 ld b,a
 ld a,(px+1)
 ld c,3
 ld d,12
 call make_rect
 ld a,(worker_alive)
 or a
 ld c,3
 jr nz,mr_worker_rect
 ld c,0
mr_worker_rect:
 ld a,(worker_y)
 ld b,a
 ld a,(worker_x)
 ld d,12
 call make_rect
 ld a,(assembly_count)
 or a
 ld c,7
 jr z,mr_no_face
 ld a,(bs_hits)
 cp 13
 jr c,mr_piece_rect
mr_no_face:
 ld c,0
mr_piece_rect:
 ld a,(face_y+1)
 ld b,a
 ld a,(face_x+1)
 ld d,52
 call make_rect
 ld a,(bs_active)
 or a
 ld c,2
 jr nz,mr_bomb_rect
 ld c,0
mr_bomb_rect:
 ld a,(bs_y)
 ld b,a
 ld a,(bs_x)
 ld d,6
 call make_rect
 call world_clip
 ld hl,world_extension+93
 call world_call
 call $a699
 call fast_select
 ld hl,render_extension
 call incremental_call
 ; A complete current face will overwrite this region in shadow. Old
 ; rectangles only need restoration outside it, even when actors overlap.
 ld a,($78f6)
 xor 1
 ld hl,awake_done
 and (hl)
 ld ($7ba0),a
 ; A retry must retain dirty spans from the abandoned first composition.
 ld a,($7bac)
 or a
 jr nz,mr_dirty_ready
 ld hl,$7940
 ld de,$7941
 ld bc,111
 ld (hl),32
 ldir
 ld hl,$7d40
 ld de,$7d41
 ld bc,111
 ld (hl),0
 ldir
mr_dirty_ready:
 ; A stationary rock is background: only clear/compare its full area when
 call stars_clear_call
 call population_clear
 ; visibility or pixel position changes. Redrawing it in shadow repairs holes
 ; cleared by the smaller moving objects, whose rectangles remain dirty.
 ld a,(rock_x)
 ld hl,$78e6
 cp (hl)
 jr nz,rock_changed
 ld a,(rects+1)
 ld hl,oldrects+1
 cp (hl)
 jr nz,rock_changed
 ld a,(rects+3)
 ld hl,oldrects+3
 cp (hl)
 jr nz,rock_changed
 ld a,(rects+2)
 ld hl,oldrects+2
 cp (hl)
 jr nz,rock_changed
 xor a
 jr rock_dirty_flag
rock_changed:
 ld a,1
rock_dirty_flag:
 ld ($78e4),a
 ld a,(assembly_count)
 ld hl,assembly_previous
 xor (hl)
 ld b,a
 ld a,(awake_mouth)
 ld hl,awake_previous
 xor (hl)
 or b
 ld b,a
 ld a,(eye_phase)
 ld hl,eye_previous
 xor (hl)
 or b
 ld ($78d5),a
 ld b,a
 ld a,(face_x+1)
 ld hl,face_oldx
 xor (hl)
 or b
 ld b,a
 ld a,(face_y+1)
 ld hl,face_oldy
 xor (hl)
 or b
 ld b,a
 ld a,(rects+22)
 ld hl,oldrects+22
 xor (hl)
 or b
 ld ($78e5),a
 ld a,1
 ld ($78d8),a
 ld iy,oldrects
 call clear_four
 xor a
 ld ($78d8),a
 ld iy,rects
 call clear_four
composition_start:
 ld a,($78f6)
 or a
 jp nz,mr_after_piece
 ld a,(bs_hits)
 cp 13
 jp nc,mr_after_piece
 ld a,(assembly_count)
 or a
 jp z,mr_after_piece
 ; Image identity is independent of its screen coordinates.
 ld a,(sinistar_built)
 or a
 jp nz,mr_awake_image
 ld a,($78d5)
 or a
 jp z,mr_piece_cached
 ld a,(assembly_count)
 dec a
 ld l,a
 ld h,0
 ld de,288
 add hl,de
 push hl
 ld a,(assembly_count)
 dec a
 add a,a
 ld l,a
 ld h,0
 ld de,assembly_lengths
 add hl,de
 ld c,(hl)
 inc hl
 ld b,(hl)
 pop hl
 call stage
 ld a,(assembly_count)
 cp 1
 jr nz,mr_patch_start
 ld hl,$d800
 ld (hl),255
 inc hl
 ld (hl),0
 inc hl
 ld (hl),1
 ld hl,$d800
 ld de,$d803
 ld bc,1089
 ldir
mr_patch_start:
 ld hl,$b800
mr_unpack:
 ld e,(hl)
 inc hl
 ld a,(hl)
 inc hl
 cp $ff
 jp z,mr_piece_cached
 add a,$d8
 ld d,a
 ld a,(hl)
 ld (de),a
 inc hl
 inc de
 ld a,(hl)
 ld (de),a
 inc hl
 inc de
 ld a,(hl)
 ld (de),a
 inc hl
 jr mr_unpack
mr_awake_image:
 ld a,(awake_done)
 or a
 jr z,mr_phase_zero
 ld a,(face_x+1)
 and 7
 jr z,mr_phase_zero
 dec a
 ld c,a
 ld a,(eye_phase)
 ld b,a
 add a,a
 add a,a
 add a,a
 sub b
 add a,c
 ld l,a
 ld h,0
 ld de,326
 add hl,de
 jr mr_select_face
mr_phase_zero:
 ld a,(eye_phase)
 ld b,a
 add a,a
 add a,b
 ld b,a
 ld a,(awake_mouth)
 add a,b
 ld l,a
 ld h,0
 ld de,308
 add hl,de
mr_select_face:
 ld d,h
 ld e,l
 add hl,hl
 add hl,de
 ld de,sprites
 add hl,de
 ld a,(hl)
 inc hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ; Atlas banks 0/1/7 cannot cover the HOME composition planes.
 ld c,a
 ld a,(awake_done)
 or a
 jr nz,mr_face_atlas
 ld a,(face_x+1)
 and 7
 jr z,mr_face_atlas
 ld hl,world_extension+90
 call world_call
 ld l,5
 call scene_sprite
 jr mr_after_piece
mr_face_atlas:
 ld a,c
 ld ($78df),a
 out ($f4),a
mr_shift_ready:
 xor a
 ld ($78ee),a
 ld bc,(rects+20)
 ld a,52
 call draw_cached_face
 ld a,$10
 ld ($78df),a
 out ($f4),a
 jr mr_after_piece
mr_piece_cached:
 ld a,(game_mode)
 or a
 jr z,mr_stationary
 ld a,(assembly_count)
 ld ($5bd7),a
 xor a
 call assembly_cache_call
 xor a
 call assembly_cache_call
 call $df70
 jp mr_after_piece
mr_stationary:
 ld a,1
 ld ($78ee),a
 ld bc,(rects+20)
 ld a,52
 ld e,7
 call draw_assembly
 xor a
 ld ($78ee),a
mr_after_piece:
 ld a,(rects+2)
 or a
 jr z,mr_draw_crystal
 ld a,(rock_x)
 and 7
 ld l,a
 ld h,1
 call draw_rock
mr_draw_crystal:
 call population_draw
 ld a,(rects+18)
 or a
 jr z,mr_after_worker
 ld a,(worker_x)
 and 7
 add a,24
 ld l,a
 ld h,1
 ld bc,108
 call stage
 ld l,4
 call scene_sprite
mr_after_worker:
 ld a,(rects+6)
 or a
 jr z,mr_draw_bullet
 ld a,(cx+1)
 and 7
 add a,8
 ld l,a
 ld h,1
 ld bc,24
 call stage
 ld l,1
 call scene_sprite
mr_draw_bullet:
 ld a,(rects+10)
 or a
 jr z,mr_draw_player
 ld a,(bx+1)
 and 7
 add a,16
 ld l,a
 ld h,1
 ld bc,12
 call stage
 ld l,2
 call scene_sprite
mr_draw_player:
 ld a,(rects+14)
 or a
 jr z,mr_after_player
 ld a,(angle)
 add a,4
 and $f8
 ld e,a
 ld a,(px+1)
 and 7
 or e
 ld l,a
 ld h,0
 ld a,($78f5)
 or a
 jr z,mr_ship_refresh
 ld a,($78f3)
 cp l
 jr z,mr_ship_ready
mr_ship_refresh:
 ld a,l
 ld ($78f3),a
 ld bc,108
 call stage
 ld a,1
 ld ($78f5),a
mr_ship_ready:
 ld bc,(rects+12)
 ld a,12
 ld e,3
 call draw_ship
mr_after_player:
 ld a,(rects+26)
 or a
 jr z,mr_no_bomb
 ld a,(bs_x)
 and 7
 ld l,a
 ld h,0
 ld de,317
 add hl,de
 ld bc,36
 call stage
 ld l,6
 call scene_sprite
mr_no_bomb:
 call stars_draw_call
 ld hl,render_extension+24
 call incremental_call
 call compile
 ld a,($78f6)
 or a
 jr z,ready
 ld hl,($78f0)
 ld de,$e000
 or a
 sbc hl,de
 ld de,($580c)
 or a
 sbc hl,de
 jr c,ready
 ; Retry composition without the transition path if publication is too large.
 ld a,1
 ld ($580f),a
 call world_restore
 jp render
ready:
 halt
publish:
 call radar_publish
 call publish_records
 call fast_publish
publication_done:
 ld a,($78f6)
 ld ($78f7),a
 ld a,(face_x+1)
 ld (face_oldx),a
 ld a,(face_y+1)
 ld (face_oldy),a
 ld a,(eye_phase)
 ld (eye_previous),a
 ld a,(awake_mouth)
 ld (awake_previous),a
 ld a,(assembly_count)
 ld (assembly_previous),a
 ld a,(rock_x)
 ld ($78e6),a
 ld hl,rects
 ld de,oldrects
 ld bc,28
 ldir
 call world_restore
 call radar_step
 ld hl,render_extension+15
 call incremental_call
 ret
make_rect:
 srl a
 srl a
 srl a
 ld (hl),a
 inc hl
 ld (hl),b
 inc hl
 ld (hl),c
 inc hl
 ld (hl),d
 inc hl
 ret
clear_four:
 ld b,7
 ld a,($78e4)
 or a
 jr nz,cf_loop
 ld de,4
 add iy,de
 dec b
cf_loop:
 ; Check whether the direct face has deliberately been omitted from shadow.
 ld a,b
 cp 2
 jr nz,cf_clear
 ld a,($78f6)
 or a
 jr z,cf_normal_face
 ld a,($78d8)
 or a
 jr z,cf_skip
 ld a,($78f7)
 or a
 jr nz,cf_skip
 ; First fast frame removes the previous composed face from HOME shadow.
 jr cf_clear
cf_normal_face:
 ld a,($78e5)
 or a
 jr z,cf_skip
 ; If the old and new face rectangles coincide, clear only the new one.
 ld a,($78d8)
 or a
 jr z,cf_clear
 ld a,(sinistar_built)
 or a
 jr z,cf_clear
 ; Compare all four fields, including clipped height at the radar boundary.
 push iy
 pop de
 ld hl,rects+20
 ld c,4
cf_same_rect:
 ld a,(de)
 cp (hl)
 jr nz,cf_clear
 inc de
 inc hl
 dec c
 jr nz,cf_same_rect
 jr cf_skip
cf_clear:
 push bc
 ld a,b
 cp 2
 jr nz,cf_regular
 ld a,(sinistar_built)
 or a
 jr z,cf_regular
 ld a,($78d8)
 or a
 jr nz,cf_regular
cf_mark_new:
 ld a,($7ba1)
 or a
 jr z,cf_mark_all
 ld hl,render_extension+3
 call incremental_call
 jr cf_cleared
cf_mark_all:
 ; A complete planar face copy overwrites the new rectangle in shadow RAM.
 ; Mark it for comparison without first filling the same cells with black.
 call mark_object
 jr cf_cleared
cf_regular:
 ld a,($78d8)
 or a
 jr nz,cf_erase
 call mark_object
 jr cf_cleared
cf_erase:
 call clear_object
cf_cleared:
 pop bc
cf_skip:
 push bc
 ld de,4
 add iy,de
 pop bc
 djnz cf_loop
 ret
mark_object:
 ld a,(iy+2)
 or a
 ret z
 ld e,a
 ld d,(iy+3)
 ld c,(iy+0)
 ld b,(iy+1)
mo_row:
 ld l,b
 ld h,$79
 ld a,c
 cp (hl)
 jr nc,mo_max
 ld (hl),a
mo_max:
 ld h,$7d
 ld a,e
 add a,c
 cp (hl)
 jr c,mo_next
 ld (hl),a
mo_next:
 inc b
 dec d
 jr nz,mo_row
 ret
clear_object:
 ld a,($7ba0)
 or a
 jp z,clear_plain
 ld hl,render_extension+9
 jp incremental_call
stage:
 ld ($78ec),bc
 ld a,h
 or a
 ld a,0
 jr nz,stage_format
 inc a
stage_format:
 ld ($78d4),a
 ld d,h
 ld e,l
 add hl,hl
 add hl,de
 ld de,sprites
 add hl,de
 ld a,(hl)
 inc hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ex de,hl
 ld b,a
 and $f7
 ld ($78df),a
 out ($f4),a
 ld de,$b800
 cp $30
 jr nz,stage_direct
 ld de,$dc80
stage_direct:
 push af
 bit 3,b
 jr z,stage_raw
 cp $50
 jr nz,stage_unmapped
 xor a
 ld ($5bdb),a ; this transfer overwrites the retained BF00 mask lookup
 ld de,$be00
 ld bc,512
 ldir
 ld hl,$be00
 ld de,$b800
 ld a,$10
 ld ($78df),a
 out ($f4),a
stage_unmapped:
 ld a,($78d4)
 or a
 jr z,stage_compressed
 ld de,$7c00
stage_compressed:
 call unpack_ship
 ld a,($78d4)
 or a
 jr z,stage_copied
 pop af
 ld a,$10
 ld ($78df),a
 out ($f4),a
 ret
stage_raw:
 ld bc,($78ec)
 ldir
stage_copied:
 pop af
 ld b,a
 ld a,$10
 ld ($78df),a
 out ($f4),a
 ld a,b
 cp $30
 ret nz
 ld hl,$dc80
 ld de,$b800
 ld bc,($78ec)
 ldir
 ret
unpack_ship:
 ; Count, ceil(count/8) occupancy bytes, then common triples/literals.
 ld a,(hl)
 inc hl
 push af
 push de
 add a,7
 srl a
 srl a
 srl a
 ld c,a
 ld b,0
 ld de,$7c70
 ldir
 pop de
 pop af
 ld b,a
 ld ix,$7c70
 ld c,8
us_cell:
 srl (ix+0)
 jr nc,us_empty
 ld a,(hl)
 inc hl
 cp 255
 jr z,us_literal
 push hl
 push bc
 ld l,a
 ld h,0
 ld c,a
 ld b,0
 add hl,hl
 add hl,bc
 ld bc,$c000
 add hl,bc
 ld a,(hl)
 ld (de),a
 inc de
 inc hl
 ld a,(hl)
 ld (de),a
 inc de
 inc hl
 ld a,(hl)
 pop bc
 pop hl
 jr us_last
us_literal:
 ld a,(hl)
 inc hl
 ld (de),a
 inc de
 ld a,(hl)
 inc hl
 ld (de),a
 inc de
 ld a,(hl)
 inc hl
 jr us_last
us_empty:
 ld a,255
 ld (de),a
 inc de
 xor a
 ld (de),a
 inc de
us_last:
 ld (de),a
 inc de
 dec c
 jr nz,us_next
 inc ix
 ld c,8
us_next:
 djnz us_cell
 ret

draw_cached_face:
 ld hl,render_extension+30
 jp incremental_call
draw_assembly:
assembly_select:
 ld a,(rects+22)
 or a
 ret z
assembly_full:
 ld bc,(rects+20)
 ld a,52
 ld e,7
 ld ($78e0),a
 ld a,e
 ld ($78e1),a
 ld de,$d800
 jr sprite_row
draw_ship:
 ld hl,render_extension+27
 jp incremental_call
draw_ship_raw:
 ld ($78e0),a
 ld a,e
 ld ($78e1),a
 ld de,$7c00
 jr sprite_row
draw_sprite:
 ld ($78e0),a
 ld a,e
 ld ($78e1),a
 ld de,$b800
sprite_row:
 ld a,($78ee)
 or a
 jr z,sprite_row_draw
 ld l,b
 ld h,$79
 ld a,(hl)
 cp 31
 jr nc,sprite_row_skip
 ld h,$7d
 ld a,(hl)
 cp 25
 jr nc,sprite_row_draw
sprite_row_skip:
 ex de,hl
 ld a,l
 add a,21
 ld l,a
 jr nc,sprite_skip_carry
 inc h
sprite_skip_carry:
 ex de,hl
 jr sprite_row_finish
sprite_row_draw:
 call offset
 ld a,h
 or $a0
 ld h,a
 push bc
 ld a,($78e1)
 ld b,a
sprite_cell:
 ld a,(de)
 inc de
 cp 255
 jr z,sprite_transparent
 and (hl)
 ld c,a
 ld a,(de)
 or c
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
 jr sprite_next
sprite_transparent:
 inc de
sprite_next:
 inc de
 inc l
 djnz sprite_cell
 pop bc
sprite_row_finish:
 inc b
 ld a,($78e0)
 dec a
 ld ($78e0),a
 jr nz,sprite_row
 ret
 INCLUDE "../build/incremental-origin.asm"
incremental_call:
 ld a,($78df)
 push af
 or 4
 ld ($78df),a
 out ($f4),a
 call world_dispatch
 pop af
 ld ($78df),a
 out ($f4),a
 ret
compile EQU compile_stream
compile_count:
 ; Seven budget units per record conservatively cover the 28T writer.
 ld hl,$fffe
 ld de,($7bb2)
 or a
 sbc hl,de
 srl h
 rr l
 srl h
 rr l
 ld d,h
 ld e,l
 add hl,hl
 add hl,hl
 add hl,hl
 or a
 sbc hl,de
 ld de,$e000
 add hl,de
 ld ($78f0),hl
 ret
span_lookup:
 push hl
 ld a,b
 dec a
 add a,a
 ld l,a
 ld h,0
 ld bc,span_entries
 add hl,bc
 ld c,(hl)
 inc hl
 ld b,(hl)
 ld ($7bbd),bc
 pop hl
 jp $7bbc
 INCLUDE "mining-fast.asm"
 INCLUDE "../build/render-kernels.asm"
 INCLUDE "fast-eyes.asm"
; B=y, C=byte x. Both nonlinear scanline address bytes are precomputed.
offset:
 ld l,b
 ld h,scanline_low / 256
 ld a,(hl)
 or c
 inc h
 ld h,(hl)
 ld l,a
 ret






; Fully visible rocks use offline row programs; clipped edges keep the
; reference masked compositor. Neither route erases the live display.
draw_rock:
 ld a,(rects+2)
 cp 5
 jp nz,rock_fallback
 ld a,(rects+3)
 cp 28
 jp nz,rock_fallback
 ld a,$14
 ld ($78df),a
 out ($f4),a
 ld a,l
 add a,a
 ld l,a
 ld h,0
 ld de,rock_programs
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 push de
 pop iy
 ld hl,rock_program_row
 ld a,($78e4)
 or a
 jr nz,rock_loop_selected
 ld hl,rock_program_dirty
rock_loop_selected:
 ld ($7be4),hl
 ld a,$c3
 ld ($7be3),a
 ld bc,(rects)
 ld a,28
 jp $7be3
rock_program_dirty:
 push af
 ld l,b
 ld h,$79
 ld a,(hl)
 sub c
 cp 5
 jr c,rock_row_needed
 ld h,$7d
 ld a,(hl)
 cp c
 jr c,rock_row_skip
 jr z,rock_row_skip
 ld h,$79
 ld a,(hl)
 cp c
 jr c,rock_row_needed
rock_row_skip:
 inc iy
 inc iy
 pop af
 jr rock_row_advance
rock_row_needed:
 pop af
rock_program_row:
 push af
 push bc
 call offset
 ld a,h
 or $a0
 ld h,a
 xor $60
 ld d,a
 ld e,l
 ld c,(iy+0)
 ld b,(iy+1)
 inc iy
 inc iy
 push bc
 pop ix
 call rock_program_call
 pop bc
 pop af
rock_row_advance:
 inc b
 dec a
 jp nz,$7be3
 ld a,$10
 ld ($78df),a
 out ($f4),a
 ret
rock_program_call:
 jp (ix)
rock_fallback:
 ld bc,420
 call stage
 ld l,0
 jp scene_sprite
 INCLUDE "../build/rock-programs.asm"



clear_plain:
 ld a,(iy+2)
 or a
 ret z
 ld ($78e1),a
 dec a
 add a,a
 ld l,a
 ld h,0
 ld bc,clear_entries
 add hl,bc
 ld c,(hl)
 inc hl
 ld b,(hl)
 ld ($7be1),bc
 ld a,(iy+3)
 ld ($78e0),a
 ld c,(iy+0)
 ld b,(iy+1)
co_row:
 ld l,b
 ld h,$79
 ld a,c
 cp (hl)
 jr nc,co_max
 ld (hl),a
co_max:
 ld h,$7d
 ld a,($78e1)
 add a,c
 cp (hl)
 jr c,co_clear
 ld (hl),a
co_clear:
 call offset
 ld a,h
 or $a0
 ld h,a
 xor $60
 ld d,a
 ld e,l
 push bc
 ld a,7
 call $7be0
 pop bc
 inc b
 ld hl,$78e0
 dec (hl)
 jr nz,co_row
 ret

; Build all ordinary-frame records in one descending stack pass. Ordinary
; calls may use free stack space transiently; emit kernels return by JP.
compile_stream:
 ld ($7bb0),sp
 ld sp,$fffe
 ld a,$c3
 ld ($7bbc),a
 ld a,175
 ld ($7bc0),a
stream_row:
 xor a
 ld ($7bc3),a
 ld ($7bd0),a
 ld a,($7bc0)
 ld b,a
 ld l,a
 ld h,$79
 ld c,(hl)
 ld h,$7d
 ld a,(hl)
 ld e,a
 sub c
 jp c,stream_next
 jp z,stream_next
 ; Direct transitions omit their protected envelope from comparison.
 ld a,($78f6)
 or a
 jr z,stream_whole
stream_face_cut:
 ld a,($5802)
 cp b
 jr z,stream_face_bottom
 jr nc,stream_whole
stream_face_bottom:
 ld a,($5803)
 cp b
 jr c,stream_whole
 jr z,stream_whole
 ld a,($5800)
 ld d,a
 ld a,($5801)
stream_cut:
 ; C/E = full interval, D/A = excluded middle interval.
 cp c
 jr c,stream_whole
 jr z,stream_whole
 ld l,a
 ld a,d
 cp e
 jr nc,stream_whole
 sub c
 jr c,stream_no_left
 jr z,stream_no_left
 ld ($7bd0),a
 ld a,c
 ld ($7bd1),a
stream_no_left:
 ld a,l
 cp e
 jr nc,stream_left_only
 ld c,a
 jr stream_whole
stream_left_only:
 ld a,($7bd0)
 or a
 jp z,stream_next
 ld e,d
 xor a
 ld ($7bd0),a
stream_whole:
 ld a,e
 sub c
 ld ($7bc2),a
 dec a
 add a,c
 ld c,a
 call offset
 ld a,h
 or $a0
 ld h,a
 xor $e0
 ld d,a
 ld e,l
 ld ($7bc4),hl
 ld ($7bc6),de
 ld a,($7bc2)
 ld b,a
 jp span_lookup
stream_after_span:
 ld a,($7bc3)
 or a
 jr nz,stream_after_pair
 inc a
 ld ($7bc3),a
 ld hl,($7bc4)
 ld a,h
 xor $60
 ld h,a
 ld de,($7bc6)
 ld a,d
 xor $20
 ld d,a
 jp $7bbc
stream_after_pair:
 ld a,($7bd0)
 or a
 jr z,stream_next
 ld e,a
 xor a
 ld ($7bd0),a
 ld ($7bc3),a
 ld a,($7bd1)
 ld c,a
 add a,e
 ld e,a
 ld a,($7bc0)
 ld b,a
 jp stream_whole
stream_next:
 ld hl,$7bc0
 dec (hl)
 ld a,(hl)
 cp 63
 jp nz,stream_row
 ld ($7bb2),sp
 ld sp,($7bb0)
 jp compile_count
