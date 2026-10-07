; Source: historicalsource/sinistar dc00bce37e5c5c7947369cf5040c10e4799f4a06.
; WITT/VELOCITY.SRC:newvelocity. HL=distance, IX=5-byte table.
; Returns HL=desired velocity, A=acceleration shift. BC/DE/IX clobbered.
; Domain -32767..32767: source cannot range absolute -32768.
; Table rows: distance word, speed word, arithmetic shift byte (little endian).
new_velocity:
 push ix
 ld a,h
 push af
 bit 7,h
 call nz,neg_hl
nv_distance:
 ld e,(ix+0)
 ld d,(ix+1)
 or a
 sbc hl,de
 add hl,de
 jr nc,nv_found
 ld de,5
 add ix,de
 jr nv_distance
nv_found:
 ld l,(ix+2)
 ld h,(ix+3)
 pop af
 bit 7,a
 call z,neg_hl
 pop ix
 push hl
 bit 7,h
 call nz,neg_hl
; Original searches again by speed, rather than reusing the distance row.
nv_speed:
 ld e,(ix+2)
 ld d,(ix+3)
 or a
 sbc hl,de
 add hl,de
 jr nc,nv_accel
 ld de,5
 add ix,de
 jr nv_speed
nv_accel:
 ld a,(ix+4)
 pop hl
 ret

neg_hl:
 xor a
 sub l
 ld l,a
 sbc a,a
 sub h
 ld h,a
 ret

; WITT/VELOCITY.SRC:updscreen arithmetic core, SAM/FUNCTION.SRC:asrdN.
; HL=desired, DE=current, A=shift 0..7. Returns HL=new current.
; Deliberately preserves original ORB #1 (not conventional rounding).
smooth_velocity:
 ld b,a
 or a
 sbc hl,de
 jr z,sv_same
 ld a,b
 or a
 jr z,sv_odd
sv_shift:
 sra h
 rr l
 djnz sv_shift
sv_odd:
 set 0,l
 add hl,de
 ret
sv_same:
 ex de,hl
 ret

; SAM/EXECJNK.SRC:rotate player, from SUBB PLYRANG through STA PLYRANG.
; A=current angle, B=joystick angle, C=radius (0..255).
; Returns A=new angle. 256 units/circle. Clobbers all main registers.
; 6809 MUL's N flag is unchanged: source correction uses signed delta.
player_turn:
 ld e,a
 ld a,b
 sub e
 push de
 ld e,c
 ld d,0
 ld b,8
 ld hl,0
 ld c,a
pt_multiply:
 srl a
 jr nc,pt_noadd
 add hl,de
pt_noadd:
 sla e
 rl d
 djnz pt_multiply
; DE now equals radius<<8; subtract it for a negative signed delta.
 bit 7,c
 jr z,pt_round
 or a
 sbc hl,de
pt_round:
 ld de,128
 add hl,de
 pop de
 ld a,h
 add a,e
 ret

; Original WITT/STBLSINI.SRC, expressions resolved by build.py.
sinistar_speeds:
 INCLUDE "../build/sinistar-speeds.asm"
