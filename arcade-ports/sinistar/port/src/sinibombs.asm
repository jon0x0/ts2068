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
 ld hl,world_extension+60
 jp world_call
; Independent four-picture impact object, centered on the actual bomb.
; 783C/D low coordinates; 7C9E/F high bits join normal world projection.
bomb_impact:
 ld a,(bs_x)
 sub 8
 ld ($783c),a
 ld a,($7c9c)
 sbc a,0
 and 1
 ld ($7c9e),a
 ld a,(bs_y)
 sub 10
 ld ($783d),a
 ld a,($7c9d)
 sbc a,0
 and 1
 ld ($7c9f),a
 ld a,4
 ld ($783e),a
 ret
bs_kill:
 xor a
 ld (bs_active),a
 ret

 INCLUDE "../build/sinibomb-speeds.asm"
