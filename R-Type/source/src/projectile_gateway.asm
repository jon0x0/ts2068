; Reclaims the unreachable old coarse player movement, not the live player path.
        ORG $94F9
install:
        CALL $0D00
        LD A,2
        JP gateway
gateway:
        DI
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        LD B,A
        LD A,($5BD2)
        LD C,A
        LD A,1
        LD ($5BD2),A
        LD ($5BD4),SP
        LD SP,$5CA0              ; DOCK2 stack, below the L5 shader private stack
        LD A,$8D
        OUT ($F4),A
        LD A,C
        OR A
        JR NZ,ready
        LD HL,$F100
        LD DE,$5880
        LD BC,ENGINE_LENGTH
        LDIR
        LD B,2
ready:  LD A,$0D
        OUT ($F4),A
        LD A,B
        ADD A,A
        ADD A,B
        ADD A,$80
        LD L,A
        LD H,$58
        LD B,E
        CALL invoke
        JR done
invoke: JP (HL)
done:   LD B,A
        LD A,9
        OUT ($F4),A
        LD SP,($5BD4)
        LD A,B
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        RET
        ASSERT $ <= $9559
