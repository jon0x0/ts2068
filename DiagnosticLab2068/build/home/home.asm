; TS2068 diagnostic v0.2: stackless native LROS kernel.
; HSR=01 during destructive tests; DECR=40; DI except optional IRQ module.
; Default control has no CALL/RET/PUSH/POP/RST/HALT or ROM calls.
; Explicit L data PUSH/POP and confirmed IRQ-return bridges are isolated.
;
; Main HL=target, D=expected, B=observed, E=error scratch.
; I=current phase; IY=fixed ROM comparison continuation; IX=first address.
; Alternate H/L/D=error unions for 4000/8000/C000 regions.
; Alternate E=first failing phase, B=expected, C=observed.
; Alternate AF holds selection (0 all, 1 patterns, 2 march).
 ORG 0
 jp entry
 DS 5-$,255
 ; Bounded training UI in unused header space; vectors remain fixed.
soundguide_ready:
 ld iy,soundguide_poll
 jp key_gate
soundguide_poll:
 ld bc,$7ffe
 in a,(c)
 bit 2,a
 jp z,load_help
 ld bc,$f7fe
 in a,(c)
 ld h,a
 cpl
 and d
 ld d,h
 cpl
 bit 0,a
 jp z,sounddemo_ram
 bit 1,a
 jp z,sounddemo_bank
 bit 2,a
 jp z,sounddemo_cpu
 jp soundguide_poll
 ASSERT $ <= $38
 DS $38-$,255
 jp irq_dispatch
sounddemo_ram:
 ld d,6
 ld e,2
 ld b,180
 ld iy,sounddemo_class
 jp sync_tone
sounddemo_class:
 ld c,2
 ld iy,sounddemo_chip
 jp pulse_group
sounddemo_chip:
 ld c,6
 ld iy,sounddemo_bit
 jp pulse_group
sounddemo_bit:
 ld c,2
 ld iy,soundguide_ready
 jp pulse_group
 ASSERT $ <= $66
 DS $66-$,255
 jp entry
 ; Startup helper occupies spare low-ROM space after the NMI vector.
cartridge_checked:
 xor a
 in a,($fe)
 and $1f
 cp $17
 jp nz,startup_quick
 ld bc,$fdfe
 in a,(c)
 and $1f
 cp $17
 ld a,7
 jp z,startup_extended
 ld bc,$fbfe
 in a,(c)
 and $1f
 cp $17
 jp nz,startup_quick
 xor a
startup_extended:
 ex af,af'
 jp load_startupfull
startup_quick:
 ld a,8
 or a
 ex af,af'
 jp load_startupquick
startupfull_ready:
 ; Highlight the RAM-only or full-suite label before the finite startup notice.
 ex af,af'
 cp 7
 ld hl,$58c1
 jp nz,startup_choice_label
 ld hl,$5901
startup_choice_label:
 ex af,af'
 ld b,30
startup_choice_highlight:
 ld (hl),$46
 inc hl
 djnz startup_choice_highlight
 jp startupquick_ready
startup_helper_end:
sounddemo_bank:
 ld c,4
 ld iy,soundguide_ready
 jp pulse_group
sounddemo_cpu:
 ld c,8
 ld iy,sounddemo_stage
 jp pulse_group
sounddemo_stage:
 ld c,3
 ld iy,soundguide_ready
 jp pulse_group
help_c_poll:
 ld bc,$fefe
 in a,(c)
 bit 3,a
 jp z,load_soundguide
 jp help_poll
 ASSERT startup_helper_end <= $100
 ASSERT $ <= $100
 DS $100-$,255
entry:
 di
 ld a,$40
 out ($ff),a
 ld a,$01
 xor a
 out ($f4),a
 ld a,1
 out ($fe),a
 jp boot_cpu_start
startupquick_ready:
 ld b,3
startup_notice:
 ld hl,60000
startup_notice_loop:
 dec hl
 ld a,h
 or l
 jp nz,startup_notice_loop
 djnz startup_notice
 ex af,af'
 jp selection_store
ram_start:
 di
 ld a,$01
 xor a
 out ($f4),a
 ld ix,0
 exx
 ld hl,0
 ld de,0
 exx
 ex af,af'
 ld b,a
 ex af,af'
 bit 7,b
 jp nz,ram_keep_count
 exx
 ld bc,0
 exx
ram_keep_count:
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 and $7f
 cp 2
 jp z,march_start
 cp 3
 jp z,address_start
 cp 4
 jp z,random_start
 cp 5
 jp z,retention_start
 ld a,1
 ld i,a
 ld d,$00
 ld a,1
 out ($fe),a
 ld hl,$4000
fill_1:
 ld (hl),d
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_1
 ld iy,ram_poll_done_1
 jp ram_key_poll
ram_poll_done_1:
 ld a,h
 or l
 jp nz,fill_1
 ld hl,$4000
read_1:
 ld iy,read_next_1
 jp compare_byte
read_next_1:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_2
 ld iy,ram_poll_done_2
 jp ram_key_poll
ram_poll_done_2:
 ld a,h
 or l
 jp nz,read_1
 ld a,2
 ld i,a
 ld d,$ff
 ld a,1
 out ($fe),a
 ld hl,$4000
fill_2:
 ld (hl),d
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_3
 ld iy,ram_poll_done_3
 jp ram_key_poll
ram_poll_done_3:
 ld a,h
 or l
 jp nz,fill_2
 ld hl,$4000
read_2:
 ld iy,read_next_2
 jp compare_byte
read_next_2:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_4
 ld iy,ram_poll_done_4
 jp ram_key_poll
ram_poll_done_4:
 ld a,h
 or l
 jp nz,read_2
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 cp 8
 jp z,tests_done
 ld a,3
 ld i,a
 ld d,$55
 ld a,1
 out ($fe),a
 ld hl,$4000
fill_3:
 ld (hl),d
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_5
 ld iy,ram_poll_done_5
 jp ram_key_poll
ram_poll_done_5:
 ld a,h
 or l
 jp nz,fill_3
 ld hl,$4000
read_3:
 ld iy,read_next_3
 jp compare_byte
read_next_3:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_6
 ld iy,ram_poll_done_6
 jp ram_key_poll
ram_poll_done_6:
 ld a,h
 or l
 jp nz,read_3
 ld a,4
 ld i,a
 ld d,$aa
 ld a,1
 out ($fe),a
 ld hl,$4000
fill_4:
 ld (hl),d
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_7
 ld iy,ram_poll_done_7
 jp ram_key_poll
ram_poll_done_7:
 ld a,h
 or l
 jp nz,fill_4
 ld hl,$4000
read_4:
 ld iy,read_next_4
 jp compare_byte
read_next_4:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_8
 ld iy,ram_poll_done_8
 jp ram_key_poll
ram_poll_done_8:
 ld a,h
 or l
 jp nz,read_4
 ld a,5
 ld i,a
 ld d,$0f
 ld a,1
 out ($fe),a
 ld hl,$4000
fill_5:
 ld (hl),d
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_9
 ld iy,ram_poll_done_9
 jp ram_key_poll
ram_poll_done_9:
 ld a,h
 or l
 jp nz,fill_5
 ld hl,$4000
read_5:
 ld iy,read_next_5
 jp compare_byte
read_next_5:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_10
 ld iy,ram_poll_done_10
 jp ram_key_poll
ram_poll_done_10:
 ld a,h
 or l
 jp nz,read_5
 ld a,6
 ld i,a
 ld d,$f0
 ld a,1
 out ($fe),a
 ld hl,$4000
fill_6:
 ld (hl),d
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_11
 ld iy,ram_poll_done_11
 jp ram_key_poll
ram_poll_done_11:
 ld a,h
 or l
 jp nz,fill_6
 ld hl,$4000
read_6:
 ld iy,read_next_6
 jp compare_byte
read_next_6:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_12
 ld iy,ram_poll_done_12
 jp ram_key_poll
ram_poll_done_12:
 ld a,h
 or l
 jp nz,read_6
 ld a,7
 ld i,a
 ld d,$33
 ld a,1
 out ($fe),a
 ld hl,$4000
fill_7:
 ld (hl),d
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_13
 ld iy,ram_poll_done_13
 jp ram_key_poll
ram_poll_done_13:
 ld a,h
 or l
 jp nz,fill_7
 ld hl,$4000
read_7:
 ld iy,read_next_7
 jp compare_byte
read_next_7:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_14
 ld iy,ram_poll_done_14
 jp ram_key_poll
ram_poll_done_14:
 ld a,h
 or l
 jp nz,read_7
 ld a,8
 ld i,a
 ld d,$cc
 ld a,1
 out ($fe),a
 ld hl,$4000
fill_8:
 ld (hl),d
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_15
 ld iy,ram_poll_done_15
 jp ram_key_poll
ram_poll_done_15:
 ld a,h
 or l
 jp nz,fill_8
 ld hl,$4000
read_8:
 ld iy,read_next_8
 jp compare_byte
read_next_8:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_16
 ld iy,ram_poll_done_16
 jp ram_key_poll
ram_poll_done_16:
 ld a,h
 or l
 jp nz,read_8
 ld a,9
 ld i,a
 ld d,$01
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_9:
 ld iy,walk_next_9
 ld (hl),d
 jp compare_byte
walk_next_9:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_17
 ld iy,ram_poll_done_17
 jp ram_key_poll
ram_poll_done_17:
 ld a,h
 or l
 jp nz,walk_9
 ld a,10
 ld i,a
 ld d,$fe
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_10:
 ld iy,walk_next_10
 ld (hl),d
 jp compare_byte
walk_next_10:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_18
 ld iy,ram_poll_done_18
 jp ram_key_poll
ram_poll_done_18:
 ld a,h
 or l
 jp nz,walk_10
 ld a,11
 ld i,a
 ld d,$02
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_11:
 ld iy,walk_next_11
 ld (hl),d
 jp compare_byte
walk_next_11:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_19
 ld iy,ram_poll_done_19
 jp ram_key_poll
ram_poll_done_19:
 ld a,h
 or l
 jp nz,walk_11
 ld a,12
 ld i,a
 ld d,$fd
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_12:
 ld iy,walk_next_12
 ld (hl),d
 jp compare_byte
walk_next_12:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_20
 ld iy,ram_poll_done_20
 jp ram_key_poll
ram_poll_done_20:
 ld a,h
 or l
 jp nz,walk_12
 ld a,13
 ld i,a
 ld d,$04
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_13:
 ld iy,walk_next_13
 ld (hl),d
 jp compare_byte
walk_next_13:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_21
 ld iy,ram_poll_done_21
 jp ram_key_poll
ram_poll_done_21:
 ld a,h
 or l
 jp nz,walk_13
 ld a,14
 ld i,a
 ld d,$fb
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_14:
 ld iy,walk_next_14
 ld (hl),d
 jp compare_byte
walk_next_14:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_22
 ld iy,ram_poll_done_22
 jp ram_key_poll
ram_poll_done_22:
 ld a,h
 or l
 jp nz,walk_14
 ld a,15
 ld i,a
 ld d,$08
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_15:
 ld iy,walk_next_15
 ld (hl),d
 jp compare_byte
walk_next_15:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_23
 ld iy,ram_poll_done_23
 jp ram_key_poll
ram_poll_done_23:
 ld a,h
 or l
 jp nz,walk_15
 ld a,16
 ld i,a
 ld d,$f7
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_16:
 ld iy,walk_next_16
 ld (hl),d
 jp compare_byte
walk_next_16:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_24
 ld iy,ram_poll_done_24
 jp ram_key_poll
ram_poll_done_24:
 ld a,h
 or l
 jp nz,walk_16
 ld a,17
 ld i,a
 ld d,$10
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_17:
 ld iy,walk_next_17
 ld (hl),d
 jp compare_byte
walk_next_17:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_25
 ld iy,ram_poll_done_25
 jp ram_key_poll
ram_poll_done_25:
 ld a,h
 or l
 jp nz,walk_17
 ld a,18
 ld i,a
 ld d,$ef
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_18:
 ld iy,walk_next_18
 ld (hl),d
 jp compare_byte
walk_next_18:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_26
 ld iy,ram_poll_done_26
 jp ram_key_poll
ram_poll_done_26:
 ld a,h
 or l
 jp nz,walk_18
 ld a,19
 ld i,a
 ld d,$20
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_19:
 ld iy,walk_next_19
 ld (hl),d
 jp compare_byte
walk_next_19:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_27
 ld iy,ram_poll_done_27
 jp ram_key_poll
ram_poll_done_27:
 ld a,h
 or l
 jp nz,walk_19
 ld a,20
 ld i,a
 ld d,$df
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_20:
 ld iy,walk_next_20
 ld (hl),d
 jp compare_byte
walk_next_20:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_28
 ld iy,ram_poll_done_28
 jp ram_key_poll
ram_poll_done_28:
 ld a,h
 or l
 jp nz,walk_20
 ld a,21
 ld i,a
 ld d,$40
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_21:
 ld iy,walk_next_21
 ld (hl),d
 jp compare_byte
walk_next_21:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_29
 ld iy,ram_poll_done_29
 jp ram_key_poll
ram_poll_done_29:
 ld a,h
 or l
 jp nz,walk_21
 ld a,22
 ld i,a
 ld d,$bf
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_22:
 ld iy,walk_next_22
 ld (hl),d
 jp compare_byte
walk_next_22:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_30
 ld iy,ram_poll_done_30
 jp ram_key_poll
ram_poll_done_30:
 ld a,h
 or l
 jp nz,walk_22
 ld a,23
 ld i,a
 ld d,$80
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_23:
 ld iy,walk_next_23
 ld (hl),d
 jp compare_byte
walk_next_23:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_31
 ld iy,ram_poll_done_31
 jp ram_key_poll
ram_poll_done_31:
 ld a,h
 or l
 jp nz,walk_23
 ld a,24
 ld i,a
 ld d,$7f
 ld a,5
 out ($fe),a
 ld hl,$4000
walk_24:
 ld iy,walk_next_24
 ld (hl),d
 jp compare_byte
walk_next_24:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_32
 ld iy,ram_poll_done_32
 jp ram_key_poll
ram_poll_done_32:
 ld a,h
 or l
 jp nz,walk_24
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 cp 1
 jp z,tests_done
march_start:
 ld a,25
 ld i,a
 ld d,$00
 ld a,6
 out ($fe),a
 ld hl,$4000
march_fill_25:
 ld (hl),d
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_33
 ld iy,ram_poll_done_33
 jp ram_key_poll
ram_poll_done_33:
 ld a,h
 or l
 jp nz,march_fill_25
 ld a,26
 ld i,a
 ld d,$00
 ld a,6
 out ($fe),a
 ld hl,$4000
march_read_26:
 ld iy,march_next_26
 jp compare_byte
march_next_26:
 ld (hl),$ff
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_34
 ld iy,ram_poll_done_34
 jp ram_key_poll
ram_poll_done_34:
 ld a,h
 or l
 jp nz,march_read_26
 ld a,27
 ld i,a
 ld d,$ff
 ld a,6
 out ($fe),a
 ld hl,$4000
march_read_27:
 ld iy,march_next_27
 jp compare_byte
march_next_27:
 ld (hl),$00
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_35
 ld iy,ram_poll_done_35
 jp ram_key_poll
ram_poll_done_35:
 ld a,h
 or l
 jp nz,march_read_27
 ld a,28
 ld i,a
 ld d,$00
 ld a,6
 out ($fe),a
 ld hl,$4000
 ld hl,$ffff
march_read_28:
 ld iy,march_next_28
 jp compare_byte
march_next_28:
 ld (hl),$ff
 dec hl
 ld a,l
 or a
 jp nz,ram_poll_done_36
 ld iy,ram_poll_done_36
 jp ram_key_poll
ram_poll_done_36:
 ld a,h
 cp $3f
 jp nz,march_read_28
 ld a,29
 ld i,a
 ld d,$ff
 ld a,6
 out ($fe),a
 ld hl,$4000
 ld hl,$ffff
march_read_29:
 ld iy,march_next_29
 jp compare_byte
march_next_29:
 ld (hl),$00
 dec hl
 ld a,l
 or a
 jp nz,ram_poll_done_37
 ld iy,ram_poll_done_37
 jp ram_key_poll
ram_poll_done_37:
 ld a,h
 cp $3f
 jp nz,march_read_29
 ld a,30
 ld i,a
 ld d,$00
 ld a,6
 out ($fe),a
 ld hl,$4000
march_read_30:
 ld iy,march_next_30
 jp compare_byte
march_next_30:
 inc hl
 ld a,l
 or a
 jp nz,ram_poll_done_38
 ld iy,ram_poll_done_38
 jp ram_key_poll
ram_poll_done_38:
 ld a,h
 or l
 jp nz,march_read_30
 jp extended_start

tests_done:
 ld a,0
 out ($fe),a
 exx
 ld a,h
 or l
 or d
 exx
 jp nz,fault_report
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 cp 8
 jp z,boot_alias_start
 cp 6
 jp z,irq_start
 cp 7
 jp z,load_bank
 or a
 jp z,load_rampass ; Only completed Complete RAM earns the all-chip result.
 bit 7,b
 jp z,load_pass ; A completed partial RAM selection gets its own result.
 exx
 inc bc
 exx
 jp load_soak
; Always-selected ROM0 boot checks. No stack, HOME code or ROM2 transfer.
; CPU stages precede cartridge integrity; address checks follow successful
; quick00/FF. Fault pulses do not draw or wait for RAM/keyboard/interrupts.
boot_cpu_start:
 ld a,1
 ld i,a
 ld bc,$55aa
 ld de,$aa55
 ld hl,$0ff0
boot_register_check:
 ld a,b
 cp $55
 jp nz,boot_cpu_failed
 ld a,c
 cp $aa
 jp nz,boot_cpu_failed
 ld a,d
 cp $aa
 jp nz,boot_cpu_failed
 ld a,e
 cp $55
 jp nz,boot_cpu_failed
 ld a,h
 cp $0f
 jp nz,boot_cpu_failed
 ld a,l
 cp $f0
 jp nz,boot_cpu_failed
 ld bc,$aa55
 ld a,b
 cp $aa
 jp nz,boot_cpu_failed
 ld a,c
 cp $55
 jp nz,boot_cpu_failed
 ld a,2
 ld i,a
 ld a,$ff
 add a,1
boot_math_check:
 jp nc,boot_cpu_failed
 jp nz,boot_cpu_failed
 ld a,$7f
 add a,1
 jp po,boot_cpu_failed
 jp p,boot_cpu_failed
 cp $80
 jp nz,boot_cpu_failed
 xor a
 sub 1
 jp nc,boot_cpu_failed
 cp $ff
 jp nz,boot_cpu_failed
 ld a,$a5
 and $0f
 cp 5
 jp nz,boot_cpu_failed
 xor $ff
 cp $fa
 jp nz,boot_cpu_failed
 ld a,3
 ld i,a
 ld b,$81
 rlc b
boot_shift_check:
 jp nc,boot_cpu_failed
 ld a,b
 cp 3
 jp nz,boot_cpu_failed
 srl b
 jp nc,boot_cpu_failed
 ld a,b
 cp 1
 jp nz,boot_cpu_failed
 jp cartridge_check

boot_alias_start:
 ld ix,1
 ld a,48
 ld i,a
boot_alias_probe:
 ld hl,$4000
 ld a,ixh
 cp $40
 jp nz,boot_alias_base
 ld h,$80 ; A14 pair uses8000/C000, never HOME ROM0000.
boot_alias_base:
 xor h
 ld d,a
 ld a,ixl
 xor l
 ld e,a
 ld b,2
boot_pair_qualify:
 ld c,$55
 ld (hl),c
 ld a,(hl)
 cp c
 jp nz,boot_data_failed
 ld c,$aa
 ld (hl),c
 ld a,(hl)
 cp c
 jp nz,boot_data_failed
 ex de,hl
 djnz boot_pair_qualify
 ld (hl),$55
 ld a,$aa
 ld (de),a
boot_alias_compare:
 ld a,(hl)
 cp $55
 jp nz,boot_alias_failed
 ld a,(de)
 cp $aa
 jp nz,boot_alias_failed
 ld (hl),$aa
 ld a,$55
 ld (de),a
 ld a,(hl)
 cp $aa
 jp nz,boot_alias_failed
 ld a,(de)
 cp $55
 jp nz,boot_alias_failed
 ld a,i
 inc a
 ld i,a
 cp 64
 jp z,menu_draw
 add ix,ix
 jp boot_alias_probe
boot_data_failed:
 ; Join the normal first-fault/nibble classifier, preserving the actual read.
 ld b,a
 ld d,c
 xor c
 ld e,a
 ld iy,fault_report
 ld a,h
 cp $80
 jp c,error_lower
 cp $c0
 jp c,error_middle
 ld a,e
 exx
 or d
 ld d,a
 exx
 jp first_error
boot_cpu_failed:
 ld a,i
 ld e,a
 ld c,8
 jp boot_fault_group
boot_alias_failed:
 ld a,i
 sub 47
 ld e,a
 ld c,9
boot_fault_group:
 ld a,c
 ld i,a ; Persistent family in I; detail in E, no RAM state.
 ld iy,boot_fault_detail
 jp pulse_group
boot_fault_detail:
 ld c,e
 ld iy,boot_fault_repeat
 jp pulse_group
boot_fault_repeat:
 ld a,i
 ld c,a
 jp boot_fault_group

menu_draw:
 di
 ld a,$40
 out ($ff),a
 ld a,1
 xor a
 out ($f4),a
 ld a,0
 out ($fe),a
 xor a
 ex af,af'
 jp load_menu
menu_ready:
 ld iy,menu_edge_init
 jp key_gate
menu_edge_init:
 ld bc,$bffe
 in a,(c)
 ld ixl,a
 jp menu_poll
menu_poll:
 ld bc,$f7fe
 in a,(c)
 ld h,a
 cpl
 and d
 ld d,h
 cpl
 bit 0,a
 jp z,load_fullinfo
 bit 1,a
 jp z,load_rammenu
 bit 2,a
 jp z,load_videomenu
 bit 3,a
 jp z,load_keyboard
 bit 4,a
 jp z,load_soundmenu
 ld bc,$effe
 in a,(c)
 ld h,a
 cpl
 and e
 ld e,h
 cpl
 bit 4,a
 jp z,load_bank
 bit 3,a
 jp z,select_soak
 bit 2,a
 jp z,load_rommenu
 bit 1,a
 jp z,load_irqmenu
 bit 0,a
 jp z,load_help
 ld bc,$bffe
 in a,(c)
 ld h,a
 cpl
 and ixl
 bit 1,a
 jp nz,load_select
 bit 3,a
 ld a,h
 ld ixl,a
 jp nz,load_inputs
 jp menu_poll
select_full:
 ld a,7
 jp selection_store
select_all:
 xor a
 jp selection_store
select_patterns:
 ld a,1
 jp selection_store
select_march:
 ld a,2
 jp selection_store
select_address:
 ld a,3
 jp selection_store
select_random:
 ld a,4
 jp selection_store
select_retention:
 ld a,5
 jp selection_store
select_soak:
 exx
 ld bc,0
 exx
 ld a,$80
selection_store:
 or a
 ex af,af'
 xor a
 in a,($fe)
 and $1f
 cp $1f
 jp nz,ram_start
 ex af,af'
 scf
 ex af,af'
 jp ram_start
ram_cancel:
 exx
 ld a,h
 or l
 or d
 exx
 jp nz,fault_report
 ex af,af'
 ld b,a
 ex af,af'
 bit 7,b
 jp z,menu_draw
 ex af,af'
 ld a,$40
 ex af,af'
 jp load_soakstop
; Comparison never returns through RAM. All caller continuations are ROM labels.
compare_byte:
 ld b,(hl)
compare_observed:
 ld a,b
 cp d
 jp z,compare_exit
 ld a,b
 xor d
 ld e,a
 ld a,h
 cp $80
 jp c,error_lower
 cp $c0
 jp c,error_middle
 ld a,e
 exx
 or d
 ld d,a
 exx
 jp first_error
error_lower:
 ld a,e
 exx
 or h
 ld h,a
 exx
 jp first_error
error_middle:
 ld a,e
 exx
 or l
 ld l,a
 exx
first_error:
 exx
 ld a,e
 exx
 or a
 jp nz,compare_exit
 ld a,i
 exx
 ld e,a
 exx
 ld a,d
 exx
 ld b,a
 exx
 ld a,b
 exx
 ld c,a
 exx
 ld b,h
 ld c,l
 ld ix,0
 add ix,bc
compare_exit:
 jp (iy)

fault_report:
 ; All unions and first-fault fields remain in CPU registers.
report_u6:
 exx
 ld a,h
 exx
 and $0f
 ld d,1
 jp nz,report_detail
report_u7:
 exx
 ld a,h
 exx
 rrca
 rrca
 rrca
 rrca
 and $0f
 ld d,2
 jp nz,report_detail
report_u12:
 exx
 ld a,l
 exx
 and $0f
 ld d,3
 jp nz,report_detail
report_u13:
 exx
 ld a,l
 exx
 rrca
 rrca
 rrca
 rrca
 and $0f
 ld d,4
 jp nz,report_detail
report_u17:
 exx
 ld a,d
 exx
 and $0f
 ld d,5
 jp nz,report_detail
report_u18:
 exx
 ld a,d
 exx
 rrca
 rrca
 rrca
 rrca
 and $0f
 ld d,6
 jp nz,report_detail
report_restart_poll:
 ld bc,$fbfe
 in a,(c)
 bit 3,a             ; R restarts all tests, without a RAM return path.
 jp nz,report_stop_poll
 ex af,af'
 jp nc,report_retry_held
 ex af,af'
 jp select_all
report_retry_held:
 ex af,af'
report_stop_poll:
 ld iy,report_u6
 jp ram_key_poll
report_detail:
 ld e,1
 cp 1
 jp z,report_sync
 inc e
 cp 2
 jp z,report_sync
 inc e
 cp 4
 jp z,report_sync
 inc e
 cp 8
 jp z,report_sync
 inc e
report_sync:
 jp fault_draw
fault_draw_done:
 ; Long white tone then three pulse groups: class 2, chip index, nibble bit.
 ld b,180
 ld iy,report_class
sync_tone:
 ld a,$17
 out ($fe),a
 ld hl,480
sync_high:
 dec hl
 ld a,h
 or l
 jp nz,sync_high
 ld a,7
 out ($fe),a
 ld hl,480
sync_low:
 dec hl
 ld a,h
 or l
 jp nz,sync_low
 djnz sync_tone
 xor a
 out ($fe),a
 ld b,2
sync_gap_pass:
 ld hl,65535
sync_gap:
 dec hl
 ld a,h
 or l
 jp nz,sync_gap
 djnz sync_gap_pass
 jp (iy)
report_class:
 ld c,2
 ld iy,report_item
 jp pulse_group
report_item:
 ld c,d
 ld iy,report_bit
 jp pulse_group
report_bit:
 ld c,e
 ld iy,report_next
 jp pulse_group
report_next:
 ld a,d
 cp 1
 jp z,report_u7
 cp 2
 jp z,report_u12
 cp 3
 jp z,report_u13
 cp 4
 jp z,report_u17
 cp 5
 jp z,report_u18
 jp report_restart_poll

; Count C, continuation IY; preserve D/E/IX and alternate result registers.
; Nominal beeps/delays use CPU instruction timing, independent of interrupts.
pulse_group:
 ld b,255
pulse_tone:
 ld a,$17
 out ($fe),a
 ld hl,170
pulse_high:
 dec hl
 ld a,h
 or l
 jp nz,pulse_high
 ld a,7
 out ($fe),a
 ld hl,170
pulse_low:
 dec hl
 ld a,h
 or l
 jp nz,pulse_low
 djnz pulse_tone
 xor a
 out ($fe),a
 ld hl,60000 ; approximately0.4 seconds between counting tones.
pulse_gap:
 dec hl
 ld a,h
 or l
 jp nz,pulse_gap
 dec c
 jp nz,pulse_group
 ld b,2
group_gap_pass:
 ld hl,65535
group_gap:
 dec hl
 ld a,h
 or l
 jp nz,group_gap
 djnz group_gap_pass ; plus pulse_gap: approximately1.3 seconds between groups.
 jp (iy)
; Stackless suite modules. Alternate result registers stay untouched in loaders.
; BC=remaining output, HL=ROM source, DE=HOME destination; I=source-bank end.
; IXH=packet count, IXL=repeat value; IY=fixed ROM continuation.
unpack:
 ld a,b
 or c
 jp z,unpack_done
 ld a,i
 cp h
 jp z,asset_error
 ld a,(hl)
 inc hl
 ld ixh,a
 and $7f
 inc a
 ld ixh,a
 dec hl
 ld a,(hl)
 inc hl
 bit 7,a
 jp z,unpack_literal
 ld a,i
 cp h
 jp z,asset_error
 ld a,(hl)
 inc hl
 ld ixl,a
unpack_run:
 ld a,ixl
 ld (de),a
 inc de
 dec bc
 ld a,b
 or c
 jp z,unpack_done
 dec ixh
 jp nz,unpack_run
 jp unpack
unpack_literal:
 ld a,i
 cp h
 jp z,asset_error
 ld a,(hl)
 inc hl
 ld (de),a
 inc de
 dec bc
 ld a,b
 or c
 jp z,unpack_done
 dec ixh
 jp nz,unpack_literal
 jp unpack
unpack_done:
 ld a,1
 xor a
 out ($f4),a
 jp (iy)
asset_error:
 ld a,$40
 out ($ff),a
 ld a,1
 xor a
 out ($f4),a
 ld a,$12
 out ($fe),a
 jp cartridge_alarm
asset_error_poll:
 ld bc,$7ffe
 in a,(c)
 bit 2,a
 jp z,menu_draw
 jp asset_error_poll

; All guided menus poll M; waiting for input is intentional, never a release wait.
fullinfo_ready:
 ld iy,fullinfo_poll
 jp key_gate
fullinfo_poll:
 ld bc,$7ffe
 in a,(c)
 bit 2,a
 jp z,menu_draw
 ld bc,$f7fe
 in a,(c)
 ld h,a
 cpl
 and d
 ld d,h
 cpl
 bit 0,a
 jp z,select_full
 jp fullinfo_poll
fullsummary_ready:
 ; Quarantine the still-held keyboard exit chord; accept a new key edge.
 ld bc,$00fe
 in a,(c)
 and $1f
 ld d,a
fullsummary_poll:
 ld bc,$00fe
 in a,(c)
 and $1f
 ld h,a
 cpl
 and d
 ld d,h
 or a
 jp nz,menu_draw
 jp fullsummary_poll
rammenu_ready:
 ld iy,rammenu_poll
 jp key_gate
rammenu_poll:
 ld bc,$7ffe
 in a,(c)
 bit 2,a
 jp z,menu_draw
 ld bc,$f7fe
 in a,(c)
 ld h,a
 cpl
 and d
 ld d,h
 cpl
 bit 0,a
 jp z,select_all
 bit 1,a
 jp z,select_patterns
 bit 2,a
 jp z,select_march
 bit 3,a
 jp z,select_address
 bit 4,a
 jp z,select_random
 ld bc,$effe
 in a,(c)
 ld h,a
 cpl
 and e
 ld e,h
 cpl
 bit 4,a
 jp z,select_retention
 jp rammenu_poll
videomenu_ready:
 ld iy,videomenu_poll
 jp key_gate
videomenu_poll:
 ld bc,$7ffe
 in a,(c)
 bit 2,a
 jp z,menu_draw
 ld bc,$f7fe
 in a,(c)
 ld h,a
 cpl
 and d
 ld d,h
 cpl
 bit 0,a
 jp z,load_bars
 bit 1,a
 jp z,load_standard
 bit 2,a
 jp z,load_secondary
 bit 3,a
 jp z,load_ecm
 bit 4,a
 jp z,load_hires
 ld bc,$effe
 in a,(c)
 ld h,a
 cpl
 and e
 ld e,h
 cpl
 bit 4,a
 jp z,load_mix128
 jp videomenu_poll
video_bars_ready:
 ld e,1
 ld a,$40
 jp video_mode
video_standard_ready:
 ld e,2
 ld a,$40
 jp video_mode
video_mix128_ready:
 ld e,6
 ld a,$40
 jp video_mode
video_secondary_ready:
 ld e,3
 ld a,$41
 jp video_mode
video_ecm_ready:
 ld e,4
 ld a,$42
 jp video_mode
video_hires_ready:
 ld e,5
 ld a,$46
video_mode:
 out ($ff),a
 ld d,180
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 cp 7
 jp nz,video_budget
 ld d,8
video_budget:
 ld ix,$ffff
video_wait:
 ld iy,video_stop_continue
 jp menu_stop_poll
video_stop_continue:
 dec ix
 ld a,ixh
 or ixl
 jp nz,video_wait
 dec d
 jp nz,video_budget
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 cp 7
 jp nz,menu_draw
 ld a,e
 cp 1
 jp z,load_standard
 cp 2
 jp z,load_secondary
 cp 3
 jp z,load_ecm
 cp 4
 jp z,load_hires
 cp 5
 jp z,load_mix128
 jp load_keyboard
soundmenu_ready:
 ld iy,soundmenu_poll
 jp key_gate
soundmenu_poll:
 ld bc,$7ffe
 in a,(c)
 bit 2,a
 jp z,menu_draw
 ld bc,$f7fe
 in a,(c)
 ld h,a
 cpl
 and d
 ld d,h
 cpl
 bit 0,a
 jp z,load_beeper
 bit 1,a
 jp z,ay_test
 jp soundmenu_poll
fail_ready:
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 ld de,$48c9
 ld iy,fail_address_high
 jp hex_byte
fail_address_high:
 exx
 ld a,h
 exx
 ld de,$48e9
 ld iy,fail_address_low
 jp hex_byte
fail_address_low:
 exx
 ld a,l
 exx
 ld de,$48eb
 ld iy,fail_extra
 jp hex_byte
fail_extra:
 exx
 ld a,c
 exx
 ld de,$5031
 ld iy,aux_fault_start
 jp hex_byte
result_failure:
 ex af,af'
 jp load_fail
rampass_ready:
 jp fullsummary_ready ; Reuse held-key quarantine and new-key result dismissal.
pass_ready EQU fullsummary_ready
result_wait:
 xor a
 in a,($fe)
 and $1f
 cp $1f
 jp nz,audio_exit
 jp result_wait
help_ready:
 ld iy,help_edge_init
 jp key_gate
help_poll:
 ld bc,$7ffe
 in a,(c)
 bit 2,a
 jp z,menu_draw
 ld bc,$dffe
 in a,(c)
 ld h,a
 cpl
 and d
 ld d,h
 cpl
 bit 0,a
 jp z,load_inputs
 jp help_c_poll

; Added RAM algorithms retain the same compare_byte result contract.
extended_start:
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 and $7f
 cp 7
 jp z,address_start
 or a
 jp nz,tests_done
address_start:
 ld a,3
 out ($fe),a
 ld a,31
 ld i,a
 ld hl,$4000
address_fill:
 ld a,h
 xor l
 rlca
 add a,h
 xor $5a
 ld (hl),a
 inc hl
 ld a,h
 or l
 jp nz,address_fill
 ld hl,$4000
address_read:
 ld iy,address_next
 ld a,h
 xor l
 rlca
 add a,h
 xor $5a
 ld d,a
 jp compare_byte
address_next:
 inc hl
 ld a,l
 or a
 jp nz,address_poll_done
 ld iy,address_poll_done
 jp ram_key_poll
address_poll_done:
 ld a,h
 or l
 jp nz,address_read
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 and $7f
 jp address_lanes_start
random_start:
 ld a,4
 out ($fe),a
 ld a,32
 ld i,a
 ld hl,$4000
 ld de,$ace1
random_fill:
 ld (hl),d
 srl d
 rr e
 jp nc,random_fill_noxor
 ld a,d
 xor $b4
 ld d,a
random_fill_noxor:
 inc hl
 ld a,h
 or l
 jp nz,random_fill
 ld hl,$4000
 ld de,$ace1
random_read:
 ld iy,random_next
 jp compare_byte
random_next:
 ld a,b
 cp d
 jp nz,fault_report
 srl d
 rr e
 jp nc,random_read_noxor
 ld a,d
 xor $b4
 ld d,a
random_read_noxor:
 inc hl
 ld a,l
 or a
 jp nz,random_poll_done
 ld iy,random_poll_done
 jp ram_key_poll
random_poll_done:
 ld a,h
 or l
 jp nz,random_read
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 and $7f
 cp 4
 jp z,tests_done
retention_start:
 ld a,2
 out ($fe),a
 ld a,33
 ld i,a
 ld d,$55
retention_fill_start:
 ld hl,$4000
retention_fill:
 ld (hl),d
 inc hl
 ld a,h
 or l
 jp nz,retention_fill
 ; Instruction-timed hold; refresh remains active. Poll stop during the hold.
 ld bc,500
retention_hold:
 ld hl,3000
retention_delay:
 dec hl
 ld a,h
 or l
 jp nz,retention_delay
 dec bc
 ld a,b
 or c
 jp z,retention_read_start
 ld iy,retention_hold
 jp ram_key_poll
retention_read_start:
 ld hl,$4000
retention_read:
 ld iy,retention_next
 jp compare_byte
retention_next:
 inc hl
 ld a,l
 or a
 jp nz,retention_poll_done
 ld iy,retention_poll_done
 jp ram_key_poll
retention_poll_done:
 ld a,h
 or l
 jp nz,retention_read
 ld a,d
 cp $aa
 jp z,tests_done
 ld d,$aa
 ld a,34
 ld i,a
 jp retention_fill_start

soakstop_ready EQU soak_ready
soak_ready:
 ; Loader clobbers only main registers. Alternate BC is a 16-bit pass count.
 exx
 ld a,b
 exx
 ld de,$48cf
 ld iy,soak_count_low
 jp hex_byte
soak_count_low:
 exx
 ld a,c
 exx
 ld de,$48d1
 ld iy,soak_count_done
 jp hex_byte
soak_count_done:
 ex af,af'
 ld b,a
 ex af,af'
 bit 7,b
 jp z,fullsummary_ready
 jp soak_pause
soak_pause:
 ; Four register-only batches: 197832 * 107T ~= 6s at 3.528MHz.
 ; Released-key poll path is timed; a new key still cancels immediately.
 ld b,4
soak_pause_batch:
 ld hl,49458
soak_pause_loop:
 ld iy,soak_pause_continue
 jp ram_key_poll
soak_pause_continue:
 dec hl
 ld a,h
 or l
 jp nz,soak_pause_loop
 djnz soak_pause_batch
 jp ram_start

; One byte -> two hexadecimal glyphs, DE=bitmap row0 position.
; Immutable font index, fixed IY continuation. All input byte values are bounded.
hex_byte:
 ld c,a
 ld a,$03
 xor a
 out ($f4),a
 ld a,c
 rrca
 rrca
 rrca
 rrca
 and 15
 ld ixh,2
hex_digit:
 add a,48
 cp 58
 jp c,hex_ascii
 add a,7
hex_ascii:
 sub 32
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 add hl,hl
 ld b,0
 ld a,c
 ld c,0
 ld bc,font_data
 add hl,bc
 ld c,a
 ld b,8
hex_rows:
 ld a,(hl)
 ld (de),a
 inc hl
 inc d
 djnz hex_rows
 ld a,d
 sub 8
 ld d,a
 inc e
 dec ixh
 jp z,hex_done
 ld a,c
 and 15
 jp hex_digit
hex_done:
 ld a,1
 xor a
 out ($f4),a
 jp (iy)

; Reporter display never uses decoder registers, and preserves D/E/IX/results.
fault_draw:
 jp fault_draw_done ; HOME minimal fault output is border/beeper only.
keyboard_ready:
 ld hl,$5b00
 ld b,41 ; 40 electrical contacts plus the derived BREAK history.
 xor a
keyboard_clear:
 ld (hl),a
 inc hl
 djnz keyboard_clear
 ld ix,$ffff
 ld d,64
keyboard_scan:
 ld bc,$fefe
 in a,(c)
 ld e,a
 ld hl,$5b00
 bit 0,e
 jr nz,key_up_0
 ld (hl),1
 ld a,$60
 jr key_color_0
key_up_0:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_0
 ld a,$68
key_color_0:
 ld hl,$59c0
 ld b,3
 ld iy,key_painted_0_0
 jp keyboard_paint
key_painted_0_0:
 ld a,c
 ld hl,$59dd
 ld b,3
 ld iy,key_painted_0_1
 jp keyboard_paint
key_painted_0_1:
 ld hl,$5b01
 bit 1,e
 jr nz,key_up_1
 ld (hl),1
 ld a,$60
 jr key_color_1
key_up_1:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_1
 ld a,$68
key_color_1:
 ld hl,$59c3
 ld b,2
 ld iy,key_painted_1_0
 jp keyboard_paint
key_painted_1_0:
 ld hl,$5b02
 bit 2,e
 jr nz,key_up_2
 ld (hl),1
 ld a,$60
 jr key_color_2
key_up_2:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_2
 ld a,$68
key_color_2:
 ld hl,$59c6
 ld b,2
 ld iy,key_painted_2_0
 jp keyboard_paint
key_painted_2_0:
 ld hl,$5b03
 bit 3,e
 jr nz,key_up_3
 ld (hl),1
 ld a,$60
 jr key_color_3
key_up_3:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_3
 ld a,$68
key_color_3:
 ld hl,$59c9
 ld b,2
 ld iy,key_painted_3_0
 jp keyboard_paint
key_painted_3_0:
 ld hl,$5b04
 bit 4,e
 jr nz,key_up_4
 ld (hl),1
 ld a,$60
 jr key_color_4
key_up_4:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_4
 ld a,$68
key_color_4:
 ld hl,$59cc
 ld b,2
 ld iy,key_painted_4_0
 jp keyboard_paint
key_painted_4_0:
 ld bc,$fdfe
 in a,(c)
 ld e,a
 ld hl,$5b05
 bit 0,e
 jr nz,key_up_5
 ld (hl),1
 ld a,$60
 jr key_color_5
key_up_5:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_5
 ld a,$68
key_color_5:
 ld hl,$5962
 ld b,2
 ld iy,key_painted_5_0
 jp keyboard_paint
key_painted_5_0:
 ld hl,$5b06
 bit 1,e
 jr nz,key_up_6
 ld (hl),1
 ld a,$60
 jr key_color_6
key_up_6:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_6
 ld a,$68
key_color_6:
 ld hl,$5965
 ld b,2
 ld iy,key_painted_6_0
 jp keyboard_paint
key_painted_6_0:
 ld hl,$5b07
 bit 2,e
 jr nz,key_up_7
 ld (hl),1
 ld a,$60
 jr key_color_7
key_up_7:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_7
 ld a,$68
key_color_7:
 ld hl,$5968
 ld b,2
 ld iy,key_painted_7_0
 jp keyboard_paint
key_painted_7_0:
 ld hl,$5b08
 bit 3,e
 jr nz,key_up_8
 ld (hl),1
 ld a,$60
 jr key_color_8
key_up_8:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_8
 ld a,$68
key_color_8:
 ld hl,$596b
 ld b,2
 ld iy,key_painted_8_0
 jp keyboard_paint
key_painted_8_0:
 ld hl,$5b09
 bit 4,e
 jr nz,key_up_9
 ld (hl),1
 ld a,$60
 jr key_color_9
key_up_9:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_9
 ld a,$68
key_color_9:
 ld hl,$596e
 ld b,2
 ld iy,key_painted_9_0
 jp keyboard_paint
key_painted_9_0:
 ld bc,$fbfe
 in a,(c)
 ld e,a
 ld hl,$5b0a
 bit 0,e
 jr nz,key_up_10
 ld (hl),1
 ld a,$60
 jr key_color_10
key_up_10:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_10
 ld a,$68
key_color_10:
 ld hl,$5901
 ld b,2
 ld iy,key_painted_10_0
 jp keyboard_paint
key_painted_10_0:
 ld hl,$5b0b
 bit 1,e
 jr nz,key_up_11
 ld (hl),1
 ld a,$60
 jr key_color_11
key_up_11:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_11
 ld a,$68
key_color_11:
 ld hl,$5904
 ld b,2
 ld iy,key_painted_11_0
 jp keyboard_paint
key_painted_11_0:
 ld hl,$5b0c
 bit 2,e
 jr nz,key_up_12
 ld (hl),1
 ld a,$60
 jr key_color_12
key_up_12:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_12
 ld a,$68
key_color_12:
 ld hl,$5907
 ld b,2
 ld iy,key_painted_12_0
 jp keyboard_paint
key_painted_12_0:
 ld hl,$5b0d
 bit 3,e
 jr nz,key_up_13
 ld (hl),1
 ld a,$60
 jr key_color_13
key_up_13:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_13
 ld a,$68
key_color_13:
 ld hl,$590a
 ld b,2
 ld iy,key_painted_13_0
 jp keyboard_paint
key_painted_13_0:
 ld hl,$5b0e
 bit 4,e
 jr nz,key_up_14
 ld (hl),1
 ld a,$60
 jr key_color_14
key_up_14:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_14
 ld a,$68
key_color_14:
 ld hl,$590d
 ld b,2
 ld iy,key_painted_14_0
 jp keyboard_paint
key_painted_14_0:
 ld bc,$f7fe
 in a,(c)
 ld e,a
 ld hl,$5b0f
 bit 0,e
 jr nz,key_up_15
 ld (hl),1
 ld a,$60
 jr key_color_15
key_up_15:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_15
 ld a,$68
key_color_15:
 ld hl,$58a0
 ld b,2
 ld iy,key_painted_15_0
 jp keyboard_paint
key_painted_15_0:
 ld hl,$5b10
 bit 1,e
 jr nz,key_up_16
 ld (hl),1
 ld a,$60
 jr key_color_16
key_up_16:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_16
 ld a,$68
key_color_16:
 ld hl,$58a3
 ld b,2
 ld iy,key_painted_16_0
 jp keyboard_paint
key_painted_16_0:
 ld hl,$5b11
 bit 2,e
 jr nz,key_up_17
 ld (hl),1
 ld a,$60
 jr key_color_17
key_up_17:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_17
 ld a,$68
key_color_17:
 ld hl,$58a6
 ld b,2
 ld iy,key_painted_17_0
 jp keyboard_paint
key_painted_17_0:
 ld hl,$5b12
 bit 3,e
 jr nz,key_up_18
 ld (hl),1
 ld a,$60
 jr key_color_18
key_up_18:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_18
 ld a,$68
key_color_18:
 ld hl,$58a9
 ld b,2
 ld iy,key_painted_18_0
 jp keyboard_paint
key_painted_18_0:
 ld hl,$5b13
 bit 4,e
 jr nz,key_up_19
 ld (hl),1
 ld a,$60
 jr key_color_19
key_up_19:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_19
 ld a,$68
key_color_19:
 ld hl,$58ac
 ld b,2
 ld iy,key_painted_19_0
 jp keyboard_paint
key_painted_19_0:
 ld bc,$effe
 in a,(c)
 ld e,a
 ld hl,$5b14
 bit 0,e
 jr nz,key_up_20
 ld (hl),1
 ld a,$60
 jr key_color_20
key_up_20:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_20
 ld a,$68
key_color_20:
 ld hl,$58bb
 ld b,2
 ld iy,key_painted_20_0
 jp keyboard_paint
key_painted_20_0:
 ld hl,$5b15
 bit 1,e
 jr nz,key_up_21
 ld (hl),1
 ld a,$60
 jr key_color_21
key_up_21:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_21
 ld a,$68
key_color_21:
 ld hl,$58b8
 ld b,2
 ld iy,key_painted_21_0
 jp keyboard_paint
key_painted_21_0:
 ld hl,$5b16
 bit 2,e
 jr nz,key_up_22
 ld (hl),1
 ld a,$60
 jr key_color_22
key_up_22:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_22
 ld a,$68
key_color_22:
 ld hl,$58b5
 ld b,2
 ld iy,key_painted_22_0
 jp keyboard_paint
key_painted_22_0:
 ld hl,$5b17
 bit 3,e
 jr nz,key_up_23
 ld (hl),1
 ld a,$60
 jr key_color_23
key_up_23:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_23
 ld a,$68
key_color_23:
 ld hl,$58b2
 ld b,2
 ld iy,key_painted_23_0
 jp keyboard_paint
key_painted_23_0:
 ld hl,$5b18
 bit 4,e
 jr nz,key_up_24
 ld (hl),1
 ld a,$60
 jr key_color_24
key_up_24:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_24
 ld a,$68
key_color_24:
 ld hl,$58af
 ld b,2
 ld iy,key_painted_24_0
 jp keyboard_paint
key_painted_24_0:
 ld bc,$dffe
 in a,(c)
 ld e,a
 ld hl,$5b19
 bit 0,e
 jr nz,key_up_25
 ld (hl),1
 ld a,$60
 jr key_color_25
key_up_25:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_25
 ld a,$68
key_color_25:
 ld hl,$591c
 ld b,2
 ld iy,key_painted_25_0
 jp keyboard_paint
key_painted_25_0:
 ld hl,$5b1a
 bit 1,e
 jr nz,key_up_26
 ld (hl),1
 ld a,$60
 jr key_color_26
key_up_26:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_26
 ld a,$68
key_color_26:
 ld hl,$5919
 ld b,2
 ld iy,key_painted_26_0
 jp keyboard_paint
key_painted_26_0:
 ld hl,$5b1b
 bit 2,e
 jr nz,key_up_27
 ld (hl),1
 ld a,$60
 jr key_color_27
key_up_27:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_27
 ld a,$68
key_color_27:
 ld hl,$5916
 ld b,2
 ld iy,key_painted_27_0
 jp keyboard_paint
key_painted_27_0:
 ld hl,$5b1c
 bit 3,e
 jr nz,key_up_28
 ld (hl),1
 ld a,$60
 jr key_color_28
key_up_28:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_28
 ld a,$68
key_color_28:
 ld hl,$5913
 ld b,2
 ld iy,key_painted_28_0
 jp keyboard_paint
key_painted_28_0:
 ld hl,$5b1d
 bit 4,e
 jr nz,key_up_29
 ld (hl),1
 ld a,$60
 jr key_color_29
key_up_29:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_29
 ld a,$68
key_color_29:
 ld hl,$5910
 ld b,2
 ld iy,key_painted_29_0
 jp keyboard_paint
key_painted_29_0:
 ld bc,$bffe
 in a,(c)
 ld e,a
 ld hl,$5b1e
 bit 0,e
 jr nz,key_up_30
 ld (hl),1
 ld a,$60
 jr key_color_30
key_up_30:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_30
 ld a,$68
key_color_30:
 ld hl,$597d
 ld b,3
 ld iy,key_painted_30_0
 jp keyboard_paint
key_painted_30_0:
 ld hl,$5b1f
 bit 1,e
 jr nz,key_up_31
 ld (hl),1
 ld a,$60
 jr key_color_31
key_up_31:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_31
 ld a,$68
key_color_31:
 ld hl,$597a
 ld b,2
 ld iy,key_painted_31_0
 jp keyboard_paint
key_painted_31_0:
 ld hl,$5b20
 bit 2,e
 jr nz,key_up_32
 ld (hl),1
 ld a,$60
 jr key_color_32
key_up_32:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_32
 ld a,$68
key_color_32:
 ld hl,$5977
 ld b,2
 ld iy,key_painted_32_0
 jp keyboard_paint
key_painted_32_0:
 ld hl,$5b21
 bit 3,e
 jr nz,key_up_33
 ld (hl),1
 ld a,$60
 jr key_color_33
key_up_33:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_33
 ld a,$68
key_color_33:
 ld hl,$5974
 ld b,2
 ld iy,key_painted_33_0
 jp keyboard_paint
key_painted_33_0:
 ld hl,$5b22
 bit 4,e
 jr nz,key_up_34
 ld (hl),1
 ld a,$60
 jr key_color_34
key_up_34:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_34
 ld a,$68
key_color_34:
 ld hl,$5971
 ld b,2
 ld iy,key_painted_34_0
 jp keyboard_paint
key_painted_34_0:
 ld bc,$7ffe
 in a,(c)
 ld e,a
 ld hl,$5b23
 bit 0,e
 jr nz,key_up_35
 ld (hl),1
 ld a,$60
 jr key_color_35
key_up_35:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_35
 ld a,$68
key_color_35:
 ld hl,$5a27
 ld b,18
 ld iy,key_painted_35_0
 jp keyboard_paint
key_painted_35_0:
 ld hl,$5b24
 bit 1,e
 jr nz,key_up_36
 ld (hl),1
 ld a,$60
 jr key_color_36
key_up_36:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_36
 ld a,$68
key_color_36:
 ld hl,$59d8
 ld b,3
 ld iy,key_painted_36_0
 jp keyboard_paint
key_painted_36_0:
 ld hl,$5b25
 bit 2,e
 jr nz,key_up_37
 ld (hl),1
 ld a,$60
 jr key_color_37
key_up_37:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_37
 ld a,$68
key_color_37:
 ld hl,$59d5
 ld b,2
 ld iy,key_painted_37_0
 jp keyboard_paint
key_painted_37_0:
 ld hl,$5b26
 bit 3,e
 jr nz,key_up_38
 ld (hl),1
 ld a,$60
 jr key_color_38
key_up_38:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_38
 ld a,$68
key_color_38:
 ld hl,$59d2
 ld b,2
 ld iy,key_painted_38_0
 jp keyboard_paint
key_painted_38_0:
 ld hl,$5b27
 bit 4,e
 jr nz,key_up_39
 ld (hl),1
 ld a,$60
 jr key_color_39
key_up_39:
 bit 0,(hl)
 ld a,$78
 jr z,key_color_39
 ld a,$68
key_color_39:
 ld hl,$59cf
 ld b,2
 ld iy,key_painted_39_0
 jp keyboard_paint
key_painted_39_0:
 ld bc,$fefe
 in a,(c)
 bit 0,a
 jr nz,break_up
 ld bc,$7ffe
 in a,(c)
 bit 0,a
 jr nz,break_up
 ld hl,$5b28
 ld (hl),1
 ld a,$60
 jr break_color
break_up:
 ld hl,$5b28
 bit 0,(hl)
 ld a,$78
 jr z,break_color
 ld a,$68
break_color:
 ld hl,$59db
 ld b,2
 ld iy,keyboard_break_done
 jp keyboard_paint
keyboard_break_done:

 ; Both physical CAPS highlighted; BREAK follows CAPS+SPACE.
 ld bc,$fefe
 in a,(c)
 bit 0,a
 jp z,keyboard_exit_space
 ld bc,$bffe
 in a,(c)
 bit 0,a
 jp nz,keyboard_release
keyboard_exit_space:
 ld bc,$7ffe
 in a,(c)
 bit 0,a
 jp nz,keyboard_release
 dec d
 jp z,keyboard_finished
 jp keyboard_continue
keyboard_release:
 ld d,64
keyboard_continue:
 dec ix
 ld a,ixh
 or ixl
 jp nz,keyboard_scan
keyboard_finished:
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 cp 7
 jp z,load_fullsummary
 jp menu_draw

; Paint a fixed-ROM key rectangle: HL=HOME attributes, B=width, A=color.
; Two rows only. Preserve D hold counter, E input bits, IX scan budget and AF'.
keyboard_paint:
 ld c,a
 ld a,b
 ld i,a
keyboard_paint_top:
 ld (hl),c
 inc hl
 djnz keyboard_paint_top
 ld a,i
 ld b,a
 neg
 add a,32
 add a,l
 ld l,a
 jp nc,keyboard_paint_bottom
 inc h
keyboard_paint_bottom:
 ld (hl),c
 inc hl
 djnz keyboard_paint_bottom
 jp (iy)

; EAR/joystick reads do not imply a successful tape transfer.
inputs_ready:
 ld bc,$00f5
 ld a,7
 out (c),a
 inc c
 ld a,$3f
 out (c),a
 exx
 ld hl,$ffff
 exx
input_scan:
 ld bc,$fffe
 in a,(c)
 and $40
 ld de,$508e
 ld iy,input_joy1
 jp hex_byte
input_joy1:
 ld bc,$00f5
 ld a,14
 out (c),a
 ld bc,$01f6
 in a,(c)
 ld ixl,a
 ld de,$40e6
 ld iy,input_paint1
 jp hex_byte
input_paint1:
 ld e,0
 jp input_paint
input_joy2:
 ld bc,$02f6
 in a,(c)
 ld ixl,a
 ld de,$40f6
 ld iy,input_paint2
 jp hex_byte
input_paint2:
 ld e,16
input_paint:
 ld a,3
 xor a
 out ($f4),a
 ld a,($3f00)
 cp $21
 jp nz,cartridge_alarm
 ld hl,$3f00
 ld b,96
 ld c,0
input_paint_qualify:
 ld a,(hl)
 add a,c
 ld c,a
 inc hl
 djnz input_paint_qualify
 cp (hl)
 jp nz,cartridge_alarm
 jp $3f00
input_paint_done:
 ld a,1
 xor a
 out ($f4),a
 ld a,e
 or a
 jp z,input_joy2
 jp input_pause
input_pause:
 ld iy,input_stop_continue
 jp menu_stop_poll
input_stop_continue:
 exx
 dec hl
 ld a,h
 or l
 exx
 jp nz,input_scan
 jp menu_draw

; Bounded beeper segments, M polled between each full waveform.
beeper_ready:
 ld d,3
 ld e,0
beeper_segment:
 ld ix,700
beeper_wave:
 ld a,e
 add a,$12 ; Speaker high; red/magenta/green for low/mid/high.
 out ($fe),a
 ld hl,900
 ld a,e
 or a
 jp z,beeper_delay_high
 ld hl,450
 cp 1
 jp z,beeper_delay_high
 ld hl,225
beeper_delay_high:
 dec hl
 ld a,h
 or l
 jp nz,beeper_delay_high
 ld a,e
 add a,2 ; Speaker low; preserve the same border for this tone.
 out ($fe),a
 ld hl,900
 ld a,e
 or a
 jp z,beeper_delay_low
 ld hl,450
 cp 1
 jp z,beeper_delay_low
 ld hl,225
beeper_delay_low:
 dec hl
 ld a,h
 or l
 jp nz,beeper_delay_low
 ld iy,audio_stop_continue_1
 jp menu_stop_poll
audio_stop_continue_1:
 dec ix
 ld a,ixh
 or ixl
 jp nz,beeper_wave
 inc e
 dec d
 jp nz,beeper_segment
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 cp 7
 jp z,ay_test
 jp audio_exit

; AY readback masks exclude port A and nonexistent register15.
ay_test:
 ld bc,$00f5
 ld a,7
 out (c),a
 inc c
 ld a,$3f
 out (c),a
 ld d,0
ay_write_loop:
 ld bc,$00f5
 ld a,d
 out (c),a
 inc c
 ; differing index-derived patterns catch address aliases. R7 remains safe.
 ld a,d
 xor $a5
 ld hl,ay_masks
 ld e,d
 ld d,0
 add hl,de
 ld d,e
 and (hl)
 cp 0
 ; No branch depends on target data; only readback generates a result.
 ld e,a
 ld a,d
 cp 7
 ld a,e
 jp nz,ay_write_safe
 or $3f
ay_write_safe:
 out (c),a
 inc d
 ld a,d
 cp 14
 jp nz,ay_write_loop
 ld d,0
ay_read_loop:
 ld bc,$00f5
 ld a,d
 out (c),a
 inc c
 in a,(c)
 ld e,a
 ld hl,ay_masks
 ld a,d
 add a,l
 ld l,a
 jp nc,ay_mask_no_carry
 inc h
ay_mask_no_carry:
 ld a,d
 xor $a5
 and (hl)
 ld b,a
 ld a,d
 cp 7
 jp nz,ay_expect_ready
 ld b,$3f
ay_expect_ready:
 ld a,e
 and (hl)
 cp b
 jp nz,ay_failure
 inc d
 ld a,d
 cp 14
 jp nz,ay_read_loop
 jp load_aylisten
ay_masks:
 db $ff,$0f,$ff,$0f,$ff,$0f,$1f,$3f,$1f,$1f,$1f,$ff,$ff,$0f
ay_failure:
 ; Latch failing AY index in alternate BC, display after immutable page loader.
 ld a,d
 exx
 ld c,a
 ld b,0
 exx
 jp audio_fail_mute
aylisten_ready:
 xor a
 ld i,a
ay_step:
 ld iy,ay_step_configure
 jp mute_ay
ay_step_configure:
 ; I is the immutable-bound step counter, never read from HOME/table data.
 ; Table has24 entries of14 register values plus bounded highlight coordinates.
 ld a,5
 xor a
 out ($f4),a
 ld a,i
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,$2300
 add hl,de
 ld d,0
 ld ix,ay_masks
ay_step_registers:
 ld bc,$00f5
 ld a,d
 out (c),a
 inc c
 ld a,(hl)
 and (ix)
 out (c),a
 inc hl
 inc ix
 inc d
 ld a,d
 cp 14
 jp nz,ay_step_registers
 ; Table coordinates are display data only, independently clamped.
 ld a,(hl)
 and 15
 ld c,a
 inc hl
 ld a,(hl)
 and $18
 ld b,a
 ld a,1
 xor a
 out ($f4),a
 exx
 ld hl,$58c0
 ld bc,448
ay_clear_active:
 ld (hl),$47
 inc hl
 dec bc
 ld a,b
 or c
 jp nz,ay_clear_active
 exx
 ld h,0
 ld l,c
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,$58c0
 add hl,de
 ld a,b
 add a,l
 ld l,a
 jp nc,ay_highlight_ready
 inc h
ay_highlight_ready:
 ld b,8
ay_highlight:
 ld (hl),$46
 inc hl
 djnz ay_highlight
 ld a,i
 add a,$a1
 ld l,a
 ld h,$5a
 ld (hl),$46
 ; Short visual fallback marks each active step on the border.
 ld a,i
 and 7
 out ($fe),a
 ld ix,320
ay_listen_delay:
 ld hl,400
ay_listen_inner:
 dec hl
 ld a,h
 or l
 jp nz,ay_listen_inner
 ld iy,audio_stop_continue_2
 jp menu_stop_poll
audio_stop_continue_2:
 dec ix
 ld a,ixh
 or ixl
 jp nz,ay_listen_delay
 ld a,i
 add a,$a1
 ld l,a
 ld h,$5a
 ld (hl),$44
 ld a,i
 inc a
 ld i,a
 cp 24
 jp nz,ay_step
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 cp 7
 jp nz,audio_exit
 ld iy,load_bars
 jp mute_ay
; Every exit lowers FE and writes zero amplitude without reading target state.
audio_fail_mute:
 ld a,5
 ex af,af'
 ld iy,load_fail
 jp mute_ay
audio_exit:
 ld iy,menu_draw
mute_ay:
 xor a
 out ($fe),a
 ld d,8
mute_volume:
 ld bc,$00f5
 ld a,d
 out (c),a
 inc c
 xor a
 out (c),a
 inc d
 ld a,d
 cp 11
 jp nz,mute_volume
 dec c
 ld a,7
 out (c),a
 inc c
 ld a,$3f
 out (c),a
 jp (iy)
; Banking: low ROM anchor never deliberately removed. Alternate BC pass counter.
bank_ready:
 jp load_beeper
rommenu_ready:
 ld iy,rommenu_edge_init
 jp key_gate
rommenu_poll:
 ld bc,$7ffe
 in a,(c)
 bit 2,a
 jp z,menu_draw
 ld bc,$bffe
 in a,(c)
 ld h,a
 cpl
 and d
 ld d,h
 cpl
 bit 4,a
 jp z,home_crc_select
 ld bc,$fbfe
 in a,(c)
 ld h,a
 cpl
 and e
 ld e,h
 cpl
 bit 2,a
 jp z,exrom_crc_select
 jp rommenu_poll
home_crc_select:
exrom_crc_select:
romresult_ready:
 jp load_unavailable
irqmenu_ready:
 ld iy,irqmenu_edge_init
 jp key_gate
irqmenu_poll:
 ld bc,$7ffe
 in a,(c)
 bit 2,a
 jp z,menu_draw
 ld bc,$dffe
 in a,(c)
 ld h,a
 cpl
 and d
 ld d,h
 cpl
 bit 2,a
 jp z,irq_baseline
 bit 3,a
 jp z,cpu_select
 jp irqmenu_poll
irq_baseline:
 jp irq_start
irq_start:
 di
 xor a
 ld i,a
 im 1
 ld sp,$bfff
 ld a,$40
 out ($ff),a
 ld d,0
 ld ix,60000
 ei
irq_inhibit_wait:
 dec ix
 ld a,ixh
 or ixl
 jp nz,irq_inhibit_wait
 di
 ld a,0
 out ($ff),a
 ld d,1
 ld ix,60000
 ei
irq_arrival_wait:
 dec ix
 ld a,ixh
 or ixl
 jp nz,irq_arrival_wait
 di
 jp irq_failed
irq_arrived:
 di
 ld a,d
 cp 1
 jp nz,irq_failed
 ld sp,$bfff
 ld a,$40
 out ($ff),a
 ld a,4
 out ($fe),a
 jp load_pass
irq_failed:
 di
 ld a,d
 exx
 ld c,a
 ld hl,0
 exx
 ld sp,$bfff
 ld a,$40
 out ($ff),a
 ld a,7
 jp result_failure
; B/C = attribute destination, IX = fixed-size optional character buffer.
; RAM-held characters/colors are clamped data; never continuations or counts.
render_tiles:
 ld a,3
 xor a
 out ($f4),a
 ld ix,$6400
 ld bc,$5800
render_tile:
 ld a,ixh
 add a,3
 ld h,a
 ld a,ixl
 ld l,a
 ld a,(hl)
 ld d,b
 ld e,c
 ld (de),a
 ld a,b
 sub $58
 add a,a
 add a,a
 add a,a
 add a,$40
 ld d,a
 ld a,(ix)
 inc ix
 cp 32
 jp nc,render_char_min
 ld a,32
render_char_min:
 cp 128
 jp c,render_char_ready
 ld a,63
render_char_ready:
 sub 32
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 add hl,hl
 ld a,l
 add a,font_data & 255
 ld l,a
 ld a,h
 adc a,font_data >> 8
 ld h,a
 ld a,8
 ld i,a
render_glyph:
 ld a,(hl)
 ld (de),a
 inc hl
 inc d
 ld a,i
 dec a
 ld i,a
 jp nz,render_glyph
 inc c
 jp nz,render_tile
 inc b
 ld a,b
 cp $5b
 jp nz,render_tile
 ld a,1
 xor a
 out ($f4),a
 jp (iy)
; Bounded release gate prevents one held selection entering a submenu test.
key_gate:
 ld ix,5000
key_gate_poll:
 ld bc,$00fe
 in a,(c)
 and $1f
 cp $1f
 jp z,key_gate_done
 dec ix
 ld a,ixh
 or ixl
 jp nz,key_gate_poll
 jp key_gate_done
key_gate_done:
 ld bc,$f7fe
 in a,(c)
 ld d,a
 ld bc,$effe
 in a,(c)
 ld e,a
 jp (iy)
; Bounded register-only cartridge data integrity before HOME RAM tests.
; Additive16 covers first8144 bytes of each chunk, excluding checksum/marker tail.
cartridge_check:
 jp home_integrity
cartridge_alarm:
 ld c,3
 ld iy,cartridge_alarm_poll
 jp pulse_group
cartridge_alarm_poll:
 ld bc,$fbfe
 in a,(c)
 bit 3,a
 jp z,entry
 jp cartridge_alarm

; Two address-byte planes ensure all sixteen logical address bits are compared.
address_lanes_start:
 ld a,3
 out ($fe),a
 ld a,35
 ld i,a
address_lane_fill_start:
 ld hl,$4000
address_lane_fill:
 ld a,i
 cp 35
 ld a,l
 jp z,address_lane_write
 ld a,h
address_lane_write:
 ld (hl),a
 inc hl
 ld a,h
 or l
 jp nz,address_lane_fill
 ld hl,$4000
address_lane_read:
 ld iy,address_lane_next
 ld a,i
 cp 35
 ld d,l
 jp z,address_lane_compare
 ld d,h
address_lane_compare:
 jp compare_byte
address_lane_next:
 inc hl
 ld a,l
 or a
 jp nz,address_lane_poll_done
 ld iy,address_lane_poll_done
 jp ram_key_poll
address_lane_poll_done:
 ld a,h
 or l
 jp nz,address_lane_read
 ld a,i
 cp 36
 jp z,address_lane_done
 ld a,36
 ld i,a
 jp address_lane_fill_start
address_lane_done:
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 and $7f
 cp 3
 jp z,tests_done
 jp random_start

; Peripheral/mapping failures keep audible class codes even with unreadable UI.
aux_fault_start:
 ex af,af'
 ld b,a
 ex af,af'
 ld c,b
 ld iy,aux_fault_poll
 jp pulse_group
aux_fault_poll:
 xor a
 in a,($fe)
 and $1f
 cp $1f
 jp nz,audio_exit
 jp aux_fault_start

rommenu_edge_init:
 ld bc,$bffe
 in a,(c)
 ld d,a
 ld bc,$fbfe
 in a,(c)
 ld e,a
 jp rommenu_poll

irqmenu_edge_init:
 ld bc,$dffe
 in a,(c)
 ld d,a
 jp irqmenu_poll

help_edge_init:
 ld bc,$dffe
 in a,(c)
 ld d,a
 jp help_poll

; AF' carry remembers M released; a stuck initial stop key cannot skip RAM.
; Preserve HL/BC/DE/IX/I and result registers; IY is a fixed ROM callback.
ram_key_poll:
 xor a
 in a,($fe)
 and $1f
 cp $1f
 jp z,ram_stop_released
 ex af,af'
 jp nc,ram_stop_held
 ex af,af'
 ; Reporter callback requests acknowledgment rather than cancelling a sweep.
 ld a,iyh
 cp report_u6 >> 8
 jp nz,ram_cancel
 ld a,iyl
 cp report_u6 & 255
 jp nz,ram_cancel
 jp menu_draw
ram_stop_held:
 ex af,af'
 jp (iy)
ram_stop_released:
 ex af,af'
 scf
 ex af,af'
 jp (iy)

menu_stop_poll:
 xor a
 in a,($fe)
 and $1f
 cp $1f
 jp z,menu_stop_released
 ex af,af'
 jp nc,menu_stop_held
 ex af,af'
 jp audio_exit
menu_stop_held:
 ex af,af'
 jp (iy)
menu_stop_released:
 ex af,af'
 scf
 ex af,af'
 jp (iy)

; Explicit CPU module in ROM2. Low bridge exposes all HOME RAM for alias probes.
cpu_select:
cpuinfo_ready:
 jp load_unavailable
load_select:
 jp load_unavailable
irq_dispatch:
 jp irq_arrived
home_integrity:
 ld hl,0
 ld de,0
 ld bc,$3ffe
home_sum:
 ld a,(hl)
 add a,e
 ld e,a
 jp nc,home_sum_no_carry
 inc d
home_sum_no_carry:
 inc hl
 dec bc
 ld a,b
 or c
 jp nz,home_sum
 ld a,($3ffe)
 cp e
 jp nz,cartridge_alarm
 ld a,($3fff)
 cp d
 jp nz,cartridge_alarm
 jp cartridge_checked

font_data EQU $2000
load_menu:
 ld hl,$2480
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_menu
 jp unpack
render_menu:
 ld iy,menu_ready
 jp render_tiles
load_fullinfo:
 ld hl,$25f2
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_fullinfo
 jp unpack
render_fullinfo:
 ld iy,fullinfo_ready
 jp render_tiles
load_fullsummary:
 ld hl,$2706
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_fullsummary
 jp unpack
render_fullsummary:
 ld iy,fullsummary_ready
 jp render_tiles
load_startupquick:
 ld hl,$2810
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_startupquick
 jp unpack
render_startupquick:
 ld iy,startupquick_ready
 jp render_tiles
load_startupfull:
 ld hl,$292d
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_startupfull
 jp unpack
render_startupfull:
 ld iy,startupfull_ready
 jp render_tiles
load_rammenu:
 ld hl,$2a30
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_rammenu
 jp unpack
render_rammenu:
 ld iy,rammenu_ready
 jp render_tiles
load_rampass:
 ld hl,$2b51
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_rampass
 jp unpack
render_rampass:
 ld iy,rampass_ready
 jp render_tiles
load_soak:
 ld hl,$2c54
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_soak
 jp unpack
render_soak:
 ld iy,soak_ready
 jp render_tiles
load_soakstop:
 ld hl,$2d4a
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_soakstop
 jp unpack
render_soakstop:
 ld iy,soakstop_ready
 jp render_tiles
load_soundmenu:
 ld hl,$2e33
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_soundmenu
 jp unpack
render_soundmenu:
 ld iy,soundmenu_ready
 jp render_tiles
load_beeper:
 ld hl,$2ef5
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_beeper
 jp unpack
render_beeper:
 ld iy,beeper_ready
 jp render_tiles
load_help:
 ld hl,$2fd2
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_help
 jp unpack
render_help:
 ld iy,help_ready
 jp render_tiles
load_soundguide:
 ld hl,$30ea
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_soundguide
 jp unpack
render_soundguide:
 ld iy,soundguide_ready
 jp render_tiles
load_pass:
 ld hl,$31ec
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_pass
 jp unpack
render_pass:
 ld iy,pass_ready
 jp render_tiles
load_fail:
 ld hl,$32bb
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_fail
 jp unpack
render_fail:
 ld iy,fail_ready
 jp render_tiles
load_inputs:
 ld hl,$3392
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_inputs
 jp unpack
render_inputs:
 ld iy,inputs_ready
 jp render_tiles
load_irqmenu:
 ld hl,$34ed
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_irqmenu
 jp unpack
render_irqmenu:
 ld iy,irqmenu_ready
 jp render_tiles
load_unavailable:
 ld hl,$35d2
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_unavailable
 jp unpack
render_unavailable:
 ld iy,unavailable_ready
 jp render_tiles
load_aylisten:
 ld hl,$36a0
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_aylisten
 jp unpack
render_aylisten:
 ld iy,aylisten_ready
 jp render_tiles
load_keyboard:
 ld hl,$3843
 ld de,$6400
 ld bc,1536
 ld a,$40
 ld i,a
 ld iy,render_keyboard
 jp unpack
render_keyboard:
 ld iy,keyboard_ready
 jp render_tiles
load_videomenu:
 jp load_unavailable
load_bars:
 jp load_keyboard
load_standard:
 jp load_unavailable
load_secondary:
 jp load_unavailable
load_ecm:
 jp load_unavailable
load_hires:
 jp load_unavailable
load_mix128:
 jp load_unavailable
load_rommenu:
 jp load_unavailable
load_romresult:
 jp load_unavailable
load_cpuinfo:
 jp load_unavailable
load_bank:
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 cp 7
 jp z,load_beeper
 jp load_unavailable
unavailable_ready:
 jp result_wait
home_code_end:
 ASSERT $ <= $2000
 DS $2000-$,255
 INCBIN "pool.bin"
 DS $3ffe-$,255
 DW 0
