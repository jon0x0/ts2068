; Native TS2068 platform routines. No ROM service calls or Pico firmware use.
IFDEF TS2068
TsJoyInit:
                ld      a,7
                out     ($F5),a
                in      a,($F6)
                and     $BF             ; AY port A input (bit 6 clear)
                out     ($F6),a
                ld      a,1
                ld      (JoyOn),a
                ret

; Merge both native sticks into C's left/right/up/down bits.
; Preserve BC: C already contains the keyboard directions.
TsReadJoy:
                push    bc
                ld      a,14
                out     ($F5),a
                ld      bc,$03F6
                in      a,(c)
                pop     bc
                bit     0,a
                jr      nz,TsNoUp
                set     2,c
TsNoUp:         bit     1,a
                jr      nz,TsNoDown
                set     3,c
TsNoDown:       bit     2,a
                jr      nz,TsNoLeft
                set     0,c
TsNoLeft:       bit     3,a
                jr      nz,TsNoRight
                set     1,c
TsNoRight:      bit     7,a
                ret     nz
                ld      a,(Buttons)
                res     1,a
                ld      (Buttons),a
                ret
ENDIF
