; Persistent DOCK0 code, HSR=$01 during gameplay; no game RAM reservation.
; Separate from cartridge copy logic. Keyboard and both native sticks merge.
        ORG $1A00
read_input:
        LD HL,($74FC)
        LD DE,after_keyboard
        PUSH DE
        JP (HL)
after_keyboard:
        PUSH DE
        PUSH HL
        ; Mask the periodic source before sampling IFF2. Real Z80/Fuse can
        ; clear LD A,I parity if an interrupt is accepted before DI.
        IN A,($FF)
        PUSH AF
        OR $40
        OUT ($FF),A
        LD A,I
        PUSH AF
        DI
        LD A,7
        LD BC,$00F5
        OUT (C),A
        LD C,$F6
        IN A,(C)
        AND $BF
        OUT (C),A
        LD A,14
        LD C,$F5
        OUT (C),A
        LD BC,$01F6
        IN A,(C)
port1_value:
        LD D,A
        LD B,2
        IN A,(C)
port2_value:
        AND D
        CPL
        AND $8F
        LD E,A
        LD D,0
        BIT 0,E             ; up
        JR Z,no_up
        SET 3,D
no_up:  BIT 1,E             ; down
        JR Z,no_down
        SET 2,D
no_down: BIT 2,E            ; left
        JR Z,no_left
        SET 0,D
no_left: BIT 3,E            ; right
        JR Z,no_right
        SET 1,D
no_right: BIT 7,E
        JR Z,no_fire
        SET 4,D
no_fire:
        LD A,($74FA)
        OR D
        LD C,A
        LD ($74FA),A
        POP AF
        JP PO,no_enable
        EI
no_enable:
        POP AF
        OUT ($FF),A
        LD A,C
        OR A
        POP HL
        POP DE
input_done:
        RET
        ASSERT $ <= $1B00


        ; Key-definition completion must consume the final held key before menu.
        DS $1B00-$,$FF
finish_keys:
        CALL $C2C5
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
release_final_key:
        CALL $BF55
        LD A,D
        CP $FF
        JR NZ,release_final_key
        POP HL
        POP DE
        POP BC
        POP AF
        RET
        ASSERT $ <= $1B40
