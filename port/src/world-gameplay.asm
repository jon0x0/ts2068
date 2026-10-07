; Gameplay state in formerly unused HOME 5C24..5C3F.
; 24 worker kills, 25 bounce recovery, 26 SFX hold, 27 explosion ticks,
; 29..2A worker score (150 per kill; HUD score display remains pending).
wb_thrust:
 ld hl,$5c25
 ld a,(hl)
 or a
 jr z,wb_thrust_ready
 dec (hl)
 ret
wb_thrust_ready:
 ld a,(control_power)
 or a
 ret z
 ld a,($78e9)
 call signed_word
 add hl,hl
 add hl,hl
 ld de,(pvx)
 ld c,127
 call player_accelerate
 ld (pvx),hl
 ld a,($78e8)
 cpl
 call signed_word
 inc hl
 add hl,hl
 add hl,hl
 ld de,(pvy)
 ld c,127
 call player_accelerate
 ld (pvy),hl
 ret

wb_planet_bounce:
 ld l,(ix+0)
 ld h,(ix+1)
 ld e,(ix+2)
 ld d,(ix+3)
 ld a,(ix+6)
wb_bounce_call:
 ; Cheap necessary X condition before switching ROM banks. The full 9-bit
 ; wrapped X/Y test still runs for candidates, including opposite sectors.
 ld c,a
 ld a,(px+1)
 sub l
 add a,10
 cp 34
 ret nc
 ld a,($5c2b) ; Nonzero disables planetoid bounce for keyboard play.
 or a
 ret nz
 ld a,c
 push af
 ld a,$d0
 ld ($78df),a
 out ($f4),a
 pop af
 call effects_origin+6
 ld a,$50
 ld ($78df),a
 out ($f4),a
 ret

wb_explosion_sprite:
 ld a,(worker_alive)
 cp 2
 ret nz
 ld a,$d0
 ld ($78df),a
 out ($f4),a
 call effects_origin+9
 ld a,$50
 ld ($78df),a
 out ($f4),a
 ret

wb_worker_hit:
 ld a,(worker_alive)
 cp 1
 ret nz
 ld a,4
 ld c,8
 call wb_delta
 ld de,1
 add hl,de
 ld a,h
 or a
 ret nz
 ld a,l
 cp 12
 ret nc
 ld a,5
 ld c,9
 call wb_delta
 ld de,1
 add hl,de
 ld a,h
 or a
 ret nz
 ld a,l
 cp 14
 ret nc
 ld a,(worker_mission)
 cp 6
 jr nz,wb_worker_explode
 ld a,1
 ld (crystal_alive),a
wb_worker_explode:
 call worker_impact_origin
 ld a,2
 ld (worker_alive),a
 ld a,32
 ld ($5c27),a
 ld hl,$5c24
 inc (hl)
 ld hl,($5c29)
 ld de,150
 add hl,de
 ld ($5c29),hl
 xor a
 ld (worker_mission),a
 call sfx_explosion
 jp kill_bullet

wb_worker_dying:
 ld hl,$5c27
 dec (hl)
 ret nz
 xor a
 ld (worker_alive),a
 ld a,180
 ld (worker_delay),a
 ret

; ISR may interrupt the comparison stream with SP in HOME E000-FFFF.
; Keep the audio decoder in DOCK6: mapping DOCK7 would hide that stack.
wb_sfx_frame:
 ld e,0
 ld a,(hl)
 inc hl
 call wb_ay_write
 ld d,(hl)
 inc hl
 ld a,d
 and 15
 ld e,8
 call wb_ay_write
 ld a,d
 rrca
 rrca
 rrca
 rrca
 and 15
 ld e,1
 call wb_ay_write
 ld d,(hl)
 inc hl
 ld a,d
 srl a
 srl a
 ld e,6
 call wb_ay_write
 ld a,d
 and 1
 or $36
 ld e,a
 ld a,d
 and 2
 rlca
 rlca
 or e
 ld e,7
wb_ay_write:
 ld bc,$fff5
 out (c),e
 inc c
 out (c),a
 ret
