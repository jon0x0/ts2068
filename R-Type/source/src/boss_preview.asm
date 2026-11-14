; Main-loop only, before native input. Two B press edges, with release between.
; Never runs from IRQ, title menus or key definition. FD4B is outside music stack.
        ORG $1FA3
        LD BC,$7FFE
        IN A,(C)
        AND $10
        JR NZ,boss_released
        LD A,($FD4B)
        CP 2
        JR Z,boss_jump
        OR A
        JR NZ,boss_done
        INC A
        LD ($FD4B),A
        JR boss_done
boss_released:
        LD A,($FD4B)
        CP 3
        JR Z,boss_unlatch
        CP 1
        JR NZ,boss_done
        INC A
        LD ($FD4B),A
        JR boss_done
boss_unlatch:
        XOR A
        LD ($FD4B),A
boss_done:
        JP $8B06
boss_jump:
        LD A,3
        LD ($FD4B),A
        LD HL,($0D71)
        LD ($C4AF),HL
        LD A,($0D73)
        LD ($C4AE),A
        CALL $1485 ; full ECM game initializer, including retained/front planes
        CALL $8721
        LD A,($0D74)
        LD ($7A9E),A
        CALL $8BAE
        JP $8B06
        ASSERT $ <= $2000
