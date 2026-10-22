; Modern APPEND writes one multi-CODE disk TAP; stock firmware writes chunks.
; Both formats reload directly; the split descriptor records geometry/checksums.
    org $100
    jp save_disk
WORK_BASE equ $c000
    DEFINE SAVE_APPEND 1
    include "tspico-layout.inc"
    include "../build/tpi-dual-cpm.asm"
    include "../third_party/tspico-filelib/files_legacy.asm"
    include "../build/sram-api.inc"
save_disk:
    ld a,($eff4)
    cp 1
    jr z,save_ram_disk
    ld de,not_ram
    ld c,9
    jp 5
save_ram_disk:
    xor a
    ld (force_split),a
    ld a,($80)
    ld b,a
    or a
    jr z,args_ok
    ld hl,$81
.spaces:
    ld a,(hl)
    cp ' '
    jr nz,.word
    inc hl
    djnz .spaces
    jr args_ok
.word:
    ld a,b
    cp 5
    jr c,bad_arguments
    ld de,split_word
    ld c,5
.match:
    ld a,(de)
    cp (hl)
    jr nz,bad_arguments
    inc hl
    inc de
    dec b
    dec c
    jr nz,.match
    ld a,1
    ld (force_split),a
    ld a,b
    or a
    jr z,args_ok
.trailing:
    ld a,(hl)
    cp ' '
    jr nz,bad_arguments
    inc hl
    djnz .trailing
    jr args_ok
bad_arguments:
    ld de,usage
    ld c,9
    jp 5
args_ok:
    ld a,'0'
    ld (page_name+3),a
    ld (page_name+4),a
    ld de,warning
    ld c,9
    call 5
    ld c,1
    call 5
    and $df
    cp 'Y'
    ret nz
    xor a
    ld (save_append),a
    ; Use a dedicated existing SD directory; never scatter exports over root.
    ld hl,root_directory
    call legacy_chdir
    jp c,save_error
    ld hl,cpm_directory
    call legacy_chdir
    jp c,save_error
    ld hl,save_directory
    call legacy_chdir
    jp c,save_error
    ld a,(force_split)
    or a
    jr nz,legacy_split_save
    ld a,($eff3)
    cp 2
    jp z,save_single
legacy_split_save:
    ; Invalidate the descriptor before replacing any disk page.
    xor a
    ld (saved_state),a
    ld a,($eff1)
    ld (saved_geometry),a
    add a,a
    add a,a
    ld (saved_pages),a
    call save_descriptor
    jp c,save_error
    xor a
    ld (disk_page),a
save_page:
    ld a,(disk_page)
    call SRAM_FETCH_PAGE
    jp c,save_error
    ld hl,$a000
    ld bc,8192
    call page_checksum
    ld a,(disk_page)
    add a,a
    ld l,a
    ld h,0
    ld bc,saved_checksums
    add hl,bc
    ld (hl),e
    inc hl
    ld (hl),d
    ld hl,page_name
    ld de,$a000
    ld bc,8192
    call f_save
    jp c,save_error
    ld hl,page_name+4
    inc (hl)
    ld a,(hl)
    cp ':'
    jr nz,save_next
    ld (hl),'0'
    dec hl
    inc (hl)
save_next:
    ld hl,disk_page
    inc (hl)
    ld a,(hl)
    ld c,a
    ld a,($eff1)
    add a,a
    add a,a
    cp c
    jr nz,save_page
    ld a,1
    ld (saved_state),a
    call save_descriptor
    jp c,save_error
    ld de,done
    jp save_print
save_descriptor:
    ld hl,state_name
    ld de,saved_descriptor
    ld bc,128
    jp f_save
save_single:
    ; One ordinary TAP, containing metadata and 20/40 CODE page pairs.
    ld a,($eff1)
    ld (single_metadata+9),a
    add a,a
    add a,a
    ld (single_metadata+10),a
    ld a,($eff1)
    cp 5
    ld a,16
    jr z,.block
    ld a,32
.block:
    ld (single_metadata+11),a
    ld hl,single_metadata
    ld de,$a000
    ld bc,128
    ldir
    ld hl,single_name
    ld de,$a000
    ld bc,128
    call f_save
    jp c,save_error
    ld hl,single_file
    call legacy_mount
    jp c,save_error
    ld hl,append_command
    xor a
    call legacy_execute
    jp c,save_error
    ld a,1
    ld (save_append),a
    xor a
    ld (disk_page),a
.page:
    ld a,(disk_page)
    call SRAM_FETCH_PAGE
    jr c,save_error
    ld hl,page_name
    ld de,$a000
    ld bc,8192
    call f_save
    jr c,save_error
    call next_page_name
    ld hl,disk_page
    inc (hl)
    ld a,($eff1)
    add a,a
    add a,a
    cp (hl)
    jr nz,.page
    ld hl,legacy_close_cmd
    xor a
    call legacy_execute
    jr c,save_error
    xor a
    ld (save_append),a
    ld de,single_done
    jr save_print
next_page_name:
    ld hl,page_name+4
    inc (hl)
    ld a,(hl)
    cp ':'
    ret nz
    ld (hl),'0'
    dec hl
    inc (hl)
    ret
save_error:
    xor a
    ld (save_append),a
    ld de,failed
save_print:
    ld c,9
    call 5
    ret
page_name: db 'CPM00',0
disk_page: db 0
root_directory: db '/',0
cpm_directory: db 'CPM',0
save_directory: db 'SAVE',0
warning: db 'Save RAMDisk in /CPM/SAVE?',13,10
    db 'TPSAVE: modern one TAP; legacy reloadable chunks.',13,10
    db 'TPSAVE SPLIT: chunks under either protocol.',13,10
    db 'Existing save will be replaced. Type Y to save: $'
done: db 13,10,'Saved disk chunks. Reload directly; no PC repack needed.',13,10,'$'
single_done: db 13,10,'Saved one disk TAP: /CPM/SAVE/CPMRAM.TAP',13,10,'$'
failed: db 13,10,'SAVE FAILED. Export is incomplete; retain the RAMDisk.',13,10,'$'
not_ram: db 'TPSAVE is for RAMDisk mode. Use CPMDISK SAVE for SD disks.',13,10,'$'
save_append: db 0
force_split: db 0
split_word: db 'SPLIT'
usage: db 'TPSAVE: modern single TAP, legacy reloadable chunks.',13,10,'TPSAVE SPLIT: reloadable chunks for either protocol.',13,10,'$'
single_name: db 'CPMRAM',0
single_file: db 'CPMRAM.TAP',0
append_command: db 'tpi:append on',0
state_name: db 'CPMSTATE',0
single_metadata: db 'CPMRAM1',0,0,10,40,32
    ds 116
saved_descriptor: db 'CPMSAV1',0
saved_state: db 0
saved_geometry: db 10
saved_pages: db 40
    db 0
saved_checksums: ds 80
    ds 36
    include "page_checksum.asm"
    assert $ < $4000
