; TS2068 diagnostic v0.2: stackless native LROS kernel.
; HSR=01 during destructive tests; DECR=40; DI except optional IRQ module.
; No CALL/RET/PUSH/POP/RST/HALT or ROM calls. Optional UI state is bounded data.
;
; Main HL=target, D=expected, B=observed, E=error scratch.
; I=current phase; IY=fixed ROM comparison continuation; IX=first address.
; Alternate H/L/D=error unions for 4000/8000/C000 regions.
; Alternate E=first failing phase, B=expected, C=observed.
; Alternate AF holds selection (0 all, 1 patterns, 2 march).
 ORG 0
 DB 0,1
 DW entry
 DB $ee
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
 jp irq_arrived
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
 INCLUDE "../build/ram-tests.asm"
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
 INCLUDE "boot.asm"
menu_draw:
 di
 ld a,$40
 out ($ff),a
 ld a,1
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
 INCLUDE "modules.asm"
 INCLUDE "../build/suite-assets.asm"
kernel_end:
 ASSERT kernel_end < $1fd0
 DS $1fd0-$,255
 DS 16,0
 DS $2000-$,255
