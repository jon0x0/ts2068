; Assembled separately for each SECTION. All are DOCK0 and remain mapped.
        IF SECTION == 0
        ORG $0190
        LD A,1
        OUT ($F4),A
        LD B,(HL)
        SET 5,H
        LD C,(HL)
        RES 5,H
        LD A,$0D
        OUT ($F4),A
        RET
        ASSERT $ <= $01A0
        ENDIF
        IF SECTION == 1
        ORG $1E20
        LD A,1
        OUT ($F4),A
        LD (HL),B
        SET 5,H
        LD (HL),C
        RES 5,H
        LD A,$0D
        OUT ($F4),A
        RET
        ASSERT $ <= $1E30
        ENDIF
        IF SECTION == 2
        ORG $19E3
        LD A,B
        ADD A,A
        ADD A,B
        ADD A,$B4
        LD L,A
        LD H,$5E
        LD A,9
        OUT ($F4),A
        LD C,(HL)
        INC L
        LD D,(HL)
        INC L
        LD E,(HL)
        LD A,$0D
        OUT ($F4),A
        LD A,C
        RET
        ASSERT $ <= $1A00
        ENDIF
        IF SECTION == 3
        ORG $09B6
        LD C,A
        LD A,B
        ADD A,A
        ADD A,B
        ADD A,$B4
        LD L,A
        LD H,$5E
        LD A,9
        OUT ($F4),A
        LD (HL),C
        INC L
        LD (HL),D
        INC L
        LD (HL),E
        LD A,$0D
        OUT ($F4),A
        RET
        ASSERT $ <= $09D0
        ENDIF
