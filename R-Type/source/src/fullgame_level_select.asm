; Full-game only. FD95/FD96 and FD97..FDA2 are free resident HOME bytes.
        ORG $0C00
SELECTED EQU $FD95
SHOWN EQU $FD96
MESSAGE EQU $FD97
select_input:
        CALL $1A00
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        XOR A
        LD ($FDA2),A
        LD BC,$F7FE
        IN A,(C)
        CPL
        AND $1F
        LD D,1
        JR Z,select_upper
select_low_bit:
        RRA
        JR C,select_store
        INC D
        JR select_low_bit
select_upper:
        LD B,$EF
        IN A,(C)
        CPL
        AND $1C
        JR Z,select_display
        LD D,6
        BIT 4,A
        JR NZ,select_store
        INC D
        BIT 3,A
        JR NZ,select_store
        INC D
select_store:
        LD A,1
        LD ($FDA2),A
        LD A,D
        LD (SELECTED),A
select_display:
        IN A,($FF)
        AND 7
        CP 2
        JR NZ,select_done
        LD A,(SELECTED)
        LD D,A
        LD A,(SHOWN)
        CP D
        JR Z,select_done
        LD A,D
        LD (SHOWN),A
        ADD A,'0'
        OR $80
        LD (MESSAGE+10),A
        LD HL,select_message
        LD DE,MESSAGE
        LD BC,10
        LDIR
        LD HL,MESSAGE
        LD BC,$090A
        CALL $C084
        ; The original font has no hyphen glyph. Draw its middle stroke.
        LD A,$7E
        LD ($4B2B),A
        LD A,3
        OUT ($F4),A
        LD HL,$682A
        LD B,8
select_colour_row:
        PUSH BC
        LD C,11
select_colour_byte:
        LD (HL),$47
        INC L
        DEC C
        JR NZ,select_colour_byte
        LD A,L
        SUB 11
        LD L,A
        INC H
        POP BC
        DJNZ select_colour_row
        LD A,9
        OUT ($F4),A
select_done:
        POP HL
        POP DE
        POP BC
        POP AF
        RET
select_title_init:
        XOR A
        LD (SHOWN),A
        LD ($FDA3),A
        JP $0F20
select_start:
        CALL $73D8
        LD A,($FDA3)
        OR A
        RET Z
        XOR A
        LD ($FDA3),A
        LD A,(SELECTED)
        ADD A,'0'
        LD B,A
        LD A,($719C)
        CP B
        JR Z,select_checkpoint
        LD A,B
        DEC A
        LD ($719C),A
        CALL $0A08
select_checkpoint:
        CALL $8696
        RET
select_dispatch:
        DI
        CALL select_input
        EI
        PUSH AF
        LD A,($FDA2)
        OR A
        JR Z,select_original_actions
        POP AF
        RET
select_original_actions:
        POP AF
        JP $C014
select_arm:
        LD ($74FB),A
        PUSH AF
        LD A,1
        LD ($FDA3),A
        POP AF
        RET
select_message: DB "1-8 LEVEL "
        ASSERT $ <= $0D00
