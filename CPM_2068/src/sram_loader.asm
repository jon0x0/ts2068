; Cold-boot-only loader copied from DOCK chunk 7 into HOME 8000.
    include "../build/disk-layout.inc"
    org $8000
    jp load_sram_disk
    jp protocol_notice
WORK_BASE equ $c000
    DEFINE LEGACY_PARAMETERS 1
    DEFINE LEGACY_DISCOVERY 1
    DEFINE LEGACY_FAST_SETTLE 1
    include "tspico-layout.inc"
    include "../build/tpi-dual-cpm.asm"
    include "../third_party/tspico-filelib/files_legacy.asm"
    include "../build/sram-api.inc"
; Print diagnostics here while the cold loader is still resident. The BIOS
; only has room for its generic failure notice.
load_sram_disk:
    xor a
    ld (LEGACY_PHASE),a
    ld (LEGACY_BYTE),a
    ld (disk_page),a
    ld (LEGACY_REPLY_BUFFER),a
    ld (CMD_PTR),a
    ld (CMD_PTR+1),a
    call load_sram_disk_impl
    ret nc
    ld (diagnostic_error),a
    ld a,15
    out ($f4),a
    ld hl,diagnostic_clear
    call PUTS
    ld a,($eff3)
    ld hl,diagnostic_protocol
    call diagnostic_hex
    ld a,(diagnostic_stage)
    ld hl,diagnostic_where
    call diagnostic_hex
    ld a,(diagnostic_error)
    ld hl,diagnostic_code
    call diagnostic_hex
    ld a,(LEGACY_PHASE)
    ld hl,diagnostic_phase
    call diagnostic_hex
    ld a,(LEGACY_BYTE)
    ld hl,diagnostic_byte
    call diagnostic_hex
    ld a,(disk_page)
    ld hl,diagnostic_page
    call diagnostic_hex
    ld hl,RX_BUFFER
    ld de,diagnostic_header_bytes
    ld b,10
.header:
    push bc
    push hl
    ld a,(hl)
    ld h,d
    ld l,e
    call diagnostic_hex
    inc hl
    inc hl
    ld d,h
    ld e,l
    pop hl
    inc hl
    pop bc
    djnz .header
    ld a,(LEGACY_FUNCTION)
    ld hl,diagnostic_function
    call diagnostic_hex
    ld a,(REPLY_STATUS)
    ld hl,diagnostic_status
    call diagnostic_hex
    ld hl,diagnostic_message
    call PUTS
    ld a,(LEGACY_TADDR)
    ld hl,diagnostic_direction
    call diagnostic_hex
    ld hl,diagnostic_command_label
    call PUTS
    ld hl,(CMD_PTR)
    ld a,h
    or l
    jr z,.no_command
    call diagnostic_text
.no_command:
    ld hl,diagnostic_reply_label
    call PUTS
    ld hl,LEGACY_REPLY_BUFFER
    call diagnostic_text
    ld hl,diagnostic_newline
    call PUTS
    ld hl,diagnostic_header_label
    call PUTS
    ld a,(diagnostic_error)
    cp E_TIMEOUT
    jr z,.skip_info
    ld a,($eff3)
    or a
    jr z,.no_info
    xor a
    ld (PMR1),a
    ld (PMR1+1),a
    ld (PMR2),a
    ld (PMR2+1),a
    ld hl,diagnostic_info_command
    call legacy_execute
    ld (diagnostic_info_status),a
    ld hl,diagnostic_info_label
    call PUTS
    ld a,(diagnostic_info_status)
    ld hl,diagnostic_info_code
    call diagnostic_hex
    ld hl,diagnostic_info_result
    call PUTS
    ld hl,LEGACY_REPLY_BUFFER
    ld de,diagnostic_info_buffer
    ld b,192
.info_copy:
    ld a,(hl)
    or a
    jr z,.info_end
    ld (de),a
    inc hl
    inc de
    djnz .info_copy
.info_end:
    xor a
    ld (de),a
    ld hl,diagnostic_info_buffer
    call PUTS
    ld hl,diagnostic_newline
    call PUTS
    jr .no_info
.skip_info:
    ld hl,diagnostic_timeout
    call PUTS
.no_info:
    scf
    ret
; Bound strings even if a transport failed before terminating its reply.
diagnostic_text:
    ld de,diagnostic_buffer
    ld b,89
.copy:
    ld a,(hl)
    or a
    jr z,.end
    ld (de),a
    inc hl
    inc de
    djnz .copy
.end:
    xor a
    ld (de),a
    ld hl,diagnostic_buffer
    jp PUTS
diagnostic_command_label: db 'Command (LOAD=01 / SAVE=00): '
diagnostic_direction: db '00',13,10,0
diagnostic_reply_label: db 13,10,'Reply: ',0
diagnostic_newline: db 13,10,0
diagnostic_clear: db 12,0
diagnostic_timeout: db 'Transport timed out; power-cycle before retrying.',13,10,0
diagnostic_info_command: db 'tpi:getinfo',0
diagnostic_info_label: db 'GETINFO (read-only)',13,10,0
diagnostic_info_result: db 'query status='
diagnostic_info_code: db '00',13,10,0
diagnostic_info_status: db 0
diagnostic_info_buffer: ds 193
diagnostic_header_label: db 'Header: '
diagnostic_header_bytes: db '00 00 00 00 00 00 00 00 00 00',13,10,'Function='
diagnostic_function: db '00',' status='
diagnostic_status: db '00',13,10,0
diagnostic_buffer: ds 90
diagnostic_hex:
    push af
    rrca
    rrca
    rrca
    rrca
    call diagnostic_digit
    ld (hl),a
    inc hl
    pop af
    call diagnostic_digit
    ld (hl),a
    ret
diagnostic_digit:
    and 15
    add a,'0'
    cp '9'+1
    ret c
    add a,7
    ret
diagnostic_message: db 'RAMDisk diagnostic (hex): protocol='
diagnostic_protocol: db '00',' stage='
diagnostic_where: db '00',13,10,'error='
diagnostic_code: db '00',' phase='
diagnostic_phase: db '00',' token='
diagnostic_byte: db '00',' page='
diagnostic_page: db '00',13,10,0
diagnostic_error: db 0
diagnostic_stage: db 0
load_sram_disk_impl:
    xor a
    ld ($eff6),a
    ld (load_mode),a
    ld (check_pages),a
    ld hl,0
    ld (PMR1),hl
    ld (PMR2),hl
    ld a,1
    ld ($eff4),a
    call detect_protocol
    ret c
    IF BUILD_DUAL
    ld a,($eff3)
    cp 2
    jr nz,.not_modern
    call modern_choice
    ret c
.not_modern:
    ld a,(service_ram)
    or a
    jp nz,load_service_ram
    ENDIF
    ld hl,loading_message
    call PUTS
    ld a,10
    ld ($eff1),a
    xor a
    out ($f4),a
    ld (disk_page),a
    ld (volume_index),a
    ld a,'0'
    ld (volume_digit),a
    ld (page_name+3),a
    ld (page_name+4),a
    ld a,2
    ld (diagnostic_stage),a
    ld hl,root_directory
    call legacy_chdir
    ret c
    ld a,3
    ld (diagnostic_stage),a
    ld hl,cpm_directory
    call legacy_chdir
    ret c
    call try_saved
    ret c
    or a
    ret nz
    call mount_volume
    ret c
    jp load_page
; Complete a harmless CD / transaction to leave the FIFO at a command
; boundary. A modern MID is required before ever writing the SYNC port.
detect_protocol:
    push af
    ld a,1
    ld (diagnostic_stage),a
    pop af
    xor a
    ld ($eff3),a
    ld hl,detect_header
    ld b,10
    ld d,0
.send:
    ld a,(hl)
    inc hl
    call tpi_tx
    djnz .send
.ack_start:
    ld bc,0
.ack:
    call tpi_rx
    cp 1
    jr z,.ack_ok
    dec bc
    ld a,b
    or c
    jr nz,.ack
    jp loader_error
.ack_ok:
    ld bc,0
.ready:
    in a,($0f)
    cp $f7
    jr z,.modern
    cp $40
    jr z,.legacy
    dec bc
    ld a,b
    or c
    jr nz,.ready
    jp loader_error
.legacy:
    ld a,1
    ld ($eff3),a
    ld d,0
    ld hl,detect_body
    ld b,12
.body:
    ld a,(hl)
    inc hl
    call tpi_tx
    djnz .body
    call legacy_wait_ready
    ret c
    xor a
    ld (LEGACY_TEXT),a
    jp legacy_reply
.modern:
    ld a,2
    ld ($eff3),a
    ; MID belongs to our validated probe header, so abort it directly.
    ; Waiting for IDLE here would wait for the command body we never send.
    xor a
    out ($0f),a
    call dual_ready
    ret c
    call tpi_rx
    cp 1
    ret z
    jp loader_error
detect_header: db $42,0,$ff,0,0,0,0,8,0,$b5
detect_body: db $44,8,0,'tpi:cd /',$44^8^'t'^'p'^'i'^':'^'c'^'d'^' '^'/'
protocol_notice:
    ld a,($eff3)
    cp 2
    ld hl,notice_legacy
    jr nz,.print
    ld hl,notice_modern
.print:
    call PUTS
    ld a,($eff6)
    cp 1
    ld hl,notice_chunks
    jr z,.source
    cp 2
    ld hl,notice_single
    jr nz,.reminder
.source:
    call PUTS
.reminder:
    ld hl,notice_save
    jp PUTS
notice_legacy: db 'Legacy FIFO protocol (1.00 compatible)',13,10,0
notice_modern: db 'Modern protocol; RAMDisk mode',13,10,0
notice_save: db 'RAMDisk: run TPSAVE before power off!',13,10,0
notice_chunks: db 'Restored saved disk chunks directly.',13,10,0
notice_single: db 'Restored /CPM/SAVE/CPMRAM.TAP.',13,10,0
    IF BUILD_DUAL
modern_choice:
    xor a
    ld (service_ram),a
    ld (PMR1),a
    ld (PMR1+1),a
    ld (PMR2),a
    ld (PMR2+1),a
    ld hl,cap_command
    call legacy_command
    jp c,.fallback
    ld de,cap_data
    ld b,8
    call service_packet
    jp c,.fallback
    ld hl,cap_data
    ld de,cap_prefix
    ld b,3
.prefix:
    ld a,(de)
    cp (hl)
    jp nz,.fallback
    inc hl
    inc de
    djnz .prefix
    ld a,(hl)
    cp '1'
    jr z,.image
    cp 'D'
    jp nz,.fallback
    ld a,(cap_data+4)
    cp 2
    jp nz,.fallback
    ld a,(cap_data+7)
    cp 10
    jp nz,.fallback
    jr .common
.image:
    ld a,(cap_data+4)
    cp 1
    jp nz,.fallback
.common:
    ld a,(cap_data+5)
    cp 128
    jp nz,.fallback
    ld a,(cap_data+6)
    or a
    jp nz,.fallback
    ld a,(cap_data+7)
    cp 5
    jr z,.choose
    cp 10
    jp nz,.fallback
.choose:
    ld ($eff1),a
    ld hl,choice_message
    call PUTS
.key:
    call $e609
    and $df
    cp 'L'
    jr z,.saved
    cp 'R'
    jr z,.ram
    cp 13
    jr nz,.key
    ld a,3
    out ($f4),a
    jp $5b03
.ram:
    ld a,1
    ld (service_ram),a
    or a
    ret
.saved:
    xor a
    ld (service_ram),a
    ret
.fallback:
    ld hl,fallback_message
    call PUTS
    or a
    ret
service_packet:
    call tpi_rx
    cp 1
    jr nz,.bad
    call tpi_rx
    cp b
    jr nz,.bad
    ld c,0
.data:
    call tpi_rx
    ld (de),a
    inc de
    xor c
    ld c,a
    djnz .data
    call tpi_rx
    cp c
    ret z
.bad:
    scf
    ret
load_service_ram:
    ld hl,loading_message
    call PUTS
    xor a
    ld (disk_page),a
    ld hl,0
    ld (service_lba),hl
.page:
    call load_progress
    ld hl,$a000
    ld (service_dest),hl
    ld a,64
    ld (service_left),a
.sector:
    ld hl,(service_lba)
    ld (PMR1),hl
    ld hl,read_command
    call legacy_command
    ret c
    ld de,(service_dest)
    ld b,128
    call service_packet
    ret c
    ld (service_dest),de
    ld hl,(service_lba)
    inc hl
    ld (service_lba),hl
    ld hl,service_left
    dec (hl)
    jr nz,.sector
    ld a,8
    ld (diagnostic_stage),a
    ld a,(disk_page)
    call SRAM_INSTALL_PAGE
    ret c
    xor a
    out ($f4),a
    ld hl,disk_page
    inc (hl)
    ld a,($eff1)
    add a,a
    add a,a
    cp (hl)
    jr nz,.page
    jp loader_done
cap_command: db 'tpi:.cpmcap',0
read_command: db 'tpi:.cpmrd',0
cap_prefix: db 'CPM'
cap_data: ds 8
service_ram: db 0
service_lba: dw 0
service_dest: dw 0
service_left: db 0
choice_message: db 'Modern protocol + disk service.',13,10,'ENTER: persistent SD; R: copy disk into RAMDisk',13,10,'L: reload saved RAMDisk',13,10,0
fallback_message: db 'Modern protocol; no usable disk service.',13,10,'Loading saved RAMDisk or preload TAPs.',13,10,0
    ENDIF
; New saves reload directly. Old untyped chunk sets need only a geometry
; choice on the TS2068, never a PC repack. A present but invalid descriptor
; must not silently fall back to an older factory disk.
try_saved:
    push af
    ld a,4
    ld (diagnostic_stage),a
    pop af
    xor a
    ld (has_descriptor),a
    ld hl,save_directory
    call legacy_chdir
    jr nc,.opened
    cp 3
    jp nz,saved_error
    jp no_saved
.opened:
    ld a,($eff3)
    cp 1
    jr nz,.probe_state
    call saved_directory_snapshot
    ret c
.probe_state:
    ld hl,state_file
    ld de,saved_descriptor
    ld bc,128
    call saved_descriptor_load
    jr nc,.descriptor
    call saved_file_missing
    jp nz,saved_error
    jr .single
.descriptor:
    ld a,1
    ld (has_descriptor),a
.single:
    ld a,($eff3)
    cp 2
    jp nz,load_saved_chunks
    ld hl,saved_image_name
    call legacy_mount
    jr nc,.found_single
    call saved_file_missing
    jp nz,saved_error
    jp load_saved_chunks
.found_single:
    ld a,(has_descriptor)
    or a
    jr z,.use_single
    ld hl,choose_saved_message
    call PUTS
.choice:
    call $e609
    and $df
    cp 'C'
    jp z,load_saved_chunks
    cp 'T'
    jr nz,.choice
.use_single:
    ld a,2
    ld (load_mode),a
    ld ($eff6),a
    call mount_volume
    ret c
    jp load_saved_pages
no_saved:
    ; Restore the factory preload's directory after probing SAVE.
    ld hl,root_directory
    call legacy_chdir
    ret c
    ld hl,cpm_directory
    call legacy_chdir
    ret c
    xor a
    ret
 ; Directory capability evidence avoids ambiguous missing-name status 05.
saved_descriptor_load:
    ld a,($eff3)
    cp 1
    jp nz,f_load
    ld a,(saved_presence)
    bit 0,a
    jp nz,f_load
    xor a
    scf
    ret
saved_chunk_mount:
    ld a,($eff3)
    cp 1
    jp nz,legacy_mount
    ld a,(saved_presence)
    bit 1,a
    jp nz,legacy_mount
    xor a
    scf
    ret
saved_directory_snapshot:
    ld a,9
    ld (diagnostic_stage),a
    xor a
    ld (saved_presence),a
    call legacy_directory
    ret c
    ld a,(LEGACY_FUNCTION)
    cp $81
    jr z,.text
    cp $86
    jp nz,loader_error
.text:
    ld de,directory_marker
    call saved_name_present
    jp nz,loader_error
    ld de,state_file
    call saved_name_present
    jr nz,.chunks
    ld a,1
    ld (saved_presence),a
.chunks:
    ld de,chunk_file
    call saved_name_present
    jr nz,.done
    ld a,(saved_presence)
    or 2
    ld (saved_presence),a
.done:
    ld a,4
    ld (diagnostic_stage),a
    or a
    ret
; Search an exact, case-insensitive space-delimited name in a complete list.
; Previous byte must be whitespace, so paths and <directory names> cannot match.
; The bounded transport refuses truncated lists instead of asserting absence.
saved_name_present:
    ld hl,LEGACY_REPLY_BUFFER
    ld c,32
.scan:
    ld a,(hl)
    or a
    jr z,.absent
    ld a,c
    cp 33
    jr nc,.next
    push hl
    push de
.match:
    ld a,(de)
    or a
    jr z,.end_name
    ld b,a
    ld a,(hl)
    cp 'a'
    jr c,.upper
    cp 'z'+1
    jr nc,.upper
    and $df
.upper:
    cp b
    jr nz,.miss
    inc hl
    inc de
    jr .match
.end_name:
    ld a,(hl)
    cp 33
    jr nc,.miss
    pop de
    pop hl
    xor a
    ret
.miss:
    pop de
    pop hl
.next:
    ld c,(hl)
    inc hl
    jr .scan
.absent:
    ld a,1
    or a
    ret
saved_presence: db 0
directory_marker: db 'FILE NAME',0
; Z only for a missing optional filename, never unknown command 05.
; Original PROCESS_CMD uses status 00 for a missing named LOAD (10045366).
; Modern service/transport and older compatible implementations use 03.
saved_file_missing:
    cp 3
    ret z
    or a
    ret nz
    ld a,($eff3)
    cp 1
    ret z
    ld a,1
    or a
    ld a,0
    ret
saved_error:
    scf
    ret
load_saved_chunks:
    ld a,(has_descriptor)
    or a
    jr z,untyped_chunks
    ld hl,saved_descriptor
    ld de,saved_magic
    ld b,8
.magic:
    ld a,(de)
    cp (hl)
    jp nz,loader_error
    inc hl
    inc de
    djnz .magic
    ld a,(hl)
    cp 1
    jp nz,loader_error
    inc hl
    ld a,(hl)
    call saved_geometry
    ret c
    ld a,(saved_descriptor+10)
    ld hl,page_count
    cp (hl)
    jp nz,loader_error
    ld a,1
    ld (check_pages),a
    jr chunks_ready
untyped_chunks:
    ld hl,chunk_file
    call saved_chunk_mount
    jr nc,.found
    call saved_file_missing
    jp nz,saved_error
    jp no_saved
.found:
    ld hl,old_chunks_message
    call PUTS
.choice:
    call $e609
    cp '1'
    ld b,5
    jr z,.size
    cp '2'
    jr nz,.choice
    ld b,10
.size:
    ld a,b
    call saved_geometry
    ret c
chunks_ready:
    ld a,1
    ld (load_mode),a
    ld ($eff6),a
load_saved_pages:
    call load_page
    ret c
    ld a,1
    or a
    ret
saved_geometry:
    cp 5
    jr z,.valid
    cp 10
    jp nz,loader_error
.valid:
    ld ($eff1),a
    add a,a
    add a,a
    ld (page_count),a
    or a
    ret
mount_volume:
    push af
    ld a,5
    ld (diagnostic_stage),a
    pop af
    ld hl,image_name
    ld a,(load_mode)
    cp 2
    jr nz,.mount
    ld hl,saved_image_name
.mount:
    ; Disk-pair commands use a short resident guard. At a volume transition,
    ; allow the cold transport housekeeping interval before another SD mount.
    call legacy_slow_settle
    call legacy_mount
    ret c
    call read_header
    ret c
    ld hl,(NAME_BUFFER+11)
    ld de,128
    or a
    sbc hl,de
    jp nz,loader_error
    ld de,$a000
    ld bc,128
    ld a,$ff
    call legacy_read_block
    ret c
    ld hl,$a000
    ld de,magic
    ld b,9
check_magic:
    ld a,(de)
    cp (hl)
    jp nz,loader_error
    inc hl
    inc de
    djnz check_magic
    ld a,(hl)
    cp 5
    jr z,loader_single
    cp 10
    jp nz,loader_error
loader_single:
    ld ($eff1),a
    ld c,a
    add a,a
    add a,a
    ld (page_count),a
    inc hl
    cp (hl)
    jp nz,loader_error
    inc hl
    ; block-size metadata is 16 for 160K, 32 for 320K.
    ld a,c
    cp 5
    ld a,16
    jr z,loader_block_size
    ld a,32
loader_block_size:
    cp (hl)
    jp nz,loader_error
    inc hl
    ld a,(load_mode)
    cp 2
    ret z
    ld a,(volume_index)
    cp (hl)
    jp nz,loader_error
    inc hl
    ld a,(hl)
    ld c,a
    ld a,($eff1)
    cp 5
    ld a,4
    jr z,loader_volume_count
    ld a,8
loader_volume_count:
    cp c
    jp nz,loader_error
    ld a,(volume_index)
    or a
    jr nz,check_image_identity
    ld hl,$a010
    ld de,image_identity
    ld bc,32
    ldir
    jr volume_valid
check_image_identity:
    ld hl,$a010
    ld de,image_identity
    ld b,32
identity_byte:
    ld a,(de)
    cp (hl)
    jp nz,loader_error
    inc hl
    inc de
    djnz identity_byte
volume_valid:
    ld a,5
    ld (volume_left),a
    xor a
    ret
load_page:
    call load_progress
    push af
    ld a,6
    ld (diagnostic_stage),a
    pop af
    ld a,(load_mode)
    cp 1
    jr nz,.header
    ld hl,page_name
    ld de,chunk_file
    ld bc,5
    ldir
    ld hl,chunk_file
    call legacy_mount
    ret c
.header:
    call read_header
    ret c
    ld hl,(NAME_BUFFER+11)
    ld de,8192
    or a
    sbc hl,de
    jp nz,loader_error
    ld hl,NAME_BUFFER+1
    ld de,page_name
    ld b,5
check_name:
    ld a,(de)
    cp (hl)
    jp nz,loader_error
    inc hl
    inc de
    djnz check_name
    ld de,$a000
    ld bc,8192
    ld a,$ff
    call legacy_read_block
    ret c
    ld a,(check_pages)
    or a
    jr z,.install
    ld hl,$a000
    ld bc,8192
    call page_checksum
    ld a,(disk_page)
    add a,a
    ld l,a
    ld h,0
    ld bc,saved_descriptor+12
    add hl,bc
    ld a,(hl)
    cp e
    jp nz,loader_error
    inc hl
    ld a,(hl)
    cp d
    jp nz,loader_error
.install:
    ld a,(disk_page)
    call SRAM_INSTALL_PAGE
    ret c
    ; A restored slot maps the low TPA; loader work is all in HOME 8000+.
    xor a
    out ($f4),a
    ld hl,page_name+4
    inc (hl)
    ld a,(hl)
    cp ':'
    jr nz,page_name_ready
    ld (hl),'0'
    dec hl
    inc (hl)
page_name_ready:
    ld hl,disk_page
    inc (hl)
    ld a,(hl)
    ld hl,page_count
    cp (hl)
    jp nc,loader_done
    ld a,(load_mode)
    or a
    jp nz,load_page
    ld hl,volume_left
    dec (hl)
    jp nz,load_page
    ld hl,volume_index
    inc (hl)
    ld hl,volume_digit
    inc (hl)
    call mount_volume
    ret c
    jp load_page
load_progress:
    ld a,(disk_page)
    inc a
    ld hl,progress_current
    call progress_decimal
    ld a,($eff1)
    add a,a
    add a,a
    ld hl,progress_total
    call progress_decimal
    ld hl,progress_message
    jp PUTS
progress_decimal:
    ld b,'0'
.tens:
    cp 10
    jr c,.digits
    sub 10
    inc b
    jr .tens
.digits:
    ld (hl),b
    inc hl
    add a,'0'
    ld (hl),a
    ret
loading_message: db 'Loading disk image to RAMDisk',13,10,0
progress_message: db 13,'Loading block '
progress_current: db '00',' of '
progress_total: db '40','   ',13,0
loader_done:
    ld a,15
    out ($f4),a
    xor a
    ret
read_header:
    push af
    ld a,7
    ld (diagnostic_stage),a
    pop af
    xor a
    ld de,NAME_BUFFER
    ld bc,17
    call legacy_read_block
    ret c
    ld a,(NAME_BUFFER)
    cp 3
    ret z
loader_error:
    ld a,1
    scf
    ret
root_directory: db '/',0
cpm_directory: db 'CPM',0
image_name: db 'CPM3200'
volume_digit: db '0','.TAP',0
magic: db 'CPMRAM1',0,0,10,40,32
page_name: db 'CPM00'
disk_page: db 0
volume_index: db 0
volume_left: db 0
image_identity: ds 32
page_count: db 40
load_mode: db 0
check_pages: db 0
has_descriptor: db 0
save_directory: db 'SAVE',0
state_file: db 'CPMSTATE.TAP',0
saved_image_name: db 'CPMRAM.TAP',0
chunk_file: db 'CPM00.TAP',0
saved_magic: db 'CPMSAV1',0
choose_saved_message: db 'Saved TAP and saved chunks found. T=TAP, C=chunks: ',0
old_chunks_message: db 'Saved chunks found (old format). 1=160K, 2=320K: ',0
saved_descriptor: ds 128
    include "page_checksum.asm"
    assert $ <= $a000
