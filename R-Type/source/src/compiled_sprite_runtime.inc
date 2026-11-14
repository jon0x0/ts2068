        ASSERT $ <= $FB00
        DS $FB00-$,$FF
; Normal-direction3x1 ship poses only; clipping/collision already checked.
compiled_ship_dispatch:
        CALL $FBA8
        JP NC,$8EA2
        LD A,($8EBF)
        CP $60
        JP NZ,$8EA2
        LD A,($8EB1)
        AND A
        JP NZ,$8EA2
        LD A,($7A9C)
        AND A
        JP Z,$8EA2
        IN A,($FF)
        AND 7
        CP 2
        JP NZ,$8EA2
        PUSH AF ; IRQ gateway makes both cache mappings safe
        PUSH BC
        PUSH HL
        PUSH DE
        LD A,L
        LD HL,$F8B0
        LD B,10
compiled_ship_search:
        CP (HL)
        JR Z,compiled_ship_found
        INC HL
        INC HL
        INC HL
        DJNZ compiled_ship_search
        POP DE
        POP HL
        POP BC
        LD A,2
        OUT ($FF),A
        POP AF
compiled_ship_fallback:
        JP $8EA2
compiled_ship_found:
        INC HL
        LD C,(HL)
        INC HL
        LD B,(HL)
        POP DE
        POP HL
        PUSH HL
        LD A,($7A9C)
        LD (DE),A
        LD A,D
        SUB 6
        LD D,A
        LD A,(HL)
        LD (DE),A
        LD A,D
        AND 3
        RLCA
        RLCA
        RLCA
        ADD A,$60
        LD D,A
        LD H,D
        LD L,E
        RES 5,H
        LD A,$0D
        OUT ($F4),A
        PUSH BC
        RET
        ASSERT $ <= $FB80
        DS $FB80-$,$FF
compiled_ship_finish:
        POP HL
        LD A,L
 IFDEF ROM_ONLY
        LD A,H
        CP $20
        LD A,L
        JR NZ,compiled_ship_raw
        ADD A,10
        JR compiled_ship_advance
compiled_ship_raw:
 ENDIF
        ADD A,9
compiled_ship_advance:
        LD L,A
        JR NC,compiled_ship_next
        INC H
compiled_ship_next:
        POP BC
        LD A,RUNTIME_MAP
        OUT ($F4),A
        LD A,2
        OUT ($FF),A
        POP AF
compiled_ship_no_ei:
        INC SP
        INC SP
        JP $8D4D
        ASSERT $ <= $FBA8
        DS $FBA8-$,$FF
compiled_cache_candidate:
        LD A,H
 IFDEF ROM_ONLY
        CP $20
 ELSE
        CP $A6
 ENDIF
        JP Z,$F8D0
        CP $D3
        JR NZ,compiled_cache_reject
        LD A,L
        CP $AB
        JR C,compiled_cache_reject
        CP $E3
        RET C
compiled_cache_reject:
        OR A
        RET
