; HOME-only level transition. Stock legacy TSPico MEMDOCK, regions0..7 slots0..14.
; All external code is unmapped during command exchange; eight read-only cycles
; prime selectors before the first write. Caller is the enabled-IRQ game mainline.
        ORG $A000
load_next_level:
        DI
        LD A,($719C)
        INC A
        CP '9'
        JR C,level_number_ok
        LD A,'1'
level_number_ok:
        LD ($719C),A
        SUB '1'
        ADD A,A
        LD (command_header+5),A
        LD E,0
        LD A,8
        CALL $F88C
        LD A,9
        CALL $F88C
        LD A,10
        CALL $F88C
        XOR A
        OUT ($F4),A
        ; Blank the alternate HOME display while its primary plane is a bounce.
        LD HL,$6000
        LD DE,$6001
        LD BC,$1AFF
        LD (HL),0
        LDIR
        LD A,$41
        OUT ($FF),A
        LD A,8
        OUT ($F4),A
        LD HL,$6000
        LD DE,$4000
        LD BC,$2000
        LDIR
        XOR A
        OUT ($F4),A
        ; Eight-page bounce overwrote native staging; install tail only now.
        LD A,$80
        OUT ($F4),A
        LD HL,$FBE0
        LD DE,$5E00
        LD BC,TRAMP_LENGTH
        LDIR
        XOR A
        OUT ($F4),A
        CALL select_region
        JP C,load_error
        JP $5E00

select_region:
        LD HL,command_header
        LD B,9
        XOR A
header_xor:
        XOR (HL)
        INC HL
        DJNZ header_xor
        LD (HL),A
        LD HL,command_header
        LD B,10
send_header:
        LD A,(HL)
        INC HL
        CALL tx_byte
        DJNZ send_header
        LD E,1
        CALL wait_token
        RET C
        LD E,$40
        CALL wait_token
        RET C
        LD HL,command_body
        LD B,command_body_end-command_body
send_body:
        LD A,(HL)
        INC HL
        CALL tx_byte
        DJNZ send_body
        LD E,$40
        CALL wait_token
        RET C
        CALL read_available
        RET C
        CP 1
        JR Z,command_ok
        CP $81
        JR NZ,command_failed
        CALL read_available
        RET C
        LD C,A
        LD HL,0
drain_text:
        CALL rx_byte
        OR A
        JR Z,text_finished
        DEC HL
        LD A,H
        OR L
        JR NZ,drain_text
        JR command_failed
text_finished:
        LD A,C
        CP 1
        JR NZ,command_failed
command_ok:
        ; Retain the demonstrated legacy cleanup guard (~2.4 seconds).
        LD DE,5
settle_outer:
        LD BC,0
settle_inner:
        DEC BC
        LD A,B
        OR C
        JR NZ,settle_inner
        DEC DE
        LD A,D
        OR E
        JR NZ,settle_outer
        LD A,1
        OUT ($F4),A
        LD B,8
prime_selectors:
        LD A,($0000)
        DJNZ prime_selectors
        XOR A
        OUT ($F4),A
        RET
command_failed:
        SCF
        RET
wait_token:
        LD B,20
        LD HL,0
wait_token_loop:
        CALL rx_byte
        CP E
        RET Z
        DEC HL
        LD A,H
        OR L
        JR NZ,wait_token_loop
        DJNZ wait_token_loop
        SCF
        RET
read_available:
        LD HL,0
read_available_loop:
        CALL rx_byte
        CP $FF
        JR Z,read_available_empty
        OR A
        RET
read_available_empty:
        DEC HL
        LD A,H
        OR L
        JR NZ,read_available_loop
        SCF
        RET
tx_byte:
        OUT ($0E),A
        PUSH BC
        LD B,24
tx_delay:
        DJNZ tx_delay
        POP BC
        RET
rx_byte:
        PUSH BC
        LD B,18
rx_delay:
        DJNZ rx_delay
        POP BC
        IN A,($0E)
        RET
load_error:
        XOR A
        OUT ($F4),A
        LD A,2
        OUT ($FE),A
        LD A,$82
        LD ($6000),A
        LD A,$42
        LD ($7800),A
load_error_halt:
        JR load_error_halt
command_header:
        DB $42,0,$FF,1,0,0,0,11,0,0
command_body:
        DB $44,11,0,"tpi:memdock",$44^11^'t'^'p'^'i'^':'^'m'^'e'^'m'^'d'^'o'^'c'^'k'
command_body_end:
        ASSERT $ <= $A190
