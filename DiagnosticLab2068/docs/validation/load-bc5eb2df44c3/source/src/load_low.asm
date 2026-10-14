; ROM0 bridges: all HOME RAM visible while comparing. No RAM control state.
; I=phase, IX=next address across a ROM4 load slice. AF'=options.
load_select:
 di
 ld a,$11
 out ($f4),a
 jp $8400
loadcfg_ready:
 ld a,$11
 out ($f4),a
 jp $8406
loadwarning_ready:
 ld a,$11
 out ($f4),a
 jp $8409
loadrun_ready:
 exx
 ld a,b
 exx
 ld de,$48cf
 ld iy,load_run_count_low
 jp hex_byte
load_run_count_low:
 exx
 ld a,c
 exx
 ld de,$48d1
 ld iy,load_run_count_done
 jp hex_byte
load_run_count_done:
 ld a,$11
 out ($f4),a
 jp $840f
loadstop_ready:
 ld a,$40
 ex af,af'
 jp soak_ready
irq_dispatch:
 ; Save options in an alternate scratch byte while AF' holds interrupted AF.
 ; This preserves the foreground's comparison flags in the return profile.
 ex af,af'
 exx
 ld l,a
 exx
 ld a,i
 cp $fd
 jp z,load_return_irq_bridge
 cp $fe
 jp z,load_irq_restore
 exx
 ld a,l
 exx
 ex af,af'
 jp irq_arrived
load_irq_restore:
 exx
 ld a,l
 exx
 ex af,af'
 jp load_irq_bridge
load_return_irq_bridge:
 ex af,af'
 push af ; Only genuine return profile reads this saved AF, never default tests.
 exx
 ld a,l
 exx
 ex af,af'
 jp $841e
load_irq_bridge:
 di
 ld a,$11
 out ($f4),a
 jp $8403

load_ram_begin:
 ld a,1
 out ($f4),a
 ld a,i
 cp 3
 jp z,load_ram_desc_start
 cp 4
 jp z,load_ram_desc_start
 ld hl,$4000
 jp load_ram_loop
load_ram_desc_start:
 ld hl,$ffff
load_ram_loop:
 ; IRQ hardware sink is deferred: never compare a saved-PC byte as RAM data.
 ld a,h
 cp $bf
 jp nz,load_ram_not_sink
 ld a,l
 cp $fd
 jp z,load_ram_advance
 cp $fe
 jp z,load_ram_advance
load_ram_not_sink:
 ld a,i
 cp 6
 jp nc,load_ram_hash
 ld d,0
 cp 2
 jp z,load_ram_expected_ff
 cp 4
 jp nz,load_ram_expected_ready
load_ram_expected_ff:
 ld d,$ff
load_ram_expected_ready:
 ld a,i
 or a
 jp z,load_ram_write_zero
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld a,i
 cp 5
 jp z,load_ram_advance
 ld a,d
 cpl
 ld (hl),a
 jp load_ram_advance
load_ram_write_zero:
 ld (hl),d
 jp load_ram_advance
load_ram_hash:
 ld a,h
 xor l
 xor $5a
 ld d,a
 ld a,i
 cp 6
 jp nz,load_ram_hash_read
 ld (hl),d
 jp load_ram_advance
load_ram_hash_read:
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ; Option6: dense00/FF/55/AA write/read cycles, restore pending hash data.
 ex af,af'
 ld b,a
 ex af,af'
 bit 5,b
 jp z,load_ram_advance
 ld e,d
 ld d,0
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld d,$ff
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld d,$55
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld d,$aa
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld d,e
 ld (hl),d
 jp load_ram_advance
load_ram_advance:
 ld a,i
 cp 3
 jp z,load_ram_desc
 cp 4
 jp z,load_ram_desc
 inc hl
 ld a,h
 or l
 jp z,load_ram_phase_end
 ld a,l
 or a
 jp z,load_ram_slice
 jp load_ram_loop
load_ram_desc:
 dec hl
 ld a,h
 cp $3f
 jp z,load_ram_phase_end
 ld a,l
 cp $ff
 jp z,load_ram_slice
 jp load_ram_loop
load_ram_slice:
 ld a,h
 ld ixh,a
 ld a,l
 ld ixl,a
 ld a,$11
 out ($f4),a
 jp $8412
load_ram_resume:
 di
 ld a,1
 out ($f4),a
 ld a,ixh
 ld h,a
 ld a,ixl
 ld l,a
 jp load_ram_loop
load_ram_phase_end:
 ; Both sink bytes get explicit DI-only00/FF comparisons every phase.
 ld hl,$bffd
 ld d,0
load_sink_test:
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 ld d,$ff
 ld (hl),d
 ld b,(hl)
 ld a,b
 cp d
 jp nz,load_ram_fault
 inc hl
 ld d,0
 ld a,l
 cp $ff
 jp nz,load_sink_test
 ld a,$11
 out ($f4),a
 jp $8415

; Real PUSH/POP used as data only; every HOME byte is compared, never RET.
load_stack_begin:
 di
 ld a,1
 out ($f4),a
 ld hl,$4000
load_stack_pair:
 ld sp,hl
 inc sp
 inc sp
 ld a,h
 xor l
 xor $02
 ld d,a
 cpl
 ld e,a
 push de
load_stack_read:
 pop bc
 ld a,c
 cp e
 jp nz,load_stack_low_fault
 inc hl
 ld a,b
 cp d
 jp nz,load_ram_fault
 inc hl
 ld a,h
 or l
 jp z,load_stack_end
 ld a,l
 or a
 jp nz,load_stack_pair
 ld a,h
 ld ixh,a
 ld a,l
 ld ixl,a
 ld sp,$bfff
 ld a,$11
 out ($f4),a
 jp $8418
load_stack_resume:
 ld a,1
 out ($f4),a
 ld a,ixh
 ld h,a
 ld a,ixl
 ld l,a
 jp load_stack_pair
load_stack_end:
 ld sp,$bfff
 ld a,$11
 out ($f4),a
 jp $841b
load_stack_low_fault:
 ld b,c
 ld d,e
load_ram_fault:
 ; Preserve address/data through bounded mute, then reuse chip/bit report.
 di
 ld sp,$bfff
 ld a,1
 out ($f4),a
 ld a,$40
 out ($ff),a
 exx
 ld hl,0
 ld de,0
 exx
 ld iy,load_fault_mute
 jp compare_observed ; B is the original mismatching read/POP, never reread it.
load_fault_mute:
 ld iy,fault_report
 jp mute_ay
load_aux_failure:
 ; Class in AF', address/index in HL', expected/observed in DE', phase in C'.
 ex af,af'
 ld a,h
 exx
 ld h,a
 exx
 ld a,l
 exx
 ld l,a
 exx
 ld a,d
 exx
 ld d,a
 exx
 ld a,b
 exx
 ld e,a
 exx
 ld a,i
 exx
 ld c,a
 exx
load_failure:
 di
 ld sp,$bfff
 ld a,1
 out ($f4),a
 ld a,$40
 out ($ff),a
 ld iy,load_failure_muted
 jp mute_ay
load_failure_muted:
 jp load_fail
load_exit:
 di
 ld sp,$bfff
 ld a,1
 out ($f4),a
 ld a,$40
 out ($ff),a
 ld iy,load_exit_muted
 jp mute_ay
load_exit_muted:
 jp load_loadstop
