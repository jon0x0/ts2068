        ORG HELPER
snake_part:
        CP 39
        RET NC
        CP 22
        JR Z,body
        CP 23
        JR NZ,ready
body:
        PUSH IY
        POP HL
        LD DE,-4
        ADD HL,DE
        LD DE,-9
        LD B,0
previous:
        LD A,(HL)
        CP 5
        JR NZ,classify
        INC B
        ADD HL,DE
        JR previous
classify:
        LD A,B
        CP 9
        LD A,23
        JR C,ready
        DEC A
ready:
        LD E,A
        SCF
        RET
