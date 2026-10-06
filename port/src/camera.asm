; SAM/EXECJNK.SRC SCROLL. IX points to:
; position16, velocity16, cameraVelocity16, unit8, axis8 (0=long, 1=short).
; All words little-endian. Returns/stores HL=camera velocity. Clobbers AF/BC/DE.
camera_axis:
 ld l,(ix+0)
 ld h,(ix+1)
 ld e,(ix+2)
 ld d,(ix+3)
 add hl,de
 ld c,(ix+4)
 ld b,(ix+5)
 add hl,bc
 ld a,(ix+7)
 or a
 ld a,h
 jr nz,ca_short_limits
 cp $08
 jr c,ca_hard
 cp $6c
 jr c,ca_soft
 jr ca_hard
ca_short_limits:
 cp $10
 jr c,ca_hard
 cp $f0
 jr c,ca_soft
ca_hard:
 ex de,hl
 call neg_hl
 ld c,l
 ld b,h
ca_soft:
; B,C now hold the hard-limited camera speed.
 ld a,(ix+6)
 sra a
 sra a
 sra a
 ld e,a
 ld a,(ix+7)
 or a
 jr nz,ca_short_error
 ld a,$38
 sub (ix+1)
 jr ca_direction
ca_short_error:
 ld a,$7b
 sub (ix+1)
 sra a
ca_direction:
 sub e
 ld l,a
 add a,a
 sbc a,a
 ld h,a
 add hl,hl
 add hl,hl
 add hl,hl
 ld e,(ix+2)
 ld d,(ix+3)
 or a
 sbc hl,de
 or a
 sbc hl,bc
 DUP 5
 sra h
 rr l
 EDUP
 ld e,l
 ld d,h
 sra h
 rr l
 add hl,de
 add hl,bc
 ld (ix+4),l
 ld (ix+5),h
 ret

; Signed 16-bit DE added to 24-bit little-endian camera coordinate at HL.
; Matches EXECJNK's carry/borrow propagation, wrapping modulo 2^24.
camera_integrate:
 ld a,(hl)
 add a,e
 ld (hl),a
 inc hl
 ld a,(hl)
 adc a,d
 ld (hl),a
 inc hl
 ld a,0
 adc a,0
 bit 7,d
 jr z,ci_positive
 dec a
ci_positive:
 add a,(hl)
 ld (hl),a
 ret
