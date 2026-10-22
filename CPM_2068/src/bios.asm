    include "../build/disk-layout.inc"
    org $e600
    jp cold
    jp warm
    jp const
    jp conin
    jp conout
    jp dummy
    jp dummy
    jp reader
    jp home
    jp seldsk
    jp settrk
    jp setsec
    jp setdma
    jp read
    jp write
    jp listst
    jp sectran
cold:
    ld sp,$ff00
    ld a,15
    out ($f4),a
    ld a,$3e
    out ($ff),a
    xor a
    ld (4),a
    ld (3),a
    IF BUILD_OLIGER
    ld a,(8) ; release Board B without fetching its activation addresses
    ENDIF
    call video_init
    call cls
    ld hl,banner
    call puts
    call video_notice
    IF BUILD_BANKED
    ld hl,msg_loading
    call puts
    call $8000
    jr nc,sram_boot_ready
    ld a,15
    out ($f4),a
    ld hl,msg_sram_error
    call puts
sram_boot_failed:
    halt
    jr sram_boot_failed
sram_boot_ready:
    call cls
    ld hl,msg_sram
    call puts
    call video_notice
    call $8003
    jp warm
    ENDIF
    IF BUILD_TSPICO
    call storage_init
    cp $ff
    jr z,no_disk
    or a
    ld hl,msg_ram
    jr z,disk_ready
    cp 1
    ld hl,msg_tspico
    jr z,disk_ready
    cp 3
    jr nz,disk_readonly
    IF BUILD_DIRECTORY = 0
    ld hl,sd_dpb
    ld (dph+10),hl
    ld a,128
    ld (disk_tracks),a
    ENDIF
    ld hl,msg_directory
    jr disk_ready
disk_readonly:
    ld hl,msg_readonly
disk_ready:
    call puts
    IF BUILD_SD320
    ld hl,modern_notice
    call puts
    ENDIF
    jr warm
no_disk:
    ld hl,msg_no_disk
    call puts
    halt
    jr no_disk
    ELSE
    IF BUILD_OLIGER
ol_boot_retry:
    call oliger_init
    jr c,ol_boot_error
    or a
    jr nz,ol_boot_error
    ld hl,0
    ld c,0
    call oliger_read
    or a
    jr nz,ol_boot_error
    ld hl,msg_oliger
    ELSE
    ld hl,msg_ram
    ENDIF
    call puts
    ENDIF
    IF BUILD_OLIGER
    jr warm
ol_boot_error:
    ld hl,msg_ol_error
    call puts
    call conin
    jr ol_boot_retry
    ENDIF
warm:
    di
    ld sp,$ff00
    IF BUILD_SD320
    call mounted_geometry
    jp c,no_disk
    ENDIF
    IF BUILD_BANKED
    ld a,($eff1)
    call select_geometry
    ENDIF
    IF BUILD_OLIGER
    call ol_invalidate
    ENDIF
    ; Restore CCP + BDOS from immutable cartridge system pages.
    ld a,$2f
    out ($f4),a
    ld hl,$a000
    ld de,$d000
    ld bc,$1600
    ldir
    ld a,15
    out ($f4),a
    ld a,$c3
    ld (0),a
    ld (5),a
    ld hl,$e603
    ld (1),hl
    ld hl,$d806
    ld (6),hl
    ld bc,$80
    call setdma
    ld a,($eff0)
    or a
    jr z,start_ccp
    xor a
    ld ($eff0),a
    ld hl,autocmd
    ld de,$d007
    ld bc,6
    ldir
start_ccp:
    IF BUILD_OLIGER
    ld a,(4)
    and 15
    ld c,a
    ELSE
    ld c,0
    ENDIF
    jp $d000
dummy:
    ret
reader:
    ld a,$1a
    ret
listst:
    xor a
    ret
home:
    IF BUILD_OLIGER
    call ol_invalidate
    ENDIF
    ld bc,0
settrk:
    ld (track),bc
    ret
setsec:
    ld (sector),bc
    ret
setdma:
    ld (dma),bc
    ret
seldsk:
    ld hl,0
    ld a,c
    IF BUILD_OLIGER
    cp 2
    ret nc
    inc a
    ld (ol_drive),a
    call ol_invalidate
    ld hl,dph
    ld a,c
    or a
    ret z
    ld hl,dph_b
    ret
    ELSE
    or a
    ret nz
    ld hl,dph
    ret
    ENDIF
sectran:
    ld h,b
    ld l,c
    ret
read:
    call logical_sector
    ret nz
    ld c,0
    call block_read
    or a
    ret nz
    ld hl,bounce
    ld de,(dma)
    ld bc,128
    ldir
    xor a
    ret
write:
    ld a,c
    ld (write_mode),a
    ld hl,(dma)
    ld de,bounce
    ld bc,128
    ldir
    call logical_sector
    ret nz
    ld a,(write_mode)
    ld b,a
    ld c,0
    jp block_write
; BIOS geometry/DMA glue is independent of the physical storage backend.
logical_sector:
    ld hl,(track)
    ld a,h
    or a
    jr nz,ioerror
    ld a,(disk_tracks)
    cp l
    jr z,ioerror
    jr c,ioerror
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,(sector)
    ld a,d
    or a
    jr nz,ioerror
    ld a,e
    cp 16
    jr nc,ioerror
    add hl,de
    xor a
    ret
ioerror:
    ld a,1
    or a
    ret
block_read:
    IF BUILD_SD320
    jp tsp_disk_read
    ELSE
    IF BUILD_BANKED
    jp sram_read
    ELSE
    IF BUILD_TSPICO
    ld a,(storage_kind)
    or a
    jp nz,tsp_disk_read
    ENDIF
    IF BUILD_OLIGER
    jp oliger_read
    ELSE
    jp ram_block_read
    ENDIF
    ENDIF
    ENDIF
block_write:
    IF BUILD_SD320
    jp tsp_disk_write
    ELSE
    IF BUILD_BANKED
    jp sram_write
    ELSE
    IF BUILD_TSPICO
    ld a,(storage_kind)
    or a
    jp nz,tsp_disk_write
    ENDIF
    IF BUILD_OLIGER
    jp oliger_write
    ELSE
    jp ram_block_write
    ENDIF
    ENDIF
    ENDIF
    IF BUILD_BANKED = 0 && BUILD_SD320 = 0
    include "blockdev_ramdisk.asm"
    ENDIF
dph:
    dw 0,0,0,0,dirbuf,dpb,0,alv
    IF BUILD_OLIGER
dph_b:
    dw 0,0,0,0,dirbuf,dpb,0,alv_b
alv_b: ds 32
    ENDIF
dpb:
    dw 16
    db DISK_BSH,DISK_BLM,DISK_EXM
    dw DISK_BLOCKS-1,DISK_DIRECTORY_ENTRIES-1
    IF BUILD_OLIGER
    db DISK_AL0,0
    ELSE
    db $c0,0
    ENDIF
    dw 0,0
sd_dpb:
    dw 16
    db 3,7,0
    dw 255,127
    db $f0,0
    dw 0,0
disk_tracks: db DISK_TRACKS
track: dw 0
sector: dw 0
dma: dw $80
write_mode: db 0
autocmd: db 5,"HELLO"
banner: db "TS2068 CP/M 2.2",13,10,"DOCK RAM OK",13,10,0
    IF BUILD_OLIGER
msg_ol_error: db 'Insert CP/M disk in JLO drive 0.',13,10,'Press a key to retry.',13,10,0
msg_oliger: db 'A: Oliger disk',13,10,0
    ENDIF
msg_ram: db 'A: 48K RAM disk',13,10,0
    IF BUILD_BANKED
msg_loading: db 'Detecting TSPico / preparing disk...',13,10,0
msg_sram: db 'A: TSPico RAMDisk',13,10,0
msg_sram_error: db 'RAMDisk load/verify failed. Do not boot.',13,10,0
    ENDIF
    IF BUILD_TSPICO
msg_tspico: db 'A: TSPico SD image R/W',13,10,0
    IF BUILD_DIRECTORY
msg_directory: db 'A: TSPico directory 320K',13,10,0
    ELSE
msg_directory: db 'A: TSPico directory 256K',13,10,0
    ENDIF
msg_readonly: db 'A: TSPico SD image READ ONLY',13,10,0
msg_no_disk: db 'No usable disk',13,10,0
    ENDIF
    include "console.asm"
alv: ds 32
dirbuf: ds 128
bounce: ds 128
    assert $ < $eff0
    ; Versioned console descriptor for transient utilities. EFF5 is active
    ; renderer; EFF7 is capability, so choosing 64 does not forget PicoVideo.
    defs $eff8-$,0
    dw columns
    db 'COLS'
    IF BUILD_BANKED
    defs $f000-$,0
    include "sram_disk.asm"
    ENDIF
    IF BUILD_TSPICO
    defs $f000-$,0
    include "tspico.asm"
    ENDIF

    IF BUILD_OLIGER
    defs $f000-$,0
    include "blockdev_oliger.asm"
    ENDIF
