; HL/DE rock origin, A direction. Heavy-rock collision approximation:
; reflect approaching player velocity in the rock's moving reference frame.
; Both axes use wrapped world coordinates; broad-phase only, no pixel tests.
fx_bounce:
 ld c,a
 ld a,($5c25)
 or a
 ret nz
 push de
 ld a,(px+1)
 ld e,a
 ld a,($7c96)
 ld d,a
 ex de,hl
 or a
 sbc hl,de
 ld de,10
 add hl,de
 ld a,h
 and 1
 jr nz,fx_no_contact
 ld a,l
 cp 34
 jr nc,fx_no_contact
 sub 17
 ld b,a
 pop de
 ld a,(py+1)
 ld l,a
 ld a,($7c97)
 ld h,a
 or a
 sbc hl,de
 ld de,10
 add hl,de
 ld a,h
 and 1
 ret nz
 ld a,l
 cp 36
 ret nc
 sub 18
 ld d,a
 bit 7,a
 jr z,fx_abs_y
 neg
fx_abs_y:
 ld e,a
 ld a,b
 bit 7,a
 jr z,fx_abs_x
 neg
fx_abs_x:
 cp e
 ld hl,pvx
 ld a,b
 jr nc,fx_axis
 ld hl,pvy
 inc c
 ld a,d
fx_axis:
 ld b,a
 push hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 push de
 ld l,c
 ld h,0
 ld de,fx_rock_speeds
 add hl,de
 ld a,(hl)
 call signed_word
 ex de,hl
 pop hl
 or a
 sbc hl,de
 ; Relative velocity must point toward the rock, not away from contact.
 ld a,h
 xor b
 jp p,fx_bounce_reject
 ; v' = rock velocity - (player velocity - rock velocity).
 ex de,hl
 or a
 sbc hl,de
 ex de,hl
 pop hl
 ld (hl),e
 inc hl
 ld (hl),d
 ld a,8
 ld ($5c25),a
 ret
fx_bounce_reject:
 pop hl
 ret
fx_no_contact:
 pop de
 ret
fx_rock_speeds:
 INCLUDE "../build/effect-rock-speeds.asm"

; Eight precomputed fragment positions per frame; only the selected byte's
; pixel mask is shifted at staging time. Reuses the worker's 12x12 rectangle.
fx_explosion:
 ld hl,$b800
 ld (hl),255
 inc hl
 ld (hl),0
 inc hl
 ld (hl),$46
 ld hl,$b800
 ld de,$b803
 ld bc,105
 ldir
 ld a,($5c27)
 dec a
 and 24
 xor 24
 add a,a
 ld l,a
 ld h,0
 ld de,fx_particles
 add hl,de
 push hl
 pop ix
 ld b,8
fx_particle:
 push bc
 ld a,(worker_x)
 and 7
 add a,(ix+0)
 ld c,a
 and 7
 ld b,a
 ld a,$80
 jr z,fx_particle_mask
fx_particle_shift:
 rrca
 djnz fx_particle_shift
fx_particle_mask:
 ld e,a
 ld a,c
 srl a
 srl a
 srl a
 ld c,a
 ld a,(ix+1)
 add a,a
 add a,(ix+1)
 add a,c
 ld c,a
 add a,a
 add a,c
 ld l,a
 ld h,$b8
 ld a,e
 cpl
 and (hl)
 ld (hl),a
 inc hl
 ld a,e
 or (hl)
 ld (hl),a
 inc ix
 inc ix
 pop bc
 djnz fx_particle
 ret
fx_particles:
 DB 4,4,6,4,8,4,4,6,8,6,4,8,6,8,8,8
 DB 3,3,6,3,9,3,3,6,9,6,3,9,6,9,9,9
 DB 2,2,6,2,10,2,2,6,10,6,2,10,6,10,10,10
 DB 1,1,6,1,11,1,1,6,11,6,1,11,6,11,11,11

