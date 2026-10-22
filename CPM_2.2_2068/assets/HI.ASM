        ORG     100H
        LXI     D,MSG
        MVI     C,9
        CALL    5
        RET
MSG:    DB      'Assembled on the TS2068!',13,10,'$'
        END
