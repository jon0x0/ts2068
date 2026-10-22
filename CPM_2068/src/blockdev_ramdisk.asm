; Backend contract: C = drive (0), HL = zero-based 128-byte LBA;
; B = CP/M write mode (WRITE only); bounce = common RAM buffer.
; A=0 success, A=1 error. BC/DE/HL/flags clobbered. DI required.
; All exits restore DOCK selection/F4=$0F, preserving FF video/color bits.
; Code/stack/bounce are in HOME page 7.
ram_block_read:
    xor a
    jr block_transfer
ram_block_write:
    ld a,1
block_transfer:
    ld (writing),a
    ld a,c
    or a
    jr nz,block_error
    ; Reject LBA >= 384 (48KB), including nonzero upper bits.
    ld a,h
    cp 2
    jr nc,block_error
    or a
    jr z,block_valid
    ld a,l
    cp $80
    jr nc,block_error
block_valid:
    ; LBA / 64 yields bank index 0..5. EXROM page = index + 1.
    ld a,l
    and 63
    ld e,a
    ld a,l
    rlca
    rlca
    and 3
    ld b,a
    ld a,h
    add a,a
    add a,a
    or b
    inc a
    ld b,a
    ld c,a
    ld a,1
block_mask:
    add a,a
    djnz block_mask
    ld (bankmask),a
    ; Page base = page * $2000; offset = (LBA & 63) * 128.
    ld a,c
    rrca
    rrca
    rrca
    ld h,a
    ld l,0
    ld a,e
    srl a
    or h
    ld h,a
    ld a,e
    and 1
    rrca
    ld l,a
    ld de,bounce
    ld a,(writing)
    or a
    jr z,block_copy
    ex de,hl
block_copy:
    in a,($ff)
    or $80
    out ($ff),a
    ld a,(bankmask)
    out ($f4),a
    ld bc,128
    ldir
    in a,($ff)
    and $7f
    out ($ff),a
    ld a,$0f
    out ($f4),a
    xor a
    ret
block_error:
    ld a,1
    ret
writing: db 0
bankmask: db 0
