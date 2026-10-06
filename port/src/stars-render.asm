stars_clear_call:
 ld hl,world_extension+66
 jp world_call
stars_draw_call:
 ld hl,world_extension+69
 jp world_call
stars_attribute:
 ld a,$10
 ld ($78df),a
 out ($f4),a
 ld a,h
 xor $60
 ld h,a
 ld (hl),7
 ld a,$50
 ld ($78df),a
 out ($f4),a
 ret
