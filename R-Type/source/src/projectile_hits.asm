; Main-loop collision handoff. IRQ never enters the non-reentrant native renderer.
        ORG $9DA5
        LD IX,$5EB4
        LD B,16
loop:
        PUSH BC
        LD A,16
        SUB B
        LD E,A
        LD A,3
        CALL GATEWAY
        OR A
        JR Z,next
        CP $FB
        JR NC,next
        LD ($7AD8),A
        XOR A
        LD ($7AD7),A
        LD ($7AD9),A
        INC A
        LD ($7A95),A
        LD A,(IX+1)
        LD ($71E1),A
        LD A,(IX+2)
        LD ($71E2),A
        PUSH IX
        CALL $A490
        POP IX
next:   EI
        LD DE,3
        ADD IX,DE
        POP BC
        DJNZ loop
        RET
        ASSERT $ <= $9DFA
