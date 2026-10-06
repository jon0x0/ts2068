; Ownership/mission integration of COLLISIO crystal/worker and GivCrys.
; Motion is a one-pixel-per-tick fixture, not the arcade scanner/velocity engine.
worker_x EQU $78b0
worker_y EQU $78b1
worker_mission EQU $78b2
worker_alive EQU $78b3
worker_pickups EQU $78b4
worker_deliveries EQU $78b5
worker_caller EQU $78b6
assembly_count EQU $78b7
sinistar_built EQU $78bc
assembly_previous EQU $78b8
worker_delay EQU $78b9
assembly_target_x EQU $78ba
assembly_target_y EQU $78bb
; Stationary body origin; per-piece targets come from PIECETB.
assembly_x EQU 192
assembly_y EQU 80
worker_step:
 ld a,(game_mode)
 or a
 ld hl,world_extension+42
 jp nz,world_call
 ld a,(worker_alive)
 or a
 jp z,worker_resupply
 ld a,(worker_mission)
 cp 6
 jr z,worker_deliver
 ld a,(crystal_alive)
 cp 1
 jp nz,worker_mine
 ; The fixture assigns its sole free crystal (identity 1) to this worker.
 ld a,1
 ld (worker_caller),a
 ld a,4
 ld (worker_mission),a
 ld a,(cx+1)
 sub 4
 ld b,a
 ld hl,worker_x
 call worker_move
 ld a,(cy+1)
 sub 4
 ld b,a
 ld hl,worker_y
 call worker_move
 ld a,(cx+1)
 sub 4
 ld hl,worker_x
 cp (hl)
 ret nz
 ld a,(cy+1)
 sub 4
 ld hl,worker_y
 cp (hl)
 ret nz
 ; Only the assigned caller can be taken; never duplicate a free crystal.
 ld a,(worker_caller)
 cp 1
 ret nz
 ld a,2
 ld (crystal_alive),a
 ld a,6
 ld (worker_mission),a
 ld hl,worker_pickups
 inc (hl)
 jr worker_attach
worker_deliver:
 ld a,(assembly_count)
 cp 20
 ret nc
 add a,a
 ld l,a
 ld h,0
 ld de,assembly_targets
 add hl,de
 ld a,(hl)
 ld (assembly_target_x),a
 inc hl
 ld a,(hl)
 ld (assembly_target_y),a
 ld hl,worker_x
 ld a,(assembly_target_x)
 ld b,a
 call worker_move
 ld hl,worker_y
 ld a,(assembly_target_y)
 ld b,a
 call worker_move
 ld a,(worker_x)
 ld hl,assembly_target_x
 cp (hl)
 jr nz,worker_attach
 ld a,(worker_y)
 ld hl,assembly_target_y
 cp (hl)
 jr nz,worker_attach
 ; Delivery consumes carrier and crystal, as WORKER.SRC does after AddPart.
 ; Advance one outer piece, then consume the carrier.
worker_not_built_entry:
 ld hl,assembly_count
 inc (hl)
 ld a,(hl)
 cp 20
 jr nz,worker_not_built
 ld a,1
 ld (sinistar_built),a
 ; Only the diagnostic grants test ammunition.
 ld a,(game_mode)
 or a
 jr nz,worker_not_built
 ld a,13
 ld (bombs),a
worker_not_built:
 ld a,60
 ld (worker_delay),a
 xor a
 ld (crystal_alive),a
 ld (worker_alive),a
 ld (worker_mission),a
 ld (worker_caller),a
 ld hl,worker_deliveries
 inc (hl)
 jp sfx_assembly
worker_attach:
 ld a,(worker_x)
 add a,4
 ld h,a
 ld l,0
 ld (cx),hl
 ld a,(worker_y)
 sub 2
 ld h,a
 ld (cy),hl
 ret
worker_move:
 ld a,(hl)
 cp b
 ret z
 jr c,worker_increase
 dec (hl)
 ret
worker_increase:
 inc (hl)
 ret

; Deterministic test supply after the first genuinely mined crystal.
; This is not the arcade worker spawner or resource economy.
worker_resupply:
 ld a,(assembly_count)
 or a
 ret z
 cp 20
 ret nc
 ld hl,worker_delay
 ld a,(hl)
 or a
 jr z,worker_supply_ready
 dec (hl)
 ret nz
worker_supply_ready:
 ld a,(game_mode)
 or a
 jr z,worker_fixture_supply
 ld a,1
 ld (worker_alive),a
 ret
worker_fixture_supply:
 ld a,(crystal_alive)
 or a
 ret nz
 ld a,184
 ld (worker_x),a
 ld a,80
 ld (worker_y),a
 ld hl,152*256
 ld (cx),hl
 ld hl,114*256
 ld (cy),hl
 ld a,1
 ld (crystal_alive),a
 ld (worker_alive),a
 ret
 INCLUDE "../build/assembly-targets.asm"

; Original AniSC2 mouth positions/durations, advanced once per physics tick.
; AY speech is started by the ISR; arcade off-sector/death gates remain pending.
awake_mouth EQU $78bd
awake_timer EQU $78be
awake_previous EQU $78bf
awake_index EQU $78c0
awake_done EQU $78c1
eye_phase EQU $78c2
eye_timer EQU $78c3
eye_previous EQU $78c4
awakening_step:
 ld a,(sinistar_built)
 or a
 ret z
 call eyebrow_step
 ld a,(awake_done)
 or a
 ret nz
 ld hl,awake_timer
 ld a,(hl)
 or a
 jr z,awake_next
 dec (hl)
 ret nz
awake_next:
 ld a,(awake_index)
 ld l,a
 ld h,0
 ld de,awakening_sequence
 add hl,de
 ld a,(hl)
 cp 255
 jr z,awake_end
 ld (awake_mouth),a
 inc hl
 ld a,(hl)
 ld (awake_timer),a
 ld hl,awake_index
 inc (hl)
 inc (hl)
 ret
awake_end:
 ld a,1
 ld (awake_done),a
 ret
 INCLUDE "../build/awakening-sequence.asm"

; Task16-style cadence adapter; source cycles AEYE1,2,3 independently of speech.
eyebrow_step:
 ld hl,eye_timer
 inc (hl)
 ld a,(hl)
 cp 16
 ret c
 ld (hl),0
 ld hl,eye_phase
 inc (hl)
 ld a,(hl)
 cp 3
 ret c
 ld (hl),0
 ret
