; Legacy backend: TAP CODE blocks, not raw byte-file channels.
; f_load HL=current-folder filename or &nnn, DE=buffer, BC=capacity.
; f_save HL=1..10 uppercase letters/digits (no suffix), DE=buffer, BC=len.
; Firmware adds .tap. Existing append mode is explicitly disabled first.
; All payload bytes, including $17, are supported. No BASIC/ROM calls.
LEGACY_CAP equ WORK_BASE+49
LEGACY_SOURCE equ WORK_BASE+51
LEGACY_LENGTH equ WORK_BASE+53
LEGACY_DEST equ WORK_BASE+55
LEGACY_POST_ERROR equ WORK_BASE+57

; A=7: directory text, TAP CODE load, TAP CODE save. No raw-file channels.
legacy_capabilities:
        ld a,7
        or a
        ret

str_copy:
        ld a,(hl)
        ld (de),a
        inc hl
        inc de
        or a
        jr nz,str_copy
        dec de
        ret

legacy_mount:
        push hl
        ld hl,legacy_prefix
        ld de,COMMAND_BUFFER
        call str_copy
        pop hl
        ld b,80
.copy:  ld a,(hl)
        ld (de),a
        inc hl
        inc de
        or a
        jr z,.send
        djnz .copy
        ld a,E_PATH
        scf
        ret
.send:  ld hl,COMMAND_BUFFER
        ld a,1
        jp legacy_execute

legacy_directory:
        ld hl,legacy_dir_cmd
        ld a,1
        jp legacy_execute

; HL=folder name, / for root, .. for parent. Changes Pico's global cwd.
legacy_chdir:
        push hl
        ld hl,legacy_cd_cmd
        ld de,COMMAND_BUFFER
        call str_copy
        pop hl
        ld b,76
.copy:  ld a,(hl)
        ld (de),a
        inc hl
        inc de
        or a
        jr z,.send
        djnz .copy
        ld a,E_PATH
        scf
        ret
.send:  ld hl,COMMAND_BUFFER
        xor a
        jp legacy_execute

; A=expected TAP flag, DE=destination, BC=payload length.
; Caller must know length; TAP protocol does not send a length prefix.
legacy_read_block:
        ld (LEGACY_FLAG),a
        ld (FILE_PTR),de
        ld (FILE_LEFT),bc
        ld e,1
        call legacy_make_pre
        call legacy_preheader
        ret c
        ld a,5
        ld (LEGACY_PHASE),a
        ld a,(LEGACY_FLAG)              ; original LOAD_TS consumes flag echo
        ld d,0
        call tpi_tx
        call tpi_rx
        ld d,a
        ld a,(LEGACY_FLAG)
        cp d
        ld a,0
        jr z,.flag_ok
        ld a,E_SYNC
.flag_ok:
        ld (LEGACY_POST_ERROR),a
        ld hl,(FILE_PTR)
        ld bc,(FILE_LEFT)
        ld a,b
        or c
        jr z,.crc
.read:
        IFDEF FULL_STREAM
        call full_rx_payload
        ELSE
        call tpi_rx
        ld (hl),a
        inc hl
        xor d
        ld d,a
        dec bc
        ld a,b
        or c
        jr nz,.read
        ENDIF
.crc:   call tpi_rx
        xor d
        ld (LEGACY_CRC),a
        ld d,0
        call tpi_tx                      ; XOR residual: zero is correct
        call legacy_wait_ready
        ret c
        xor a
        ld (LEGACY_TEXT),a
        call legacy_reply
        ret c
        ld a,(LEGACY_POST_ERROR)
        or a
        jr nz,.error
        ld a,(LEGACY_CRC)
        or a
        ret z
        ld a,E_CHECKSUM
.error: scf
        ret

legacy_prefix: db 'tpi:',0
legacy_dir_cmd: db 'tpi:dir',0
legacy_cd_cmd: db 'tpi:cd ',0
legacy_close_cmd: db 'tpi:close',0
