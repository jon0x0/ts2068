; Mirrored in HOME and DOCK7 so the instruction stream survives F4 bank7 changes.
        ORG $FB00
irq_pixel:
        CALL $F930
        LD A,($5BCD)
        OR A
        JR NZ,irq_done
        LD A,($5BC5)
        XOR 1
        LD ($5BC5),A
        JR NZ,irq_done
        LD A,($5BC2)
        OR A
        JR Z,irq_done
        CALL $8B06
        XOR A
        CALL gateway
        LD A,($5BC8)
        OR A
        JR Z,irq_done
        XOR A
        LD ($5BC8),A
        LD DE,($5BC9)
        CALL $9D5C
irq_done:
        LD HL,$7A8A
        RET
gateway:
        DI
        LD ($5BC6),A
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        LD ($5BC0),SP
        LD SP,$5CF0
        DI
        LD A,$89
        OUT ($F4),A
        LD A,($5BC6)
        OR A
        JR Z,do_tick
        DEC A
        JR Z,do_prepare
        DEC A
        JR Z,do_restore
        CALL $E409
        JR gateway_done
do_tick:
        CALL $E400
        JR gateway_done
do_prepare:
        CALL $E403
        JR gateway_done
do_restore:
        CALL $E406
gateway_done:
        LD A,9
        OUT ($F4),A
        LD SP,($5BC0)
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        RET
copy_pixel:
        PUSH AF
        LD A,1
        CALL gateway
        POP AF
        EI
        CALL $8842
        PUSH AF
        LD A,2
        CALL gateway
        POP AF
        EI
        RET
sync_pixel:
        LD A,3
        CALL gateway
        EI
        JP $9559
collision_pixel:
        LD A,($5BC4)
        OR A
        JP NZ,$91F2
        JP $9577
        ASSERT $ <= $FBC0
