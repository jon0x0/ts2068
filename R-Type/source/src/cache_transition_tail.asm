; Executed at HOME5E00. Restore code before using native8100 scratch helpers.
        LD HL,$8100
        LD DE,$A000
        LD BC,DRIVER_LENGTH
        LDIR
        LD HL,cache_clear_helper
        LD DE,$8100
        LD BC,cache_clear_end-cache_clear_helper
        LDIR
        CALL $8100
        LD A,8
        OUT ($F4),A
        LD HL,$4000
        LD DE,$6000
        LD BC,$2000
        LDIR
cached_metadata_done:
        LD A,$20
        OUT ($F4),A
        LD HL,$A4AE
        LD DE,$C4AE
        LD BC,$1B52
        LDIR
        LD A,$40
        OUT ($F4),A
        LD HL,$C000
        LD DE,$E000
        LD BC,$187C
        LDIR
        LD HL,$DBD0
        LD DE,$FBD0
        LD BC,128
        LDIR
        LD A,$80
        OUT ($F4),A
        LD HL,$FB00
        LD DE,$5B00
        LD BC,512
        LDIR
        LD HL,$FB00
        LD DE,$6000
        LD BC,512
        LDIR
        XOR A
        OUT ($F4),A
        LD HL,cache_ship_helper
        LD DE,$8100
        LD BC,cache_ship_end-cache_ship_helper
        LDIR
        CALL $8100
        LD A,9
        OUT ($F4),A
        LD A,($FDA4)
        SUB '1'
        LD ($FD49),A
        XOR A
        LD ($FBC0),A
        LD ($FBC1),A
        LD ($FBC2),A
        LD ($FD92),A
        CALL $1485
        EI
        RET
cache_clear_helper:
        LD A,4
        OUT ($F4),A
        LD HL,$4000
        LD DE,$4001
        LD BC,$1FFF
        LD (HL),0
        LDIR
        XOR A
        OUT ($F4),A
        RET
cache_clear_end:
cache_ship_helper:
        LD A,4
        OUT ($F4),A
        LD HL,$6000
        LD DE,$5B00
        LD BC,512
        LDIR
        XOR A
        OUT ($F4),A
        RET
cache_ship_end:
        ASSERT $ <= $5F20

