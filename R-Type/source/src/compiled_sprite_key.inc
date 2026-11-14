        DS $F8D0-$,$FF
compiled_ship_candidate:
        LD A,L
 IFDEF ROM_ONLY
        CP $1E
 ELSE
        CP $1F
 ENDIF
        JR Z,compiled_ship_accept
        CP $28
        JR Z,compiled_ship_accept
 IFDEF ROM_ONLY
        CP $32
 ELSE
        CP $31
 ENDIF
        JR Z,compiled_ship_accept
        OR A
        RET
compiled_ship_accept:
        SCF
        RET
        ASSERT $ <= $F8E8
