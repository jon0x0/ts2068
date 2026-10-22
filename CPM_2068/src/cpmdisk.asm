; Modern directory/DSK/TAP bridge utility. Warm boot refreshes disk geometry.
    org $100
    jp main
WORK_BASE equ $c000
    include "tspico-layout.inc"
    include "../third_party/tspico-filelib/tpi.asm"
    include "tspico-probe.asm"
main:
    ld a,($eff4)
    or a
    jp nz,ram_mode
    ld a,($80)
    or a
    jp z,help
    ld b,a
    ld hl,$81
leading:
    ld a,(hl)
    cp ' '
    jr nz,argument
    inc hl
    djnz leading
    jp help
argument:
    ld de,input
    push de
copy_argument:
    ld a,(hl)
    ld (de),a
    inc hl
    inc de
    djnz copy_argument
    xor a
    ld (de),a
trim:
    dec de
    ld a,(de)
    cp ' '
    jr nz,trimmed
    xor a
    ld (de),a
    jr trim
trimmed:
    pop hl
    ld (arg_start),hl
    xor a
    ld (saving),a
    ld de,save_word
    call matches
    jr z,save_mode
    ld hl,(arg_start)
    ld de,mount_word
    call matches
    jr z,mount_mode
    ld hl,(arg_start)
mount_mode:
    push hl
    ld hl,mount_command
    jr prepare
save_mode:
    ld a,1
    ld (saving),a
    push hl
    ld hl,save_command
prepare:
    ld de,COMMAND_BUFFER
    call append
    pop hl
    ld a,(hl)
    or a
    jp z,help
    call append
    ; The link is used only after a verified modern handshake.
    call tsp_probe
    jr c,failed
    ld c,13
    call 5
    ld hl,0
    ld (PMR1),hl
    ld (PMR2),hl
    ld hl,COMMAND_BUFFER
    call tpi_execute
    jr c,failed
    ld de,success
    ld c,9
    call 5
    ld a,(saving)
    or a
    ret nz
    jp 0
failed:
    ld de,error
    jr print
ram_mode:
    ld de,ram_warning
    jr print
help:
    ld de,usage
print:
    ld c,9
    call 5
    ret
append:
    ld a,(hl)
    ld (de),a
    inc hl
    inc de
    or a
    jr nz,append
    dec de
    ret
matches:
    ld a,(de)
    or a
    ret z
    cp (hl)
    jr nz,no_match
    inc de
    inc hl
    jr matches
no_match:
    ld a,1
    or a
    ret
save_word: db 'SAVE ',0
mount_word: db 'MOUNT ',0
mount_command: db 'tpi:.cpmmount ',0
save_command: db 'tpi:.cpmsave ',0
saving: db 0
arg_start: dw 0
input: ds 128
success: db 'Disk operation completed.',13,10,'$'
error: db 'Disk operation failed; check file/configuration and service logs.',13,10,'$'
ram_warning: db 'RAMDisk mode: use TPSAVE; restart to select an SD disk.',13,10,'$'
usage:
    db 'CPMDISK DIR              Mount/refresh /CPM/FILES',13,10
    db 'CPMDISK MOUNT NAME.DSK   Mount a 160K/320K DSK or TAP in /CPM',13,10
    db 'CPMDISK SAVE NAME.TAP    Export to a new TAP or DSK',13,10
    db 'Writes update the mounted file; SAVE makes a snapshot.',13,10
    db 'Close files before switching. Existing exports are not replaced.',13,10,'$'
