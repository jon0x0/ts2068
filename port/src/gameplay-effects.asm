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

; Four original IEXPLO frames, shared by workers and bomb impacts.
fx_explosion:
 ld a,(worker_x)
 and 7
 ld c,a
 ld a,($5c27)
 dec a
 and 24
 xor 24
 rrca
 rrca
 rrca
fx_arcade_explosion:
 add a,a
 ld l,a
 ld h,0
 ld de,fx_explosion_pointers
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ex de,hl
 ld de,fx_explosion_dictionary
 jp explosion_unpack
 INCLUDE "../build/explosion-art.asm"
