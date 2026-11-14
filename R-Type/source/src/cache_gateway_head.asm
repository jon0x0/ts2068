        ORG $A000
        DI
        LD A,($719C)
        INC A
        CP '9'
        JR C,cache_level_ok
        LD A,'1'
cache_level_ok:
        LD ($719C),A
        LD ($FDA4),A
        LD E,0
        LD A,8
        CALL $F88C
        LD A,9
        CALL $F88C
        LD A,10
        CALL $F88C
        CALL $0DA0
        LD A,8
        OUT ($F4),A
        LD HL,$6000
        LD DE,$4000
        LD BC,$2000
        LDIR
        XOR A
        OUT ($F4),A
        LD A,($FDA4)
        SUB '1'
        LD E,A
        LD D,0
        LD HL,cache_bits
        ADD HL,DE
        LD B,(HL)
        LD A,($FD4A)
        AND B
        JR Z,cache_need_resident
        LD A,($FD48)
        CP E
        JR Z,cache_need_resident
        LD A,1
        OUT ($F4),A
        CALL $0D40
        LD (command_header+5),A
        CALL select_region
        JP C,load_error
        JP $5E00
cache_need_resident:
        LD A,($FD48)
        ADD A,A
        LD (command_header+5),A
        CALL select_region
        JP C,load_error
        LD A,4
        OUT ($F4),A
        LD HL,$4000
        LD DE,$6000
        LD BC,LOADER_LENGTH
        LDIR
        XOR A
        OUT ($F4),A
        LD HL,demand_restore
        LD DE,$5E00
        LD BC,demand_restore_end-demand_restore
        LDIR
        JP $5E00
demand_restore:
        DISP $5E00
        LD HL,$8100
        LD DE,$A000
        LD BC,DRIVER_LENGTH
        LDIR
        JP $6000
        ENT
demand_restore_end:
cache_bits: DB 1,2,4,8,16,32,64,128

