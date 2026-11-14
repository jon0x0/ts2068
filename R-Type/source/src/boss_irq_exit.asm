        ORG $0971
        LD SP,($5BCE)
        LD A,($FBCA)
        JP $FD40
        ASSERT $ == $097B
        LD A,$84
        LD I,A
        XOR A
        LD ($9000),A
        RET
        ASSERT $ <= $0990
