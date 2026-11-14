; Reject clipped cells and valid fully opaque foreground before planning source.
; Unlike retained pixel contents, metadata0/3 is not proof of foreground ownership.
        ORG $0080
        LD A,(SCREEN_Y)
        CP 20
        JR NC,skip
        LD C,A
        LD A,(SCREEN_X)
        OR A
        JR Z,skip
        CP 31
        JR NC,skip
        LD E,A
        LD A,C
        AND 7
        RRCA
        RRCA
        RRCA
        ADD A,E
        LD E,A
        LD A,C
        RRCA
        RRCA
        RRCA
        AND 3
        ADD A,$7E
        LD D,A
        CP $80
        JR C,read_metadata
        DI
        LD A,$4F
        OUT ($F4),A
        LD A,(DE)
        LD B,A
        LD A,$5F
        OUT ($F4),A
        EI
        LD A,B
        JR metadata_ready
read_metadata:
        LD A,(DE)
metadata_ready:
        OR A
        RET Z
        CP 3
        RET Z
        LD A,C
        AND $18
        OR $40
        LD D,A
        LD B,8
opaque_row:
        LD A,(DE)
        AND 7
        RET Z
        LD A,(DE)
        AND $38
        RET Z
        INC D
        DJNZ opaque_row
skip:
        SCF
        RET
        ASSERT $ <= $0100
