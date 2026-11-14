        ORG $0EA0
        LD A,($FBC1)
        CP 11
        JR Z,death_owns_ab
        LD A,($FBC0)
        CP 11
        JR Z,death_owns_ab
        OR A
        JR NZ,effect_owns_a
        LD A,($FBC1)
        OR A
        RET Z
effect_owns_a:
        LD A,C
        CP 2
        JR C,music_skip_reg
        CP 8
        JR Z,music_skip_reg
        OR A
        RET
death_owns_ab:
        LD A,C
        CP 4
        JR C,music_skip_reg
        CP 8
        JR Z,music_skip_reg
        CP 9
        JR Z,music_skip_reg
        OR A
        RET
music_skip_reg:
        SCF
        RET
        ASSERT $ <= $0EF0

        DS $0ED4-$,$FF
music_muted_volume:
        LD E,(HL)
        LD A,C
        CP 8
        RET C
        LD A,($FD93)
        OR A
        RET Z
        LD E,0
        RET
        ASSERT $ <= $0EF0
