; One toggle per press. Called from native50Hz music IRQ before song decoding.
; Bit2 of row7FFE is M. No AY joystick registers are touched.
        ORG $11D0
        LD BC,$7FFE
        IN A,(C)
        AND 4
        LD HL,$FD94
        JR NZ,music_key_released
        LD A,(HL)
        OR A
        RET NZ
        INC (HL)
        LD HL,$FD93
        LD A,(HL)
        XOR 1
        LD (HL),A
        RET
music_key_released:
        XOR A
        LD (HL),A
        RET
        ASSERT $ <= $1200
