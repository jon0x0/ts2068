        ORG $0D00
 IFDEF ROM_ONLY
FRAME_SHADOW EQU $BE01
 ELSE
FRAME_SHADOW EQU $3FF1
 ENDIF
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
 IFNDEF ROM_ONLY
        LD A,$0B
        OUT ($F4),A
 ENDIF
        LD A,($7A89)
        AND 3
        LD L,A
        LD H,0
        LD BC,$10F0
        ADD HL,BC
        LD A,(HL)
        LD (FRAME_SHADOW),A
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        LD E,L
        LD D,H
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,DE
        LD BC,$1000
        ADD HL,BC
        LD DE,$D550
        LD BC,36
        LDIR
 IFNDEF ROM_ONLY
        LD A,9
        OUT ($F4),A
 ENDIF
        POP HL
        POP DE
        POP BC
        POP AF
        RET
        ASSERT $ <= $0E00
