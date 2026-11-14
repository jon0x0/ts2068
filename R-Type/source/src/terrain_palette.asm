        ORG $0E00
; A is legacy attribute or encoded terrain row. IYL is source scanline0..7.
terrain_decode_colour:
        OR A
        RET P
        PUSH HL
        PUSH BC
        AND $7F
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$FBD0
        ADD HL,BC
        LD C,IYL
        LD B,0
        ADD HL,BC
        LD A,(HL)
        POP BC
        POP HL
        RET
        ASSERT $ <= $0E40
        DS $0E40-$,$FF
terrain_copy_colour:
        OR A
        JP P,terrain_copy_native
        PUSH HL
        PUSH BC
        AND $7F
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$FBD0
        ADD HL,BC
        SET 5,D
        DUP 7
        LD A,(HL)
        LD (DE),A
        INC HL
        INC D
        EDUP
        LD A,(HL)
        LD (DE),A
        LD A,D
        SUB 7
        LD D,A
        RES 5,D
        POP BC
        POP HL
        RET
terrain_copy_native:
        SET 5,D
        DUP 7
        LD (DE),A
        INC D
        EDUP
        LD (DE),A
        LD A,D
        SUB 7
        LD D,A
        RES 5,D
        RET
        ASSERT $ <= $0EF0
        DS $0EF0-$,$FF
terrain_reverse_attribute:
        LD A,(HL)
        BIT 7,A
        JR Z,terrain_reverse_done
        OR $04
terrain_reverse_done:
        LD (DE),A
        INC E
        RET
        ASSERT $ <= $0F00
