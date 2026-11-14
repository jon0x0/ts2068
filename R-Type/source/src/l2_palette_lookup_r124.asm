        ORG $0F80
palette_lookup:
        LD A,H
        CP $C7
        JR Z,lookup_attribute
        CP $DC
        JR C,lookup_no
lookup_attribute:
        LD A,(HL)
        CP $10
        JR C,lookup_no
        CP $20
        JR C,lookup_rich
        CP $90
        JR NC,lookup_rich
        LD A,$0B
        CALL row_palette
        CALL REVERSE_FLAG
        OR A
        CALL NZ,reverse_cache
lookup_terrain_done:
        LD A,$86
        SCF
        RET
lookup_rich:
        PUSH AF
        PUSH BC
        CALL $0E78
        POP BC
        POP AF
        SCF
        RET
lookup_no:
        OR A
        RET
        ASSERT $ <= $0FC3
