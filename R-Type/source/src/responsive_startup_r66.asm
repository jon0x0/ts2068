; Cold startup only: complete 1KB replies before switching files.
START_ACTIVE EQU $D610
RX_TICKS EQU $D611
WANTED EQU $D612
RUN_LEVEL EQU $D613
PIECE EQU $D614
CORE_PIECE EQU $D615
SHOWN_LEVEL EQU $D616
SHOW_COUNT EQU $D617
LOGO_COL EQU $D618
HASH_SAVE EQU $D61A
SAVED_HOLDER EQU $D61C
START_BUFFER EQU $D61D
ACTUAL_BANK EQU $D61F
START_ALL EQU $D623

early_start:
        DI
        LD SP,$FFF0
        XOR A
        OUT ($F4),A
        OUT ($FE),A
        LD (VALID),A
        LD (RX_TICKS),A
        LD (SHOWN_LEVEL),A
        LD (LOGO_COL),A
        LD (SHOW_COUNT),A
        LD (BOOT_FLAG),A
        LD (START_ALL),A
        INC A
        LD (START_ACTIVE),A
        LD A,'1'
        LD (WANTED),A
        LD HL,loading_screen
        LD DE,$4000
        CALL startup_unpack
        XOR A
        OUT ($FF),A
        CALL install_gateways
start_restart:
        LD A,(WANTED)
        LD (RUN_LEVEL),A
        LD (DESIRED),A
        LD (start_name+6),A
        SUB '1'
        LD (TARGET),A
        CALL select_region
        JP C,fatal
        LD HL,start_name
        CALL startup_mount
        JP C,fatal
        XOR A
        LD (PIECE),A
start_asset:
        CALL startup_progress
        CALL startup_asset_address
        CALL startup_read_fragment
        JP C,fatal
        CALL startup_cancelled
        JP NZ,start_restart
        CALL startup_hash
        LD (HASH_SAVE),DE
        CALL startup_hash_slot
        LD (HL),E
        INC HL
        LD (HL),D
        CALL startup_write_fragment
        CALL startup_readback
        CALL startup_hash
        LD HL,(HASH_SAVE)
        OR A
        SBC HL,DE
        JP NZ,startup_verify_error
        LD HL,PIECE
        INC (HL)
        LD A,(HL)
        CP 48
        JR C,start_asset
        LD HL,core_name
        CALL startup_mount
        JP C,fatal
        XOR A
        LD (CORE_PIECE),A
start_core:
        CALL startup_progress
        LD HL,$A000
        LD (START_BUFFER),HL
        LD A,(CORE_PIECE)
        CALL startup_read_fragment_index
        JP C,fatal
        CALL startup_cancelled
        JP NZ,start_restart
        LD A,(CORE_PIECE)
        CP 16
        JR NC,core_home
        ADD A,16
        ; Core0..15 -> physical fragments16..31 (banks2/3).
        CALL startup_actual_address
        CALL startup_hash
        CALL startup_hash_slot
        LD (HL),E
        INC HL
        LD (HL),D
        CALL startup_write_fragment
        JR core_next
core_home:
        CP 20
        JR C,core_workspace
        SUB 20
        ADD A,A
        ADD A,A
        ADD A,$D8
        JR core_store
core_workspace:
        SUB 16
        ADD A,A
        ADD A,A
        ADD A,$C0
core_store:
        LD D,A
        LD E,0
        LD HL,$A000
        LD BC,1024
        LDIR
core_next:
        LD HL,PIECE
        INC (HL)
        LD HL,CORE_PIECE
        INC (HL)
        LD A,(HL)
        CP 22
        JR C,start_core
        LD HL,verify_message
        LD DE,$5003
        CALL puts
        XOR A
        LD (CORE_PIECE),A
start_verify:
        CALL startup_poll
        CALL startup_cancelled
        JP NZ,start_restart
        LD A,(CORE_PIECE)
        CALL startup_actual_address
        CALL startup_readback
        CALL startup_hash
        CALL startup_hash_slot
        LD A,(HL)
        CP E
        JP NZ,startup_verify_error
        INC HL
        LD A,(HL)
        CP D
        JP NZ,startup_verify_error
        LD HL,CORE_PIECE
        INC (HL)
        LD A,(HL)
        CP 64
        JR C,start_verify
        CALL startup_cancelled
        JP NZ,start_restart
        LD HL,prepare_message
        LD DE,$5003
        CALL puts
        LD A,(TARGET)
        INC A
        AND 7
        LD (SAVED_HOLDER),A
        LD (RESIDENT),A
        CALL select_region
        JP C,fatal
        LD HL,$6000
        LD DE,$4000
        LD BC,program_end-$6000
        LD A,4
        CALL $7B00
        LD A,(TARGET)
        CALL select_region
        JP C,fatal
        CALL startup_cancelled
        JP NZ,start_restart
        XOR A
        LD (START_ACTIVE),A
        ; Blank the secondary standard screen before hiding the loader.
        LD HL,$7800
        LD DE,$7801
        LD BC,$2FF
        LD (HL),0
        LDIR
        LD A,$41
        OUT ($FF),A
        LD HL,$E000
        LD DE,$4000
        LD BC,$2000
        LD A,$80
        CALL $7B00
        CALL refresh_gateways
        LD HL,$4000
        LD DE,$8000
        LD BC,$2000
        LD A,4
        CALL $7B00
        LD HL,$6000
        LD DE,$A000
        LD BC,$2000
        LD A,8
        CALL $5E00
        LD A,(SAVED_HOLDER)
        LD (cold_start_image+cold_holder-cold_start+1),A
        LD A,(TARGET)
        LD (cold_start_image+cold_current-cold_start+1),A
        LD E,A
        LD D,0
        LD HL,cache_masks
        ADD HL,DE
        LD A,(HL)
        LD (cold_start_image+cold_valid-cold_start+1),A
        LD A,(RUN_LEVEL)
        LD (cold_start_image+cold_level-cold_start+1),A
        SUB '0'
        LD (cold_start_image+cold_selected-cold_start+1),A
        LD A,(START_ALL)
        LD (cold_start_image+cold_all-cold_start+1),A
        LD HL,cold_start_image
        LD DE,$5E00
        LD BC,cold_start_end-cold_start
        LDIR
        JP $5E00
startup_verify_error:
        LD A,E_CHECKSUM
        JP fatal
startup_cancelled:
        LD A,(RUN_LEVEL)
        LD HL,WANTED
        CP (HL)
        RET
startup_mount:
        LD A,1
        LD (SLOW_REPLY),A
        LD (LOAD_OP),A
        JP legacy_mount
startup_read_fragment:
        LD A,(PIECE)
startup_read_fragment_index:
        LD (expected_fragment),A
        XOR A
        LD (SLOW_REPLY),A
        LD A,2
        LD (LOAD_OP),A
        LD DE,NAME_BUFFER
        LD BC,17
        XOR A
        CALL legacy_read_block
        RET C
        LD A,(NAME_BUFFER)
        CP 3
        JR NZ,start_bad
        LD HL,(NAME_BUFFER+11)
        LD DE,1024
        OR A
        SBC HL,DE
        JR NZ,start_bad
        LD HL,(NAME_BUFFER+13)
        LD A,(expected_fragment)
        CP L
        JR NZ,start_bad
        LD A,H
        OR A
        JR NZ,start_bad
        LD A,3
        LD (LOAD_OP),A
        LD DE,(START_BUFFER)
        LD BC,1024
        LD A,$FF
        JP legacy_read_block
start_bad:
        LD A,E_SYNC
        SCF
        RET
startup_asset_address:
        LD A,(PIECE)
        RRCA
        RRCA
        RRCA
        AND 7
        LD E,A
        LD D,0
        LD HL,start_banks
        ADD HL,DE
        LD A,(HL)
        ADD A,A
        ADD A,A
        ADD A,A
        LD E,A
        LD A,(PIECE)
        AND 7
        OR E
startup_actual_address:
        LD (actual_fragment),A
        RRCA
        RRCA
        RRCA
        AND 7
        LD (PAGE_NO),A
        LD (ACTUAL_BANK),A
        LD HL,$A000
        CP 5
        JR NZ,start_buf_ready
        LD HL,$8000
        LD A,(START_ACTIVE)
        CP 1
        JR Z,start_buf_ready
        LD HL,$C000
start_buf_ready:
        LD (START_BUFFER),HL
        RET
startup_transfer_regs:
        CALL page_registers
        LD A,(actual_fragment)
        AND 7
        ADD A,A
        ADD A,A
        ADD A,D
        LD D,A
        LD BC,1024
        LD A,(ACTUAL_BANK)
        LD L,A
        LD H,0
        PUSH DE
        LD DE,bank_masks
        ADD HL,DE
        LD A,(HL)
        POP DE
        RET
startup_write_fragment:
        LD A,4
        LD (LOAD_OP),A
        CALL startup_transfer_regs
        LD HL,(START_BUFFER)
        CP 4
        JP Z,$7B00
        JP $5E00
startup_readback:
        LD A,5
        LD (LOAD_OP),A
        CALL startup_transfer_regs
        EX DE,HL
        LD DE,(START_BUFFER)
        CP 4
        JP Z,$7B00
        JP $5E00
startup_hash_slot:
        LD A,(actual_fragment)
        ADD A,A
        LD L,A
        LD H,0
        LD BC,CHECKSUMS
        ADD HL,BC
        RET
startup_hash:
        LD HL,(START_BUFFER)
        LD BC,1024
        LD DE,0
start_hash_byte:
        LD A,(HL)
        ADD A,E
        LD E,A
        JR NC,start_hash_no_carry
        INC D
start_hash_no_carry:
        INC HL
        DEC BC
        LD A,B
        OR C
        JR NZ,start_hash_byte
        RET
startup_rx_hook:
        PUSH AF
        LD A,(START_ACTIVE)
        OR A
        JR Z,start_hook_done
        LD A,(RX_TICKS)
        INC A
        LD (RX_TICKS),A
        AND $7F
        JR NZ,start_hook_done
        PUSH BC
        PUSH DE
        PUSH HL
        LD A,(START_ACTIVE)
        CP 1
        CALL Z,startup_poll
        LD A,(START_ACTIVE)
        CP 1
        CALL NZ,start_sweep
        POP HL
        POP DE
        POP BC
start_hook_done:
        POP AF
        RET
startup_poll:
        LD A,(START_ALL)
        OR A
        JR NZ,poll_level
        LD BC,$FEFE
        IN A,(C)
        AND 1
        JR NZ,poll_level
        LD B,$BF
        IN A,(C)
        AND 2
        JR NZ,poll_level
        LD A,1
        LD (START_ALL),A
        LD HL,all_queued
        LD DE,$4804
        CALL puts
poll_level:
        LD BC,$F7FE
        IN A,(C)
        CPL
        AND 31
        LD D,'1'
        JR Z,start_upper
start_bit:
        RRA
        JR C,start_set
        INC D
        JR start_bit
start_upper:
        LD B,$EF
        IN A,(C)
        CPL
        AND $1C
        JR Z,start_show
        LD D,'6'
        BIT 4,A
        JR NZ,start_set
        INC D
        BIT 3,A
        JR NZ,start_set
        INC D
start_set:
        LD A,D
        LD (WANTED),A
start_show:
        LD A,(WANTED)
        LD HL,SHOWN_LEVEL
        CP (HL)
        JR Z,start_sweep
        LD (HL),A
        SUB '0'
        LD DE,$4895
        CALL startup_digit
start_sweep:
        LD A,(LOGO_COL)
        LD E,A
        LD HL,logo_attributes
        LD A,E
        ADD A,$20
        LD E,A
        LD D,$58
        LD B,6
start_restore_col:
        LD A,(HL)
        LD (DE),A
        INC HL

        LD A,E
        ADD A,32
        LD E,A
        DJNZ start_restore_col
        LD A,(LOGO_COL)
        INC A
        AND 31
        LD (LOGO_COL),A
        ADD A,$20
        LD E,A
        LD D,$58
        LD B,6
start_light_col:
        LD A,7
        LD (DE),A
        LD A,E
        ADD A,32
        LD E,A
        DJNZ start_light_col
        RET
startup_progress:
        CALL startup_poll
        LD A,(PIECE)
        INC A
        CP 71
        JR C,start_count_ok
        LD A,70
start_count_ok:
        LD L,A
        LD H,0
        LD DE,$5063
        JP startup_number
runtime_loading_ui:
        LD HL,$7800
        LD DE,$7801
        LD BC,$2FF
        LD (HL),0
        LDIR
        LD HL,loading_screen
        LD DE,$4000
        CALL startup_unpack
        XOR A
        OUT ($FF),A
        LD A,(DESIRED)
        SUB '0'
        LD DE,$4895
        CALL startup_digit
        LD HL,8
        LD DE,$5071
        CALL startup_number
        LD A,2
        LD (START_ACTIVE),A
        RET
runtime_progress_ui:
        LD A,(PAGE_NO)
        INC A
        LD L,A
        LD H,0
        LD DE,$5063
        JP startup_number
startup_number:
        PUSH DE
        LD BC,100
        XOR A
number_hundreds:
        OR A
        SBC HL,BC
        JR C,number_h_done
        INC A
        JR number_hundreds
number_h_done:
        ADD HL,BC
        LD ($D620),A
        LD A,L
        LD B,0
number_tens:
        CP 10
        JR C,number_t_done
        SUB 10
        INC B
        JR number_tens
number_t_done:
        LD ($D622),A
        LD A,B
        LD ($D621),A
        POP DE
        PUSH DE
        LD A,($D620)
        CALL startup_digit
        POP DE
        INC E
        INC E
        PUSH DE
        LD A,($D621)
        CALL startup_digit
        POP DE
        INC E
        INC E
        LD A,($D622)
        JP startup_digit
preload_entry:
        DI
        LD SP,$FFF0
        LD E,0
        LD A,8
        CALL $F88C
        LD A,9
        CALL $F88C
        LD A,10
        CALL $F88C
        XOR A
        OUT ($F4),A
        LD (BOOT_FLAG),A
        CALL install_gateways
        LD A,($FDA7)
        ADD A,'1'
        LD (DESIRED),A
        CALL runtime_loading_ui
        LD A,3
        LD (START_ACTIVE),A
        LD HL,preload_name
        CALL startup_mount
        JP C,fatal
        LD A,2
        LD (LOAD_OP),A
        LD DE,NAME_BUFFER
        LD BC,17
        XOR A
        CALL legacy_read_block
        JP C,fatal
        LD HL,(NAME_BUFFER+11)
        LD DE,8192
        OR A
        SBC HL,DE
        JP NZ,bad_header
        LD DE,$8000
        LD BC,8192
        LD A,$FF
        CALL legacy_read_block
        JP C,fatal
        JP $8000
preload_name: DB 'RTPRELD.TAP',0
startup_digit:
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,loading_digits
        ADD HL,BC
        LD C,2
start_digit_half:
        LD B,8
start_digit_row:
        LD A,(HL)
        INC HL
        LD (DE),A
        INC E
        LD A,(HL)
        INC HL
        LD (DE),A
        DEC E
        INC D
        DJNZ start_digit_row
        LD A,D
        SUB 8
        LD D,A
        LD A,E
        ADD A,32
        LD E,A
        DEC C
        JR NZ,start_digit_half
        RET
startup_unpack:
        LD A,(HL)
        INC HL
        OR A
        RET Z
        JP M,start_backref
        LD C,A
        LD B,0
        LDIR
        JR startup_unpack
start_backref:
        AND $7F
        ADD A,3
        LD C,(HL)
        INC HL
        LD B,(HL)
        INC HL
        PUSH HL
        LD H,D
        LD L,E
        OR A
        SBC HL,BC
        LD C,A
        LD B,0
        LDIR
        POP HL
        JR startup_unpack
start_banks: DB 0,1,4,5,6,7
start_name: DB 'START01.TAP',0
core_name: DB 'RTCORE.TAP',0
verify_message: DB 'VERIFYING MEMORY',0
prepare_message: DB 'PREPARING GAME  ',0
all_queued: DB 'LOAD ALL QUEUED ',0
expected_fragment: DB 0
actual_fragment: DB 0
cold_start_image:
        DISP $5E00
cold_start:
        LD A,8
        OUT ($F4),A
        LD HL,$C000
        LD DE,$6000
        CALL cold_unpack
        XOR A
        OUT ($F4),A
        LD A,$40
        OUT ($F4),A
        LD HL,$C000
        LD DE,$E000
        LD BC,$2000
        LDIR
        XOR A
        OUT ($F4),A
        LD HL,$CC00
        LD DE,$FC50
        LD BC,$3B0
        LDIR
        LD HL,$D800
        LD DE,$C000
        LD BC,$04AE
        LDIR
        LD A,$20
        OUT ($F4),A
        LD HL,$A4AE
        LD DE,$C4AE
        LD BC,$1B52
        LDIR
        LD A,9
        OUT ($F4),A
        LD HL,$FB7E
        LD ($C291),HL
cold_holder:
        LD A,1
        LD ($FD48),A
cold_current:
        LD A,0
        LD ($FD49),A
cold_valid:
        LD A,1
        LD ($FD4A),A
cold_level:
        LD A,'1'
        LD ($719C),A
        LD ($FDA4),A
cold_selected:
        LD A,1
        LD ($FD95),A
        XOR A
        LD ($FD4B),A
        LD ($FDA5),A
cold_all:
        LD A,0
        LD ($FDA6),A
        LD HL,$5B00
        LD DE,$FB00
        LD BC,$00C0
        LDIR
        CALL $00D4
        XOR A
        LD HL,$4000
        LD DE,$4001
        LD BC,$1AFF
        LD (HL),A
        LDIR
        OUT ($FF),A
        LD HL,$1809
        LD ($58FD),HL
        LD HL,$203B
        LD ($58FF),HL
        LD SP,$58FD
        POP AF
        EX AF,AF'
        POP AF
        LD HL,$4747
        LD ($58FD),HL
        LD HL,$4743
        LD ($58FF),HL
        LD BC,$081A
        LD DE,$6F9E
        LD HL,$B049
        EXX
        LD BC,$0104
        LD DE,$2027
        LD HL,$017F
        LD IX,$F85A
        LD IY,$5C3A
        LD SP,$FFFE
        LD A,$84
        LD I,A
        IM 2
        LD A,9
        EI
        OUT ($F4),A
        LD HL,$8634
        PUSH HL
        JP $00DB
cold_unpack:
        LD A,(HL)
        INC HL
        OR A
        RET Z
        JP M,cold_backref
        LD C,A
        LD B,0
        LDIR
        JR cold_unpack
cold_backref:
        AND $7F
        ADD A,3
        LD C,(HL)
        INC HL
        LD B,(HL)
        INC HL
        PUSH HL
        LD H,D
        LD L,E
        OR A
        SBC HL,BC
        LD C,A
        LD B,0
        LDIR
        POP HL
        JR cold_unpack
cold_start_end:
        ASSERT $ <= $6000
        ENT
loading_screen: INCBIN "build/fullgame/startup_r61/loading_ui.lz"
loading_digits: INCBIN "build/fullgame/startup_r61/loading_digits.bin"
logo_attributes: INCBIN "build/fullgame/startup_r61/loading_logo_attrs.bin"
