; Three native travel steps, one draw. Stop at the first enemy/terrain cell.
        ORG $19E3
        PUSH HL
        PUSH DE
        LD E,A
        LD D,3
step:
        LD A,E
        CALL $C3D1
        AND 15
        CP 3
        JR C,double_vector
        INC C
        JP $09B6
double_vector:
        LD A,E
        CALL $C3D1
        JP $09B6
        ASSERT step == $19E8
        ASSERT $ <= $1A00
