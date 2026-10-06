; Original speed/acceleration table with screen-coordinate collision adapters.
bs_px EQU $7830
bs_py EQU $7832
bs_vx EQU $7834
bs_vy EQU $7836
bs_active EQU $78a8
bs_x EQU bs_px+1
bs_y EQU bs_py+1
bs_fuel EQU $78ab
bs_hits EQU $78ac
bs_fired EQU $78ad
bs_expired EQU $78ae
sinibomb_step:
 ld a,(game_mode)
 or a
 ld hl,world_extension+60
 jp nz,world_call
 ld a,(bs_active)
 or a
 jr nz,bs_move
 ld a,(bombs)
 or a
 ret z
 ld bc,$7ffe
 in a,(c)
 bit 4,a
 ret nz
 ld hl,bombs
 dec (hl)
 ld hl,bs_fired
 inc (hl)
 ld a,(px+1)
 add a,6
 ld (bs_x),a
 ld h,a
 ld l,0
 ld (bs_px),hl
 ld a,(py+1)
 ld (bs_y),a
 ld h,a
 ld l,0
 ld (bs_py),hl
 ld hl,0
 ld (bs_vx),hl
 ld (bs_vy),hl
 ld a,180
 ld (bs_fuel),a
 ld a,1
 ld (bs_active),a
 jp sfx_bomb
bs_move:
 ld hl,bs_fuel
 dec (hl)
 jr nz,bs_track
 ld hl,bs_expired
 inc (hl)
 jp bs_kill
bs_track:
 ld a,(sinistar_built)
 or a
 ret z
 ld a,(bs_hits)
 cp 13
 ret nc
 ld a,(bs_x)
 ld l,a
 ld h,0
 ld a,(face_x+1)
 add a,24
 ld e,a
 ld d,0
 or a
 sbc hl,de
 ld ix,bomb_speeds
 call new_velocity
 add hl,hl
 ld de,(bs_vx)
 call smooth_velocity
 ld (bs_vx),hl
 ld de,(bs_px)
 add hl,de
 ld (bs_px),hl
 ld a,h
 cp 248
 jp nc,bs_kill
 ld (bs_x),a
 ld a,(bs_y)
 ld l,a
 ld h,0
 ld a,(face_y+1)
 add a,26
 ld e,a
 ld d,0
 or a
 sbc hl,de
 add hl,hl
 ld ix,bomb_speeds
 call new_velocity
 ld de,(bs_vy)
 call smooth_velocity
 ld (bs_vy),hl
 ld de,(bs_py)
 add hl,de
 ld (bs_py),hl
 ld a,h
 cp 64
 jp c,bs_kill
 cp 170
 jp nc,bs_kill
 ld (bs_y),a

 ld a,(face_x+1)
 add a,24
 ld hl,bs_x
 sub (hl)
 add a,4
 cp 9
 ret nc
 ld a,(face_y+1)
 add a,26
 ld hl,bs_y
 sub (hl)
 add a,4
 cp 9
 ret nc
 ld hl,bs_hits
 inc (hl)
 call sinistar_hit_response
 call speech_hit
bs_kill:
 xor a
 ld (bs_active),a
 ret

 INCLUDE "../build/sinibomb-speeds.asm"
