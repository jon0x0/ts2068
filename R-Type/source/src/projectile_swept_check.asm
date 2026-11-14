        ORG $09B6
        LD A,B
        CP 20
        JP NC,$0190
        LD A,C
        CP 31
        JP NC,$0190
        PUSH DE
        CALL $C0E4
        CP $80 ; friendly player/shot IDs and dirty cells do not block
        POP DE
        JP NC,$0190
        JP $1E20
        ASSERT $ <= $09D0
