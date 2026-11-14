        ORG $5E00
restore_begin:
        DI
        LD SP,$FFF0
        XOR A
        OUT ($F4),A
        OUT ($FF),A
        LD HL,$5800
        LD DE,$5801
        LD BC,767
        LD (HL),A
        LDIR
        LD A,(PRELOAD_DRIVER_STATE+4)
        CALL PRELOAD_SELECT
        JP C,restore_error
        LD HL,$4000
        LD DE,$8000
        LD BC,$2000
        LD A,4
        CALL PRELOAD_COPY
        LD HL,$8000
        LD DE,$4000
        LD BC,$1E00
        LDIR
        LD HL,$6000
        LD DE,$8000
        LD BC,$2000
        LD A,8
        CALL PRELOAD_COPY
        LD HL,$8000
        LD DE,$6000
        LD BC,$2000
        LDIR
        LD SP,$5CC0
        LD A,(PRELOAD_DRIVER_STATE+3)
        CALL PRELOAD_SELECT
        JP C,restore_error
        LD HL,$4000
        LD DE,$C000
        LD BC,$2000
        LD A,4
        CALL PRELOAD_COPY
        LD HL,$6000
        LD DE,$E000
        LD BC,$2000
        LD A,8
        CALL PRELOAD_COPY
        LD A,$FF
        LD ($FD4A),A
        LD A,(PRELOAD_DRIVER_STATE+2)
        CALL PRELOAD_SELECT
        JP C,restore_error
        LD HL,$4000
        LD DE,$8000
        LD BC,$2000
        LD A,4
        CALL PRELOAD_COPY
        LD HL,final_tail_image
        LD DE,$7C00
        LD BC,final_tail_end-final_tail
        LDIR
        LD A,8
        OUT ($F4),A
        LD HL,$6000
        LD DE,$A000
        LD BC,$2000
        LDIR
        XOR A
        OUT ($F4),A
        JP $7C00
final_tail_image:
        DISP $7C00
final_tail:
        LD A,(FINAL_DRIVER_STATE+4)
        CALL FINAL_SELECT
        JP C,restore_error
        LD HL,$5E00
        LD DE,$7E00
        LD BC,$0200
        LD A,4
        CALL FINAL_COPY
        LD HL,$7E00
        LD DE,$5E00
        LD BC,$0200
        LDIR
        LD A,(FINAL_DRIVER_STATE)
        CALL FINAL_SELECT
        JP C,restore_error
        LD A,($FD49)
        CP 4
        LD A,$0B
        LD HL,$3E43
        JR NZ,bridge_target
        LD A,$19
        LD HL,$9EA3
bridge_target:
        LD ($5E01),A
        LD ($5E05),HL
        LD A,$3E
        LD ($5E00),A
        LD HL,$F4D3
        LD ($5E02),HL
        LD A,$C3
        LD ($5E04),A
        JP $5E00
restore_error:
        LD A,2
        OUT ($FE),A
        JR restore_error
final_tail_end:
        ASSERT $ <= $7E00
        ENT
        ASSERT $ <= $6000
