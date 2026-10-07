; Playable fixed-screen rules. The diagnostic sequence uses game_mode=0.
game_mode EQU $782e
game_status EQU $782f ; 0 playing, 1 won, 2 lost
lives EQU $7838
invulnerable EQU $7839
rock_respawn EQU $783a
crystals_taken EQU $783b
game_init:
 xor a
 ld ($7bfb),a
 ld a,1
 ld (game_mode),a
 ld (control_mode),a
 ld a,3
 ld (lives),a
 ld (bombs),a
 ld a,($5e7b)
 or a
 ret z
 xor a
 ld (bombs),a
 ret
game_gate:
 ld a,($7bfb)
 or a
 jp nz,death_tick
 ld hl,world_extension+120
 call world_call
 ret c
 ld a,(game_status)
 or a
 ret z
 ld hl,world_extension+96
 jp world_call
game_rules:
 ld a,(game_mode)
 or a
 ret z
 ld a,(bs_hits)
 cp 13
 jr c,game_contact
 ld a,2
 jp death_start
game_contact:
 ld hl,invulnerable
 ld a,(hl)
 or a
 jr z,game_vulnerable
 dec (hl)
 jr game_resources
game_vulnerable:
 ld a,(awake_done)
 or a
 jr z,game_resources
 ; Ship center inside the face's inner contact rectangle.
 ld hl,world_extension+48
 call world_call
 jr nc,game_resources
game_touch:
 ld a,1
 jp death_start
game_death_done:
 xor a
 ld (sini_stun),a
 ld hl,0
 ld (face_vx),hl
 ld (face_vy),hl
 ld hl,lives
 dec (hl)
 call speech_death
 jr nz,game_respawn
 ld a,2
 ld (game_status),a
 ret
game_respawn:
 xor a
 ld ($7c96),a
 ld ($7c97),a
 ld a,180
 ld (invulnerable),a
 ld hl,8*256
 ld (px),hl
 ld hl,152*256
 ld (py),hl
 ld hl,0
 ld (pvx),hl
 ld (pvy),hl
 ; Preserve earned ammunition and active target damage.
game_resources:
 ld a,(rock_alive)
 or a
 ret nz
 ld hl,rock_respawn
 inc (hl)
 ld a,(hl)
 cp 90
 ret c
 ld (hl),0
 ld a,1
 ld (rock_alive),a
 ld a,96
 ld (mass),a
 xor a
 ld (richter),a
 ld (vib_tick),a
 jp rock_next_velocity
