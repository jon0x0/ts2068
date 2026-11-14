        ORG $FDC3
logical_player:
        LD A,($5BC2)
        OR A
        JR Z,logical_done
        LD A,($7AA4)
        SUB 2
        CP 3
        JR NC,logical_done
        ; Native collisions use character coordinates, independently of pixels.
        LD BC,($7AA1)
        LD A,B
        CP 20
        JR NC,logical_done
        LD A,C
        DEC A
        CP 28
        JR NC,logical_done
        LD A,B
        RRCA
        RRCA
        RRCA
        AND 3
        ADD A,$7E
        LD H,A
        LD A,B
        AND 7
        RRCA
        RRCA
        RRCA
        ADD A,C
        LD L,A
        LD B,4
mark:
        LD A,(HL)
        OR A
        JR NZ,next
        LD (HL),3
next:
        INC HL
        DJNZ mark
logical_done:
        JP $9559

        ASSERT $ <= $FE03
