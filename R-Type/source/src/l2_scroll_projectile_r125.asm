        ORG $0FB1
scroll_row:
        LD A,3
        CALL row_palette
        SCF
        RET
global_gateway:
        LD A,I
        PUSH AF
        DI
        LD A,$4B
        OUT ($F4),A
        JP $D920
        ASSERT $ <= $0FC3
        ORG $0E91
        JP scroll_row
        ORG $D920
global_copy:
        PUSH BC
        PUSH DE
        LD DE,$D940
        ADD HL,DE
        LD DE,row_cache
        LD BC,8
        LDIR
        POP DE
        POP BC
        LD HL,row_cache
        JP global_return
        ASSERT $ <= $D940
