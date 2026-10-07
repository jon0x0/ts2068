 INCLUDE "../build/boot-equ.asm"
 ORG boot_source
 DISP $b800
 di
 ld sp,$7fff
 ld a,$10
 out ($f4),a
 ld a,2
 out ($ff),a
 xor a
 out ($fe),a
 ld a,$c3
 ld ($7be0),a
 xor a
 ld hl,$7800
 ld de,$7801
 ld bc,255
 ld (hl),a
 ldir
 ld hl,$e000
 ld ($78f0),hl
 xor a
 ld ($580f),a
 ld a,7
 out ($f5),a
 ld a,$3f
 out ($f6),a
 ld hl,$a000
 ld de,$a001
 ld bc,6143
 ld (hl),0
 ldir
 ld hl,$4000
 ld de,$4001
 ld bc,6143
 ld (hl),0
 ldir
 ld hl,$c000
 ld de,$c001
 ld bc,6143
 ld (hl),7
 ldir
 ld hl,$6000
 ld de,$6001
 ld bc,6143
 ld (hl),7
 ldir
 ld a,$93
 ld ($78df),a
 out ($f4),a
 ld hl,ship_dictionary_source
 ld de,$c000
 ld bc,765
 ldir
 ld a,$10
 ld ($78df),a
 out ($f4),a
 INCLUDE "../build/fast-cache-init.asm"
 INCLUDE "../build/sfx-cache-init.asm"
 INCLUDE "../build/home-render-init.asm"
 INCLUDE "../build/roar-init.asm"
 xor a
 ld ($7f53),a
 INCLUDE "../build/assembly-home-init.asm"
 ld hl,$5bb1
 ld de,$5bb2
 ld bc,29
 ld (hl),0
 ldir
 ld a,2
 ld ($5bcb),a ; Background stars are occluded; player remains visible.
 ld hl,$5bd0
 ld de,$5bd1
 ld bc,111
 ld (hl),0
 ldir
 ld a,$80
 ld ($5bd3),a
 ld hl,192*256
 ld (face_x),hl
 ld hl,80*256
 ld (face_y),hl
 ld hl,72*256
 ld (px),hl
 ld hl,112*256
 ld (py),hl
 ld a,64
 ld (angle),a
 ld a,1
 ld (rock_alive),a
 ld a,96
 ld (mass),a
 ld a,152
 ld (rock_x),a
 ld a,100
 ld (rock_y),a
 ld a,17
 ld (seed),a
 ld a,184
 ld (worker_x),a
 ld a,80
 ld (worker_y),a
 ld a,1
 ld (worker_alive),a
 xor a
 ld (sini_think_phase),a
 ld (sini_stun),a
 ld hl,$7c90
 ld de,$7c91
 ld bc,95
 ld (hl),0
 ldir
 ld hl,$5884
 ld de,$5885
 ld bc,47
 ld (hl),0
 ldir
 jp start_resume
 ENT
