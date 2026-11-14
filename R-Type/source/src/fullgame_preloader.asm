; Stock-legacy TSPico SD/TAP preloader. Client and stack stay in HOME.
; Sixteen four-page TAP volumes, followed by a complete64-page verification sweep.
        DEFINE LEGACY_VIDEO 1
        DEFINE WORK_BASE $D000
        INCLUDE "third_party/fullgame_tspico/layout.inc"
PAGE_NO EQU $D600
REGION EQU $D601
BANK_CMD EQU $D602
REQUEST EQU $D603
SLOW_REPLY EQU $D604
BUFFER EQU $D606
CHECKSUMS EQU $D700
        ORG $8000
start:
        DI
        LD SP,$FFF0
        XOR A
        OUT ($F4),A
        LD HL,$6000
        LD DE,$6001
        LD BC,$1AFF
        LD (HL),0
        LDIR
        LD HL,$7800
        LD DE,$7801
        LD BC,767
        LD (HL),$47
        LDIR
        LD A,$41
        OUT ($FF),A
        LD HL,title_text
        LD DE,$6044
        CALL puts
        LD HL,load_text
        LD DE,$60C4
        CALL puts
        LD HL,copy_gateway
        LD DE,$FC00
        LD BC,copy_gateway_end-copy_gateway
        LDIR
        XOR A
        LD (PAGE_NO),A
        LD (BANK_CMD),A
        LD A,$FF
        LD (REGION),A
        LD A,1
        LD (SLOW_REPLY),A
        LD HL,root_name
        CALL legacy_chdir
        JP C,fatal
        LD HL,folder_name
        CALL legacy_chdir
        JP C,fatal
preload_page:
        LD A,(PAGE_NO)
        AND 3
        JR NZ,volume_ready
        LD A,(PAGE_NO)
        SRL A
        SRL A
        LD HL,file_name+4
        CALL hex_string
        LD A,1
        LD (SLOW_REPLY),A
        LD HL,file_name
        CALL legacy_mount
        JP C,fatal
volume_ready:
        XOR A
        LD (SLOW_REPLY),A
        CALL choose_buffer
        LD A,(PAGE_NO)
        LD HL,page_text+5
        CALL hex_string
        LD HL,page_text
        LD DE,$6844
        CALL puts
        LD DE,NAME_BUFFER
        LD BC,17
        XOR A
        CALL legacy_read_block
        JP C,fatal
        LD A,(NAME_BUFFER)
        CP 3
        JP NZ,bad_header
        LD HL,(NAME_BUFFER+11)
        LD DE,8192
        OR A
        SBC HL,DE
        JP NZ,bad_header
        LD HL,(NAME_BUFFER+13)
        LD A,(PAGE_NO)
        CP L
        JP NZ,bad_header
        LD A,H
        OR A
        JP NZ,bad_header
        LD DE,(BUFFER)
        LD BC,8192
        LD A,$FF
        CALL legacy_read_block
        JP C,fatal
        LD HL,(BUFFER)
        CALL checksum
        PUSH DE
        CALL checksum_address
        POP DE
        LD (HL),E
        INC HL
        LD (HL),D
        CALL ensure_region
        JP C,fatal
        CALL write_page
        CALL read_page
        CALL verify_buffer
        JP C,fatal
        LD HL,PAGE_NO
        INC (HL)
        LD A,(HL)
        CP 64
        JP C,preload_page
        XOR A
        LD (PAGE_NO),A
verify_page:
        CALL choose_buffer
        LD A,(PAGE_NO)
        LD HL,verify_text+7
        CALL hex_string
        LD HL,verify_text
        LD DE,$6884
        CALL puts
        CALL ensure_region
        JP C,fatal
        CALL read_page
        CALL verify_buffer
        JP C,fatal
        LD HL,PAGE_NO
        INC (HL)
        LD A,(HL)
        CP 64
        JR C,verify_page
        XOR A
        CALL select_region
        JP C,fatal
launch:
        LD HL,start_gateway
        LD DE,$FC00
        LD BC,start_gateway_end-start_gateway
        LDIR
        XOR A
        OUT ($FF),A
        JP $FC00
choose_buffer:
        LD HL,$4000
        LD A,(PAGE_NO)
        AND 7
        CP 2
        JR NZ,buffer_chosen
        LD HL,$A000
buffer_chosen:
        LD (BUFFER),HL
        RET
checksum_address:
        LD A,(PAGE_NO)
        LD L,A
        LD H,0
        ADD HL,HL
        LD BC,CHECKSUMS
        ADD HL,BC
        RET
checksum:
        LD DE,0
        LD BC,8192
checksum_loop:
        LD A,(HL)
        INC HL
        ADD A,E
        LD E,A
        ADD A,D
        LD D,A
        DEC BC
        LD A,B
        OR C
        JR NZ,checksum_loop
        RET
verify_buffer:
        LD HL,(BUFFER)
        CALL checksum
        PUSH DE
        CALL checksum_address
        POP DE
        LD A,(HL)
        CP E
        JR NZ,bad_checksum
        INC HL
        LD A,(HL)
        CP D
        JR NZ,bad_checksum
        OR A
        RET
bad_checksum:
        LD A,E_CHECKSUM
        SCF
        RET
page_registers:
        LD A,(PAGE_NO)
        AND 7
        LD C,A
        RRCA
        RRCA
        RRCA
        LD D,A
        LD E,0
        LD B,0
        LD HL,bank_masks
        ADD HL,BC
        LD A,(HL)
        LD BC,8192
        RET
write_page:
        CALL page_registers
        LD HL,(BUFFER)
        CP $80
        JP NZ,$FC00
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        LD HL,copy_gateway
        LD DE,$A000
        LD BC,copy_gateway_end-copy_gateway
        LDIR
        POP HL
        POP DE
        POP BC
        POP AF
        JP $A000
read_page:
        CALL page_registers
        EX DE,HL
        LD DE,(BUFFER)
        CP $80
        JP NZ,$FC00
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        LD HL,copy_gateway
        LD DE,$A000
        LD BC,copy_gateway_end-copy_gateway
        LDIR
        POP HL
        POP DE
        POP BC
        POP AF
        JP $A000
copy_gateway:
        OUT ($F4),A
        LDIR
        XOR A
        OUT ($F4),A
        RET
copy_gateway_end:
start_gateway:
        LD A,$10
        OUT ($F4),A
        JP $8008
start_gateway_end:
ensure_region:
        LD A,(PAGE_NO)
        SRL A
        SRL A
        SRL A
        LD B,A
        LD A,(REGION)
        CP B
        RET Z
        LD A,B
select_region:
        LD (REQUEST),A
        XOR A
        OUT ($F4),A
        INC A
        LD (BANK_CMD),A
        LD (SLOW_REPLY),A
        LD HL,memdock_name
        XOR A
        CALL legacy_execute
        RET C
        XOR A
        LD (BANK_CMD),A
        LD A,(REQUEST)
        LD (REGION),A
        LD A,1
        OUT ($F4),A
        LD B,8
prime:
        LD A,($0000)
        DJNZ prime
        XOR A
        OUT ($F4),A
        RET
ram_parameters:
        LD A,(BANK_CMD)
        OR A
        RET Z
        LD A,1
        LD (RX_BUFFER+3),A
        LD A,(REQUEST)
        ADD A,A
        LD (RX_BUFFER+5),A
        LD HL,RX_BUFFER
        LD B,9
        XOR A
parameter_xor:
        XOR (HL)
        INC HL
        DJNZ parameter_xor
        LD (HL),A
        LD HL,RX_BUFFER
        RET
video_settle:
        PUSH BC
        LD BC,8192
        LD A,(SLOW_REPLY)
        OR A
        JR Z,settle
        LD BC,0
settle:
        DEC BC
        LD A,B
        OR C
        JR NZ,settle
        POP BC
        RET
hex_string:
        PUSH AF
        RRCA
        RRCA
        RRCA
        RRCA
        CALL hex_digit
        LD (HL),A
        INC HL
        POP AF
        CALL hex_digit
        LD (HL),A
        RET
hex_digit:
        AND 15
        ADD A,'0'
        CP '9'+1
        RET C
        ADD A,7
        RET
puts:
        LD A,(HL)
        INC HL
        OR A
        RET Z
        PUSH HL
        SUB 32
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,font
        ADD HL,BC
        LD B,8
glyph:
        LD A,(HL)
        INC HL
        LD (DE),A
        INC D
        DJNZ glyph
        LD A,D
        SUB 8
        LD D,A
        INC E
        POP HL
        JR puts
bad_header:
        LD A,E_SYNC
fatal:
        LD HL,error_text+6
        CALL hex_string
        LD HL,error_text
        LD DE,$68C4
        CALL puts
        LD A,2
        OUT ($FE),A
fatal_halt:
        JR fatal_halt
bank_masks: DB 1,2,4,8,16,32,64,128
root_name: DB '/',0
folder_name: DB 'RTYPE',0
file_name: DB 'RTFG00.TAP',0
memdock_name: DB 'tpi:memdock',0
title_text: DB 'R-TYPE TS2068',0
load_text: DB 'LOADING 512K GAME',0
page_text: DB 'PAGE 00 / 3F',0
verify_text: DB 'VERIFY 00 / 3F',0
error_text: DB 'ERROR 00 - RESET TO RETRY',0
font: INCBIN "assets/fullgame_preloader_font.bin"
        INCLUDE "third_party/fullgame_tspico/ram512_transport.inc"
        INCLUDE "third_party/fullgame_tspico/ram512b_files.inc"
        ASSERT $ < $A000
