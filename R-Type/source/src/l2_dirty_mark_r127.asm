        ORG MARK_ENTRY
mark_boss_dirty:
        LD A,(reveal_index)
        CP 18
        RET C
        LD A,(repair_mode)
        OR A
        RET NZ
        LD A,B
        CP 20
        RET NC
        LD A,C
        CP 32
        RET NC
        LD (left),A
        ADD A,E
        LD (right),A
        LD A,B
        LD (top),A
        ADD A,D
        LD (bottom),A
        LD HL,REVEAL_COORDS
        LD IX,dirty_tiles
        LD B,18
        LD C,1
mark_tile:
        LD A,(HL)
        LD D,A
        AND 7
        ADD A,A
        ADD A,A
        LD E,A
        LD A,(right)
        CP E
        JR C,next_tile
        JR Z,next_tile
        LD A,E
        ADD A,4
        LD E,A
        LD A,(left)
        CP E
        JR NC,next_tile
        LD A,D
        AND $38
        RRCA
        LD E,A
        LD A,(bottom)
        CP E
        JR C,next_tile
        JR Z,next_tile
        LD A,E
        ADD A,4
        LD E,A
        LD A,(top)
        CP E
        JR NC,next_tile
        LD A,(IX)
        OR C
        LD (IX),A
next_tile:
        INC HL
        SLA C
        JR NZ,same_byte
        LD C,1
        INC IX
same_byte:
        DJNZ mark_tile
        RET
left: DB 0
right: DB 0
top: DB 0
bottom: DB 0
        ASSERT $ <= $B0DE
