        ORG $0100
; Authoring palette tables below0200 are compile-time only. This live kernel
; uses the already-built row cache and never reads those authoring tables.
        PUSH HL
        PUSH BC
        LD A,IXL
        AND $7F
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$FBD0
        ADD HL,BC
        PUSH HL
        LD A,IXH
        AND $7F
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,BC
        PUSH HL
        POP IX
        POP HL
        POP BC
        LD A,(DE)
        AND B
        LD A,(HL)
        JR NZ,terrain_fast_selected_0
        LD A,(IX+0)
terrain_fast_selected_0:
        SET 5,D
        LD (DE),A
        RES 5,D
        INC D
        INC HL
        LD A,(DE)
        AND B
        LD A,(HL)
        JR NZ,terrain_fast_selected_1
        LD A,(IX+1)
terrain_fast_selected_1:
        SET 5,D
        LD (DE),A
        RES 5,D
        INC D
        INC HL
        LD A,(DE)
        AND B
        LD A,(HL)
        JR NZ,terrain_fast_selected_2
        LD A,(IX+2)
terrain_fast_selected_2:
        SET 5,D
        LD (DE),A
        RES 5,D
        INC D
        INC HL
        LD A,(DE)
        AND B
        LD A,(HL)
        JR NZ,terrain_fast_selected_3
        LD A,(IX+3)
terrain_fast_selected_3:
        SET 5,D
        LD (DE),A
        RES 5,D
        INC D
        INC HL
        LD A,(DE)
        AND B
        LD A,(HL)
        JR NZ,terrain_fast_selected_4
        LD A,(IX+4)
terrain_fast_selected_4:
        SET 5,D
        LD (DE),A
        RES 5,D
        INC D
        INC HL
        LD A,(DE)
        AND B
        LD A,(HL)
        JR NZ,terrain_fast_selected_5
        LD A,(IX+5)
terrain_fast_selected_5:
        SET 5,D
        LD (DE),A
        RES 5,D
        INC D
        INC HL
        LD A,(DE)
        AND B
        LD A,(HL)
        JR NZ,terrain_fast_selected_6
        LD A,(IX+6)
terrain_fast_selected_6:
        SET 5,D
        LD (DE),A
        RES 5,D
        INC D
        INC HL
        LD A,(DE)
        AND B
        LD A,(HL)
        JR NZ,terrain_fast_selected_7
        LD A,(IX+7)
terrain_fast_selected_7:
        SET 5,D
        LD (DE),A
        RES 5,D
        INC D
        INC HL
        LD A,D
        SUB 8
        LD D,A
        POP HL
        RET
        ASSERT $ <= $0200
