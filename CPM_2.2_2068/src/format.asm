; Initialize a CP/M directory using the selected BIOS/DPB; no media geometry change.
    include "../build/disk-layout.inc"
    org $100
    jp start
start:
    ld a,($80)
    ld b,a
    ld hl,$81
    or a
    jp z,usage
.space:
    ld a,(hl)
    cp ' '
    jr nz,.drive
    inc hl
    djnz .space
    jp usage
.drive:
    sub 'A'
    cp 16
    jp nc,usage
    ld (drive),a
    add a,'A'
    ld (drive_text),a
    inc hl
    dec b
    jr z,.parsed
    ld a,(hl)
    cp ':'
    jr nz,.trailing
    inc hl
    dec b
    jr z,.parsed
.trailing:
    ld a,(hl)
    cp ' '
    jp nz,usage
    inc hl
    djnz .trailing
.parsed:
    ld hl,(1)
    dec hl
    dec hl
    dec hl
    ld (bios_base),hl
    ld a,(drive)
    ld c,a
    ld e,0
    ld a,27
    call bios
    ld a,h
    or l
    ld de,no_drive
    jp z,print_return
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld (translation),de
    ld de,9
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de,hl
    ld (dpb),hl
    ld c,(hl)
    inc hl
    ld b,(hl)
    ld a,b
    or c
    jp z,bad_geometry
    ld (spt),bc
    ; Directory sectors = ceil((DRM+1)/4); support up to 1024 entries.
    ld hl,(dpb)
    ld de,7
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld a,d
    cp 4
    jp nc,bad_geometry
    ex de,hl
    ld de,4
    add hl,de
    srl h
    rr l
    srl h
    rr l
    ld (remaining),hl
    ld hl,(dpb)
    ld de,13
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld (track),de
    ld hl,0
    ld (sector),hl
    ld de,warning
    ld c,9
    call 5
    ld c,1
    call 5
    and $df
    cp 'Y'
    jr z,confirmed
    ld de,cancelled
    jp finish
confirmed:
    IF BUILD_BANKED
    ld a,($eff4)
    cp 1
    jr nz,.no_saver
    call load_saver
    or a
    jp nz,saver_missing
.no_saver:
    ENDIF
    ld hl,buffer
    ld de,buffer+1
    ld bc,127
    ld (hl),$e5
    ldir
.next:
    ld bc,(track)
    ld a,30
    call bios
    ld bc,(sector)
    ld de,(translation)
    ld a,48
    call bios
    ld b,h
    ld c,l
    ld a,33
    call bios
    ld bc,buffer
    ld a,36
    call bios
    ld c,1                     ; directory write, immediate on cached BIOSes
    ld a,42
    call bios
    or a
    jr nz,io_error
    ld bc,verify
    ld a,36
    call bios
    ld a,39
    call bios
    or a
    jr nz,io_error
    ld hl,verify
    ld b,128
.check:
    ld a,(hl)
    cp $e5
    jr nz,io_error
    inc hl
    djnz .check
    ld hl,(remaining)
    dec hl
    ld (remaining),hl
    ld a,h
    or l
    jr z,done
    ld hl,(sector)
    inc hl
    ld (sector),hl
    ld de,(spt)
    or a
    sbc hl,de
    jr nz,.next
    ld hl,0
    ld (sector),hl
    ld hl,(track)
    inc hl
    ld (track),hl
    jr .next
done:
    IF BUILD_BANKED
    ld a,($eff4)
    cp 1
    jr nz,.no_saver
    call restore_saver
    or a
    jr nz,io_error
    ld de,saver_kept
    ld c,9
    call 5
.no_saver:
    ENDIF
    ld de,complete
    jr finish
io_error:
    ld de,failed
finish:
    ld c,9
    call 5
    jp 0                       ; discard BDOS allocation/directory state
bad_geometry:
    ld de,unsupported
    jr finish
usage:
    ld de,help
print_return:
    ld c,9
    jp 5
bios:
    push de
    ld hl,(bios_base)
    ld e,a
    ld d,0
    add hl,de
    pop de
    jp (hl)
    IF BUILD_BANKED
; Preserve the save tool before deleting its directory entry. Limit to 16KB.
load_saver:
    ld de,saver_fcb
    ld c,15
    call 5
    cp $ff
    ret z
    ld hl,$8000
    ld (saver_dma),hl
    xor a
    ld (saver_records),a
.read:
    ld de,(saver_dma)
    ld c,26
    call 5
    ld de,saver_fcb
    ld c,20
    call 5
    or a
    jr nz,.end
    ld a,(saver_records)
    inc a
    ld (saver_records),a
    cp 128
    jr z,.bad
    ld hl,(saver_dma)
    ld de,128
    add hl,de
    ld (saver_dma),hl
    jr .read
.end:
    cp 1
    jr nz,.bad
    ld a,(saver_records)
    or a
    jr z,.bad
    xor a
    ret
.bad:
    ld a,$ff
    ret
restore_saver:
    ld c,13
    call 5
    ld hl,saver_fcb+12
    ld de,saver_fcb+13
    ld bc,23
    ld (hl),0
    ldir
    ld de,saver_fcb
    ld c,22
    call 5
    cp $ff
    ret z
    ld hl,$8000
    ld (saver_dma),hl
.write:
    ld de,(saver_dma)
    ld c,26
    call 5
    ld de,saver_fcb
    ld c,21
    call 5
    or a
    ret nz
    ld hl,(saver_dma)
    ld de,128
    add hl,de
    ld (saver_dma),hl
    ld hl,saver_records
    dec (hl)
    jr nz,.write
    ld de,saver_fcb
    ld c,16
    call 5
    cp $ff
    ret z
    xor a
    ret
saver_missing:
    ld de,saver_error
    jp finish
saver_error: db 13,10,'Cannot retain TPSAVE.COM. Nothing formatted.',13,10,'$'
saver_kept: db 13,10,'TPSAVE.COM retained so RAMDisk can be saved.',13,10,'$'
saver_fcb: db 0,'TPSAVE  COM'
    defs 24,0
saver_records: db 0
saver_dma: dw 0
    ENDIF
drive: db 0
bios_base: dw 0
translation: dw 0
dpb: dw 0
spt: dw 0
remaining: dw 0
track: dw 0
sector: dw 0
help: db 'FORMAT A: initializes the mounted disk directory.',13,10
    db 'Erases all files; keeps disk size. Not a secure data wipe.',13,10,'$'
no_drive: db 'Drive unavailable. Nothing formatted.',13,10,'$'
unsupported: db 'Unsupported directory geometry.',13,10,'$'
warning: db 'Erase ALL files on drive '
drive_text: db 'A',':? Type Y to format: $'
cancelled: db 13,10,'Cancelled.',13,10,'$'
complete: db 13,10,'Disk initialized and directory verified.',13,10
    db 'RAMDisk: run TPSAVE before power off.',13,10,'$'
failed: db 13,10,'Format failed: disk directory may be partly erased.',13,10,'$'
buffer: defs 128,0
verify: defs 128,0
