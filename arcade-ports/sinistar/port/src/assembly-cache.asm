; Double-buffered assembly bitmap phases with exact alpha masks.
; Omit universally transparent row zero from eight bitmap phases (357 each).
; The reclaimed 56 bytes hold full per-scanline overlap flags.
; Then 364 mask-pattern indices and 100 eight-phase mask patterns.
 INCLUDE "../build/world-equ.asm"
 ORG assembly_cache_source
ac_entry:
 ld a,$08
 out ($f4),a
 ld a,c
 ld ($5bd9),a
 ld a,iyl
 ld ($5bda),a
 ld ($5bd5),sp
 ld sp,$bfff
 ld a,c
 or a
 jp z,ac_build
 cp 1
 jp z,ac_draw
 cp 3
 jp z,ac_overlap
 ld a,b
 ld ($5bd8),a
 ld ($5bdc),hl
 ld ($5bde),de
 ld ($5be4),ix
 jp ac_prepare
ac_build:
 ld a,($5bd7)
 ld hl,$5bd0
 cp (hl)
 jp z,ac_exit
 inc hl
 cp (hl)
 jr z,ac_build_row
 ld (hl),a
 xor a
 ld ($5bd2),a
 ld a,($5bd3)
 xor $10
 ld ($5bd4),a
 ld h,a
 ld l,0
 ld de,4095
 add hl,de
 ld (hl),0
 ld hl,$5c14
 ld de,$5c15
 ld bc,15
 ld (hl),0
 ldir
ac_build_row:
 ld a,($5bd2)
 call ac_times7
 ld ($5be6),hl
 ld d,h
 ld e,l
 add hl,hl
 add hl,de
 ld de,$d800
 add hl,de
 ld de,$bf80
 ld bc,21
 ldir
 ; Intern each adjacent-mask pair as all eight final shifted bytes.
 ld a,($5bd4)
 ld h,a
 ld l,0
 ld de,2912
 add hl,de
 ld de,($5be6)
 add hl,de
 ld ($5bf8),hl
 ld ix,$bf80
 ld c,255
 ld b,7
ac_intern_cells:
 push bc
 ld a,(ix+0)
 ld ($5bfa),a
 ld a,c
 and 127
 rlca
 ld ($5bfb),a
 call ac_intern
 ld hl,($5bf8)
 ld (hl),a
 inc hl
 ld ($5bf8),hl
 pop bc
 ld c,(ix+0)
 inc ix
 inc ix
 inc ix
 djnz ac_intern_cells
 ld a,($5bd2)
 or a
 jp z,ac_row_done
 xor a
 ld ($5be0),a
ac_build_phase:
 ld a,($5be0)
 call ac_phase_pointer_back
 ld de,($5be6)
 add hl,de
 ld de,-7
 add hl,de
 ex de,hl
 ld hl,$bf81
 ld b,7
ac_store_bits:
 ld a,(hl)
 ld (de),a
 inc de
 inc hl
 inc hl
 inc hl
 djnz ac_store_bits
 ld hl,$5be0
 inc (hl)
 ld a,(hl)
 cp 8
 jr z,ac_row_done
 ld hl,$bf81
 ld b,7
 or a
ac_shift_bits:
 rr (hl)
 inc hl
 inc hl
 inc hl
 djnz ac_shift_bits
 jr ac_build_phase
ac_row_done:
 ld hl,$5bd2
 inc (hl)
 ld a,(hl)
 cp 52
 jp nz,ac_exit
 ld a,($5bd4)
 ld ($5bd3),a
 ld a,($5bd1)
 ld ($5bd0),a
 ; Only a complete new front changes the live normalized color plane.
 ld hl,$d802
 ld de,$de00
 ld b,52
ac_commit_colors:
 push bc
 ld c,7
 ld b,7
ac_commit_cell:
 ld a,(hl)
 cp 1
 jr nz,ac_commit_color
 ld a,c
ac_commit_color:
 ld c,a
 ld (de),a
 inc de
 inc hl
 inc hl
 inc hl
 djnz ac_commit_cell
 pop bc
 djnz ac_commit_colors
 jp ac_exit
; Pattern phase 0 is the current mask. Phase 7 encodes the previous
; byte's low seven bits, so these two bytes identify all eight phases.
ac_intern:
 ld a,($5bfb)
 ld b,a
 ld a,($5bfa)
 xor b
 and 15
 add a,$14
 ld ($5bff),a
 ld l,a
 ld h,$5c
 ld a,(hl)
 or a
 jr z,ac_search_all
 dec a
 ld e,a
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 add hl,hl
 ld bc,3276
 add hl,bc
 ld a,($5bd4)
 add a,h
 ld h,a
 ld a,($5bfa)
 cp (hl)
 jr nz,ac_search_all
 ld bc,7
 add hl,bc
 ld a,(hl)
 and 254
 ld b,a
 ld a,($5bfb)
 cp b
 jr z,ac_pattern_found
ac_search_all:
 ld a,($5bd4)
 ld h,a
 ld l,0
 ld de,4095
 add hl,de
 ld a,(hl)
 ld ($5bfc),a
 ld a,($5bd4)
 ld h,a
 ld l,0
 ld de,3276
 add hl,de
 ld e,0
ac_find_pattern:
 ld a,($5bfc)
 cp e
 jr z,ac_new_pattern
 ld a,($5bfa)
 cp (hl)
 jr nz,ac_next_pattern
 push hl
 ld bc,7
 add hl,bc
 ld a,(hl)
 and 254
 ld c,a
 ld a,($5bfb)
 cp c
 pop hl
 jr z,ac_pattern_found
ac_next_pattern:
 ld bc,8
 add hl,bc
 inc e
 jr ac_find_pattern
ac_new_pattern:
 push de
 ld a,($5bfb)
 rrca
 ld c,a
 ld a,($5bfa)
 ld b,8
ac_pattern_phase:
 ld (hl),a
 inc hl
 srl c
 rra
 djnz ac_pattern_phase
 ld a,($5bd4)
 ld h,a
 ld l,0
 ld bc,4095
 add hl,bc
 inc (hl)
 pop de
ac_pattern_found:
 ld a,($5bff)
 ld l,a
 ld h,$5c
 ld a,e
 inc a
 ld (hl),a
 dec a
 ret
ac_times7:
 ld l,a
 ld h,0
 ld d,h
 ld e,l
 add hl,hl
 add hl,hl
 add hl,hl
 or a
 sbc hl,de
 ret
ac_phase_pointer_back:
 ld hl,$5bd4
 jr ac_phase_pointer
ac_phase_pointer_front:
 ld hl,$5bd3
ac_phase_pointer:
 ld b,(hl)
 add a,a
 ld l,a
 ld h,0
 ld de,ac_phase_offsets
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld h,b
 ld l,0
 add hl,de
 ret
ac_front_offset:
 ld a,($5bd3)
 ld h,a
 ld l,0
 add hl,de
 ret
ac_prepare:
 ; Every horizontal mask phase is already in the immutable front set.
 xor a
 jp ac_exit
; A = pattern index. Returns the final mask for the selected pixel phase.
; Preserves BC/DE/HL and both index registers for compositor/culling loops.
ac_mask:
 push hl
 push de
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 add hl,hl
 ld a,($5bd8)
 ld e,a
 ld d,0
 add hl,de
 ld de,3276
 add hl,de
 ld a,($5bd3)
 add a,h
 ld h,a
 ld a,(hl)
 pop de
 pop hl
 ret
; Prepare overlap rows and cull only rectangles wholly covered by solid mask.
ac_overlap:
 ld a,($5bd0)
 or a
 jp z,ac_exit
 add a,a
 add a,a
 add a,a
 ld hl,$5bd8
 or (hl)
 ld hl,$5bdb
 cp (hl)
 ld a,0
 jr nz,ac_overlap_lookup
 inc a
ac_overlap_lookup:
 ld ($5bf9),a
 ld de,2856
 call ac_front_offset
 ld ($5bed),hl
 ld d,h
 ld e,l
 inc de
 ld (hl),0
 ld bc,51
 ldir
 ld ix,$b800
 ld b,8
ac_main_objects:
 push bc
 ld a,b
 cp 3
 call nz,ac_object
 ld de,4
 add ix,de
 pop bc
 djnz ac_main_objects
 ld ix,$bc80
 ld b,17
ac_population:
 push bc
 call ac_object
 ld de,9
 add ix,de
 pop bc
 djnz ac_population
 ; Stars need just one composited row and are too small to warrant staging.
 ld ix,$58c0
 ld iy,$5c00
 ld b,10
ac_stars:
 push bc
 ld a,(ix+0)
 srl a
 srl a
 srl a
 ld ($bf80),a
 ld a,(ix+1)
 add a,64
 ld ($bf81),a
 ld hl,$0101
 ld ($bf82),hl
 push ix
 ld ix,$bf80
 call ac_object
 ld a,($bf82)
 xor 1
 ld (iy+0),a
 inc iy
 inc iy
 pop ix
 inc ix
 inc ix
 pop bc
 djnz ac_stars
 xor a
 ld ($5bf2),a
 ld ($5bf3),a
 jp ac_exit
ac_object:
 ld a,(ix+2)
 or a
 ret z
 ld b,a
 ld a,($5bdc)
 ld c,a
 ld a,(ix+0)
 add a,b
 cp c
 ret c
 ret z
 ld a,($5bde)
 add a,c
 cp (ix+0)
 ret c
 ret z
 ld a,($5bdd)
 ld c,a
 ld a,(ix+1)
 add a,(ix+3)
 cp c
 ret c
 ret z
 ld b,a
 ld a,($5bdf)
 add a,c
 cp (ix+1)
 ret c
 ret z
 cp b
 jr c,ac_end_y
 ld a,b
ac_end_y:
 ld ($bf96),a
 ld a,(ix+1)
 cp c
 jr nc,ac_start_y
 ld a,c
ac_start_y:
 ld ($bf97),a
 ; Containment first; then exact mask bytes, never screen pixels.
 ld a,(ix+0)
 ld hl,$5bdc
 sub (hl)
 jr c,ac_mark_overlap
 ld e,a
 add a,(ix+2)
 ld hl,$5bde
 cp (hl)
 jr c,ac_inside_x
 jr nz,ac_mark_overlap
ac_inside_x:
 ld a,(ix+1)
 ld hl,$5bdd
 sub (hl)
 jr c,ac_mark_overlap
 ld d,a
 add a,(ix+3)
 ld hl,$5bdf
 cp (hl)
 jr c,ac_inside_y
 jr nz,ac_mark_overlap
ac_inside_y:
 ld a,($5be5)
 add a,e
 ld ($bf98),a
 ld a,($5be4)
 add a,d
 call ac_times7
 ld a,($bf98)
 ld e,a
 ld d,0
 add hl,de
 push hl
 ld de,2912
 call ac_front_offset
 pop de
 add hl,de
 ld b,(ix+3)
ac_cover_row:
 push hl
 ld c,(ix+2)
 ld a,($5bf9)
 or a
 jr z,ac_cover_cell
 ld d,$bf
ac_cover_fast:
 ld e,(hl)
 ld a,(de)
 or a
 jr nz,ac_not_covered
 inc hl
 dec c
 jr nz,ac_cover_fast
 jr ac_cover_next_row
ac_cover_cell:
 ld a,(hl)
 call ac_mask
 or a
 jr nz,ac_not_covered
 inc hl
 dec c
 jr nz,ac_cover_cell
ac_cover_next_row:
 pop hl
 ld de,7
 add hl,de
 djnz ac_cover_row
 ld (ix+2),0
 ld hl,$5bf6
 inc (hl)
 ret
ac_not_covered:
 pop hl
ac_mark_overlap:
 ld a,($bf97)
 ld hl,$5bdd
 sub (hl)
 ld hl,$5be4
 add a,(hl)
 ld c,a
 ld a,($bf97)
 ld b,a
 ld a,($bf96)
 sub b
 ld b,a
ac_mark_row:
 push bc
 ld e,c
 ld d,0
 ld hl,($5bed)
 add hl,de
 ld (hl),1
 pop bc
 inc c
 djnz ac_mark_row
 ret
ac_draw:
 ld a,($5bd0)
 or a
 jp z,ac_exit
 ld a,($5bf2)
 or a
 jr nz,ac_draw_continue
 inc a
 ld ($5bf2),a
 ld a,($5bd0)
 add a,a
 add a,a
 add a,a
 ld hl,$5bd8
 or (hl)
 ld hl,$5bdb
 cp (hl)
 jr z,ac_lookup_ready
 ld (hl),a
 ; Sprite staging is complete; BF00 now holds this phase's mask lookup.
 ld de,3276
 call ac_front_offset
 ld a,($5bd8)
 ld e,a
 ld d,0
 add hl,de
 ld de,$bf00
 ld a,($5bd3)
 add a,15
 ld b,a
 ld c,255
 ld a,(bc)
 ld b,a
ac_phase_lookup:
 ld a,(hl)
 ld (de),a
 inc de
 ld a,l
 add a,8
 ld l,a
 jr nc,ac_lookup_next
 inc h
ac_lookup_next:
 djnz ac_phase_lookup
ac_lookup_ready:
 ld a,($5bd8)
 call ac_phase_pointer_front
 ld ($5be1),hl
 ld a,($5be4)
 call ac_times7
 ld a,($5be5)
 ld e,a
 ld d,0
 add hl,de
 push hl
 ld de,($5be1)
 add hl,de
 ld de,-7
 add hl,de
 ld ($5be6),hl
 pop hl
 push hl
 ld de,$de00
 add hl,de
 ld ($5be8),hl
 pop hl
 push hl
 ld de,2912
 call ac_front_offset
 pop de
 add hl,de
 ld ($5beb),hl
ac_draw_continue:
 ld a,13
 ld ($5bef),a
ac_blit_row:
 ld a,($5bf3)
 ld hl,$5be4
 add a,(hl)
 jr nz,ac_nonblank_row
 ld hl,$5bf3
 inc (hl)
 jp ac_row_next
ac_nonblank_row:
 ld a,($5bf3)
 ld l,a
 ld h,$be
 inc a
 ld ($5bf3),a
 ld a,($5bdc)
 ld c,a
 ld a,($5bde)
 add a,c
 cp (hl)
 jp c,ac_row_next
 jp z,ac_row_next
 ld a,l
 add a,64
 ld l,a
 ld a,c
 cp (hl)
 jp nc,ac_row_next
 ld a,($5bde)
 add a,c
 cp (hl)
 jr c,ac_end_covered
 jr nz,ac_clip_dirty
ac_end_covered:
 ld a,l
 sub 64
 ld l,a
 ld a,(hl)
 cp c
 jr c,ac_whole_dirty
 jr z,ac_whole_dirty
 ld a,l
 add a,64
 ld l,a
ac_clip_dirty:
 ; Intersect the cached face with this row's dirty interval.
 ld a,(hl)
 ld e,a
 ld a,($5bde)
 add a,c
 cp e
 jr c,ac_dirty_end
 ld a,e
ac_dirty_end:
 ld e,a
 ld a,l
 sub 64
 ld l,a
 ld a,(hl)
 cp c
 jr nc,ac_dirty_start
 ld a,c
ac_dirty_start:
 sub c
 ld ($5bfd),a
 add a,c
 ld c,a
 ld a,e
 sub c
 ld ($5bfe),a
 jr ac_expand_dirty
ac_whole_dirty:
 xor a
 ld ($5bfd),a
 ld a,($5bde)
 ld ($5bfe),a
ac_expand_dirty:
 ld a,($5bf3)
 dec a
 ld hl,$5be4
 add a,(hl)
 ld e,a
 ld d,0
 ld hl,($5bed)
 add hl,de
 ld a,(hl)
 ld ($5bf4),a
 ; Expand only this dirty row; no shifting or mask arithmetic remains.
 ld hl,($5beb)
 ld de,$bf80
 ld b,$bf
 DUP 7
 ld c,(hl)
 ld a,(bc)
 ld (de),a
 inc de
 inc hl
 EDUP
 ld bc,($5bdc)
 ld a,($5bfd)
 add a,c
 ld c,a
 ld a,b
 and 7
 ld d,a
 ld a,b
 and $c0
 rrca
 rrca
 rrca
 or d
 or $a0
 ld d,a
 ld a,b
 and $38
 rlca
 rlca
 or c
 ld e,a
ac_masked_row:
 ld hl,($5be6)
 ld ix,$bf80
 ld iy,($5be8)
 push de
 ld a,($5bfd)
 ld e,a
 ld d,0
 add hl,de
 add ix,de
 add iy,de
 pop de
 ld a,($5bf4)
 or a
 jr z,ac_direct_row
 ld a,($5bfe)
 ld b,a
ac_masked_cell:
 ld a,(ix+0)
 cp 255
 jr z,ac_masked_next
 ld c,a
 ld a,(de)
 and c
 or (hl)
 ld (de),a
 ld a,d
 xor $60
 ld d,a
 ld a,(iy+0)
 ld (de),a
 ld a,d
 xor $60
 ld d,a
ac_masked_next:
 inc de
 inc hl
 inc ix
 inc iy
 djnz ac_masked_cell
 jr ac_row_next
ac_direct_row:
 push de
 ld a,($5bfe)
 ld c,a
 ld b,0
 ldir
 pop de
 ld a,d
 xor $60
 ld d,a
 push iy
 pop hl
 ld a,($5bfe)
 ld b,a
ac_direct_color:
 ld a,(ix+0)
 cp 255
 jr z,ac_direct_next
 ld a,(hl)
 ld (de),a
ac_direct_next:
 inc ix
 inc hl
 inc de
 djnz ac_direct_color
ac_row_next:
 ld bc,7
 ld hl,($5be6)
 add hl,bc
 ld ($5be6),hl
 ld hl,($5be8)
 add hl,bc
 ld ($5be8),hl
 ld hl,($5beb)
 add hl,bc
 ld ($5beb),hl
 ld hl,$5bdd
 inc (hl)
 ld hl,$5bdf
 dec (hl)
 jr z,ac_draw_finished
 ld hl,$5bef
 dec (hl)
 jp nz,ac_blit_row
 or 1
 jp ac_exit
ac_draw_finished:
 ld a,($5bd0)
 ld hl,$5bea
 ld b,(hl)
 ld (hl),a
 xor b
 jr z,ac_exit
 xor a
 scf ; Z=finished, C=new front stage requires full dirty publication.
ac_exit:
 ld a,$18
 out ($f4),a
 jp assembly_cache_return
ac_phase_offsets:
 DW 0,357,714,1071,1428,1785,2142,2499
ac_rotate_table:
 DW ac_rot0,ac_rot1,ac_rot2,ac_rot3,ac_rot4,ac_rot5,ac_rot6,ac_rot7
ac_rot4: rrca
ac_rot3: rrca
ac_rot2: rrca
ac_rot1: rrca
ac_rot0: ret
ac_rot5: rlca
ac_rot6: rlca
ac_rot7: rlca
 ret
ac_home_source:
 DISP $df70
ac_home_prepare:
 ld a,(rects+22)
 or a
 ret z
 ld a,($5bd0)
 ld hl,$5bea
 cp (hl)
 jr z,ac_home_rects
 ld iy,rects+20
 call clear_object
ac_home_rects:
 ld hl,rects
 ld de,$b800
 ld bc,32
 ldir
ac_home_prepare_loop:
 ld a,2
 call ac_home_call
 jr nz,ac_home_prepare_loop
 ld a,3
 call assembly_cache_call
 ld hl,$b800
 ld de,rects
 ld bc,32
 ldir
 ret
ac_home_call:
 push af
 ld a,(face_x+1)
 and 7
 ld b,a
 ld hl,(rects+20)
 ld de,(rects+22)
 ld ix,($7ce4)
 pop af
 jp assembly_cache_call
 ASSERT $ == $dfbe
ac_home_dirty:
 ld a,(rects+21)
 ld l,a
 ld h,$79
 ld de,$be00
 ld a,(rects+23)
 ld c,a
 ld b,0
 push bc
 ldir
 ld a,(rects+21)
 ld l,a
 ld h,$7d
 ld de,$be40
 pop bc
 ldir
 ASSERT $ <= $dfe0
 DS $dfe0-$,0
ac_home_draw:
 ld a,1
 call assembly_cache_call
 jr nz,ac_home_draw
 ret nc
 ld iy,rects+20
 jp mark_object
ac_home_ship_clip:
 ASSERT $ == $dfef
 ld hl,$7c00
 ld de,$b800
 ld bc,108
 ldir
 ld l,3
 jp scene_sprite
ac_home_end:
 ASSERT $ <= $e000
 ENT
ac_home_length EQU ac_home_end-ac_home_prepare
 ASSERT $ <= assembly_cache_source+1792
