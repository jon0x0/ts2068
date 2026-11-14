; L2 source tile expansion. Runs in bank1 with HOME C000..FFFF visible.
        ORG $3848
install:
        LD A,$2B
        OUT ($F4),A
        LD HL,restore_trailer
        LD DE,$A480
        LD BC,restore_end-restore_trailer
        LDIR
        LD A,$0B
        OUT ($F4),A
        LD A,$C3
        LD ($882D),A
        LD HL,$01D8
        LD ($882E),HL
        LD A,$C3
        LD ($FF81),A
        LD HL,KEEP_TOKEN
        LD ($FF82),HL
        JP $01F4
get_tile:
        POP AF
        PUSH AF
        PUSH BC
        CP 19
        JR C,native_tile
        SUB 19
        ADD A,A
        LD L,A
        LD H,0
        LD DE,tile_table
        ADD HL,DE
        LD E,(HL)
        INC HL
        LD D,(HL)
        EX DE,HL
        LD DE,$C700
        CALL expand
        LD HL,$C700
        JR done
native_tile:
        INC A
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        PUSH HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        POP DE
        ADD HL,DE
        EX DE,HL
        LD HL,$E762
        OR A
        SBC HL,DE
done:
        POP BC
        JP $01E8
expand:
        LD A,(HL)
        INC HL
        OR A
        RET Z
        LD C,A
        LD B,0
        BIT 7,A
        JR NZ,backref
        LDIR
        JR expand
backref:
        AND $7F
        ADD A,3
        LD C,(HL)
        INC HL
        LD B,(HL)
        INC HL
        PUSH HL
        LD H,D
        LD L,E
        OR A
        SBC HL,BC
        LD C,A
        LD B,0
        LDIR
        POP HL
        JR expand
restore_trailer:
        LD ($DF3A),SP
        PUSH AF
        LD A,$3C
        LD ($882D),A
        LD HL,$8787
        LD ($882E),HL
        LD A,0
        LD ($FF81),A
        LD HL,$1200
        LD ($FF82),HL
        POP AF
        JP $A1EC
restore_end:
tile_table:
        DW $D442,$D46C,$D491,$D50E,$D59A,$D629,$D6AD,$D6DF,$D760,$D7F3,$D886,$D90B,$D950,$D9D4,$DA67,$DAFA,$DB8D,$DC20
        ASSERT $ <= $3A00
