 ORG $8000
 DB $02,$02,$08,$80,$EF,$01,0,0
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
 ld ($7800),a
 ld ($7801),a
 ld ($7802),a
 ld ($7803),a
 out ($fe),a
 ld hl,$4000
 ld de,$4001
 ld bc,6143
 ld (hl),a
 ldir
 ld hl,$6000
 ld de,$6001
 ld bc,6143
 ld (hl),7
 ldir
; Tests are deliberately small here; host verifier exercises full domains.
 ld a,1
 ld ($7801),a
 ld hl,80
 ld ix,sinistar_speeds
 call new_velocity
 cp 1
 jp nz,failed
 ld de,-256
 or a
 sbc hl,de
 jp nz,failed
 ld a,2
 ld ($7801),a
 ld hl,-256
 ld de,0
 ld a,5
 call smooth_velocity
 ld de,-7
 or a
 sbc hl,de
 jp nz,failed
 ld a,3
 ld ($7801),a
 ld a,250
 ld b,6
 ld c,128
 call player_turn
 or a
 jp nz,failed
 ld a,$a5
 ld ($7800),a
 ld a,4
 out ($fe),a
; Genuine refresh interrupts exercise the resident-code/HOME stack contract.
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
idle:
 halt
 jr idle
failed:
 ld a,$ee
 ld ($7800),a
 ld a,2
 out ($fe),a
fail_loop:
 halt
 jr fail_loop
isr:
 push hl
 ld hl,($7802)
 inc hl
 ld ($7802),hl
 pop hl
 ei
 reti
 INCLUDE "motion.asm"
 INCLUDE "player.asm"
 INCLUDE "camera.asm"
 INCLUDE "chase.asm"
 INCLUDE "mining.asm"
end_code:
 ASSERT end_code <= $a000
 DS $a000-$,255
