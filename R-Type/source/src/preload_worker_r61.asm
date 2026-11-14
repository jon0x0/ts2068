        ORG $8000
worker_entry:
        LD HL,$FDA7
        LD DE,worker_state
        LD BC,9
        LDIR
        LD A,(worker_state+7)
        LD (VALID),A
        XOR A
        LD (worker_level),A
        LD (worker_done),A
        LD (worker_done+1),A
        LD A,(VALID)
        LD C,A
        LD B,8
        LD HL,0
count_missing:
        SRL C
        JR C,count_next
        LD DE,48
        ADD HL,DE
count_next:
        DJNZ count_missing
        LD (worker_total),HL
        LD A,3
        LD (START_ACTIVE),A
worker_next_level:
        LD A,(worker_level)
        LD (TARGET),A
        LD E,A
        LD D,0
        LD HL,worker_masks
        ADD HL,DE
        LD A,(VALID)
        AND (HL)
        JP NZ,worker_level_ready
        LD A,(TARGET)
        ADD A,'1'
        LD (worker_name+6),A
        LD (DESIRED),A
        CALL runtime_loading_ui
        LD A,3
        LD (START_ACTIVE),A
        LD HL,preload_message
        LD DE,$4848
        CALL puts
        CALL worker_progress
        LD A,(TARGET)
        CALL select_region
        JP C,fatal
        LD HL,worker_name
        CALL startup_mount
        JP C,fatal
        XOR A
        LD (PIECE),A
worker_piece:
        CALL startup_asset_address
        CALL startup_read_fragment
        JP C,fatal
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
        LD HL,(worker_done)
        INC HL
        LD (worker_done),HL
        CALL worker_progress
        LD HL,PIECE
        INC (HL)
        LD A,(HL)
        CP 48
        JR C,worker_piece
        XOR A
        LD (PIECE),A
worker_verify:
        CALL startup_asset_address
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
        LD HL,PIECE
        INC (HL)
        LD A,(HL)
        CP 48
        JR C,worker_verify
        CALL target_mask
        LD HL,VALID
        OR (HL)
        LD (HL),A
worker_level_ready:
        LD HL,worker_level
        INC (HL)
        LD A,(HL)
        CP 8
        JP C,worker_next_level
        LD A,(VALID)
        CP $FF
        JP NZ,startup_verify_error
        XOR A
        LD (START_ACTIVE),A
        LD HL,restore_driver_image
        LD DE,$A000
        LD BC,PRELOAD_DRIVER_BYTES
        LDIR
        LD HL,worker_state
        LD DE,PRELOAD_DRIVER_STATE
        LD BC,9
        LDIR
        LD HL,restore_image
        LD DE,$5E00
        LD BC,RESTORE_BYTES
        LDIR
        JP $5E00
worker_progress:
        LD HL,(worker_total)
        LD DE,$5071
        CALL startup_number
        LD HL,(worker_done)
        LD DE,$5063
        JP startup_number
worker_state: DS 9,0
worker_level: DB 0
worker_done: DW 0
worker_total: DW 0
preload_message: DB "PRELOADING ALL  ",0
worker_name: DB 'START01.TAP',0
worker_masks: DB 1,2,4,8,16,32,64,128
restore_driver_image: INCBIN "build/fullgame/startup_r61/preload_driver.bin"
restore_image: INCBIN "build/fullgame/startup_r61/preload_restore.bin"
        ASSERT $ <= $A000
