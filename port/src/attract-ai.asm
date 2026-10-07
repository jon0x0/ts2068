; AMSINI's mine/collect -> bomber missions, adapted to one worker slot.
; Native world coordinates; no input replay and no emulator-side injection.
front_ai:
 ld a,(frames)
 and 7
 ret nz
 ld a,1
 ld ($5c2b),a ; autonomous miner must not bounce off its target
 ld a,(front_demo)
 cp 3
 jp z,front_ai_end
 cp 2
 jr z,front_bomber
 ld a,(bombs)
 cp 4
 jr nc,front_begin_bomb
 ld a,(frames+1)
 cp 4
 jr nc,front_begin_bomb
 xor a
 ld (control_mode),a
 ld c,0
 ld de,32
 ld a,(crystal_alive)
 cp 1
 jr nz,front_miner
 ld c,2
 ld de,4
front_miner:
 push bc
 push de
 ld a,6
 call wb_delta
 pop de
 add hl,de
 call front_velocity
 ld (pvx),hl
 pop bc
 inc c
 ld a,7
 call wb_delta
 ld de,-8
 add hl,de
 call front_velocity
 ld (pvy),hl
 ld a,64
 ld (angle),a
 ret
front_begin_bomb:
 ld a,2
 ld (front_demo),a
front_bomber:
 dec a
 ld (control_mode),a
 ; Source launches crystal carriers during bombing. Serialize them through
 ; the port's worker slot; each still flies in and calls the real AddPart.
 ld a,(assembly_count)
 cp 20
 jr nc,front_orbit
 ld a,(worker_mission)
 cp 6
 jr z,front_orbit
 ld a,(worker_delay)
 or a
 jr nz,front_orbit
 ld a,6
 ld (worker_mission),a
 ld a,1
 ld (worker_alive),a
 ld a,2
 ld (crystal_alive),a
 ; Cycle entry sides around Sinistar rather than replaying one short diagonal.
 ; Signed full-world addition handles wrapping correctly at sector edges.
 ld a,(assembly_count)
 and 3
 add a,a
 ld l,a
 ld h,0
 ld de,front_carrier_offsets
 add hl,de
 ld a,(hl)
 inc hl
 push hl
 ld c,10
 call front_carrier_axis
 ld (worker_x),a
 ld a,h
 and 1
 ld ($7c98),a
 pop hl
 ld a,(hl)
 ld c,11
 call front_carrier_axis
 ld (worker_y),a
 ld a,h
 and 1
 ld ($7c99),a
front_orbit:
 ld a,(sinistar_built)
 or a
 jr z,front_orbit_move
 ld a,(bombs)
 ld hl,bs_active
 or (hl)
 jr nz,front_orbit_move
 ld a,3
 ld (front_demo),a
 ld hl,(frames)
 ld (front_end_tick),hl
front_ai_end:
 ld hl,(frames)
 ld de,(front_end_tick)
 or a
 sbc hl,de
 ld de,180
 sbc hl,de
 ret c
 jp title_boot
front_orbit_move:
 ld a,(frames)
 rrca
 rrca
 rrca
 ld b,a
 ld a,(frames+1)
 rlca
 rlca
 rlca
 rlca
 rlca
 or b
 call player_sincos
 push de
 ld a,6
 ld c,10
 call wb_delta
 pop de
 push de
 ld a,d
 sra a
 call front_orbit_axis
 ld (pvx),hl
 ld a,7
 ld c,11
 call wb_delta
 pop de
 ld a,e
 sra a
 sra a
 sra a
 call front_orbit_axis
 ld (pvy),hl
 ret
front_orbit_axis:
 ld e,a
 add a,a
 sbc a,a
 ld d,a
 add hl,de
 ld de,-18
 add hl,de
front_velocity:
 ; Same newvel selection kernel as the arcade, with screen-space thresholds.
 ld ix,front_speeds
 jp new_velocity
front_speeds:
 DW 128,768
 DB 3
 DW 32,384
 DB 3
 DW 8,128
 DB 2
 DW 2,64
 DB 1
 DW 0,0
 DB 0

front_carrier_axis:
 ld e,a
 add a,a
 sbc a,a
 ld d,a
 push de
 ld a,c
 call wb_get
 pop de
 add hl,de
 ld a,l
 ret
front_carrier_offsets:
 DB -36,-24,36,-24,36,24,-36,24
