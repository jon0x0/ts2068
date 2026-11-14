; IRQ already runs on its separate HOME stack. Main copy owns the other stack.
        ORG $0E25
        LD A,($5BC2)
        OR A
        JR Z,done
        CALL $8B06
        LD A,$89
        OUT ($F4),A
        CALL $E40C
        LD A,9
        OUT ($F4),A
done:
        LD HL,$7A8A
        RET
        ASSERT $ <= $0E40
