 DEFINE PLAYABLE_GAME
 DEFINE SCENE_FASTMATH 1
 ORG $8000
 DB $02,$02,$08,$80,$ef,$01,0,0
angle EQU $7828
frames EQU $782a
px EQU $7808
py EQU $780a
pvx EQU $780c
pvy EQU $780e
rock_alive EQU $7810
richter EQU $7811
mass EQU $7812
rock_x EQU $7813
rock_y EQU $7814
vib_tick EQU $7815
seed EQU $7816
bullet_alive EQU $7817
bx EQU $7818
by EQU $781a
bvx EQU $781c
bvy EQU $781e
crystal_alive EQU $7820
cx EQU $7822
cy EQU $7824
bombs EQU $7826
hits EQU $7827
releases EQU $782c
shattered EQU $782d
rects EQU $7840
oldrects EQU $7860
 INCLUDE "../build/title-origin.asm"
title_boot:
 di
 ld sp,$bfff
 ld a,$10
 out ($f4),a
 ld a,2
 out ($ff),a
 xor a
 out ($fe),a
 ld hl,$6000
 ld de,$6001
 ld bc,6143
 ld (hl),$42
 ldir
 ld a,$18
 out ($f4),a
 jp title_source
title_return:
 ld a,$10
 out ($f4),a
start:
 di
 ld sp,$bfff
 ld a,$18
 out ($f4),a
 ld hl,boot_source
 ld de,$b800
 ld bc,1024
 ldir
 jp $b800
start_resume:
 call game_init
 call speech_init
 ld hl,$7a00
 ld de,$7a01
 ld bc,256
 ld (hl),$7b
 ldir
 ld a,$c3
 ld ($7b7b),a
 ld hl,isr
 ld ($7b7c),hl
 ld a,$7a
 ld i,a
 im 2
 ei
loop:
 ld a,($7802)
 ld b,a
 ld a,($7806)
 cp b
 jr nz,physics
 halt
 jr loop
physics:
 inc a
 ld ($7806),a
 call game_step
 ld hl,(frames)
 inc hl
 ld (frames),hl
 ld a,($7802)
 ld b,a
 ld a,($7806)
 cp b
 jr nz,physics
frame_start:
 call render
frame_done:
 jp loop
isr:
 push af
 push bc
 push de
 push hl
 ld a,$10
 out ($f4),a
 ld ($5e70),sp
 ld sp,$5ed0
 call audio_tick
 ld sp,($5e70)
 ld a,($783f)
 or a
 jr z,border_idle
 ld hl,render_extension+12
 call incremental_call
border_idle:
 ld a,($78df)
 out ($f4),a
 ld a,($7802)
 inc a
 ld ($7802),a
 pop hl
 pop de
 pop bc
 pop af
 ei
 reti

game_step:
 call game_gate
 ret c
 call read_controls
 jr c,manual_target
 ld b,64
 ld hl,0
 ld (pvx),hl
 ld (pvy),hl
manual_target:
 ld a,(angle)
 ld c,127
 call player_turn
 ld (angle),a
 call player_sincos
 ld ($78e8),de
 ld hl,world_extension+99
 call world_call
move_player:
 call world_move_player
 call world_step
 call fire_input
 call bullet_step
 call vibration_step
 call crystal_step
 call worker_step
 call awakening_step
 call mining_pursuit_step
 call sinibomb_step
 call game_rules
 ret
signed_word:
 ld l,a
 add a,a
 sbc a,a
 ld h,a
 ret
fire_input:
 ld a,(bullet_alive)
 or a
 ret nz
 ld a,(control_mode)
 or a
 jr z,fire_shot
 ld bc,$7ffe
 in a,(c)
 bit 0,a
 jr z,fire_shot
 ld a,14
 out ($f5),a
 ld bc,$01f6
 in a,(c)
 bit 7,a
 ret nz
fire_shot:
 ld hl,world_extension+54
 call world_call
 ld hl,(px)
 ld de,6*256
 add hl,de
 ld (bx),hl
 ld hl,(py)
 add hl,de
 ld (by),hl
 ld de,($78e8)
 ld a,d
 call signed_word
 ; 12x unit vector: longer reach at the same 24-tick repeat interval.
 add hl,hl
 add hl,hl
 ld b,h
 ld c,l
 add hl,hl
 add hl,bc
 ld (bvx),hl
 ld a,e
 call signed_word
 ; 12x unit vector: longer reach at the same 24-tick repeat interval.
 add hl,hl
 add hl,hl
 ld b,h
 ld c,l
 add hl,hl
 add hl,bc
 ex de,hl
 ld hl,0
 or a
 sbc hl,de
 ld (bvy),hl
 ld a,1
 ld (bullet_alive),a
 jp sfx_shot
bullet_step:
 IFDEF PLAYABLE_GAME
 ld hl,world_extension+39
 jp world_call
 ELSE
 ld a,(game_mode)
 or a
 ld hl,world_extension+39
 jp nz,world_call
 ld a,(bullet_alive)
 or a
 ret z
 ld hl,(bx)
 ld de,(bvx)
 add hl,de
 ld (bx),hl
 ld a,h
 cp 248
 jr nc,kill_bullet
 ld hl,(by)
 ld de,(bvy)
 add hl,de
 ld (by),hl
 ld a,h
 cp 64
 jr c,kill_bullet
 cp 174
 jr nc,kill_bullet
 ld a,($586f)
 or a
 ret nz
 ld a,($586e)
 or a
 jr z,bullet_rock_sector
 ld a,(rock_x)
 cp 224
 ret c
bullet_rock_sector:
 ld a,(rock_alive)
 or a
 ret z
 ld a,(bx+1)
 ld hl,rock_x
 sub (hl)
 cp 26
 ret nc
 ld a,(by+1)
 ld hl,rock_y
 sub (hl)
 cp 28
 ret nc
 ld a,(mass)
 ld b,a
 ld a,(richter)
 call rock_add_vibration
 ld (richter),a
 ld hl,hits
 inc (hl)
 ENDIF
kill_bullet:
 xor a
 ld (bullet_alive),a
 ret
vibration_step:
 ld a,(rock_alive)
 or a
 ret z
 ld hl,vib_tick
 inc (hl)
 ld a,(hl)
 cp 12
 ret c
 ld (hl),0
 ld a,(crystal_alive)
 or a
 jr nz,vibration_damp
 ld a,(seed)
 add a,73
 ld (seed),a
 ld c,a
 ld a,(mass)
 ld b,a
 ld a,(richter)
 ld d,0
 call rock_try_crystal
 ld (richter),a
 ld a,b
 ld (mass),a
 jr nc,vibration_damp
 ld a,1
 ld (crystal_alive),a
 ld hl,releases
 inc (hl)
 ld a,(rock_x)
 add a,13
 ld h,a
 ld l,0
 ld (cx),hl
 ld a,(rock_y)
 add a,14
 ld h,a
 ld (cy),hl
 ld hl,world_extension+57
 call world_call
vibration_damp:
 ld a,(richter)
 ld c,1
 call rock_damp
 ld (richter),a
 ld a,b
 cp 2
 ret nz
 xor a
 ld (rock_alive),a
 ld a,1
 ld (shattered),a
 jp sfx_explosion
crystal_step:
 IFDEF PLAYABLE_GAME
 ld hl,world_extension+45
 jp world_call
 ELSE
 ld a,(game_mode)
 or a
 ld hl,world_extension+45
 jp nz,world_call
 ld a,(crystal_alive)
 cp 1
 ret nz
 ; Fixture supplies -127/256 horizontal launch drift, zero vertical.
 ld hl,(cx)
 ld de,-127
 add hl,de
 ld (cx),hl
 ld a,h
 cp 4
 jr c,kill_crystal
 ld a,(px+1)
 add a,6
 ld b,a
 ld a,h
 sub b
 add a,8
 cp 17
 ret nc
 ld a,(py+1)
 add a,6
 ld b,a
 ld a,(cy+1)
 sub b
 add a,8
 cp 17
 ret nc
 call sfx_pickup
 ld hl,bombs
 inc (hl)
 ld a,(game_mode)
 or a
 jr z,kill_crystal
 ld a,(hl)
 add a,2
 cp 25
 jr c,game_ammo_ok
 ld a,24
game_ammo_ok:
 ld (hl),a
 ld hl,crystals_taken
 inc (hl)
 ENDIF
kill_crystal:
 xor a
 ld (crystal_alive),a
 ret
 INCLUDE "gameplay.asm"
 INCLUDE "speech.asm"
 INCLUDE "sfx.asm"
 INCLUDE "sinibombs.asm"
 INCLUDE "mining-pursuit.asm"
 INCLUDE "chase.asm"
 INCLUDE "worker-fixture.asm"
 INCLUDE "assembly-cache-call.asm"
 INCLUDE "mining-render.asm"
 INCLUDE "mining.asm"
 INCLUDE "motion.asm"
 INCLUDE "player.asm"
 INCLUDE "world.asm"
 INCLUDE "stars-render.asm"
 INCLUDE "population-render.asm"
sprites:
 INCLUDE "../build/mining-pointers.asm"
 INCLUDE "explosion-unpack.asm"
 INCLUDE "../build/damage-pieces.asm"
audio_tick:
 ld a,$d0
 out ($f4),a
 call effects_origin+42
 ld a,$10
 out ($f4),a
 ret c
 call speech_tick
 jp sfx_tick
 INCLUDE "death-effects.asm"
end_code:
 ASSERT end_code <= $a000
 DS $a000-$,255
