 INCLUDE "../build/world-equ.asm"
 ORG world_extension
 jp wb_world_step
 jp wb_rock_next_velocity
 jp wb_worker_mine
 jp wb_rock_fully_visible
 jp speech_unpack
 jp wb_sinistar_hit
 jp wb_pursuit
 jp wb_move_player
 jp wb_project
 jp wb_restore
 jp wb_clip
 jp wb_clip_sprite
 jp wb_shift_assembly
 jp wb_bullet
 jp wb_worker
 jp wb_crystal
 jp wb_contact
 jp wb_stars_update
 jp wb_shot_high
 jp wb_crystal_high
 jp wb_bomb
 jp wb_star_overlap
 jp stars_clear
 jp stars_draw
 jp radar_entry
 jp wb_pop_begin
 jp wb_pop_clear
 jp wb_pop_draw
 jp wb_pop_finish
 jp wb_pop_overlap
 jp wb_awake_shift
 jp wb_pop_prepare
 jp wb_end_screen
wb_world_step:
 ld a,(game_mode)
 or a
 ret z
 ld hl,$5865
 inc (hl)
 call wb_population
 ld a,(rock_alive)
 or a
 ret z
 ld a,($586c)
 ld e,a
 ld d,0
 ld hl,wb_rock_speeds
 add hl,de
 ld a,(hl)
 inc hl
 push hl
 ld e,a
 add a,a
 sbc a,a
 ld d,a
 ld a,(rock_x)
 ld h,a
 ld a,($586a)
 ld l,a
 add hl,de
 ld a,l
 ld ($586a),a
 ld a,($586e)
 adc a,d
 and 1
 ld ($586e),a
 ld a,h
wb_world_x:
 ld (rock_x),a
 pop hl
 ld a,(hl)
 ld e,a
 add a,a
 sbc a,a
 ld d,a
 ld a,(rock_y)
 ld h,a
 ld a,($586b)
 ld l,a
 add hl,de
 ld a,l
 ld ($586b),a
 ld a,($586f)
 adc a,d
 and 1
 ld ($586f),a
 ld a,h
wb_world_y:
 ld (rock_y),a
 ret
wb_rock_next_velocity:
 ld a,($5bb2)
 or a
 jr z,wb_respawn_allowed
 xor a
 ld (rock_alive),a
 ret
wb_respawn_allowed:
 ld a,($586c)
 add a,2
 cp 18
 jr c,wb_world_index
 xor a
wb_world_index:
 ld ($586c),a
 ld a,(game_mode)
 or a
 ret z
 ld a,6
 call wb_get
 ld de,240
 add hl,de
 ld a,l
 ld (rock_x),a
 ld a,h
 and 1
 ld ($586e),a
 ld a,7
 call wb_get
 ld a,l
 ld (rock_y),a
 ld a,h
 ld ($586f),a
 xor a
 ld ($586a),a
 ld ($586b),a
 ret
 INCLUDE "../build/world-bank-speeds.asm"
wb_worker_mine:
 call wb_rock_fully_visible
 ret c
 ld a,(game_mode)
 or a
 ret z
 ld a,(rock_alive)
 or a
 ret z
 ld a,(rock_x)
 sub 8
 ld b,a
 ld hl,worker_x
 call worker_move
 ld a,(rock_y)
 add a,8
 ld b,a
 ld hl,worker_y
 call worker_move
 ld a,(rock_x)
 sub 8
 ld hl,worker_x
 cp (hl)
 ret nz
 ld a,(rock_y)
 add a,8
 ld hl,worker_y
 cp (hl)
 ret nz
 ld a,($5865)
 and 15
 ret nz
 ld a,(mass)
 ld b,a
 ld a,(richter)
 call rock_add_vibration
 ld (richter),a
 ret
wb_rock_fully_visible:
 ld a,(game_mode)
 or a
 ret z
 ld a,($586e)
 ld b,a
 ld a,($586f)
 or b
 scf
 ret nz
 ld a,(rock_x)
 cp 8
 ret c
 cp 209
 ccf
 ret c
 ld a,(rock_y)
 cp 72
 ret c
 cp 137
 ccf
 ret


; Lossless reconstruction of all thirteen written AY registers. Register 13
; is always 255 in these streams (no envelope restart), enforced at build time.
speech_unpack:
 ld hl,(speech_ptr)
 ld de,$5874
 ldi
 inc de
 ldi
 inc de
 ldi
 ld a,(hl)
 inc hl
 ld c,a
 and 15
 ld ($5877),a
 ld a,c
 rrca
 rrca
 rrca
 rrca
 and 15
 ld ($5875),a
 ld a,(hl)
 inc hl
 ld c,a
 and 15
 ld ($587c),a
 ld a,c
 rrca
 rrca
 rrca
 rrca
 and 15
 ld ($5879),a
 ld a,(hl)
 inc hl
 ld c,a
 and 15
 ld ($587e),a
 ld a,c
 rrca
 rrca
 rrca
 rrca
 and 15
 ld ($587d),a
 ld a,(hl)
 inc hl
 ld ($587b),a
 ld (speech_ptr),hl
 ld a,5
 ld ($587a),a
 ld a,1
 ld ($587f),a
 xor a
 ld ($5880),a
 ld hl,$5874
 ret

; COLLISIO SBOMB,SINI adds two stun decisions; SUBPART halves both
; signed screen velocities. No approximation to this arithmetic is needed.
wb_sinistar_hit:
 ld hl,(face_vx)
 sra h
 rr l
 ld (face_vx),hl
 ld hl,(face_vy)
 sra h
 rr l
 ld (face_vy),hl
 ld a,(sini_stun)
 add a,2
 ld (sini_stun),a
 ret

wb_pursuit:
 ld a,(bs_hits)
 cp 13
 ret nc
 ld a,(awake_done)
 or a
 ret z
 ld a,(game_mode)
 or a
 jr z,fp_think
 ld a,(sini_think_phase)
 inc a
 and 7
 ld (sini_think_phase),a
 jp nz,fp_integrate
 ld hl,sini_stun
 ld a,(hl)
 or a
 jr z,fp_think
 dec (hl)
 jr z,fp_think
 ld hl,0
 ld (face_vx),hl
 ld (face_vy),hl
 jp fp_integrate
fp_think:
 ld a,(game_mode)
 or a
 jr z,fp_old_x
 ld a,10
 ld c,6
 call wb_delta
 ld de,18
 add hl,de
 jr fp_x_speed
fp_old_x:
 ld a,(face_x+1)
 add a,24
 ld l,a
 ld h,0
 ld a,(px+1)
 add a,6
 ld e,a
 ld d,0
 or a
 sbc hl,de
fp_x_speed:
 ld ix,sinistar_speeds
 call new_velocity
 push af
 add hl,hl
 ld de,(pvx)
 ld bc,2047
 call chase_velocity
 ld de,(face_vx)
 pop af
 call smooth_velocity
 ld (face_vx),hl
 ld a,(game_mode)
 or a
 jr z,fp_old_y
 ld a,11
 ld c,7
 call wb_delta
 ld de,20
 add hl,de
 jr fp_y_speed
fp_old_y:
 ld a,(face_y+1)
 add a,26
 ld l,a
 ld h,0
 ld a,(py+1)
 add a,6
 ld e,a
 ld d,0
 or a
 sbc hl,de
fp_y_speed:
 add hl,hl
 ld ix,sinistar_speeds
 call new_velocity
 push af
 ld de,(pvy)
 ld bc,2047
 call chase_velocity
 ld de,(face_vy)
 pop af
 call smooth_velocity
 ld (face_vy),hl
fp_integrate:
 ld a,(game_mode)
 or a
 jr z,fp_old_integrate
 ld a,10
 ld de,(face_vx)
 call wb_integrate
 ld a,11
 ld de,(face_vy)
 jp wb_integrate
fp_old_integrate:
 ld hl,(face_vx)
 ld de,(face_x)
 add hl,de
 ld a,h
 cp 201
 jr c,fp_x_ok
 cp 248
 ld hl,200*256
 jr c,fp_x_ok
 ld hl,0
fp_x_ok:
 ld (face_x),hl
 ld hl,(face_vy)
 ld de,(face_y)
 add hl,de
 ld a,h
 cp 64
 jr nc,fp_y_upper
 ld hl,64*256
fp_y_upper:
 ld a,h
 cp 125
 jr c,fp_y_ok
 ld hl,124*256
fp_y_ok:
 ld (face_y),hl
 ret


wb_move_player:
 ld a,(game_mode)
 or a
 jr nz,wm_world
 ld hl,(px)
 ld de,(pvx)
 add hl,de
 ld a,h
 cp 8
 jr nc,wm_old_right
 ld hl,8*256
wm_old_right:
 ld a,h
 cp 233
 jr c,wm_old_xdone
 ld hl,232*256
wm_old_xdone:
 ld (px),hl
 ld hl,(py)
 ld de,(pvy)
 add hl,de
 ld a,h
 cp 64
 jr nc,wm_old_bottom
 ld hl,64*256
wm_old_bottom:
 ld a,h
 cp 161
 jr c,wm_old_ydone
 ld hl,160*256
wm_old_ydone:
 ld (py),hl
 ret
wm_world:
 ld hl,(px)
 ld de,(pvx)
 add hl,de
 ld (px),hl
 ld a,($7c96)
 adc a,0
 bit 7,d
 jr z,wm_xsign
 dec a
wm_xsign:
 and 1
 ld ($7c96),a
 ld hl,(py)
 ld de,(pvy)
 add hl,de
 ld (py),hl
 ld a,($7c97)
 adc a,0
 bit 7,d
 jr z,wm_ysign
 dec a
wm_ysign:
 and 1
 ld ($7c97),a
 ; Dead-zone camera: hard-scroll only at the safe player margins.
 ld a,(px+1)
 ld l,a
 ld a,($7c96)
 ld h,a
 ld de,($5884)
 ld bc,64*256+176
 call wm_camera
 ld ($5884),de
 ld a,(py+1)
 ld l,a
 ld a,($7c97)
 ld h,a
 ld de,($5886)
 ld bc,88*256+140
 call wm_camera
 ld ($5886),de
 ret
wm_camera:
 push hl
 or a
 sbc hl,de
 ld a,h
 and 1
 ld h,a
 jr nz,wm_low
 ld a,l
 cp b
 jr c,wm_low
 cp c
 jr nc,wm_high
 pop hl
 ret
wm_low:
 ld c,b
wm_high:
 pop hl
 ld b,0
 or a
 sbc hl,bc
 ld a,h
 and 1
 ld h,a
 ex de,hl
 ret

; Original integer coordinate bytes are restored after drawing. Physics never
; reads projected screen positions, and ISR does not advance game objects.
wb_project:
 ld a,(game_mode)
 or a
 ret z
 ld a,($586e)
 ld ($7c90),a
 ld a,($586f)
 ld ($7c91),a
 ld ix,wb_coordinates
 ld iy,$7c90
 ld b,14
wp_axis:
 push bc
 ld e,(ix+0)
 ld d,(ix+1)
 inc ix
 inc ix
 ld a,(de)
 ld (iy+16),a
 ld l,a
 ld h,(iy+0)
 bit 0,b
 jr nz,wp_y
 ld bc,($5884)
 jr wp_sub
wp_y:
 ld bc,($5886)
wp_sub:
 or a
 sbc hl,bc
 ld a,l
 ld (de),a
 ld a,h
 and 1
 ld (iy+32),a
 inc iy
 pop bc
 djnz wp_axis
 ld a,($7cb0)
 ld ($586e),a
 ld a,($7cb1)
 ld ($586f),a
 ret
wb_restore:
 ld a,(game_mode)
 or a
 ret z
 ld ix,wb_coordinates
 ld hl,$7ca0
 ld b,14
wr_axis:
 ld e,(ix+0)
 ld d,(ix+1)
 inc ix
 inc ix
 ld a,(hl)
 inc hl
 ld (de),a
 djnz wr_axis
 ld a,($7c90)
 ld ($586e),a
 ld a,($7c91)
 ld ($586f),a
 ret
wb_coordinates:
 DW rock_x,rock_y,cx+1,cy+1,bx+1,by+1,px+1,py+1
 DW worker_x,worker_y,face_x+1,face_y+1,bs_x,bs_y

; Clip seven byte rectangles; retain top/left source skips and original stride.
wb_clip:
 ld a,(game_mode)
 or a
 ret z
 ld iy,rects
 ld ix,$7cd0
 ld hl,$7cb0
 ld b,7
wc_object:
 push bc
 push hl
 ld a,(iy+2)
 ld (ix+2),a
 xor a
 ld (ix+0),a
 ld (ix+1),a
 ld a,(hl)
 ld (ix+3),a
 inc hl
 ld a,(hl)
 or a
 jr nz,wc_hidden
 ld a,(iy+2)
 or a
 jr z,wc_next
 ld a,(iy+1)
 cp 176
 jr nc,wc_hidden
 cp 64
 jr nc,wc_bottom
 neg
 add a,64
 ld (ix+0),a
 ld c,a
 ld a,(iy+3)
 sub c
 jr c,wc_hidden
 jr z,wc_hidden
 ld (iy+3),a
 ld (iy+1),64
wc_bottom:
 ld a,(iy+1)
 add a,(iy+3)
 cp 177
 jr c,wc_x
 ld a,176
 sub (iy+1)
 ld (iy+3),a
wc_x:
 ld a,(ix+3)
 or a
 jr z,wc_right
 ld a,32
 sub (iy+0)
 ld (ix+1),a
 ld c,a
 ld a,(iy+2)
 sub c
 jr c,wc_hidden
 jr z,wc_hidden
 ld (iy+2),a
 ld (iy+0),0
 jr wc_next
wc_right:
 ld a,(iy+0)
 add a,(iy+2)
 cp 33
 jr c,wc_next
 ld a,32
 sub (iy+0)
 ld (iy+2),a
 jr wc_next
wc_hidden:
 ld (iy+2),0
wc_next:
 ld de,4
 add iy,de
 add ix,de
 pop hl
 inc hl
 inc hl
 pop bc
 dec b
 jp nz,wc_object
 ret

wb_clip_sprite:
 ; A = object index. Source is staged at B800; output A/E/BC for blitter.
 add a,a
 add a,a
 ld l,a
 ld h,0
 push hl
 ld de,rects
 add hl,de
 push hl
 pop iy
 pop hl
 ld de,$7cd0
 add hl,de
 push hl
 pop ix
 ld a,(iy+2)
 or a
 scf
 ret z
 ld a,(game_mode)
 or a
 jr z,wcs_result
 ld a,(ix+0)
 or (ix+1)
 jr nz,wcs_pack
 ld a,(ix+2)
 cp (iy+2)
 jr z,wcs_result
wcs_pack:
 ld a,(ix+2)
 ld c,a
 add a,a
 add a,c
 ld ($588d),a
 ld a,(ix+0)
 ld b,a
 ld hl,$b800
 ld d,0
 ld a,($588d)
 ld e,a
 ld a,b
 or a
 jr z,wcs_left
wcs_top:
 add hl,de
 djnz wcs_top
wcs_left:
 ld a,(ix+1)
 ld e,a
 add a,a
 add a,e
 ld e,a
 add hl,de
 ld de,$b800
 ld a,(iy+3)
wcs_row:
 push af
 push hl
 ld a,(iy+2)
 ld c,a
 add a,a
 add a,c
 ld c,a
 ld b,0
 ldir
 pop hl
 ld a,($588d)
 ld c,a
 ld b,0
 add hl,bc
 pop af
 dec a
 jr nz,wcs_row
wcs_result:
 ld c,(iy+0)
 ld b,(iy+1)
 ld e,(iy+2)
 ld a,(iy+3)
 or a
 ret

wb_shift_assembly:
 or a
 ret z
 ld ($588f),a
wsa_phase:
 ld hl,$b800
 ld a,52
 ld ($5890),a
wsa_row:
 push hl
 ld b,7
 scf
wsa_mask:
 rr (hl)
 inc hl
 inc hl
 inc hl
 djnz wsa_mask
 pop hl
 push hl
 inc hl
 ld b,7
 or a
wsa_bits:
 rr (hl)
 inc hl
 inc hl
 inc hl
 djnz wsa_bits
 pop hl
 ld de,21
 add hl,de
 ld a,($5890)
 dec a
 ld ($5890),a
 jr nz,wsa_row
 ld hl,$588f
 dec (hl)
 jr nz,wsa_phase
 ; Carry the preceding cell's palette into newly exposed transparent cells.
 ld hl,$b800
 ld d,52
wsa_palette_row:
 ld b,7
 ld c,7
wsa_palette:
 ld a,(hl)
 inc hl
 inc hl
 cp 255
 jr z,wsa_palette_next
 ld a,(hl)
 cp 1
 jr nz,wsa_palette_keep
 ld (hl),c
wsa_palette_keep:
 ld c,(hl)
wsa_palette_next:
 inc hl
 djnz wsa_palette
 dec d
 jr nz,wsa_palette_row
 ret
 INCLUDE "world-actors.asm"
 INCLUDE "world-stars.asm"
 INCLUDE "world-population.asm"
 INCLUDE "radar.asm"
 INCLUDE "end-screen.asm"
