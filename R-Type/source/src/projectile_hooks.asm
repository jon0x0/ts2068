; Individually linked into verified padding / unreachable old normal-shot tail.
        IF SECTION == 0
        ORG $1928
        LD HL,$5BC3
        LD A,(HL)
        LD L,$CD
        OR (HL)
        LD HL,$7A8A
        RET NZ
        JP $0FD4
        ASSERT $ <= $1937
        ENDIF
        IF SECTION == 1
        ORG $0FD4
        LD A,($5BC2)
        OR A
        RET Z
        JP $0F70
        ASSERT $ <= $0FE0
        ENDIF
        IF SECTION == 2
        ORG $0F70
        LD A,($7AA4)
        CP 2
        RET C
        CP 5
        RET NC
        LD A,1
        JP GATEWAY
        ASSERT $ <= $0F80
        ENDIF
        IF SECTION == 3
        ORG $0986
        PUSH AF
        XOR A
        CALL GATEWAY
        POP AF
        JP $FB37
        ASSERT $ <= $0990
        ENDIF
        IF SECTION == 4
        ORG $9DE7
        LD A,($5BD2)
        OR A
        JP Z,$9554
        LD HL,$5880
        LD DE,$F100
        LD BC,ENGINE_LENGTH
        JP $1A91
        ASSERT $ <= $9DFA
        ENDIF
        IF SECTION == 5
        ORG $1A91
        LD A,$8D
        OUT ($F4),A
        LDIR
        LD A,9
        OUT ($F4),A
        JP $9554
        ASSERT $ <= $1AA0
        ENDIF
        IF SECTION == 6
        ORG $9554
        LD HL,$A000
        RET
        ASSERT $ <= $9559
        ENDIF
