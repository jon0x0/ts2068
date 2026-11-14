        ORG $0971
        LD SP,($5BCE)
        JP $0911
        DS $097B-$,$FF
        ASSERT $ == $097B
        LD A,$84
        LD I,A
        XOR A
        LD ($9000),A
        RET
        ASSERT $ <= $0990
