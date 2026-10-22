; Stock 1.00 single-FIFO slot selector and 320KB SRAM block device.
; All executing code, stack, state and bounce stay in HOME chunk 7.
    org $f000
    include "disk_geometry.asm"
WORK_BASE equ $f500
    DEFINE LEGACY_PARAMETERS 1
    DEFINE LEGACY_VIDEO 1
    include "tspico-layout.inc"
    include "../build/tpi-dual-sram.asm"
    include "../build/sram-slots.inc"

; MEMDOCK does not document DIR's two-second housekeeping pause. Retain a
; short post-reply guard; actual 1.00 SRAM timing remains a hardware test.
video_settle:
    push bc
    ld bc,2048
sram_guard:
    dec bc
    ld a,b
    or c
    jr nz,sram_guard
    pop bc
    ret
sram_select:
    ld l,a
    ld h,0
    ld (PMR2),hl
    ld hl,1
    ld (PMR1),hl
    ld hl,sram_command
    xor a
    jp legacy_execute
sram_command: db 'TPI:MEMDOCK',0

sram_read:
    xor a
    jr sram_enter
sram_write:
    ld a,1
sram_enter:
    ld (sram_saved_sp),sp
    ld sp,$f7b0
    call sram_io
    ld sp,(sram_saved_sp)
    ret
sram_io:
    ld (sram_writing),a
    ld a,c
    or a
    jp nz,sram_error
    ld a,($eff1)
    cp h
    jp z,sram_error
    jp c,sram_error
    ld a,l
    and 63
    ld e,a
    srl a
    ld d,a
    ld a,e
    and 1
    rrca
    ld e,a
    ld (sram_offset),de
    ld b,6
sram_page_shift:
    srl h
    rr l
    djnz sram_page_shift
    ld a,l
    call sram_position
    ret c
    ld de,(sram_offset)
    add hl,de
    ld de,bounce
    ld a,(sram_writing)
    or a
    jr z,sram_copy
    ex de,hl
sram_copy:
    ld a,(sram_mask)
    out ($f4),a
    ld bc,128
    ldir
    jp sram_restore

; A=8KB disk page (0..39). Select its 64KB slot pair with DOCK unmapped.
; Return HL=CPU window address and the corresponding F4 mask. Page 7 is
; never mapped: it contains the live BIOS, transport, bounce and stack.
sram_position:
    cp 40
    jr nc,sram_error
    ld b,0
sram_pair:
    cp 7
    jr c,sram_window
    sub 7
    inc b
    jr sram_pair
sram_window:
    ld (sram_chunk),a
    ld e,b
    ld d,0
    ld hl,sram_slots
    add hl,de
    ld a,(hl)
    push af
    xor a
    out ($f4),a
    pop af
    call sram_select
    jr c,sram_select_error
    ld a,(sram_chunk)
    ld b,a
    ld a,1
    inc b
sram_mask_loop:
    dec b
    jr z,sram_mask_done
    add a,a
    jr sram_mask_loop
sram_mask_done:
    ld (sram_mask),a
    ld a,(sram_chunk)
    rrca
    rrca
    rrca
    ld h,a
    ld l,0
    or a
    ret
sram_select_error:
    call sram_restore
sram_error:
    ld a,1
    or a
    scf
    ret
sram_restore:
    xor a
    out ($f4),a
    ld a,SRAM_BOOT_SLOT
    call sram_select
    jr c,sram_restore_failed
    ld a,15
    out ($f4),a
    xor a
    ret
sram_restore_failed:
    ; Returning to a different low DOCK would execute corrupted CP/M code.
    ; Remain in HOME instead; red border identifies a failed slot restore.
    ld a,2
    out ($fe),a
    di
    halt
    jr sram_restore_failed

; Loader entry: A=page, 8192 verified bytes at HOME A000. Installation does
; a byte-exact readback before returning; the A000 window uses the protected
; 128-byte bounce buffer to avoid hiding its own source. HOME chunk 7 remains accessible.
sram_install_page:
    ld (sram_saved_sp),sp
    ld sp,$f7b0
    call sram_install_inner
    ld sp,(sram_saved_sp)
    ret
sram_install_inner:
    call sram_position
    ret c
    ld (sram_address),hl
    ld de,$a000
    ld a,(sram_chunk)
    cp 5
    jr nz,sram_install_source
    ld a,1
    ld (sram_writing),a
    jp sram_window5_copy
sram_install_source:
    ld (sram_source),de
    ex de,hl
    ld a,(sram_mask)
    out ($f4),a
    ld bc,8192
    ldir
    ld hl,(sram_source)
    ld de,(sram_address)
    ld bc,8192
sram_verify:
    ld a,(de)
    cpi                         ; compare, advance source and count in one op
    jr nz,sram_verify_error
    inc de                      ; 16-bit INC preserves CPI's parity/count flag
    jp pe,sram_verify
    jp sram_restore
sram_verify_error:
    call sram_restore
    jr sram_error

; Save utility entry: fetch one page into HOME A000 without using CP/M DMA.
sram_fetch_page:
    ld (sram_saved_sp),sp
    ld sp,$f7b0
    call sram_fetch_inner
    ld sp,(sram_saved_sp)
    ret
sram_fetch_inner:
    call sram_position
    ret c
    ld (sram_address),hl
    ld a,(sram_chunk)
    cp 5
    jr nz,sram_fetch_copy
    xor a
    ld (sram_writing),a
    jp sram_window5_copy
sram_fetch_copy:
    ld de,$a000
    ld a,(sram_mask)
    out ($f4),a
    ld bc,8192
    ldir
    jp sram_restore

; HOME A000 and DOCK A000 cannot be visible together. Move each 128-byte
; span through the protected HOME bounce buffer; never borrow video RAM.
; sram_writing=1 installs HOME -> DOCK; 0 fetches DOCK -> HOME.
sram_window5_copy:
    ld a,64
    ld (sram_remaining),a
.next:
    ld a,(sram_writing)
    or a
    ld a,0
    jr nz,.source
    ld a,$20
.source:
    out ($f4),a
    ld hl,(sram_address)
    ld de,bounce
    ld bc,128
    ldir
    xor $20
    out ($f4),a
    ld hl,bounce
    ld de,(sram_address)
    ld bc,128
    ldir
    ld hl,bounce
    ld de,(sram_address)
    ld bc,128
.verify:
    ld a,(de)
    cpi
    jp nz,sram_verify_error
    inc de
    jp pe,.verify
    ld (sram_address),de
    ld hl,sram_remaining
    dec (hl)
    jr nz,.next
    jp sram_restore
sram_remaining: db 0
sram_writing: db 0
sram_offset: dw 0
sram_chunk: db 0
sram_mask: db 0
sram_address: dw 0
sram_source: dw 0
sram_saved_sp: dw 0
    assert $ <= $f500
