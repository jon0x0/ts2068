; QAOP / TS2068 joystick-1 directional adapter. D resumes diagnostic demos only.
; Native TS2068 keyboard matrix; no emulator-side movement injection.
; Returns carry=manual, B=target angle, power at $78a5 (0 or 127).
control_mode EQU $78a4
control_power EQU $78a5
read_controls:
 ld bc,$fdfe
 in a,(c)
 bit 2,a
 jr z,controls_demo
 push af
 ld a,14
 out ($f5),a
 ld bc,$01f6
 in a,(c)
 cpl
 and 15
 ld e,a
 ld bc,$fdfe
 pop af
 bit 0,a
 jr nz,rc_up
 set 1,e
rc_up:
 ld b,$fb
 in a,(c)
 bit 0,a
 jr nz,rc_horizontal
 set 0,e
rc_horizontal:
 ld b,$df
 in a,(c)
 bit 1,a
 jr nz,rc_right
 set 2,e
rc_right:
 bit 0,a
 jr nz,rc_resolve
 set 3,e
rc_resolve:
 ; Opposing directions cancel each axis.
 ld a,e
 and 3
 cp 3
 jr nz,rc_x
 ld a,e
 and 12
 ld e,a
rc_x:
 ld a,e
 and 12
 cp 12
 jr nz,rc_lookup
 ld a,e
 and 3
 ld e,a
rc_lookup:
 ld a,e
 or a
 jr z,rc_idle
 ld a,1
 ld (control_mode),a
 ld a,127
 ld (control_power),a
 ld d,0
 ld hl,control_angles
 add hl,de
 ld b,(hl)
 scf
 ret
rc_idle:
 xor a
 ld (control_power),a
 ld a,(angle)
 ld b,a
 ld a,(control_mode)
 or a
 ret z
 scf
 ret
controls_demo:
 IFDEF PLAYABLE_GAME
 ld a,(game_mode)
 or a
 jp nz,rc_idle
 ENDIF
 xor a
 ld (control_mode),a
 ret
control_angles:
 DB 0,0,128,0,192,224,160,0,64,32,96,0,0,0,0,0
