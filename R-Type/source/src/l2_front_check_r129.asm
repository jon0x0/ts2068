        ORG $A807
skip_empty_cell:
        LD A,(IX)
        CP 7
        RET NZ
        POP AF
        LD DE,9
        ADD IX,DE
        JP next_cell
        ASSERT $ <= $A816
