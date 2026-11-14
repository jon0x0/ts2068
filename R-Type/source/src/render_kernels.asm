; ROM-resident copies preserving displaced original vertical-mirror contracts.
        ORG $1200
copy_vertical:
        DUP 7
        LD A,(HL)
        LD (DE),A
        INC HL
        DEC D
        EDUP
        LD A,(HL)
        LD (DE),A
        LD IXL,1
        DEC IXL
        JP $8E10
copy_vertical_reverse_bits:
        DUP 7
        LD C,(HL)
        LD A,(BC)
        LD (DE),A
        INC HL
        DEC D
        EDUP
        LD C,(HL)
        LD A,(BC)
        LD (DE),A
        LD IXL,1
        DEC IXL
        JP $8E6C
        ASSERT $ <= $1300
