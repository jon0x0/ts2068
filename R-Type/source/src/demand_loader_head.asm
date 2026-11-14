; HOME6000 runtime. Physical region0=current level,7=resident loader + backup.
        DEFINE LEGACY_VIDEO 1
        DEFINE WORK_BASE $D000
        INCLUDE "third_party/fullgame_tspico/layout.inc"
PAGE_NO EQU $D600
REGION EQU $D601
BANK_CMD EQU $D602
REQUEST EQU $D603
SLOW_REPLY EQU $D604
BUFFER EQU $D606
BOOT_FLAG EQU $D608
LOAD_OP EQU $D609
ACTIVE_FILE EQU $D60A
CHECKSUMS EQU $D700
DESIRED EQU $FDA4
        ORG $6000
runtime_entry:
        DI
        XOR A
        OUT ($F4),A
        LD (BOOT_FLAG),A
        LD (BANK_CMD),A
        LD (PAGE_NO),A
        CALL install_gateways
        ; Preserve the old DOCK3 game state already copied to HOME4000.
        LD HL,$4000
        LD DE,$6000
        LD BC,$2000
        LD A,8
        CALL $5E00
        ; Region7 is selected by the entry gateway. Save both common code
        ; chunks before reusing them as disk buffers. HOME stack stays live.
        LD HL,$8000
        CALL backup_common
        LD HL,$A000
        CALL backup_common
        CALL refresh_gateways
        JP load_level
boot_entry:
        DI
        LD SP,$FFF0
        XOR A
        OUT ($F4),A
        LD (BANK_CMD),A
        LD (PAGE_NO),A
        INC A
        LD (BOOT_FLAG),A
        LD (DESIRED),A ; converted to ASCII below
        LD A,'1'
        LD (DESIRED),A
        LD HL,boot_name
        LD (ACTIVE_FILE),HL
        CALL draw_loading
        CALL install_gateways
        LD A,7
        CALL select_region
        JP C,fatal
        LD HL,$6000
        LD DE,0
        LD BC,program_end-$6000
        LD A,1
        CALL $5E00
load_level:
        LD A,0
        CALL select_region
        JP C,fatal
        LD HL,level_name
        LD A,(BOOT_FLAG)
        OR A
        JR Z,choose_level_name
        LD HL,boot_name
        JR name_ready
choose_level_name:
        LD A,(DESIRED)
        LD (level_name+6),A
name_ready:
        LD (ACTIVE_FILE),HL
        PUSH HL
        CALL draw_loading
        LD A,1
        LD (LOAD_OP),A
        LD (SLOW_REPLY),A
        POP HL
        CALL legacy_mount
        JP C,fatal
        XOR A
        LD (PAGE_NO),A
load_page:
        CALL draw_progress
        CALL choose_buffer
        LD A,2
        LD (LOAD_OP),A
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
        LD A,3
        LD (LOAD_OP),A
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
        LD A,4
        LD (LOAD_OP),A
        CALL write_page
        LD A,5
        LD (LOAD_OP),A
        CALL read_page
        CALL verify_buffer
        JP C,fatal
        LD HL,PAGE_NO
        INC (HL)
        LD A,(HL)
        CP 8
        JP C,load_page
        ; Check all pages again, not just the last write (alias protection).
        XOR A
        LD (PAGE_NO),A
verify_page:
        LD A,6
        LD (LOAD_OP),A
        CALL choose_buffer
        CALL read_page
        CALL verify_buffer
        JP C,fatal
        LD HL,PAGE_NO
        INC (HL)
        LD A,(HL)
        CP 8
        JR C,verify_page
        LD A,(BOOT_FLAG)
        OR A
        JR NZ,cold_launch
        LD A,7
        CALL select_region
        JP C,fatal
        LD HL,$8000
        CALL restore_common
        LD HL,$A000
        CALL restore_common
        LD HL,$6000
        LD DE,$4000
        LD BC,$2000
        LD A,8
        CALL $F900
        XOR A
        CALL select_region
        JP C,fatal
        LD HL,$D3E0
        LD DE,$F900
        LD BC,8
        LDIR
        LD HL,finish_tail
        LD DE,$5E00
        LD BC,finish_tail_end-finish_tail
        LDIR
        JP $5E00
cold_launch:
        LD HL,cold_gateway
        LD DE,$5E00
        LD BC,cold_gateway_end-cold_gateway
        LDIR
        XOR A
        OUT ($FF),A
        JP $5E00
cold_gateway:
        LD A,$10
        OUT ($F4),A
        JP $8008
cold_gateway_end:
install_gateways:
        LD HL,$F900
        LD DE,$D3E0
        LD BC,8
        LDIR
        LD HL,copy_gateway
        LD DE,$F900
        LD BC,8
        LDIR
refresh_gateways:
        LD HL,copy_gateway
        LD DE,$5E00
        LD BC,copy_gateway_end-copy_gateway
        LDIR
        LD HL,copy_gateway
        LD DE,$7800
        LD BC,copy_gateway_end-copy_gateway
        LDIR
        RET
copy_gateway:
        OUT ($F4),A
        LDIR
        XOR A
        OUT ($F4),A
        RET
copy_gateway_end:
backup_common:
        PUSH HL
        LD DE,$4000
        LD BC,$2000
        LDIR
        POP DE
        LD A,D
        CP $80
        LD A,$10
        JR Z,backup_mask
        LD A,$20
backup_mask:
        LD HL,$4000
        LD BC,$2000
        JP $F900
restore_common:
        PUSH HL
        LD A,H
        CP $80
        LD A,$10
        JR Z,restore_mask
        LD A,$20
restore_mask:
        LD DE,$4000
        LD BC,$2000
        CALL $F900
        POP DE
        LD HL,$4000
        LD BC,$2000
        LDIR
        RET
choose_buffer:
        LD HL,$A000
        LD A,(PAGE_NO)
        CP 5
        JR NZ,buffer_ready
        LD HL,$8000
buffer_ready:
        LD (BUFFER),HL
        RET
page_registers:
        LD A,(PAGE_NO)
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
        CP 4
        JP Z,$7800
        JP $5E00
read_page:
        CALL page_registers
        EX DE,HL
        LD DE,(BUFFER)
        CP 4
        JP Z,$7800
        JP $5E00
draw_loading:
        LD A,0
        OUT ($FF),A
        LD HL,$4000
        LD DE,$4001
        LD BC,$17FF
        LD (HL),0
        LDIR
        LD HL,$5800
        LD DE,$5801
        LD BC,767
        LD (HL),7
        LDIR
        LD A,(DESIRED)
        LD (load_text+14),A
        LD HL,title_text
        LD DE,$4048
        CALL puts
        LD HL,load_text
        LD DE,$40C8
        CALL puts
        LD HL,(ACTIVE_FILE)
        LD DE,$4808
        CALL puts
        RET
draw_progress:
        LD A,(PAGE_NO)
        LD HL,page_text+5
        CALL hex_string
        LD HL,page_text
        LD DE,$4848
        JP puts
bad_header:
        LD A,E_SYNC
fatal:
        LD HL,error_text+6
        CALL hex_string
        LD A,(LOAD_OP)
        LD HL,step_text+5
        CALL hex_string
        LD HL,error_text
        LD DE,$4884
        CALL puts
        LD HL,step_text
        LD DE,$48C4
        CALL puts
        LD A,2
        OUT ($FE),A
fatal_halt:
        JR fatal_halt
bank_masks: DB 1,2,4,8,16,32,64,128
boot_name: DB 'RTBOOT.TAP',0
level_name: DB 'LEVEL01.TAP',0
memdock_name: DB 'tpi:memdock',0
title_text: DB 'R-TYPE TS2068',0
load_text: DB 'LOADING LEVEL 1',0
page_text: DB 'PAGE 00 / 07',0
error_text: DB 'ERROR 00 - RESET TO RETRY',0
step_text: DB 'STEP 00',0


