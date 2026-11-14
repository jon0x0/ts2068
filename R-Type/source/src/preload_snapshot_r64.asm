; This image is linked after level_hotkeys_r61.asm in immutable bank1.
preload_begin:
        LD HL,(JOB_ORIG)
        LD D,L
        LD E,H
        LD B,0
        LD C,3
        LD HL,JOB_CTX0
choose_context:
        LD A,B
        CP D
        JR Z,next_context
        CP E
        JR Z,next_context
        LD (HL),A
        INC HL
        DEC C
        JR Z,contexts_ready
next_context:
        INC B
        JR choose_context
contexts_ready:
        LD A,($FD4A)
        LD (JOB_VALID),A
        LD HL,$A000
        LD DE,$8100
        LD BC,preload_driver_end-preload_driver
        LDIR
        LD HL,preload_driver_image
        LD DE,$A000
        LD BC,preload_driver_end-preload_driver
        LDIR
        LD HL,JOB_ORIG
        LD DE,preload_driver.state
        LD BC,9
        LDIR
        LD HL,snapshot_image
        LD DE,$7F00
        LD BC,snapshot_end-snapshot
        LDIR
        JP $7F00
snapshot_image:
        DISP $7F00
snapshot:
        LD SP,$5CC0
        LD HL,final_driver_image
        LD DE,$7B00
        LD BC,final_driver_end-final_driver
        LDIR
        LD HL,JOB_ORIG
        LD DE,final_driver.state
        LD BC,9
        LDIR
        LD A,(preload_driver.state+2)
        CALL preload_driver.select_slot
        JP C,preload_snapshot_error
        LD HL,$8000
        LD DE,$4000
        LD BC,$2000
        LD A,4
        CALL preload_driver.copy_chunk
        LD HL,$A000
        LD DE,$6000
        LD BC,$2000
        LD A,8
        CALL preload_driver.copy_chunk
        LD HL,$8100
        LD DE,$6000
        LD BC,preload_driver_end-preload_driver
        LD A,8
        CALL preload_driver.copy_chunk
        LD A,(preload_driver.state+3)
        CALL preload_driver.select_slot
        JP C,preload_snapshot_error
        LD HL,$C000
        LD DE,$4000
        LD BC,$2000
        LD A,4
        CALL preload_driver.copy_chunk
        LD HL,$E000
        LD DE,$6000
        LD BC,$2000
        LD A,8
        CALL preload_driver.copy_chunk
        LD A,(preload_driver.state+4)
        CALL preload_driver.select_slot
        JP C,preload_snapshot_error
        XOR A
        OUT ($F4),A
        LD HL,$4000
        LD DE,$8000
        LD BC,$2000
        LDIR
        LD HL,$8000
        LD DE,$4000
        LD BC,$2000
        LD A,4
        CALL preload_driver.copy_chunk
        LD HL,$6000
        LD DE,$8000
        LD BC,$2000
        LDIR
        LD HL,$8000
        LD DE,$6000
        LD BC,$2000
        LD A,8
        CALL preload_driver.copy_chunk
        LD A,(preload_driver.state+1)
        CALL preload_driver.select_slot
        JP C,preload_snapshot_error
        LD HL,$4000
        LD DE,$6000
        LD BC,NEW_LOADER_LENGTH
        LD A,4
        CALL preload_driver.copy_chunk
        JP PRELOAD_ENTRY
preload_snapshot_error:
        LD A,2
        OUT ($FE),A
        JR preload_snapshot_error
snapshot_end:
        ASSERT $ <= $8000
        ENT
