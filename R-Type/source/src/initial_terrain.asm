; Initial world draw has owner0 and direct pixels. Preserve its native
; attributes so FF7A can classify scrolling cells; actor overlays keep the
; retained background tags. No writes to ROM, and no collision rule changes.
        ORG $1160
initial_terrain_orientation:
        PUSH AF
        PUSH BC
        PUSH DE
        LD A,($7A9C)
        AND A
        JR NZ,initial_terrain_done
        LD B,(IX+10)
        LD A,(IX+16)
        CP $FD
        JR NZ,initial_terrain_other
        LD A,(IX+17)
        CP $8D
        JR Z,initial_terrain_reverse
initial_terrain_other:
        LD A,(IX+16)
        CP $57
        JR NZ,initial_terrain_store
        LD A,(IX+17)
        CP $8E
        JR NZ,initial_terrain_store
initial_terrain_reverse:
        SET 2,B
initial_terrain_store:
        LD E,(IX+8)
        LD D,(IX+9)
        LD A,B
        LD (DE),A
        LD A,D
        ADD A,9
        LD D,A
        LD A,(DE)
        OR $40
        LD (DE),A
initial_terrain_done:
        POP DE
        POP BC
        POP AF
        RET
        ASSERT $ <= $11B0
        DS $11B0-$,$FF
initial_native_attribute:
        LD A,($BE00)
        AND A
        JR Z,initial_native_store
        LD A,($7A9C)
        AND A
        RET NZ
initial_native_store:
        LD A,C
        CALL $0920
        LD C,A
        LD (DE),A
        RET
        ASSERT $ <= $1200
