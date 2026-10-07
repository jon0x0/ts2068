 ORG $8000
 DB $02,$02,$08,$80,$EF,$01,0,0
posx EQU $7870
posy EQU $7860
velx EQU $7872
vely EQU $7862
angle EQU $7828
frames EQU $782a
oldxy EQU $782c
newxy EQU $782e
delta EQU $7830
unit EQU $7831
start:
 di
 ld sp,$7fff
 ld a,$10
 ld ($7804),a
 out ($f4),a
 ld a,2
 ld ($7805),a
 out ($ff),a
 xor a
 ld ($7802),a
 ld ($7806),a
 out ($fe),a
 ld hl,$7820
 ld de,$7821
 ld bc,143
 ld (hl),a
 ldir
 ld hl,$e000
 ld de,$e001
 ld bc,6143
 ld (hl),a
 ldir
 call scene_init
 ld hl,$e000
 ld de,$a000
 ld bc,6144
 ldir
 ld hl,$e000
 ld de,$4000
 ld bc,6144
 ldir
 ld hl,$c000
 ld de,$c001
 ld bc,6143
 ld (hl),7
 ldir
 ld hl,$c000
 ld de,$6000
 ld bc,6144
 ldir
 ld hl,$7b00
 ld (posx),hl
 ld hl,$3800
 ld (posy),hl
 ld a,1
 ld ($7877),a
 ld hl,$600f
 ld (oldxy),hl
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
 call flight_step
 call pursuit_step
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
 ld hl,(rendercount)
 inc hl
 ld (rendercount),hl
 jr loop

flight_step:
; Automated joystick direction advances 1 angle unit every 2 refreshes.
; This drives the ported routines, not precomputed positions or velocities.
 ld hl,(frames)
 srl h
 rr l
 ld b,l
 ld a,(angle)
 ld c,a
 ld a,b
 sub c
 ld (delta),a
 ld a,c
 ld c,127
 call player_turn
 ld (angle),a
 call player_sincos
 ld (unit),de
 ld a,e
 ld ($7866),a
 ld a,d
 ld ($7876),a
 ld a,(delta)
 add a,$20
 cp $40
 jr nc,integrate
 ld a,(unit)
 ld l,a
 add a,a
 sbc a,a
 ld h,a
 add hl,hl
 add hl,hl
 ld de,(vely)
 ld c,127
 call player_accelerate
 ld (vely),hl
 ld a,(unit+1)
 ld l,a
 add a,a
 sbc a,a
 ld h,a
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,(velx)
 ld c,127
 call player_accelerate
 ld (velx),hl
integrate:
 ld ix,$7860
 call camera_axis
 ld ix,$7870
 call camera_axis
 ld de,($7864)
 ld hl,$7880
 call camera_integrate
 ld de,($7874)
 ld hl,$7883
 call camera_integrate
 ld hl,(posx)
 ld de,(velx)
 add hl,de
 ld de,($7874)
 add hl,de
 ld (posx),hl
 ld a,h
 srl a
 srl a
 srl a
 ld (newxy),a
 ld hl,(posy)
 ld de,(vely)
 add hl,de
 ld de,($7864)
 add hl,de
 ld (posy),hl
 ld a,152
 sub h
 ld (newxy+1),a
 ret

; Input BC=(y, byte-x), output HL=nonlinear offset. BC preserved.
offset:
 ld a,b
 and $c0
 rrca
 rrca
 rrca
 ld h,a
 ld a,b
 and 7
 or h
 ld h,a
 ld a,b
 and $38
 rlca
 rlca
 or c
 ld l,a
 ret

 INCLUDE "scene-render.asm"
isr:
 push af
 ld a,($7802)
 inc a
 ld ($7802),a
 pop af
 ei
 reti
 INCLUDE "motion.asm"
 INCLUDE "player.asm"
 INCLUDE "camera.asm"
 INCLUDE "pursuit.asm"
 INCLUDE "chase.asm"
faces:
 INCLUDE "../build/face-pointers.asm"
sprites:
 INCLUDE "../build/sprite-pointers.asm"
end_code:
 ASSERT end_code <= $a000
 DS $a000-$,255
