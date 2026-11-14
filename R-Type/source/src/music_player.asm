        ORG $9C00
MSTACK EQU $FD50
MSP EQU $FD80
MSEQ EQU $FD82
MSHADOW EQU $FD84
MRUN EQU $FD92
music_tick:
        CALL $11D0 ; edge-triggered M key, independent of native control bindings
        LD A,($7AA4)
        OR A
        JR NZ,music_game
        LD A,(MRUN)
        OR A
        RET Z
        XOR A
        LD (MRUN),A
        LD E,A
        LD A,9
        CALL $F88C
        LD A,10
        JP $F88C
music_game:
        LD A,(MRUN)
        OR A
        JR NZ,music_next
        INC A
        LD (MRUN),A
        LD HL,MSTACK
        LD (MSP),HL
        LD HL,MUSIC_SEQUENCE
        LD (MSEQ),HL
        LD HL,MSHADOW
        LD B,14
        XOR A
music_zero:
        LD (HL),A
        INC HL
        DJNZ music_zero
music_next:
        LD HL,(MSP)
        LD DE,MSTACK
        OR A
        SBC HL,DE
        JR Z,music_sequence
        LD HL,(MSP)
        DEC HL
        LD D,(HL)
        DEC HL
        LD E,(HL)
        LD (MSP),HL
        EX DE,HL
        JR music_token
music_sequence:
        LD HL,(MSEQ)
        CALL music_word
        LD (MSEQ),HL
        EX DE,HL
        LD A,H
        AND L
        INC A
        JR NZ,music_token
        LD HL,MUSIC_SEQUENCE+2
        LD (MSEQ),HL
        JR music_next
music_token:
        LD DE,MUSIC_LEAVES
        OR A
        SBC HL,DE
        JR C,music_leaf_restore
        ADD HL,HL
        ADD HL,HL
        LD DE,MUSIC_PAIRS
        ADD HL,DE
        CALL music_word
        PUSH DE
        CALL music_word
        LD HL,(MSP)
        LD (HL),E
        INC HL
        LD (HL),D
        INC HL
        POP DE
        LD (HL),E
        INC HL
        LD (HL),D
        INC HL
        LD (MSP),HL
        JR music_next
music_leaf_restore:
        ADD HL,DE
        ADD HL,HL
        LD DE,MUSIC_DIRECTORY
        ADD HL,DE
        CALL music_word
        EX DE,HL
        CALL music_byte
        LD B,E
        INC B
        DEC B
        JR Z,music_flush
music_record:
        CALL music_byte
        PUSH HL
        LD D,0
        LD HL,MSHADOW
        ADD HL,DE
        EX DE,HL
        POP HL
        PUSH DE
        CALL music_byte
        POP IX
        LD (IX+0),E
        DJNZ music_record
music_flush:
        LD HL,MSHADOW
        LD B,11
        LD C,0
music_flush_reg:
        LD A,C
        CP 6
        JR Z,music_flush_skip
        CP 7
        JR Z,music_flush_skip
        CALL $0EA0
        JR C,music_flush_skip
music_emit:
        CALL $0ED4 ; mute only music-owned volume registers
        LD A,C
        CALL $F88C
music_flush_skip:
        INC HL
        INC C
        DJNZ music_flush_reg
        LD E,$B8
        LD A,($FBC1)
        OR A
        JR Z,music_mixer
        LD A,($FBC3)
        LD E,A
music_mixer:
        LD A,7
        JP $F88C
music_word:
        CALL music_byte
        LD C,E
        CALL music_byte
        LD D,E
        LD E,C
        RET
music_byte:
        LD A,H
        CP $E0
        JR NC,music_high_byte
        LD E,(HL)
        INC HL
        RET
music_high_byte:
        CALL $1AA0
        INC HL
        RET
        ASSERT $ <= $9D80
