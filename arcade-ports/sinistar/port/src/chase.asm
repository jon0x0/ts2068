; WITT/CHASE.SRC. HL=desired, DE=target velocity, BC=maximum.
; HL=adjusted desired. Preserve the source's 16-bit wrap and signed comparison.
chase_velocity:
 ld a,h
 xor d
 ret m
 bit 7,h
 jr nz,chase_negative
 add hl,de
 push hl
 call chase_compare
 pop hl
 ret c
 ret z
 ld h,b
 ld l,c
 ret
chase_negative:
 add hl,de
 push hl
 bit 7,h
 call nz,neg_hl
 call chase_compare
 pop hl
 ret c
 ret z
 ld h,b
 ld l,c
 jp neg_hl
chase_compare:
 ld a,b
 xor 128
 ld d,a
 ld a,h
 xor 128
 cp d
 ret nz
 ld a,l
 cp c
 ret
