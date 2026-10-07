; Extracted FALS/N1ALL.SRC AddVib / TosCrys numerical rules.
; Pure kernels: scheduler, object allocation and sound belong to the caller.
; A=Richter, B=pseudo-mass; returns A=Richter after a normal rock hit.
rock_add_vibration:
 bit 7,a
 jr nz,rav_add
 cp $60
 ret nc
rav_add:
 ld c,a
 ld a,b
 rrca
 rrca
 rrca
 rrca
 and 15
 jr nz,rav_mass
 inc a
rav_mass:
 dec a
 ld l,a
 ld h,0
 ld de,rock_inverse_mass
 add hl,de
 ld a,(hl)
 srl a
 srl a
 add a,c
 ret
rock_inverse_mass:
 DB $ff,$80,$55,$40,$33,$2b,$25,$20,$1c,$1a,$17,$15,$14,$12,$11

; A=Richter B=mass C=random byte D=nonzero for Sinistar.
; Carry=set on crystal release; A/B updated, untouched on no release.
; Random sample is supplied, so the original RNG can be connected later.
rock_try_crystal:
 ld e,a
 ld a,d
 or a
 jr nz,rtc_no
 ld a,e
 sub $10
 jr c,rtc_no
 jr z,rtc_no
 cp c
 jr c,rtc_no
 ld a,b
 sub 8
 jr nc,rtc_mass
 xor a
rtc_mass:
 ld b,a
 ld a,e
 srl a
 scf
 ret
rtc_no:
 ld a,e
 or a
 ret

; A=Richter, C=on-screen (0/1). Returns A=new Richter, B=event:
; 0=continue vibration, 1=stop vibration, 2=shatter rock.
; Called after the out-and-back vibration cycle, after crystal release.
rock_damp:
 sub 2
 ld b,0
 bit 7,a
 jr nz,rd_stop
 ld d,a
 ld a,c
 or a
 ld a,d
 ret z
 cp $60
 ret c
 xor a
 ld b,2
 ret
rd_stop:
 xor a
 ld b,1
 ret
