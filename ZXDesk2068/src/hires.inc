; Native 512x192 backend. Logical byte column n lives in plane n&1,
; at offset n/2. Linear window buffers remain in logical left-to-right order.
IFDEF HIRES

; Adjacent logical screen byte. Preserve all registers except HL.
HiresRight:
                push    af
                ld      a,h
                xor     $20
                ld      h,a
                bit     5,h
                jr      nz,HrRightDone
                inc     l
HrRightDone:    pop     af
                ret
HiresLeft:
                push    af
                bit     5,h
                jr      nz,HrLeftSame
                dec     l
HrLeftSame:     ld      a,h
                xor     $20
                ld      h,a
                pop     af
                ret

; Advance screen HL by E logical byte columns. D/E and flags are scratch.
HiresAdvance:
                ld      a,e
                or      a
                ret     z
HrAdvanceLoop: call    HiresRight
                dec     e
                jr      nz,HrAdvanceLoop
                ret

; Full 9-bit X -> byte column in A, other registers preserved.
HiresPtrCol:
                push    hl
                ld      hl,(PtrX)
                call    HiresColHL
                pop     hl
                ret
HiresColHL:
                push    hl
                srl     h
                rr      l
                srl     l
                srl     l
                ld      a,l
                pop     hl
                ret

; A is signed pixel delta. Clamp full-width pointer, including 255/256.
HiresMoveX:
                ld      e,a
                ld      d,0
                bit     7,a
                jr      z,HrDeltaReady
                dec     d
HrDeltaReady:   ld      hl,(PtrX)
                add     hl,de
                bit     7,h
                jr      z,HrXPositive
                ld      hl,0
                jr      HrXStore
HrXPositive:    ld      de,PTRXMAX
                push    hl
                or      a
                sbc     hl,de
                pop     hl
                jr      c,HrXStore
                ld      hl,PTRXMAX
HrXStore:       ld      (PtrX),hl
                ld      a,l
                ret

; Carry when horizontal motion is below the icon drag threshold.
HiresDragDistance:
                ld      hl,(PtrX)
                ld      de,(DskPressX)
                or      a
                sbc     hl,de
                jr      nc,HrDistancePositive
                ex      de,hl
                ld      hl,0
                or      a
                sbc     hl,de
HrDistancePositive:
                ld      de,DSKMOVE
                or      a
                sbc     hl,de
                ret

HiresStatusX:
                ld      hl,(PtrX)
                ld      de,100
                ld      b,0
HrHundred:      or      a
                sbc     hl,de
                jr      c,HrRemainder
                inc     b
                jr      HrHundred
HrRemainder:    add     hl,de
                ld      a,b
                ld      (HrHundreds),a
                ld      a,l
                ld      c,2
                call    SsDec3
                ld      a,(HrHundreds)
                add     a,'0'
                ld      c,2
                jp      SsPut
HrHundreds:     defb    0

HiresFillRect:
                xor     a
                jr      HrFillStart
HiresFillDesk:
                ld      a,1
HrFillStart:    ld      (HrLattice),a
                ld      a,(FrW)
                or      a
                ret     z
                ld      a,(FrH)
                or      a
                ret     z
                ld      (HrRows),a
                ld      a,(FrY)
                ld      (HrY),a
HrFillRow:      ld      a,(FrX)
                ld      c,a
                ld      a,(HrY)
                call    AddrAt
                ld      de,(FrPat)
                ld      a,(HrLattice)
                or      a
                jr      z,HrFillPixels
                ld      a,(HrY)
                and     3
                jr      z,HrPatternA
                cp      2
                jr      z,HrPatternB
                xor     a
                jr      HrPatternReady
HrPatternA:     ld      a,(LatA1)
                jr      HrPatternReady
HrPatternB:     ld      a,(LatB1)
HrPatternReady: ld      d,a
                ld      e,a
HrFillPixels:   ld      a,(FrW)
                ld      b,a
HrFillByte:     ld      (hl),e
                call    HiresRight
                ld      a,e
                ld      e,d
                ld      d,a
                djnz    HrFillByte
                ld      hl,HrY
                inc     (hl)
                ld      hl,HrRows
                dec     (hl)
                jr      nz,HrFillRow
                ret
LatA1:          defb    $88
LatB1:          defb    $22
HrLattice:      defb    0
HrY:            defb    0
HrRows:         defb    0

HiresGrab:
                ld      a,(RcW)
                or      a
                ret     z
                ld      a,(RcH)
                or      a
                ret     z
                ld      b,a
                ld      a,(RcX)
                ld      c,a
                ld      a,(RcY)
                call    AddrAt
                ld      de,(RcBuf)
HrGrabRow:      push    bc
                push    hl
                ld      a,(RcW)
                ld      b,a
HrGrabByte:     ld      a,(hl)
                ld      (de),a
                inc     de
                call    HiresRight
                djnz    HrGrabByte
                pop     hl
                call    ScrDown
                pop     bc
                djnz    HrGrabRow
                ret

HiresBlit:
                ld      a,(RcW)
                ld      (HrWidth),a
                ld      a,(RcH)
                ld      (HrRows),a
                ld      a,(RcX)
                ld      c,a
                ld      a,(RcY)
                call    AddrAt
                ld      de,(RcBuf)
                xor     a
                ld      (HrSkip),a
                jr      HrBlitStart
HiresClip:
                ld      a,(BcW)
                ld      (HrWidth),a
                ld      a,(WinW)
                ld      hl,BcW
                sub     (hl)
                ld      (HrSkip),a
                ld      a,(BcH)
                ld      (HrRows),a
                ld      a,(BcX)
                ld      c,a
                ld      a,(BcY)
                call    AddrAt
                ld      de,(BcSrc)
HrBlitStart:    ld      a,(HrWidth)
                or      a
                ret     z
                cp      SCRCOLS+1
                ret     nc
                ld      a,(HrRows)
                or      a
                ret     z
HrBlitRow:      push    hl
                ld      a,(HrWidth)
                ld      b,a
HrBlitByte:     ld      a,(de)
                ld      (hl),a
                inc     de
                call    HiresRight
                djnz    HrBlitByte
                ld      a,(HrSkip)
                add     a,e
                ld      e,a
                jr      nc,HrBlitNoCarry
                inc     d
HrBlitNoCarry:  pop     hl
                call    ScrDown
                ld      a,(HrRows)
                dec     a
                ld      (HrRows),a
                jr      nz,HrBlitRow
                ret
HrWidth:        defb    0
HrSkip:         defb    0
ENDIF
