; Shared exact source classification for direct and retained enemy colours.
boss_colour_lookup:
        PUSH BC
        PUSH DE
        PUSH HL
        CALL full_enemy_source
        JR NC,full_boss_not_found
        LD A,($8EB1)
        AND A
        JR Z,full_boss_source
        LD C,A
        AND 7
        LD B,A
        LD A,C
        AND $40
        RRCA
        RRCA
        RRCA
        OR B
        JR full_boss_row
full_boss_source:
        LD A,(HL)
        AND $7F
full_boss_row:
        POP HL
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$2000
        ADD HL,BC
        POP DE
        POP BC
        SCF
        RET
full_boss_not_found:
        POP HL
        POP DE
        POP BC
        AND A
        RET
full_enemy_source:
        PUSH HL
        PUSH DE
        LD DE,$C4CE
        OR A
        SBC HL,DE
        JR C,full_source_no
        ADD HL,DE
        LD DE,SOURCE_ENEMY_END
        OR A
        SBC HL,DE
        JR C,full_source_yes
 IF ENEMY_POOL_END
        ADD HL,DE
        LD DE,ENEMY_POOL_START
        OR A
        SBC HL,DE
        JR C,full_source_no
        ADD HL,DE
        LD DE,ENEMY_POOL_END
        OR A
        SBC HL,DE
        JR NC,full_source_no
 ELSE
        JR full_source_no
 ENDIF
full_source_yes:
        POP DE
        POP HL
        SCF
        RET
full_source_no:
        POP DE
        POP HL
        OR A
        RET
full_retained_attribute:
        PUSH AF
        CALL full_enemy_source
        JR NC,full_retained_native
        POP AF
        AND $7F
        CP 16
        JR NC,full_retained_variable
        BIT 3,A
        JR Z,full_retained_done
        AND 7
        OR $40
        JR full_retained_done
full_retained_variable:
        ADD A,$90
        JR NC,full_retained_done
        ADD A,$10
full_retained_done:
        SCF
        RET
full_retained_native:
        POP AF
        OR A
        RET
        ASSERT $-boss_colour_lookup <=144
        DS 144-($-boss_colour_lookup),0
