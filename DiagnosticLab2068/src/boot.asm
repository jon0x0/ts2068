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
