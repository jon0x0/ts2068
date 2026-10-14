; Optional ROM4 mixed-load scheduler. AF'=8 option bits; BC'=batch count;
; D'=saved RAM phase; E'=armed/profile bits; IX=RAM address across slices.
; IRQ-return paths below are separately selected, explicitly RAM exposed.
 ORG $8400
 jp load_init
 jp load_irq_arrived
 jp load_config_ready
 jp load_warning_ready
 jp load_return_handler
 jp load_running_ready
 jp load_work_ram
 jp load_phase_done
 jp load_work_stack
 jp load_batch_done
 jp load_return_after_af
 ASSERT $ == $8421 ; Fixed ROM0 -> ROM4 bridge ABI, eleven JP stubs.
 INCLUDE "../build/load-low.asm"
load_init:
 di
 ld a,$40
 out ($ff),a
 ld a,$83
 ex af,af'
 exx
 ld bc,0
 ld de,0
 ld hl,0
 exx
 jp load_loadcfg
load_config_ready:
 ex af,af'
 ld e,a
 ex af,af'
 ld hl,$58c1
 ld d,8
load_config_color:
 ld a,$47
 bit 0,e
 jp z,load_config_paint
 ld a,$44
load_config_paint:
 ld b,30
load_config_row:
 ld (hl),a
 inc hl
 djnz load_config_row
 inc hl
 inc hl
 srl e
 dec d
 jp nz,load_config_color
 exx
 bit 2,e
 exx
 ld d,$47
 ld e,$44
 jp z,load_config_duration_paint
 ld d,$44
 ld e,$47
load_config_duration_paint:
 ld hl,$5a2b
 ld b,5
load_config_duration_n:
 ld (hl),d
 inc hl
 djnz load_config_duration_n
 ld hl,$5a33
 ld b,12
load_config_duration_c:
 ld (hl),e
 inc hl
 djnz load_config_duration_c
 exx
 res 7,e
 exx
load_config_poll:
 ld bc,$7ffe
 in a,(c)
 bit 2,a
 jp z,menu_draw
 ld bc,$00fe
 in a,(c)
 and $1f
 cp $1f
 jp nz,load_config_pressed
 exx
 set 7,e
 exx
 jp load_config_poll
load_config_pressed:
 exx
 bit 7,e
 res 7,e
 exx
 jp z,load_config_poll
 ld bc,$f7fe
 in a,(c)
 bit 0,a
 ld d,1
 jp z,load_toggle
 bit 1,a
 ld d,2
 jp z,load_toggle
 bit 2,a
 ld d,4
 jp z,load_toggle
 bit 3,a
 ld d,8
 jp z,load_toggle
 bit 4,a
 ld d,16
 jp z,load_toggle
 ld bc,$effe
 in a,(c)
 bit 4,a
 ld d,32
 jp z,load_toggle
 bit 3,a
 ld d,64
 jp z,load_toggle
 bit 2,a
 ld d,128
 jp z,load_toggle
 ld bc,$fdfe
 in a,(c)
 bit 0,a
 jp z,load_all_preset
 bit 1,a
 jp z,load_start_safe
 ld bc,$7ffe
 in a,(c)
 bit 4,a
 jp z,load_baseline_preset
 bit 3,a
 jp z,load_one_batch
 ld bc,$fefe
 in a,(c)
 bit 3,a
 jp z,load_continuous
 ld bc,$fbfe
 in a,(c)
 bit 3,a
 jp z,load_loadwarning
 ld bc,$dffe
 in a,(c)
 bit 0,a
 jp z,load_all_preset ; P power preset selects all, including option6 cycling.
 jp load_config_poll
load_toggle:
 ex af,af'
 xor d
 ex af,af'
 jp load_loadcfg
load_all_preset:
 ld a,$ff
 jp load_preset
load_baseline_preset:
 ld a,$83
load_preset:
 ex af,af'
 jp load_loadcfg
load_one_batch:
 exx
 set 2,e
 exx
 jp load_loadcfg
load_continuous:
 exx
 res 2,e
 exx
 jp load_loadcfg
load_warning_ready:
 exx
 ld a,e
 and 4
 ld e,a
 exx
load_warning_poll:
 ld bc,$7ffe
 in a,(c)
 bit 2,a
 jp z,load_loadcfg
 ld bc,$00fe
 in a,(c)
 and $1f
 cp $1f
 jp nz,load_warning_pressed
 exx
 set 7,e
 exx
 jp load_warning_poll
load_warning_pressed:
 exx
 bit 7,e
 res 7,e
 exx
 jp z,load_warning_poll
 ld bc,$fbfe
 in a,(c)
 bit 4,a
 jp z,load_warning_im2
 bit 3,a
 jp nz,load_warning_poll
 exx
 set 0,e
 exx
 ex af,af'
 or 8
 ex af,af'
 jp load_start
load_warning_im2:
 exx
 ld a,e
 xor 2
 ld e,a
 bit 1,e
 ld a,$47
 jp z,load_warning_im2_paint
 ld a,$44
load_warning_im2_paint:
 exx
 ld ($59a1),a
 jp load_warning_poll
load_start_safe:
 exx
 res 0,e
 res 1,e
 exx
load_start:
 exx
 ld bc,0
 res 7,e
 exx
 jp load_loadrun
load_running_ready:
 ld a,6
 out ($fe),a
 ; Six nominal seconds in ROM, cancellable after all-key release.
 ld b,15
load_notice_batch:
 ld hl,58800
load_notice_loop:
 dec hl
 ld a,h
 or l
 jp nz,load_notice_loop
 ld a,b
 exx
 ld d,a
 exx
 jp load_notice_poll
load_notice_continue:
 exx
 ld a,d
 exx
 ld b,a
 djnz load_notice_batch
load_batch_start:
 ex af,af'
 ld b,a
 ex af,af'
 ld a,$40
 bit 2,b
 jp z,load_mode_ready
 ld a,$42
load_mode_ready:
 out ($ff),a
 ld a,6
 out ($fe),a
 bit 1,b
 jp z,load_hash_start
 xor a
 ld i,a
 jp load_ram_begin
load_hash_start:
 ex af,af'
 ld b,a
 ex af,af'
 bit 0,b
 jp z,load_stack_start
 ld a,6
 ld i,a
 jp load_ram_begin
load_phase_done:
 ld a,i
 cp 5
 jp z,load_hash_start
 cp 7
 jp z,load_stack_start
 inc a
 ld i,a
 jp load_ram_begin
load_stack_start:
 ex af,af'
 ld b,a
 ex af,af'
 bit 7,b
 jp z,load_idle_start
 ld a,8
 ld i,a
 jp load_stack_begin
load_batch_done:
 exx
 bit 0,e
 exx
 jp z,load_batch_completed
 ld a,i
 exx
 ld d,a
 ld h,4
 res 0,e
 exx
 jp load_work_irq
load_return_qualified:
 exx
 ld h,3
 set 0,e
 exx
 jp load_return_start
load_batch_completed:
 exx
 inc bc
 bit 2,e
 exx
 jp nz,load_exit
 ld a,$40
 out ($ff),a
 jp load_loadrun
load_idle_start:
 ld ix,16
 ld a,9
 ld i,a
load_idle_slice:
 ld a,2
 jp load_work
load_idle_next:
 dec ix
 ld a,ixh
 or ixl
 jp nz,load_idle_slice
 jp load_batch_done

load_work_ram:
 ld a,0
 jp load_work
load_work_stack:
 ld a,1
load_work:
 exx
 ld h,a ; fixed continuation selector, never recovered from RAM
 exx
 ; Poll once per256 compared bytes, before adding the loads.
 jp load_work_poll
load_work_continue:
 ex af,af'
 ld b,a
 ex af,af'
 bit 5,b
 jp z,load_work_busy
 ; Advance deterministic quiet/busy phase in E' bits3-6.
 exx
 ld a,e
 and $78
 add a,8
 and $78
 ld l,a
 ld a,e
 and $87
 or l
 ld e,a
 bit 3,e
 exx
 jp nz,load_work_busy
 ld a,$40
 out ($ff),a
 ld a,1
 out ($fe),a
 ex af,af'
 ld b,a
 ex af,af'
 bit 6,b
 jp z,load_work_spacing
 ld iy,load_work_spacing
 jp mute_ay
load_work_busy:
 ld iy,load_work_mode_ready
 jp load_video_mode
load_work_mode_ready:
 or $40
 out ($ff),a
 ex af,af'
 ld b,a
 ex af,af'
 bit 4,b
 jp z,load_work_ay
 ld a,$d1
 out ($f4),a
 ld hl,$fff0
 ld d,$a2
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_bank_failure
 ld a,0
 ld ($fff0),a
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_bank_failure
 ld a,$51
 out ($f4),a
 ld hl,$dff0
 ld d,$a3
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_bank_failure
 ld a,$19
 out ($f4),a
 ld hl,$7ff0
 ld d,$a6
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_bank_failure
 ld a,$91
 out ($f4),a
 ld hl,$fff0
 ld d,$a2
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_bank_failure
 ld a,$11
 out ($f4),a
load_work_ay:
 ex af,af'
 ld b,a
 ex af,af'
 bit 3,b
 jp nz,load_work_irq
load_work_no_irq_audio:
 bit 6,b
 jp z,load_work_spacing
 bit 5,b
 jp nz,load_ay_unpaced
 ; Pace synthetic Speech2AY traffic with a bounded ROM frame delay
 ; when frame IRQ is disabled (approximately20ms, not a hardware timer).
 ld hl,3000
load_ay_pace:
 dec hl
 ld a,h
 or l
 jp nz,load_ay_pace
load_ay_unpaced:
 ld iy,load_work_spacing
 jp load_ay_frame
load_work_irq:
 ld a,i
 exx
 ld d,a
 bit 0,e
 exx
 jp nz,load_work_no_irq_audio
 ; Basic IRQ inhibit/arrival: no saved-PC read and no arbitrary resumption.
 ld a,$fe
 ld i,a
 im 1
 ld sp,$bfff
 ld iy,load_irq_inhibit_mode
 jp load_video_mode
load_irq_inhibit_mode:
 or $40
 out ($ff),a
 ld d,0
 ld hl,3000
 ei
load_irq_inhibit_loop:
 dec hl
 ld a,h
 or l
 jp nz,load_irq_inhibit_loop
 di
 ld iy,load_irq_enabled_mode
 jp load_video_mode
load_irq_enabled_mode:
 out ($ff),a
 ld d,1
 ld hl,60000
 ei
load_irq_wait:
 dec hl
 ld a,h
 or l
 jp nz,load_irq_wait
 jp load_irq_failure
load_irq_arrived:
 di
 ld sp,$bfff
 ld a,d
 cp 1
 jp nz,load_irq_failure
 exx
 ld a,d
 exx
 ld i,a
 ld iy,load_irq_restore_mode
 jp load_video_mode
load_irq_restore_mode:
 or $40
 out ($ff),a
 ex af,af'
 ld b,a
 ex af,af'
 bit 6,b
 jp z,load_work_spacing
 ld iy,load_work_spacing
 jp load_ay_frame
load_work_spacing:
 ex af,af'
 ld b,a
 ex af,af'
 bit 5,b
 jp z,load_work_resume
 bit 6,b
 jp z,load_power_quiet_wait
 exx
 bit 3,e
 exx
 jp z,load_power_quiet_wait
 ; Busy sound slice: bounded beeper toggles in addition to AY output.
 ld b,64
load_power_beeper:
 ld a,$16
 out ($fe),a
 ld hl,80
load_power_beeper_delay:
 dec hl
 ld a,h
 or l
 jp nz,load_power_beeper_delay
 ld a,6
 out ($fe),a
 djnz load_power_beeper
 jp load_work_resume
load_power_quiet_wait:
 ld hl,3000
load_spacing_loop:
 dec hl
 ld a,h
 or l
 jp nz,load_spacing_loop
load_work_resume:
 exx
 ld a,h
 exx
 cp 4
 jp z,load_return_qualified
 cp 3
 jp z,load_batch_completed
 cp 2
 jp z,load_idle_next
 or a
 jp nz,load_stack_resume
 jp load_ram_resume

; Only documented modes0/2/6. A=mode; fixed IY continuation, DI callers.
load_video_mode:
 ex af,af'
 ld b,a
 ex af,af'
 xor a
 bit 2,b
 jp z,load_video_return
 ld a,2
 bit 5,b
 jp z,load_video_return
 exx
 ld a,e
 exx
 and $30
 cp $10
 ld a,2
 jp z,load_video_return
 ld a,0
 exx
 ld a,e
 exx
 and $30
 cp $20
 ld a,6
 jp z,load_video_return
 xor a
load_video_return:
 jp (iy)

load_notice_poll:
 ld iy,load_notice_continue
 jp load_stop_poll
load_work_poll:
 ld iy,load_work_continue
load_stop_poll:
 ld bc,$00fe
 in a,(c)
 and $1f
 cp $1f
 jp nz,load_stop_pressed
 exx
 set 7,e
 exx
 jp (iy)
load_stop_pressed:
 exx
 bit 7,e
 exx
 jp nz,load_exit
 jp (iy)

; Fixed13 writes, changing synthetic speech-like tone/noise/amplitude frames.
; BC' count chooses a bounded table index; data never selects control flow.
load_ay_frame:
 ex af,af'
 ld b,a
 ex af,af'
 bit 5,b
 exx
 jp nz,load_ay_index_ready
 ; E' bits3-6 are a deterministic16-frame index; profile/arm bits survive.
 ld a,e
 and $78
 add a,8
 and $78
 ld l,a
 ld a,e
 and $87
 or l
 ld e,a
load_ay_index_ready:
 ld a,e
 and $78
 exx
 rrca
 rrca
 rrca
 and 15
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,load_ay_table
 add hl,de
 ld e,0
load_ay_register:
 ld bc,$fff5
 out (c),e
 inc c
 ld a,e
 cp 7
 ld a,(hl)
 jp nz,load_ay_write
 and $3f ; Corrupt table bytes must never turn port A into an output.
load_ay_write:
 ld d,a
 ex af,af'
 ld b,a
 ex af,af'
 bit 5,b
 ld a,d
 jp z,load_ay_value_ready
 ld a,e
 cp 8
 jp c,load_ay_original_value
 cp 11
 jp nc,load_ay_power_shape
 ld a,15
 exx
 bit 4,e
 exx
 jp z,load_ay_value_ready
 ld a,16
 jp load_ay_value_ready
load_ay_power_shape:
 cp 13
 jp nz,load_ay_original_value
 ld a,10
 jp load_ay_value_ready
load_ay_original_value:
 ld a,d
load_ay_value_ready:
 ld d,a
 out (c),a
 in a,(c)
 ; Values are restricted to meaningful register bits by the fixed table.
 ; Mask readback for registers whose unused bits can read as arbitrary data.
 ld b,a
 ld a,e
 cp 1
 jp z,load_ay_mask_nibble
 cp 3
 jp z,load_ay_mask_nibble
 cp 5
 jp z,load_ay_mask_nibble
 cp 13
 jp z,load_ay_mask_nibble
 cp 6
 jp z,load_ay_mask_five
 cp 7
 jp z,load_ay_mask_six
 cp 8
 jp z,load_ay_mask_five
 cp 9
 jp z,load_ay_mask_five
 cp 10
 jp z,load_ay_mask_five
 ld a,b
 jp load_ay_compare
load_ay_mask_nibble:
 ld a,b
 and $0f
 jp load_ay_compare
load_ay_mask_five:
 ld a,b
 and $1f
 jp load_ay_compare
load_ay_mask_six:
 ld a,b
 and $3f
load_ay_compare:
 cp d
 jp nz,load_ay_failure
 inc hl
 inc e
 ld a,e
 cp 13
 jp c,load_ay_register
 jp nz,load_ay_done
 ex af,af'
 ld b,a
 ex af,af'
 bit 5,b
 jp nz,load_ay_register
load_ay_done:
 jp (iy)

; Explicitly exposed advanced profile. Freshly qualify state/stack blocks
; before each bounded foreground slice. The main scheduler is still stackless.
load_return_start:
 di
 ld hl,$5e70
 ld d,$55
 ld a,1
 ld i,a
load_return_qualify:
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld a,d
 cpl
 ld (hl),a
 ld b,(hl)
 ld a,d
 cpl
 cp b
 jp nz,load_return_qualify_fault
 inc hl
 ld a,l
 cp $d1
 jp nz,load_return_qualify
 ld hl,$bfe0
 ld d,$55
load_return_upper_qualify:
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld a,d
 cpl
 ld (hl),a
 ld b,(hl)
 ld a,d
 cpl
 cp b
 jp nz,load_return_qualify_fault
 inc hl
 ld a,h
 cp $c0
 jp nz,load_return_upper_qualify
 exx
 bit 1,e
 exx
 jp z,load_return_im1
 ld hl,$7a00
 ld bc,257
 ld d,$7b
load_im2_table:
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 inc hl
 ; Bound by fixed end, not writable state/table.
 ld a,h
 cp $7b
 jp nz,load_im2_table
 ld a,l
 cp 1
 jp nz,load_im2_table
 ld hl,$7b7b
 ld d,$c3
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 inc hl
 ld d,load_return_handler & 255
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 inc hl
 ld d,load_return_handler >> 8
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld a,$7a
 ld i,a
 im 2
 jp load_return_run
load_return_im1:
 ld a,$fd
 ld i,a
 im 1
load_return_run:
 ld sp,$bfff
 xor a
 ld ($5e72),a
 exx
 ld l,0
 exx
 ld hl,$78df
 ld d,$11
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld hl,$5f00
 ld d,$02
 ld iy,load_return_mode
 jp load_video_mode
load_return_mode:
 out ($ff),a
 ld bc,60000
 ei
load_return_foreground:
 ld (hl),d
 ld a,(hl)
 cp d
 jp nz,load_return_data_fault
 inc d
 dec bc
 ld a,b
 or c
 jp nz,load_return_foreground
 di
 ; Arrival is a register-held marker; RAM frame data cannot fabricate it.
 exx
 ld a,l
 exx
 cp 1
 jp nz,load_irq_failure
 exx
 ld a,d
 exx
 ld i,a
 ld a,$40
 out ($ff),a
 jp load_work_spacing
load_return_data_fault:
 ld b,a
 jp load_ram_fault
load_return_qualify_fault:
 ld a,d
 cpl
 ld d,a
 jp load_ram_fault
load_return_handler:
 push af
load_return_after_af:
 push bc
 push de
 push hl
 ld ($5e70),sp
 ; Compare saved-SP data before choosing a fixed restore, never trust it.
 ld hl,$5e70
 ld d,$f5
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 inc hl
 ld d,$bf
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld sp,$5ed0
 ex af,af'
 ld b,a
 ex af,af'
 bit 6,b
 jp z,load_return_audio_done
 call load_return_audio
load_return_audio_done:
 ex af,af'
 ld b,a
 ex af,af'
 bit 4,b
 jp z,load_return_banks_done
 ld a,$d1
 out ($f4),a
 ld hl,$fff0
 ld d,$a2
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_bank_failure
 ld a,$51
 out ($f4),a
 ld hl,$dff0
 ld d,$a3
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_bank_failure
load_return_banks_done:
 ld hl,$78df
 ld d,$11
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld a,$11
 out ($f4),a
 ld sp,$bff5
 ld hl,$5e72
 ld a,(hl)
 inc a
 ld d,a
 ld (hl),a
 ld b,(hl)
 cp b
 jp nz,load_ram_fault
 exx
 ld l,1
 exx
 pop hl
 pop de
 pop bc
 pop af
 ei
 reti
load_return_audio:
 ld iy,load_return_audio_end
 jp load_ay_frame
load_return_audio_end:
 ret

load_bank_failure:
 ld a,4
 jp load_aux_failure
load_ay_failure:
 ; E=fixed register index, D=expected, A=masked observed.
 ld b,a
 ld h,0
 ld l,e
 ld a,5
 jp load_aux_failure
load_irq_failure:
 ld hl,0
 ld b,0
 ld d,1
 ld a,7
 jp load_aux_failure

load_ay_table:
 INCLUDE "../build/load-ay.asm"
 ASSERT $ <= $8e00
