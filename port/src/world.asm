; Original SCIVELT directions in a persistent 512x512 coordinate domain.
; Native dead-zone camera projects the wrapped world into the clipped viewport.
; Original FINON: S/2 and L/4 pixels/tick. Adaptation: X 256/304,
; Y 112/256, yielding 108/256 X and 28/256 Y (L is bottom-up).
 INCLUDE "../build/world-origin.asm"
sinistar_hit_response:
 ld hl,world_extension+15
 jr world_call
world_step:
 ld hl,world_extension
 jr world_call
rock_next_velocity:
 ld hl,world_extension+3
 jr world_call
worker_mine:
 ld hl,world_extension+6
 jr world_call
rock_fully_visible:
 ld hl,world_extension+9
world_call:
 push af
 ld a,$50
 ld ($78df),a
 out ($f4),a
 pop af
 call world_dispatch
 push af
 ld a,$10
 ld ($78df),a
 out ($f4),a
 pop af
 ret
world_dispatch:
 jp (hl)
radar_step:
 ld a,(game_mode)
 or a
 ret z
 ld a,($7802)
 ld hl,$5867
 sub (hl)
 cp 24
 ret c
 ld a,($7802)
 ld (hl),a
 ld hl,world_extension+72
 jp world_call
radar_publish:
 ld a,($5868)
 or a
 ret z
 ld b,a
 xor a
 ld ($5868),a
 ld hl,$5ea0
radar_write:
 ld e,(hl)
 inc hl
 ld d,(hl)
 inc hl
 ld a,(hl)
 inc hl
 ld (de),a
 djnz radar_write
radar_published:
 ret

world_move_player:
 ld hl,world_extension+21
 jp world_call
world_project:
 ld hl,world_extension+24
 jp world_call
world_restore:
 ld hl,world_extension+27
 jp world_call
world_clip:
 ld hl,world_extension+30
 jp world_call
scene_sprite:
 ld a,l
 ld hl,world_extension+33
 call world_call
 ret c
 jp draw_sprite
