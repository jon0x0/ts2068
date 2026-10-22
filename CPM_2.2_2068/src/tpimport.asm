; TPIMPORT /ABSOLUTE/SD/PATH.COM LOCAL.COM
; Native CP/M transient; imports raw modern TSPico bytes into the current drive.
    org $100
    jp importer
    IFNDEF LEGACY_IMPORT
    DEFINE LEGACY_IMPORT 0
    ENDIF
WORK_BASE equ $c000
    DEFINE FILE_STREAM 201
    include "tspico-layout.inc"
    IF LEGACY_IMPORT
    include "../build/tpi-legacy-cpm.asm"
    include "../third_party/tspico-filelib/files_legacy.asm"
    ELSE
    include "../third_party/tspico-filelib/tpi.asm"
    include "../third_party/tspico-filelib/files.asm"
    include "tspico-probe.asm"
    ENDIF
importer:
    ld (saved_sp),sp
    ld sp,$c700
    ld a,($80)
    or a
    jp z,usage
    ld c,a
    ld b,0
    ld hl,$81
    add hl,bc
    ld (hl),0
    ld hl,$81
    call skip_spaces
    ld de,path_name
    ld b,191
copy_path:
    ld a,(hl)
    cp ' '
    jr z,path_done
    or a
    jp z,usage
    ld (de),a
    inc de
    inc hl
    djnz copy_path
    jp usage
path_done:
    xor a
    ld (de),a
    call skip_spaces
    ; Explicit local 8.3 filename, no drive prefix/wildcards/path separators.
    push hl
    ld hl,local_fcb
    ld de,local_fcb+1
    ld bc,35
    ld (hl),0
    ldir
    ld hl,local_fcb+1
    ld b,11
blank_name:
    ld (hl),' '
    inc hl
    djnz blank_name
    pop hl
    ld de,local_fcb+1
    ld b,8
    call name_part
    jp c,usage
    cp '.'
    jp nz,usage
    inc hl
    ld de,local_fcb+9
    ld b,3
    call name_part
    jp c,usage
    or a
    jp nz,usage
    IF LEGACY_IMPORT = 0
    call tsp_probe
    jp c,link_error
    ENDIF
    ; Deterministic padding in the final CP/M record; never save stale RAM.
    ld hl,$4000
    ld de,$4001
    ld bc,$7fff
    ld (hl),0
    ldir
    ld hl,path_name
    ld de,$4000
    ld bc,$8000
    call f_load
    jp c,link_error
    ; No overwrite: OPEN must report missing before MAKE is attempted.
    ld de,local_fcb
    ld c,15
    call 5
    cp $ff
    ld de,exists_msg
    jp nz,print_exit
    ld de,local_fcb
    ld c,22
    call 5
    cp $ff
    jp z,disk_error
    ld hl,(FILE_DONE)
    ld de,127
    add hl,de
    ld b,7
record_count:
    srl h
    rr l
    djnz record_count
    ld (records_left),hl
    ld hl,$4000
    ld (import_ptr),hl
write_record:
    ld hl,(records_left)
    ld a,h
    or l
    jr z,close_file
    dec hl
    ld (records_left),hl
    ld de,(import_ptr)
    ld c,26
    call 5
    ld de,local_fcb
    ld c,21
    call 5
    or a
    jr nz,cleanup_file
    ld hl,(import_ptr)
    ld de,128
    add hl,de
    ld (import_ptr),hl
    jr write_record
close_file:
    ld de,local_fcb
    ld c,16
    call 5
    cp $ff
    jr z,cleanup_file
    ld de,ok_msg
    jr print_exit
cleanup_file:
    ld de,local_fcb
    ld c,19
    call 5
disk_error:
    ld de,disk_msg
    jr print_exit
link_error:
    ld de,link_msg
    jr print_exit
usage:
    ld de,usage_msg
print_exit:
    ld c,9
    call 5
    ld sp,(saved_sp)
    ret
skip_spaces:
    ld a,(hl)
    cp ' '
    ret nz
    inc hl
    jr skip_spaces
name_part:
    ld c,0
name_char:
    ld a,(hl)
    cp '.'
    jr z,name_end
    or a
    jr z,name_end
    cp '0'
    jr c,bad_name
    cp '9'+1
    jr c,name_accept
    cp 'A'
    jr c,bad_name
    cp 'Z'+1
    jr nc,bad_name
name_accept:
    ld (de),a
    inc de
    inc hl
    inc c
    djnz name_char
    ld a,(hl)
    or a
    jr z,name_end
    cp '.'
    jr z,name_end
bad_name:
    scf
    ret
name_end:
    push af
    ld a,c
    or a
    jr z,name_empty
    pop af
    or a
    ret
name_empty:
    pop af
    scf
    ret
saved_sp: dw 0
records_left: dw 0
import_ptr: dw 0
local_fcb: ds 36
path_name: ds 192
    IF LEGACY_IMPORT
usage_msg: db 'TPLOAD FILE.TAP LOCAL.COM',13,10,'$'
    ELSE
usage_msg: db 'TPIMPORT /SD/PATH.COM LOCAL.COM',13,10,'$'
    ENDIF
exists_msg: db 'Destination exists; no overwrite.',13,10,'$'
link_msg: db 'TSPico unavailable, read failed or file exceeds 32K.',13,10,'$'
disk_msg: db 'Import failed: disk full or write error.',13,10,'$'
ok_msg: db 'Imported.',13,10,'$'
    assert $ < $4000
