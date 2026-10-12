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
 out ($f4),a
 jp (iy)
asset_error:
 ld a,$40
 out ($ff),a
 ld a,1
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
 ld hl,30000
soak_pause_loop:
 ld iy,soak_pause_continue
 jp ram_key_poll
soak_pause_continue:
 dec hl
 ld a,h
 or l
 jp nz,soak_pause_loop
 jp ram_start

; One byte -> two hexadecimal glyphs, DE=bitmap row0 position.
; Immutable font index, fixed IY continuation. All input byte values are bounded.
hex_byte:
 ld c,a
 ld a,$03
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
 out ($f4),a
 jp (iy)

; Reporter display never uses decoder registers, and preserves D/E/IX/results.
fault_draw:
 exx
 ld a,h
 exx
 and $0f
 jp z,fault_display_ok
 exx
 ld a,h
 exx
 and $f0
 jp nz,fault_draw_done ; both display nibbles suspect: pulses only
fault_display_ok:
 ld a,3
 out ($f4),a
 ld a,d
 cp 1
 jp z,fault_u6
 cp 2
 jp z,fault_u7
 cp 3
 jp z,fault_u12
 cp 4
 jp z,fault_u13
 cp 5
 jp z,fault_u17
 ld bc,FAULT_U18
 jp fault_pixels
fault_u6:
 ld bc,FAULT_U6
 jp fault_pixels
fault_u7:
 ld bc,FAULT_U7
 jp fault_pixels
fault_u12:
 ld bc,FAULT_U12
 jp fault_pixels
fault_u13:
 ld bc,FAULT_U13
 jp fault_pixels
fault_u17:
 ld bc,FAULT_U17
fault_pixels:
 ld hl,$4000
 ; U6 uses PAPER with healthy U7 pixels zero; U7 uses healthy INK lanes.
 exx
 ld a,h
 exx
 and $0f
 ld a,0
 jp nz,fault_fill_start
 ld a,$ff
fault_fill_start:
 ld i,a
fault_fill:
 ld a,i
 ld (hl),a
 inc hl
 ld a,h
 cp $58
 jp nz,fault_fill
fault_attributes:
 ld a,(bc)
 ld i,a
 exx
 ld a,h
 exx
 and $0f
 jp z,fault_attr_original
 ld a,d
 cp 3
 jp c,fault_attr_original
 ld a,i
 or a
 ld a,0
 jp z,fault_attr_write
 ld a,$30
 jp fault_attr_write
fault_attr_original:
 ld a,i
fault_attr_write:
 ld (hl),a
 inc bc
 inc hl
 ld a,h
 cp $5b
 jp nz,fault_attributes
 ld a,1
 out ($f4),a
 jp fault_draw_done

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
 INCLUDE "../build/keyboard-scan.asm"
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
 out ($f4),a
 ld a,i
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld de,$4400
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
 exx
 ld bc,0
 exx
 ld a,1
 out ($f4),a
 ld hl,$5ff0
 ld e,2
bank_home_seed:
 ld a,e
 xor $5a
 ld (hl),a
 ld a,h
 add a,$20
 ld h,a
 inc e
 ld a,e
 cp 8
 jp nz,bank_home_seed
bank_pass:
 ld a,18
 ld i,a
 ld ix,bank_masks
bank_pattern:
 ld a,i
 or a
 jp z,bank_home_verify
 dec a
 ld i,a
 ld a,(ix)
 inc ix
 or 1
 ld d,a
 ld hl,$3ff0
 ld e,1
 ld c,2
bank_probe:
 ld a,d
 and c
 jp z,bank_probe_next
 ld a,1
 out ($f4),a
 ld a,d
 out ($f4),a
 ld b,(hl)
 ld a,e
 xor $a5
 cp b
 jp nz,bank_failure
 ld (hl),0
 ld b,(hl)
 cp b
 jp nz,bank_failure
bank_probe_next:
 sla c
 ld a,h
 add a,$20
 ld h,a
 inc e
 ld a,e
 cp 8
 jp nz,bank_probe
 ld iy,bank_stop_continue
 jp menu_stop_poll
bank_stop_continue:
 jp bank_pattern
bank_home_verify:
 ld a,1
 out ($f4),a
 ld hl,$5ff0
 ld e,2
bank_home_read:
 ld a,e
 xor $5a
 cp (hl)
 jp nz,bank_failure
 ld a,h
 add a,$20
 ld h,a
 inc e
 ld a,e
 cp 8
 jp nz,bank_home_read
 exx
 inc bc
 ld a,c
 exx
 cp 100
 jp nz,bank_progress
 ex af,af'
 ld b,a
 ex af,af'
 ld a,b
 cp 7
 jp z,load_beeper
bank_progress:
 exx
 ld a,b
 exx
 ld de,$48cf
 ld iy,bank_count_low
 jp hex_byte
bank_count_low:
 exx
 ld a,c
 exx
 ld de,$48d1
 ld iy,bank_pass
 jp hex_byte
bank_failure:
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
 ld a,1
 out ($f4),a
 ld a,$12
 out ($fe),a
 ld a,4
 jp result_failure
bank_masks:
 db $03,$05,$09,$11,$21,$41,$81,$ff,$55,$ab,$fd,$fb,$f7,$ef,$df,$bf,$7f,1,0

; Optional CRC: high code must match the immutable shadow before execution.
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
 ld e,0
 jp crc_qualify
exrom_crc_select:
 ld e,1
crc_qualify:
 ld a,$13
 out ($f4),a
 ld hl,$2000
 ld bc,$8000
 ld ix,512
crc_compare_code:
 ld a,(bc)
 cp (hl)
 jp nz,crc_code_bad
 inc hl
 inc bc
 dec ix
 ld a,ixh
 or ixl
 jp nz,crc_compare_code
 ld a,e
 or a
 jp nz,exrom_copy_gateway
 ld a,$11
 out ($f4),a
 jp $8020
exrom_copy_gateway:
 ld hl,$8100
 ld de,$c000
 ld bc,256
 ldir
 ld hl,$8100
 ld de,$c000
 ld bc,256
exrom_check_gateway:
 ld a,(de)
 cp (hl)
 jp nz,crc_code_bad
 inc hl
 inc de
 dec bc
 ld a,b
 or c
 jp nz,exrom_check_gateway
 jp $c000
crc_code_bad:
 ld a,1
 out ($f4),a
 ld a,6
 jp result_failure
crc_home_return:
 ; BCDE measured CRC, retained in alternate registers across page decoding.
 exx
 ld h,0
 exx
 jp crc_save
crc_exrom_return:
 exx
 ld h,1
 exx
crc_save:
 ld a,b
 exx
 ld b,a
 exx
 ld a,c
 exx
 ld c,a
 exx
 ld a,d
 exx
 ld d,a
 exx
 ld a,e
 exx
 ld e,a
 exx
 jp load_romresult
romresult_ready:
 exx
 ld a,b
 exx
 ld de,$40e8
 ld iy,crc_show_c
 jp hex_byte
crc_show_c:
 exx
 ld a,c
 exx
 ld de,$40ea
 ld iy,crc_show_d
 jp hex_byte
crc_show_d:
 exx
 ld a,d
 exx
 ld de,$40ec
 ld iy,crc_show_e
 jp hex_byte
crc_show_e:
 exx
 ld a,e
 exx
 ld de,$40ee
 ld iy,crc_show_stock
 jp hex_byte
crc_show_stock:
 exx
 ld a,h
 exx
 or a
 jp nz,crc_stock_exrom
 ld a,$bf
 ld de,$4848
 ld iy,crc_stock_home_c
 jp hex_byte
crc_stock_home_c:
 ld a,$44
 ld de,$484a
 ld iy,crc_stock_home_d
 jp hex_byte
crc_stock_home_d:
 ld a,$ec
 ld de,$484c
 ld iy,crc_stock_home_e
 jp hex_byte
crc_stock_home_e:
 ld a,$3f
 ld de,$484e
 ld iy,result_wait
 jp hex_byte
crc_stock_exrom:
 ld a,$ae
 ld de,$4848
 ld iy,crc_stock_exrom_c
 jp hex_byte
crc_stock_exrom_c:
 ld a,$16
 ld de,$484a
 ld iy,crc_stock_exrom_d
 jp hex_byte
crc_stock_exrom_d:
 ld a,$23
 ld de,$484c
 ld iy,crc_stock_exrom_e
 jp hex_byte
crc_stock_exrom_e:
 ld a,$3a
 ld de,$484e
 ld iy,result_wait
 jp hex_byte

; IRQ test is explicit: SP initialized for automatic entry writes only.
; No stack reads, RET/RETI/RETN or arbitrary interrupted continuation.
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
 ld b,1
 ld c,8
 ld hl,0
 ld iy,$1fd0
cartridge_chunk:
 ld a,b
 or 1
 out ($f4),a
 ld de,0
 ld ix,$1fd0
cartridge_sum:
 ld a,(hl)
 add a,e
 ld e,a
 ld a,d
 adc a,0
 ld d,a
 inc hl
 dec ix
 ld a,ixh
 or ixl
 jp nz,cartridge_sum
 ld a,(iy)
 cp e
 jp nz,cartridge_fault
 ld a,(iy+1)
 cp d
 jp nz,cartridge_fault
 inc iy
 inc iy
 dec c
 jp z,cartridge_good
 rlc b
 ld a,h
 and $e0
 add a,$20
 ld h,a
 ld l,0
 jp cartridge_chunk
cartridge_good:
 ld a,1
 out ($f4),a
 jp cartridge_checked
cartridge_fault:
 ld a,1
 out ($f4),a
 ; Latched cartridge failure: short repeating tones, R retries from entry.
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
 jp load_cpuinfo
cpuinfo_ready:
 di
 ld a,5
 out ($f4),a
 jp $4000
alias_probe:
 ld a,1
 out ($f4),a
 ld hl,$4000
 ld a,d
 cp $40
 jp nz,alias_base_ready
 ld h,$80
alias_base_ready:
 ld a,h
 xor d
 ld b,a
 ld a,l
 xor e
 ld c,a
 ld a,$55
 ld (hl),a
 ld a,$aa
 ld (bc),a
 ld a,(hl)
 cp $55
 jp nz,cpu_failed_low
 ld a,(bc)
 cp $aa
 jp nz,cpu_failed_low
 ld a,$aa
 ld (hl),a
 ld a,$55
 ld (bc),a
 ld a,(hl)
 cp $aa
 jp nz,cpu_failed_low
 ld a,(bc)
 cp $55
 jp nz,cpu_failed_low
 ld a,5
 out ($f4),a
 jp $4006
cpu_failed_low:
 ld a,5
 out ($f4),a
 jp $4003
