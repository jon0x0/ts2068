; Common enemy/boss colour lookup. All registers except AF and successful HL preserved.
        ORG $18A7
boss_colour_lookup:
        PUSH BC
        CALL full_enemy_source
        JR NC,not_found
        LD A,($8EB1)
        OR A
        JR Z,source_tag
        LD C,A
        AND 7
        LD B,A
        LD A,C
        AND $40
        RRCA
        RRCA
        RRCA
        OR B
        JR row_address
source_tag:
        LD A,(HL)
        AND $7F
row_address:
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$2000
        ADD HL,BC
        POP BC
        SCF
        RET
not_found:
        POP BC
        RET
full_enemy_source:
        LD A,H
        CP $C4
        JR C,no
        JR NZ,lower_ready
        LD A,L
        CP $CE
        JR C,no
lower_ready:
        LD A,H
        CP SOURCE_ENEMY_END >> 8
        JR C,yes
        JR NZ,pool
        LD A,L
        CP SOURCE_ENEMY_END & 255
        JR C,yes
pool:
 IF ENEMY_POOL_END
        LD A,H
        CP ENEMY_POOL_START >> 8
        JR C,no
        JR NZ,pool_lower_ready
        LD A,L
        CP ENEMY_POOL_START & 255
        JR C,no
pool_lower_ready:
        LD A,H
        CP ENEMY_POOL_END >> 8
        JR C,yes
        JR NZ,no
        LD A,L
        CP ENEMY_POOL_END & 255
        JR C,yes
 ENDIF
no:
        OR A
        RET
yes:
        SCF
        RET
        ASSERT $ <= RETAINED_ENTRY
        DS RETAINED_ENTRY-$,0
full_retained_attribute:
        PUSH AF
        CALL full_enemy_source
        JR NC,retained_native
        POP AF
        AND $7F
        CP 16
        JR NC,retained_variable
        BIT 3,A
        JR Z,retained_done
        AND 7
        OR 0 ; hardware normal-black policy
        JR retained_done
retained_variable:
        ADD A,$90
        JR NC,retained_done
        ADD A,$10
retained_done:
        SCF
        RET
retained_native:
        POP AF
        OR A
        RET
        ASSERT $ <= $1937
        DS $1937-$,0
