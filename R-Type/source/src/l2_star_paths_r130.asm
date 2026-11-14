; During the stopped L2 boss, hide stars behind its conservative x64..255 region.
; Native wrap cleanup is at x0 and cannot touch the boss.
        ORG $10D7
draw_guard:
        LD A,(BC)
        OR A
        JR NZ,reject
        CALL protected
        OR A
        RET Z
reject:
        POP AF
        RET
protected:
        LD A,($7A8E)
        OR A
        RET Z
        LD A,C
        AND $1F
        CP 8
        SBC A,A
        INC A
        RET
        ASSERT protected == $10E2
        ASSERT $ <= $10F0
