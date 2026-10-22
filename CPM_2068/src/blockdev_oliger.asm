; JLO Board A WD1770, source audited against Eduardo Fuentes's jlo-disk branch.
; 40 cylinders, one/two sides, 16 x 256-byte sectors. CP/M sees 128-byte records.
; Write through: always read/modify/write a full physical sector.
oliger_init:
    call ol_invalidate
    ld a,1
    out ($b7),a
    xor a
    call ol_command
    call ol_wait_done
    ret c
    and $18
    ret
oliger_read:
    xor a
    jr ol_transfer
oliger_write:
    ld a,1
ol_transfer:
    ld (ol_writing),a
    ld a,c
    or a
    jp nz,ol_error
    ld a,h
    cp DISK_LBA_HIGH
    ; Capacity is an exact multiple of 256 logical records.
    jp nc,ol_error
    ; A physical read already fetched the adjacent CP/M record. Offer that
    ; partner exactly once, and only to the immediately following read.
    ; Writes always fetch fresh data before modifying the other half.
    ld a,(ol_writing)
    or a
    jr nz,ol_cache_miss
    ld a,(ol_cache_valid)
    or a
    jr z,ol_cache_miss
    push hl
    ld de,(ol_cache_partner)
    or a
    sbc hl,de
    pop hl
    jr nz,ol_cache_miss
    call ol_invalidate
    ld a,l
    and 1
    ld (ol_half),a
    jp ol_copy_half
ol_cache_miss:
    call ol_invalidate
    push hl
    ld a,l
    xor 1
    ld l,a
    ld (ol_cache_partner),hl
    pop hl
    IF DISK_SIDES = 2
    ld a,l
    and 32
    rlca
    rlca
    or 1
    ELSE
    ld a,1
    ENDIF
    ld (ol_select),a
    ld a,l
    and 1
    ld (ol_half),a
    srl h
    rr l
    ld a,l
    and 15
    inc a
    ld (ol_sector),a
    ; Physical cylinder = original LBA / 32.
    ld b,3+DISK_SIDES
ol_cylinder:
    srl h
    rr l
    djnz ol_cylinder
    ld a,l
    ld (ol_track),a
    ld a,(ol_select)
    out ($b7),a
    in a,($9f)
    cp l
    jr z,ol_positioned
    ld a,l
    out ($bf),a
    ld a,$10
    call ol_command
    call ol_wait_done
    jp c,ol_error
    and $18
    jp nz,ol_error
ol_positioned:
    ld a,(ol_sector)
    out ($af),a
    ld a,$80
    call ol_command
    ld hl,ol_cache
    ld b,0
    call ol_start_timeout
ol_read_byte:
    in a,($8f)
    bit 1,a
    jr nz,ol_read_ready
    bit 0,a
    jp z,ol_error
    call ol_tick_timeout
    jp c,ol_error
    jr ol_read_byte
ol_read_ready:
    in a,($bf)
    ld (hl),a
    inc hl
    djnz ol_read_byte
    call ol_wait_done
    jp c,ol_error
    and $7c              ; lost data, CRC, RNF, deleted record, write protect
    jp nz,ol_error
    ld a,(ol_writing)
    xor 1
    ld (ol_cache_valid),a
ol_copy_half:
    ld hl,ol_cache
    ld a,(ol_half)
    or a
    jr z,ol_half_ready
    ld de,128
    add hl,de
ol_half_ready:
    ld de,bounce
    ld a,(ol_writing)
    or a
    jr nz,ol_modify
    ld bc,128
    ldir
    xor a
    ret
ol_modify:
    ex de,hl
    ld bc,128
    ldir
    ld a,(ol_sector)
    out ($af),a
    ld a,$a0
    call ol_command
    ld hl,ol_cache
    ld b,0
    call ol_start_timeout
ol_write_byte:
    in a,($8f)
    bit 1,a
    jr nz,ol_write_ready
    bit 0,a
    jp z,ol_error
    call ol_tick_timeout
    jp c,ol_error
    jr ol_write_byte
ol_write_ready:
    ld a,(hl)
    out ($bf),a
    inc hl
    djnz ol_write_byte
    call ol_wait_done
    jp c,ol_error
    and $7c
    jp nz,ol_error
    xor a
    ret
ol_command:
    out ($8f),a
    ; WD1770 command/status settling delay, also used by SAFE.
    push bc
    ld b,8
ol_settle:
    djnz ol_settle
    pop bc
    ret
ol_start_timeout:
    ld a,8
    ld (ol_timeout),a
    ld de,0
    ret
ol_tick_timeout:
    dec de
    ld a,d
    or e
    ret nz
    ld a,(ol_timeout)
    dec a
    ld (ol_timeout),a
    ret nz
    scf
    ret
ol_wait_done:
    ld a,8
    ld (ol_timeout),a
    ld de,0
ol_poll_done:
    in a,($8f)
    bit 0,a
    jr nz,ol_still_busy
    or a
    ret
ol_still_busy:
    dec de
    ld a,d
    or e
    jr nz,ol_poll_done
    ld a,(ol_timeout)
    dec a
    ld (ol_timeout),a
    jr nz,ol_poll_done
    scf
    ret
ol_error:
    call ol_invalidate
    ld a,$d0
    call ol_command
    ld a,1
    or a
    ret
ol_invalidate:
    xor a
    ld (ol_cache_valid),a
    ret
ol_cache_valid: db 0
ol_cache_partner: dw 0
ol_timeout: db 0
ol_writing: db 0
ol_half: db 0
ol_sector: db 0
ol_track: db 0
ol_select: db 1
ol_cache: ds 256
