; Original SAM/FUNCTION.SRC SINCOS, exact table/XOR quadrant semantics.
; A=angle, returns D=sine, E=cosine as signed bytes. Clobbers AF/BC/HL.
player_sincos:
 ld c,a
 and $c0
 rrca
 rrca
 rrca
 rrca
 ld l,a
 ld h,0
 ld de,quadrants
 add hl,de
 ld a,c
 xor (hl)
 ld c,a
 inc hl
 ld b,(hl)
 inc hl
 ld e,(hl)
 ld hl,sines
 ld a,l
 add a,c
 ld l,a
 jr nc,psc_no_carry
 inc h
psc_no_carry:
 ld a,(hl)
 xor b
 ld d,a
 ld a,c
 xor $3f
 ld c,a
 ld b,0
 ld hl,sines
 add hl,bc
 ld a,(hl)
 xor e
 ld e,d
 ld d,a
 ret

; SAM/EXECJNK.SRC acceleration arithmetic for either axis.
; HL=scaled unit-vector target, DE=current velocity, C=joystick radius.
; Returns HL=new velocity. All main registers clobbered.
; floor(delta*radius/256), arithmetic /8, carry round, add current.
player_accelerate:
 push de
 or a
 sbc hl,de
 ld a,h
 push af
 ld a,l
 call multiply8
 ld a,h
 pop de
 push af
 ld a,d
 push af
 call multiply8
 pop af
 bit 7,a
 jr z,pa_positive
 ld a,h
 sub c
 ld h,a
pa_positive:
 pop af
 ld e,a
 ld d,0
 add hl,de
 DUP 3
 sra h
 rr l
 EDUP
 ld a,l
 adc a,0
 ld l,a
 ld a,h
 adc a,0
 ld h,a
 pop de
 add hl,de
 ret

; Unsigned A*C -> HL. C preserved.
multiply8:
 IFDEF SCENE_FASTMATH
 ld b,a
 ld a,c
 cp 127
 ld a,b
 jr nz,mul_generic
 ld l,a
 ld h,0
 ld e,l
 ld d,h
 DUP 7
 add hl,hl
 EDUP
 or a
 sbc hl,de
 ret
mul_generic:
 ENDIF
 ld e,c
 ld d,0
 ld hl,0
 ld b,8
mul_loop:
 srl a
 jr nc,mul_skip
 add hl,de
mul_skip:
 sla e
 rl d
 djnz mul_loop
 ret

 INCLUDE "../build/player-tables.asm"
