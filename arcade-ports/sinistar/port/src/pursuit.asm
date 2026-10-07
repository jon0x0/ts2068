; Direct-pursuit branch only: SINI -> NEWVELOCITY -> CHASE -> UPDSCREEN.
; Camera-relative Q8.8 object position, not the original scanner workspace.
; Caller supplies actual player velocity to CHASE until scanner wrappers exist.
sx EQU $7890
sy EQU $7892
svx EQU $7894
svy EQU $7896
oldface EQU $7898
newface EQU $789b
rendercount EQU $789e
scene_init:
 ld hl,$4000
 ld (sx),hl
 ld hl,$4800
 ld (sy),hl
 ld hl,scene_seeds
 ld de,$7e00
 ld bc,50
 ldir
 ret
pursuit_step:
 ld hl,(sx)
 ld de,($7874)
 add hl,de
 ld (sx),hl
 ld hl,(sy)
 ld de,($7864)
 add hl,de
 ld (sy),hl
 ; SCREENCHK adapter: current renderer has an object workspace only for a
 ; fully visible face. Keep camera displacement even while pursuit is stopped.
 xor a
 ld (sini_on_screen),a
 ld a,(sx+1)
 sub 24
 jr c,pursuit_visibility_done
 cp 200
 jr nc,pursuit_visibility_done
 ld a,126
 ld hl,sy+1
 sub (hl)
 jr c,pursuit_visibility_done
 cp 40
 jr c,pursuit_visibility_done
 cp 133
 jr nc,pursuit_visibility_done
 ld a,1
 ld (sini_on_screen),a
pursuit_visibility_done:
 call sini_stop_step
 ret c
; DISTANCE.SRC doubles long-axis integer coordinates, short remains pixels.
 ld a,(sy+1)
 ld l,a
 ld h,0
 ld a,(posy+1)
 ld e,a
 ld d,0
 or a
 sbc hl,de
 add hl,hl
 ld ix,sinistar_speeds
 call new_velocity
 push af
 ld de,(vely)
 ld bc,2047
 call chase_velocity
 ld de,(svy)
 pop af
 call smooth_velocity
 ld (svy),hl
 ld de,(sy)
 add hl,de
 ld (sy),hl
 ld a,(sx+1)
 ld l,a
 ld h,0
 ld a,(posx+1)
 ld e,a
 ld d,0
 or a
 sbc hl,de
 ld ix,sinistar_speeds
 call new_velocity
 push af
 add hl,hl
 ld de,(velx)
 ld bc,2047
 call chase_velocity
 ld de,(svx)
 pop af
 call smooth_velocity
 ld (svx),hl
 ld de,(sx)
 add hl,de
 ld (sx),hl
 ret

 INCLUDE "sini-stop.asm"

scene_seeds:
 INCLUDE "../build/star-seeds.asm"
