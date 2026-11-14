; The native star ID grid ends before the IRQ stub; never extend it into8383.
        ORG $01A0
        LD A,($7AA4)
        OR A
        JR NZ,star_native_entry
        LD A,H
        AND $18
        CP $10
        JR NZ,star_native_entry
        LD A,L
        AND $E0
        CP $60
        JR C,star_native_entry
        INC E
        INC E
        RET
star_native_entry:
        LD A,(DE)
        INC E
        LD B,1
        JP $BE9B
        ASSERT $ <= $01C8
