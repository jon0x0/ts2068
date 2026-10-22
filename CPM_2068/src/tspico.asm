; Resident modern TSPico service. This code and its workspace stay in HOME 7.
    org $f000
    IF BUILD_SD320
    include "disk_geometry.asm"
    ENDIF
WORK_BASE equ $f600
    include "tspico-layout.inc"
    include "../third_party/tspico-filelib/tpi.asm"
    include "../third_party/tspico-filelib/files.asm"
    include "tspico-probe.asm"

; Return A=0 RAM, 1 binary-safe TSPico service, 2 stock read-only image,
; $ff no usable disk. Physical SRAM must already have supplied writable DOCK.
storage_init:
    xor a
    ld (storage_kind),a
    call tsp_probe
    jr c,storage_try_ram
    xor a
    ld (PMR1),a
    ld (PMR1+1),a
    ld (PMR2),a
    ld (PMR2+1),a
    ld hl,cmd_cap
    call tsp_packet
    jr c,storage_stock
    ld a,(packet_length)
    cp 8
    jr nz,storage_stock
    IF BUILD_SD320
    ld a,(RX_BUFFER+7)
    cp 5
    jr nz,storage_cap_normal
    ld a,10
    ld (RX_BUFFER+7),a
storage_cap_normal:
    ENDIF
    ld hl,RX_BUFFER
    ld de,cap_signature
    ld b,8
storage_cap_check:
    ld a,(de)
    cp (hl)
    jr nz,storage_directory_cap
    inc hl
    inc de
    djnz storage_cap_check
    ld a,1
    jr storage_selected
storage_directory_cap:
    IF BUILD_SD320 && BUILD_DIRECTORY = 0
    jp storage_missing
    ELSE
    ld hl,RX_BUFFER
    ld de,directory_signature
    ld b,8
storage_directory_check:
    ld a,(de)
    cp (hl)
    jr nz,storage_stock
    inc hl
    inc de
    djnz storage_directory_check
    ld a,3
    jr storage_selected
    ENDIF
storage_stock:
    IF BUILD_SD320
    ; Ordinary channel seeks are 16-bit and cannot cover a 320KB image.
    ; A geometry-matched binary-safe service is mandatory for this profile.
    jp storage_missing
    ELSE
    ld a,FILE_STREAM
    ld hl,tsp_image_path
    ld de,mode_rb
    call f_open
    jr c,storage_try_ram
    ld a,2
    ld (storage_kind),a
    ld hl,0
    call tsp_disk_read
    jr nz,storage_try_ram
    ; Exact first directory entry signature from our supplied image.
    ld hl,bounce
    ld de,disk_signature
    ld b,12
storage_disk_check:
    ld a,(de)
    cp (hl)
    jr nz,storage_try_ram
    inc hl
    inc de
    djnz storage_disk_check
    ld a,2
    jr storage_selected
    ENDIF
storage_try_ram:
    IF BUILD_SD320
    jp storage_missing
    ELSE
    xor a
    ld (storage_kind),a
    ld hl,0
    ld c,0
    call ram_block_read
    ld hl,bounce
    ld de,disk_signature
    ld b,12
storage_ram_check:
    ld a,(de)
    cp (hl)
    jr nz,storage_missing
    inc hl
    inc de
    djnz storage_ram_check
    xor a
    ENDIF
storage_selected:
    ld (storage_kind),a
    ret
storage_missing:
    ld a,$ff
    ret

    IF BUILD_SD320
mounted_geometry:
    ld hl,cmd_info
    call tsp_packet
    ret c
    ld a,(packet_length)
    cp 8
    jr nz,geometry_error
    ld hl,RX_BUFFER
    ld de,cap_signature
    ld b,7
geometry_check:
    ld a,(de)
    cp (hl)
    jr nz,geometry_error
    inc de
    inc hl
    djnz geometry_check
    ld a,(hl)
    cp 5
    jr z,geometry_valid
    cp 10
    jr nz,geometry_error
geometry_valid:
    call select_geometry
    or a
    ret
geometry_error:
    scf
    ret
cmd_info: db 'tpi:.cpminfo',0
    ENDIF

; Read the channel-style packet into RX_BUFFER. Validate length and checksum.
tsp_packet:
    call tpi_command
    ret c
    call tpi_rx
    cp 1
    jr nz,tsp_packet_error
    call tpi_rx
    cp 129
    jr nc,tsp_packet_error
    or a
    jr z,tsp_packet_error
    ld b,a
    ld (packet_length),a
    ld hl,RX_BUFFER
    ld e,0
tsp_packet_bytes:
    call tpi_rx
    ld (hl),a
    inc hl
    xor e
    ld e,a
    djnz tsp_packet_bytes
    call tpi_rx
    cp e
    ret z
tsp_packet_error:
    scf
    ret

tsp_disk_read:
    IF BUILD_SD320
    ld a,c
    or a
    jp nz,tsp_io_error
    ld a,h
    cp DISK_LBA_HIGH
    jp nc,tsp_io_error
    ENDIF
    ld (PMR1),hl
    ld a,(storage_kind)
    cp 2
    jr z,tsp_stock_read
    ld hl,cmd_rd
    call tsp_packet
    jp c,tsp_io_error
    ld a,(packet_length)
    cp 128
    jp nz,tsp_io_error
    ld hl,RX_BUFFER
    ld de,bounce
    ld bc,128
    ldir
    xor a
    ret
tsp_stock_read:
    ; Stock channels express absolute 16-bit seeks as TAB(position+1).
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    inc hl
    ld a,l
    ld (seek_bytes+1),a
    ld a,h
    ld (seek_bytes+2),a
    ld hl,seek_bytes
    ld a,FILE_STREAM
    ld b,3
    ; Build seek directly: f_write rightly rejects $17 in ordinary data.
    ld (PMR1),a
    xor a
    ld (PMR1+1),a
    ld (PMR2),a
    ld (PMR2+1),a
    ld hl,cmd_write
    ld de,COMMAND_BUFFER
    call str_copy
    ld hl,seek_bytes
    ld b,3
tsp_seek_hex:
    ld a,(hl)
    inc hl
    call hex_byte
    djnz tsp_seek_hex
    xor a
    ld (de),a
    ld hl,COMMAND_BUFFER
    call tpi_execute
    jp c,tsp_io_error
    ld a,FILE_STREAM
    ld b,128
    ld hl,bounce
    call f_read
    jp c,tsp_io_error
    ld a,c
    cp 128
    jp nz,tsp_io_error
    xor a
    ret
tsp_disk_write:
    IF BUILD_SD320
    ld a,c
    or a
    jp nz,tsp_io_error
    ld a,h
    cp DISK_LBA_HIGH
    jp nc,tsp_io_error
    ENDIF
    ld (PMR1),hl
    ld a,(storage_kind)
    cp 1
    jr z,tsp_write_allowed
    cp 3
    jp nz,tsp_io_error
tsp_write_allowed:
    ld hl,cmd_wr0
    ld de,bounce
    call tsp_write_half
    jp c,tsp_io_error
    ld hl,cmd_wr1
    ld de,bounce+64
    call tsp_write_half
    jp c,tsp_io_error
    xor a
    ret
tsp_io_error:
    ld a,1
    or a
    ret
tsp_write_half:
    push de
    ld de,COMMAND_BUFFER
    call str_copy
    pop hl
    ld b,64
tsp_write_hex:
    ld a,(hl)
    inc hl
    call hex_byte
    djnz tsp_write_hex
    xor a
    ld (de),a
    ld hl,COMMAND_BUFFER
    jp tpi_execute

storage_kind: db 0
packet_length: db 0
seek_bytes: db $17,0,0
cmd_cap: db 'tpi:.cpmcap',0
cmd_rd: db 'tpi:.cpmrd',0
cmd_wr0: db 'tpi:.cpmw0 ',0
cmd_wr1: db 'tpi:.cpmw1 ',0
cap_signature: db 'CPM1',1,128
    dw DISK_TRACKS*16
    IF BUILD_DIRECTORY
directory_signature: db 'CPMD',2,128,0,10
    ELSE
directory_signature: db 'CPMD',1,128,0,8
    ENDIF
tsp_image_path: db '/CPM/DRIVEA.IMG',0
    IF BUILD_SD320
modern_notice: db 'Modern protocol; persistent SD disk',13,10,0
    ENDIF
disk_signature: db 0,'HELLO   COM'
    assert $ <= $f600
