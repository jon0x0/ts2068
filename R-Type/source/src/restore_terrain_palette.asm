        ORG $0F00
        PUSH AF
        PUSH BC
        PUSH HL
        LD C,A
        PUSH AF ; keep frame layout; IRQ-safe code leaves IFF unchanged
        LD A,3
        OUT ($F4),A
        LD A,C
        CALL $0E40
        LD A,($BE00)
        OUT ($FF),A
        LD A,3
        OUT ($F4),A
        POP AF
restore_terrain_no_ei:
        POP HL
        POP BC
        POP AF
        RET
        ASSERT $ <= $1000
        DS $0F80-$,$FF
terrain_lookup_row:
        PUSH BC
        LD A,H
        CP $D9
        JR C,terrain_not_found
        CP $E6
        JR NC,terrain_not_found
        CP $D9
        JR NZ,terrain_check_end
        LD A,L
        CP $11
        JR C,terrain_not_found
terrain_check_end:
        LD A,H
        CP $E5
        JR NZ,terrain_check_marker
        LD A,L
        CP $71
        JR NC,terrain_not_found
terrain_check_marker:
        BIT 7,(HL)
        JR Z,terrain_not_found
        LD A,(HL)
        AND $F7
        LD C,A
        PUSH DE
        LD E,(IX+8)
        LD D,(IX+9)
        LD A,(DE) ; palette belongs to this retained level instance
        AND 8
        OR C
        POP DE
        AND $7F
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$FBD0
        ADD HL,BC
        POP BC
        SCF
        RET
terrain_not_found:
        POP BC
        AND A
        RET
        ASSERT $ <= $1000
        DS $0FE0-$,$FF
clear_staging_column:
        LD HL,$601F
        LD B,160
clear_staging_line:
        LD (HL),0
        INC H
        LD A,H
        AND 7
        JR NZ,clear_staging_next
        LD A,L
        ADD A,32
        LD L,A
        JR C,clear_staging_next
        LD A,H
        SUB 8
        LD H,A
clear_staging_next:
        DJNZ clear_staging_line
        RET
        ASSERT $ <= $1000
