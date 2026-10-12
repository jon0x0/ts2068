; ROM2 optional CPU and address-path checks. No RAM control or stack operations.
; Fixed entry stubs are the low bridge ABI. I=stage, E=report stage.
 ORG $4000
 jp cpu_start
 jp cpu_failed
 jp alias_next
 INCLUDE "../build/cpu-low.asm"
cpu_start:
 di
 ld a,$40
 out ($ff),a
 ld a,1
 ld i,a
 ld e,1
 ld c,8
 ld iy,cpu_checkpoint
 jp pulse_group
cpu_checkpoint:
 ld c,e
 ld iy,cpu_dispatch
 jp pulse_group
cpu_dispatch:
 ld a,i
 cp 1
 jp z,cpu_registers
 cp 2
 jp z,cpu_arithmetic
 cp 3
 jp z,cpu_shifts
 cp 4
 jp z,cpu_alternates
 cp 5
 jp z,cpu_index
 jp alias_start
cpu_advance:
 ld a,i
 inc a
 ld i,a
 ld e,a
 ld c,8
 ld iy,cpu_checkpoint
 jp pulse_group
cpu_registers:
 ld bc,$55aa
 ld de,$aa55
 ld hl,$0ff0
cpu_register_check:
 ld a,b
 cp $55
 jp nz,cpu_failed
 ld a,c
 cp $aa
 jp nz,cpu_failed
 ld a,d
 cp $aa
 jp nz,cpu_failed
 ld a,e
 cp $55
 jp nz,cpu_failed
 ld a,h
 cp $0f
 jp nz,cpu_failed
 ld a,l
 cp $f0
 jp nz,cpu_failed
 ld b,$aa
 ld c,$55
 ld d,$55
 ld e,$aa
 ld h,$f0
 ld l,$0f
 ld a,b
 cp $aa
 jp nz,cpu_failed
 ld a,c
 cp $55
 jp nz,cpu_failed
 ld a,d
 cp $55
 jp nz,cpu_failed
 ld a,e
 cp $aa
 jp nz,cpu_failed
 ld a,h
 cp $f0
 jp nz,cpu_failed
 ld a,l
 cp $0f
 jp nz,cpu_failed
 jp cpu_advance
cpu_arithmetic:
 ld a,$ff
 add a,1
cpu_arithmetic_check:
 jp nc,cpu_failed
 jp nz,cpu_failed
 ld a,$7f
 add a,1
 jp po,cpu_failed
 jp p,cpu_failed
 cp $80
 jp nz,cpu_failed
 xor a
 sub 1
 jp nc,cpu_failed
 cp $ff
 jp nz,cpu_failed
 scf
 ld a,$7f
 adc a,0
 cp $80
 jp nz,cpu_failed
 scf
 ld a,0
 sbc a,0
 cp $ff
 jp nz,cpu_failed
 ld a,$a5
 and $0f
 cp 5
 jp nz,cpu_failed
 xor $ff
 cp $fa
 jp nz,cpu_failed
 or 5
 cp $ff
 jp nz,cpu_failed
 ld hl,$ffff
 ld bc,1
 add hl,bc
 jp nc,cpu_failed
 ld a,h
 or l
 jp nz,cpu_failed
 jp cpu_advance
cpu_shifts:
 ld a,$81
 rlca
 jp nc,cpu_failed
 cp 3
 jp nz,cpu_failed
 rrca
 cp $81
 jp nz,cpu_failed
 ld b,$81
 sla b
cpu_shift_check:
 jp nc,cpu_failed
 ld a,b
 cp 2
 jp nz,cpu_failed
 srl b
 ld a,b
 cp 1
 jp nz,cpu_failed
 bit 0,b
 jp z,cpu_failed
 res 0,b
 set 7,b
 ld a,b
 cp $80
 jp nz,cpu_failed
 sra b
 ld a,b
 cp $c0
 jp nz,cpu_failed
 jp cpu_advance
cpu_alternates:
 ld bc,$1234
 ld de,$5678
 ld hl,$9abc
 exx
 ld bc,$edcb
 ld de,$a987
 ld hl,$6543
 exx
cpu_alternate_check:
 ld a,b
 cp $12
 jp nz,cpu_failed
 ld a,c
 cp $34
 jp nz,cpu_failed
 ld a,d
 cp $56
 jp nz,cpu_failed
 ld a,e
 cp $78
 jp nz,cpu_failed
 ld a,h
 cp $9a
 jp nz,cpu_failed
 ld a,l
 cp $bc
 jp nz,cpu_failed
 exx
 ld a,b
 cp $ed
 jp nz,cpu_failed
 ld a,c
 cp $cb
 jp nz,cpu_failed
 ld a,d
 cp $a9
 jp nz,cpu_failed
 ld a,e
 cp $87
 jp nz,cpu_failed
 ld a,h
 cp $65
 jp nz,cpu_failed
 ld a,l
 cp $43
 jp nz,cpu_failed
 exx
 ld a,$55
 scf
 ex af,af'
 ld a,$aa
 or a
 ex af,af'
 jp nc,cpu_failed
 cp $55
 jp nz,cpu_failed
 ex af,af'
 jp c,cpu_failed
 cp $aa
 jp nz,cpu_failed
 ex af,af'
 jp cpu_advance
cpu_index:
 ld ix,$55aa
 inc ix
cpu_index_check:
 ld a,ixh
 cp $55
 jp nz,cpu_failed
 ld a,ixl
 cp $ab
 jp nz,cpu_failed
 dec ix
 ld a,ixl
 cp $aa
 jp nz,cpu_failed
 ld iy,$aa55
 inc iy
 ld a,iyh
 cp $aa
 jp nz,cpu_failed
 ld a,iyl
 cp $56
 jp nz,cpu_failed
 dec iy
 ld a,iyl
 cp $55
 jp nz,cpu_failed
 jp cpu_advance
alias_start:
 ld de,1
 ld a,16
 ld i,a
 jp alias_probe
alias_next:
 ld a,i
 inc a
 ld i,a
 cp 32
 jp z,cpu_pass
 sla e
 rl d
 jp alias_probe
cpu_pass:
 jp load_pass
cpu_failed:
 ld a,i
 cp 16
 ld a,8
 jp c,cpu_family_ready
 ld a,9
cpu_family_ready:
 ld c,a
 ld iy,cpu_failed_stage
 jp pulse_group
cpu_failed_stage:
 ld a,i
 ld e,a
 cp 16
 jp c,cpu_stage_code
 sub 15
 ld e,a
cpu_stage_code:
 ld c,e
 ld iy,cpu_failed_poll
 jp pulse_group
cpu_failed_poll:
 xor a
 in a,($fe)
 and $1f
 cp $1f
 jp nz,cpu_return
 jp cpu_failed
cpu_return:
 jp menu_draw
cpu_end:
 ASSERT cpu_end <= $4400
