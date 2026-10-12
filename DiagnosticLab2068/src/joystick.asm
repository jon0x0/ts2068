; Called at3F00 with ROM1 visible (cartridge) or HOME ROM (U16 edition).
; IXL=active-low contacts; E=0/16 player-column offset. No RAM control state.
; Five independent highlights allow diagonals, fire+direction, or opposing faults.
 ORG $3f00
joystick_paint:
 ld hl,joystick_targets
 ld b,5
joystick_control:
 ld a,(hl)
 inc hl
 ld c,a
 ld a,ixl
 and c
 ld c,$78
 jp nz,joystick_released
 ld c,$60
joystick_released:
 ld a,(hl)
 inc hl
 add a,e
 ld iyl,a
 ld a,(hl)
 inc hl
 ld iyh,a
 ; Optional display-only history: active green, released/tested cyan.
 ; Corrupt attributes cannot change live input or control flow.
 ld a,c
 cp $60
 jr z,joystick_color_ready
 ld a,(iy+0)
 cp $60
 jr z,joystick_seen
 cp $68
 jr nz,joystick_color_ready
joystick_seen:
 ld c,$68
joystick_color_ready:
 ld ixh,6
joystick_cells:
 ld (iy+0),c
 inc iy
 dec ixh
 jp nz,joystick_cells
 djnz joystick_control
 ; Restore mapping only after reaching the always-visible low-ROM bridge.
 jp input_paint_done
joystick_targets:
 db 1
 dw $5905 ; Up:row8,col5.
 db 2
 dw $59c5 ; Down:row14,col5.
 db 4
 dw $5961 ; Left:row11,col1.
 db 8
 dw $5969 ; Right:row11,col9.
 db $80
 dw $5a25 ; Fire:row17,col5.
 ds 96-($-joystick_paint),0
 ASSERT $ <= $3fd0
