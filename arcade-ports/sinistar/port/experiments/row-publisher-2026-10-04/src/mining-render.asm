; Seven native objects, composed in HOME before changed-byte publication.
; All sprites stay at y>=64. Publication timing is checked against the raster.
render:
 ld a,(rock_x)
 ld b,100
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
 cp 12
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
 ld a,(awake_done)
 or a
 jr z,mr_maps_ready
 ld hl,$a440
 ld de,$a441
 ld bc,111
 ld (hl),32
 ldir
 ld hl,$a540
 ld de,$a541
 ld bc,111
 ld (hl),0
 ldir
mr_maps_ready:
 ; A stationary rock is background: only clear/compare its full area when
 ; visibility or pixel position changes. Redrawing it in shadow repairs holes
 ; cleared by the smaller moving objects, whose rectangles remain dirty.
 ld a,(rock_x)
 ld hl,$78e6
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
 ld a,(bs_hits)
 cp 12
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
 ld de,$d801
 ld bc,1091
 ld (hl),0
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
 ld a,(rock_alive)
 or a
 jr z,mr_draw_crystal
 ld a,(rock_x)
 and 7
 ld l,a
 ld h,1
 ld bc,420
 call stage
 ld bc,(rects)
 ld a,28
 ld e,5
 call draw_sprite
mr_draw_crystal:
 ld a,(worker_alive)
 or a
 jr z,mr_after_worker
 ld a,(worker_x)
 and 7
 add a,24
 ld l,a
 ld h,1
 ld bc,108
 call stage
 ld bc,(rects+16)
 ld a,12
 ld e,3
 call draw_sprite
mr_after_worker:
 ld a,(crystal_alive)
 or a
 jr z,mr_draw_bullet
 ld a,(cx+1)
 and 7
 add a,8
 ld l,a
 ld h,1
 ld bc,24
 call stage
 ld bc,(rects+4)
 ld a,4
 ld e,2
 call draw_sprite
mr_draw_bullet:
 ld a,(bullet_alive)
 or a
 jr z,mr_draw_player
 ld a,(bx+1)
 and 7
 add a,16
 ld l,a
 ld h,1
 ld bc,12
 call stage
 ld bc,(rects+8)
 ld a,2
 ld e,2
 call draw_sprite
mr_draw_player:
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
 ld a,(bs_active)
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
 ld bc,(rects+24)
 ld a,6
 ld e,2
 call draw_sprite
mr_no_bomb:
 call compile
ready:
 halt
publish:
 ld a,($78f6)
 or a
 jr z,publish_slow
 call $5800
 call $d800
 jr publication_done
publish_slow:
 call $e000
publication_done:
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
 xor a
 ld ($78d4),a
 ld a,b
 cp 2
 jr nz,cf_group_ready
 ld a,(awake_done)
 ld ($78d4),a
cf_group_ready:
 ; Last slot is stationary assembly: dirty only when it appears/disappears.
 ld a,b
 cp 2
 jr nz,cf_clear
 ld a,($78e5)
 or a
 jr z,cf_skip
 ; If the old and new face rectangles coincide, clear only the new one.
 ld a,($78d8)
 or a
 jr z,cf_clear
 ld a,(rects+20)
 cp (iy+0)
 jr nz,cf_clear
 ld a,(rects+21)
 cp (iy+1)
 jr nz,cf_clear
 ld a,(rects+22)
 cp (iy+2)
 jr z,cf_skip
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
 ; A complete planar face copy overwrites the new rectangle in shadow RAM.
 ; Mark it for comparison without first filling the same cells with black.
 call mark_object
 jr cf_cleared
cf_regular:
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
 ld a,($78d4)
 or a
 ld h,$79
 jr z,1F
 ld h,$a4
1:
 ld a,c
 cp (hl)
 jr nc,mo_max
 ld (hl),a
mo_max:
 ld a,h
 cp $a4
 ld h,$7d
 jr nz,1F
 ld h,$a5
1:
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
 ld a,(iy+2)
 or a
 ret z
 ld ($78e1),a
 ld a,(iy+3)
 ld ($78e0),a
 ld c,(iy+0)
 ld b,(iy+1)
co_row:
 ld l,b
 ld a,($78d4)
 or a
 ld h,$79
 jr z,1F
 ld h,$a4
1:
 ld a,c
 cp (hl)
 jr nc,co_max
 ld (hl),a
co_max:
 ld a,h
 cp $a4
 ld h,$7d
 jr nz,1F
 ld h,$a5
1:
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
 ld a,($78e1)
 ld b,a
 ld a,7
co_cell:
 ld (hl),0
 ld (de),a
 inc l
 inc e
 djnz co_cell
 pop bc
 inc b
 ld hl,$78e0
 dec (hl)
 jr nz,co_row
 ret
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
 ld ($78df),a
 out ($f4),a
 ld de,$b800
 cp $30
 jr nz,stage_direct
 ld de,$7e00
stage_direct:
 push af
 ld a,($78d4)
 or a
 jr z,stage_raw
 ld de,$7c00
 call unpack_ship
 pop af
 ld a,$10
 ld ($78df),a
 out ($f4),a
 ret
stage_raw:
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
 ld hl,$7e00
 ld de,$b800
 ld bc,($78ec)
 ldir
 ret
unpack_ship:
 ; Five little-endian occupancy bytes, then only nontransparent triples.
 push de
 ld de,$78d9
 ld bc,5
 ldir
 pop de
 ld ix,$78d9
 ld b,36
 ld c,8
us_cell:
 srl (ix+0)
 jr nc,us_empty
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
 ; The face is the bottom layer over black. Write its complete rectangle in
 ; shadow RAM; later sprites still use masks and retain their overlap order.
 ld ($78e0),a
face_row:
 call offset
 ld a,h
 or $a0
 ld h,a
 push bc
 ex de,hl
 push de
 DUP 7
 ldi
 EDUP
 pop de
 ld a,d
 xor $60
 ld d,a
 DUP 7
 ldi
 EDUP
 ex de,hl
 pop bc
 inc b
 ld a,($78e0)
 dec a
 ld ($78e0),a
 jp nz,face_row
 ret
draw_assembly:
 ld ($78e0),a
 ld a,e
 ld ($78e1),a
 ld de,$d800
 jr sprite_row
draw_ship:
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
compile:
 xor a
 ld ($78f6),a
 ld a,(awake_done)
 or a
 jr z,compile_slow
 call update_fast_rows
 ld a,($78f6)
 or a
 ret nz
 call merge_face_bounds
compile_slow:
 exx
 ld hl,$e000
 exx
 ld b,64
compile_row:
 ld l,b
 ld h,$79
 ld c,(hl)
 ld h,$7d
 ld a,(hl)
 sub c
 jr z,compile_next
 jr c,compile_next
 ld ($78ef),a
 call offset
 ld a,h
 or $a0
 ld h,a
 xor $e0
 ld d,a
 ld e,l
 push bc
 ld a,($78ef)
 ld b,a
 push hl
 push de
 call compile_span
 pop de
 pop hl
 ld a,h
 xor $60
 ld h,a
 ld a,d
 xor $20
 ld d,a
 ld a,($78ef)
 ld b,a
 call compile_span
 pop bc
compile_next:
 inc b
 ld a,b
 cp 176
 jr nz,compile_row
 exx
 ld (hl),$c9
 ld ($78f0),hl
 exx
 ret
compile_span:
 ld a,(de)
 xor (hl)
 call nz,emit_store
 inc l
 inc e
 djnz compile_span
 ret
 ; Cached row programs contain addresses, not pixels. Only changed bounds
; rebuild a row; every invocation compares against the current shadow image.
update_fast_rows:
 ld a,($78f7)
 or a
 jr nz,uf_ready
 ld hl,$a040
 ld de,$a041
 ld bc,111
 ld (hl),32
 ldir
 ld hl,$a140
 ld de,$a141
 ld bc,111
 ld (hl),0
 ldir
 ld hl,$a240
 ld de,$a241
 ld bc,111
 ld (hl),32
 ldir
 ld hl,$a340
 ld de,$a341
 ld bc,111
 ld (hl),0
 ldir
 ld iy,$5800
 call uf_init_program
 ld iy,$d800
 call uf_init_program
 ld a,1
 ld ($78f7),a
uf_ready:
 ld a,1
 ld ($78f6),a
 ld hl,0
 ld ($78d6),hl
 ld hl,$5fe0
 ld ($78f0),hl
 ld hl,$7d79
 ld ($78d9),hl
 ld hl,$a1a0
 ld ($78db),hl
 ld iy,$5800
 call update_fast_group
 ld hl,$a5a4
 ld ($78d9),hl
 ld hl,$a3a2
 ld ($78db),hl
 ld iy,$d800
 jp update_fast_group
uf_init_program:
 ld b,112
 ld de,18
uf_init:
 ld (iy+0),$18
 ld (iy+1),16
 add iy,de
 djnz uf_init
 ld (iy+0),$c9
 ret
update_fast_group:
 ld b,64
uf_row:
 ld l,b
 ld a,($78d9)
 ld h,a
 ld c,(hl)
 ld a,($78da)
 ld h,a
 ld a,(hl)
 sub c
 jr nc,uf_width
 xor a
uf_width:
 ld ($78ef),a
 ld a,($78db)
 ld h,a
 ld a,(hl)
 cp c
 jr nz,uf_changed
 ld a,($78da)
 ld h,a
 ld e,(hl)
 ld a,($78dc)
 ld h,a
 ld a,e
 cp (hl)
 jr z,uf_budget
uf_changed:
 ld a,($78db)
 ld h,a
 ld (hl),c
 ld a,($78da)
 ld h,a
 ld e,(hl)
 ld a,($78dc)
 ld h,a
 ld (hl),e
 ld a,($78ef)
 or a
 jr nz,uf_active
 ld (iy+0),$18
 ld (iy+1),16
 jr uf_budget
uf_active:
 push bc
 ld c,a
 ld a,32
 sub c
 ld l,a
 ld h,0
 ld b,h
 ld c,l
 add hl,hl
 add hl,hl
 add hl,hl
 or a
 sbc hl,bc
 ld bc,fast_cells
 add hl,bc
 push hl
 pop ix
 pop bc
 push iy
 exx
 pop hl
 exx
 call offset
 ld a,h
 or $a0
 ld h,a
 xor $e0
 ld d,a
 ld e,l
 call emit_fast_span
 ld a,h
 xor $60
 ld h,a
 ld a,d
 xor $20
 ld d,a
 call emit_fast_span
uf_budget:
 call row_budget
 ld de,18
 add iy,de
 inc b
 ld a,b
 cp 176
 jp nz,uf_row
 ret
row_budget:
 ld a,($78f6)
 or a
 ret z
 ld a,($78ef)
 or a
 ld hl,12
 jr z,rb_add
 ld l,a
 ld h,0
 push bc
 ld b,h
 ld c,l
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,bc
 add hl,hl
 add hl,hl
 add hl,hl
 ld bc,100
 add hl,bc
 pop bc
rb_add:
 ld de,($78d6)
 add hl,de
 ld ($78d6),hl
 ex de,hl
 ld a,b
 sub 64
 add a,a
 ld l,a
 ld h,0
 push de
 ld de,fast_deadlines
 add hl,de
 pop de
 ld a,(hl)
 inc hl
 ld h,(hl)
 ld l,a
 or a
 sbc hl,de
 ret nc
 xor a
 ld ($78f6),a
 ret
emit_fast_span:
 push hl
 push de
 exx
 pop de
 pop bc
 ld (hl),$21
 inc hl
 ld (hl),e
 inc hl
 ld (hl),d
 inc hl
 ld (hl),$11
 inc hl
 ld (hl),c
 inc hl
 ld (hl),b
 inc hl
 ld (hl),$cd
 inc hl
 ld a,ixl
 ld (hl),a
 inc hl
 ld a,ixh
 ld (hl),a
 inc hl
 exx
 ret
fast_cells:
 DUP 32
 ld a,(de)
 cp (hl)
 jr z,1F
 ld (hl),a
1:
 inc e
 inc l
 EDUP
 ret
fast_deadlines:
 DUP 112,y
 DW (y+64+40)*224-1200
 EDUP
merge_face_bounds:
 ld b,64
mfb_row:
 ld l,b
 ld h,$a4
 ld a,(hl)
 ld h,$79
 cp (hl)
 jr nc,mfb_max
 ld (hl),a
mfb_max:
 ld h,$a5
 ld a,(hl)
 ld h,$7d
 cp (hl)
 jr c,mfb_next
 ld (hl),a
mfb_next:
 inc b
 ld a,b
 cp 176
 jr nz,mfb_row
 ret
emit_store:
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
; B=y, C=byte x; same nonlinear address in bitmap and attribute planes.
offset:
 ld a,b
 and 7
 ld h,a
 ld a,b
 and $c0
 rrca
 rrca
 rrca
 or h
 ld h,a
 ld a,b
 and $38
 rlca
 rlca
 or c
 ld l,a
 ret


 INCLUDE "../build/assembly-lengths.asm"




