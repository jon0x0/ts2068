        DEFINE VIDEO_RAM 1
        DEFINE LEGACY_VIDEO 1
        DEFINE LEGACY_VIDEO2 1
        DEFINE FULL_STREAM 1
        DEFINE WORK_BASE $fa00
        include "layout.inc"
TICK equ $fe00
PLAY equ $fe02
BUSY equ $fe03
STOP equ $fe04
PAUSED equ $fe05
KEY_OLD equ $fe06
IRQ_ALLOW equ $fe07
TARGET equ $fe08
FRAME_PTR equ $fe0a
INDEX_END equ $fe0c
SHOWN equ $fe0e
LOOPS equ $fe10
LATE equ $fe12
REGION equ $fe14
REQUEST equ $fe15
BANK_CMD equ $fe16
BANK_TYPE equ $fe17
CACHE_IDS equ $fe18
FETCH_ACTIVE equ $fe1b
FETCH_PAGE equ $fe1c
FETCH_SLOT equ $fe1d
FETCH_CHUNK equ $fe1e
FETCH_PIECE equ $fe1f
FETCH_SRC equ $fe20
FETCH_DST equ $fe22
W_SOURCE equ $fe24
W_SAVED_SP equ $fe26
PROFILE equ $fe28
LOAD_PAGE equ $fe29
LOAD_VOLUME equ $fe2a
LOAD_INFILE equ $fe2b
FERROR equ $fe2c
NEED_FIRST equ $fe30
NEED_LAST equ $fe31
WANT equ $fe32
CURRENT_PAGE equ $fe35
CURRENT_BLOCK equ $fe36
BLOCKS_LEFT equ $fe38
FILE_NAME equ $fe40
COMMANDS equ $fe50
PARAM_MEM equ $fe52
FULL_FAST equ $fe54
LAST_HOOK_TICK equ $fe56
B_COUNT equ $fe60
B_TOTAL equ $fe62
B_MAX equ $fe64
B_START equ $fe66
B_MEASURE equ $fe68
D_STAGE equ $fe6a
D_OFFSET equ $fe6c
D_EXPECT equ $fe6e
D_ACTUAL equ $fe6f
LOADING equ $fe70
SUMS equ $7e00
META equ $7e80
INDEX equ $7800
BOUNCE equ $5e00
        org $c000
ram_gate_template:
        di
        ld ($5cf0),sp
        ld sp,$7ff0
        ld a,$80
        out ($f4),a
        ld bc,256
        ldir
        xor a
        out ($f4),a
        ld sp,($5cf0)
        ld a,(IRQ_ALLOW)
        or a
        ret z
        ei
        ret
ram_gate_end:
        ds $e000-$,0
        jp start
        ds $e038-$,0
irq:    push af
        push hl
        ld hl,(TICK)
        inc hl
        ld (TICK),hl
        pop hl
        pop af
        ei
        ret
        ds $e066-$,0
        retn
        ds $e100-$,0
start:  di
        ld sp,$fff0
        xor a
        out ($f4),a
        out ($ff),a
        out ($fe),a
        ld hl,WORK_BASE
        ld de,WORK_BASE+1
        ld bc,$3ff
        ld (hl),0
        ldir
        ld hl,$fe00
        ld de,$fe01
        ld bc,$ff
        ld (hl),0
        ldir
        xor a
        ld (FULL_FAST),a
        ld hl,ram_gate_template
        ld de,$5b00
        ld bc,ram_gate_end-ram_gate_template
        ldir
        ld hl,$f800
        ld de,$f801
        ld bc,256
        ld (hl),$f9
        ldir
        ld a,$c3
        ld ($f9f9),a
        ld hl,irq
        ld ($f9fa),hl
        ld a,$f8
        ld i,a
        im 2
menu:   di
        xor a
        ld (PLAY),a
        ld (IRQ_ALLOW),a
        out ($f4),a
        ld a,$40
        out ($ff),a
        call screen_clear
        ld hl,title
        call screen_puts
        ld hl,help
        call screen_puts
menu_key:
        call key_get
        cp 'Q'
        jp z,quit
        cp '1'
        jr z,.full
        cp '2'
        jr nz,menu_key
        ld a,'W'
        jr .choose
.full:  ld a,'F'
.choose:ld (PROFILE),a
        xor a
        ld (STOP),a
        ld a,1
        ld (LOADING),a
        call preload
        push af
        xor a
        ld (LOADING),a
        pop af
        jr nc,.loaded
        cp E_CANCEL
        jp nz,error_screen
        jp stopped
.loaded:
        call begin_play
        jp c,error_screen
.play:  call pump
        ld a,(STOP)
        or a
        jr nz,stopped
        call prefetch
        jp c,error_screen
        jr .play
stopped:
        call restore_host
        jp c,error_screen
        ld a,(STOP)
        cp 2
        jp z,quit_reboot
        cp 3
        jp nz,menu
        call screen_clear
        ld hl,done_text
        call screen_puts
        ld hl,(SHOWN)
        call hexword
        ld hl,loop_text
        call screen_puts
        ld hl,(LOOPS)
        call hexword
        ld hl,late_text
        call screen_puts
        ld hl,(LATE)
        call hexword
        ld hl,tick_text
        call screen_puts
        ld hl,(TICK)
        call hexword
        ld hl,cmd_text
        call screen_puts
        ld hl,(B_COUNT)
        call hexword
        ld hl,bank_ticks_text
        call screen_puts
        ld hl,(B_TOTAL)
        call hexword
        ld hl,bank_max_text
        call screen_puts
        ld hl,(B_MAX)
        call hexword
        call key_get
        jp menu
quit:
        call restore_host
        jp c,error_screen
quit_reboot:
        ; This full-control player overwrites BASIC's workspace: cold ROM
        ; entry is safe; returning through the original USR stack is not.
        di
        xor a
        out ($f4),a
        out ($ff),a
        im 1
        ld sp,$ffff
        jp $0000
restore_host:
        xor a
        ld (PLAY),a
        ld (IRQ_ALLOW),a
        di
        out ($f4),a
        ld a,2
        ld (PARAM_MEM),a
        xor a
        call select_region
        jp c,error_screen
        ld a,$40
        out ($ff),a
        ret
error_screen:
        ld (FERROR),a
        xor a
        ld (PLAY),a
        ld (IRQ_ALLOW),a
        di
        out ($f4),a
        ld a,$40
        out ($ff),a
        call screen_clear
        ld hl,error_text
        call screen_puts
        ld a,(FERROR)
        call screen_hex
        ld hl,stage_text
        call screen_puts
        ld a,(D_STAGE)
        call screen_char
        ld hl,volume_diag
        call screen_puts
        ld a,(LOAD_VOLUME)
        call screen_hex
        ld hl,page_text
        call screen_puts
        ld a,(LOAD_PAGE)
        call screen_hex
        ld hl,fetch_diag
        call screen_puts
        ld a,(FETCH_PAGE)
        call screen_hex
        ld hl,phase_text
        call screen_puts
        ld a,(LEGACY_PHASE)
        call screen_hex
        ld hl,function_diag
        call screen_puts
        ld a,(LEGACY_FUNCTION)
        call screen_hex
        ld hl,status_diag
        call screen_puts
        ld a,(REPLY_STATUS)
        call screen_hex
        ld hl,crc_diag
        call screen_puts
        ld a,(LEGACY_CRC)
        call screen_hex
        ld hl,flag_diag
        call screen_puts
        ld a,(LEGACY_POST_ERROR)
        call screen_hex
        ld hl,file_diag
        call screen_puts
        ld hl,FILE_NAME
        call screen_puts
        ld hl,cmd_diag
        call screen_puts
        ld hl,COMMAND_BUFFER
        call screen_puts
        ld hl,mismatch_diag
        call screen_puts
        ld hl,(D_OFFSET)
        call hexword
        ld hl,expected_diag
        call screen_puts
        ld a,(D_EXPECT)
        call screen_hex
        ld hl,actual_diag
        call screen_puts
        ld a,(D_ACTUAL)
        call screen_hex
        ld hl,err_help
        call screen_puts
.halt:  jr .halt

; Original 1.00 command, with explicit SRAM/Flash and even slot parameters.
ram_parameters:
        ld a,(BANK_CMD)
        or a
        ret z
        ld a,(PARAM_MEM)
        ld (RX_BUFFER+3),a
        ld a,(REQUEST)
        add a,a
        ld (RX_BUFFER+5),a
        ld hl,RX_BUFFER
        ld b,9
        xor a
.x:     xor (hl)
        inc hl
        djnz .x
        ld (hl),a
        ld hl,RX_BUFFER
        ret
select_region:
        cp 8
        jp nc,bad
        ld (REQUEST),a
        ld a,(PLAY)
        ld (B_MEASURE),a
        ld hl,(TICK)
        ld (B_START),hl
        xor a
        out ($f4),a
        ld a,1
        ld (BANK_CMD),a
        ld hl,memdock_text
        xor a
        call legacy_execute
        push af
        ld a,(B_MEASURE)
        or a
        jr z,.not_measured
        ld hl,(B_COUNT)
        inc hl
        ld (B_COUNT),hl
        ld hl,(TICK)
        ld de,(B_START)
        or a
        sbc hl,de
        push hl
        ld de,(B_MAX)
        or a
        sbc hl,de
        pop hl
        jr c,.not_max
        ld (B_MAX),hl
.not_max:
        ld de,(B_TOTAL)
        add hl,de
        ld (B_TOTAL),hl
.not_measured:
        xor a
        ld (BANK_CMD),a
        ld a,(REQUEST)
        ld (REGION),a
        ld hl,(COMMANDS)
        inc hl
        ld (COMMANDS),hl
        pop af
        ret c
        ; PIO selectors can be waiting inside their old access loop when
        ; MEMDOCK queues new words. Time alone cannot advance that loop.
        ; Read-only DOCK cycles consume pending selectors before any write.
        ld a,1
        out ($f4),a
        ld b,8
.prime: ld a,($0000)
        djnz .prime
        xor a
        out ($f4),a
        ret

; All 64 pages are loaded and read back before video starts.
preload:
        xor a
        ld (PLAY),a
        ld (LOAD_VOLUME),a
        ld (LOAD_PAGE),a
        ld (FETCH_ACTIVE),a
        ld a,1
        ld (PARAM_MEM),a
        ld a,$ff
        ld (REGION),a
        call screen_clear
        ld hl,loading_text
        call screen_puts
        ld a,'C'
        ld (D_STAGE),a
        ld hl,root
        call legacy_chdir
        ret c
        call check_cancel
        ret c
.volume:
        ld d,4
        ld e,0
        call screen_at
        ld hl,volume_text
        call screen_puts
        ld a,(LOAD_VOLUME)
        call screen_hex
        call make_name
        ld a,'M'
        ld (D_STAGE),a
        ld hl,FILE_NAME
        call legacy_mount
        ret c
        call check_cancel
        ret c
        ld a,(LOAD_VOLUME)
        or a
        jr nz,.pages
        ld de,META
        ld bc,64
        call read_code
        ret c
        ld a,'F'
        ld (D_STAGE),a
        ld hl,META
        ld de,meta_magic
        ld b,4
.magic: ld a,(de)
        cp (hl)
        jp nz,bad
        inc de
        inc hl
        djnz .magic
        ld a,(META+4)
        cp 1
        jp nz,bad
        ld a,(META+5)
        cp 5
        jr z,.rate_ok
        cp 4
        jp nz,bad
.rate_ok:
        ld a,(META+6)
        cp 64
        jp nz,bad
        ld hl,(META+10)
        ld a,h
        or l
        jp z,bad
        ld de,385
        or a
        sbc hl,de
        jp nc,bad
        ld hl,(META+10)
        add hl,hl
        add hl,hl
        ld de,(META+12)
        or a
        sbc hl,de
        jp nz,bad
        ld de,INDEX
        ld bc,(META+12)
        call read_code
        ret c
        ld de,(META+12)
        ld hl,INDEX
        add hl,de
        ld (INDEX_END),hl
        ld de,SUMS
        ld bc,128
        call read_code
        ret c
.pages: xor a
        ld (LOAD_INFILE),a
.page:  ld de,$8000
        ld bc,8192
        call read_code
        ret c
        ld a,'B'
        ld (D_STAGE),a
        ld a,(LOAD_PAGE)
        call ensure_region
        ret c
        ld a,'W'
        ld (D_STAGE),a
        xor a
        ld (FETCH_PIECE),a
.write: call write_piece
        ld hl,FETCH_PIECE
        inc (hl)
        ld a,(hl)
        cp 32
        jr nz,.write
        ld a,'R'
        ld (D_STAGE),a
        ld a,1
        ld (FETCH_SLOT),a
        ld a,(LOAD_PAGE)
        call fetch_begin
.verify:call fetch_piece
        ret c
        ld a,(FETCH_ACTIVE)
        or a
        jr nz,.verify
        ld a,'V'
        ld (D_STAGE),a
        ld hl,$8000
        ld de,$a000
        ld bc,8192
.cmp:   ld a,(de)
        cp (hl)
        jp nz,bad_compare
        inc de
        inc hl
        dec bc
        ld a,b
        or c
        jr nz,.cmp
        ld hl,LOAD_PAGE
        inc (hl)
        ld hl,LOAD_INFILE
        inc (hl)
        ld a,(hl)
        cp 4
        jr nz,.page
        ld hl,LOAD_VOLUME
        inc (hl)
        ld a,(hl)
        cp 16
        jp nz,.volume
        ld d,6
        ld e,0
        call screen_at
        ld hl,verify_text
        call screen_puts
        ; A second sweep catches aliasing after later region writes.
        xor a
        ld (LOAD_PAGE),a
.sweep: call keys
        call check_cancel
        ret c
        ld a,'S'
        ld (D_STAGE),a
        ld a,1
        ld (FETCH_SLOT),a
        ld a,(LOAD_PAGE)
        call ensure_region
        ret c
        ld a,(LOAD_PAGE)
        call fetch_begin
.sread: call fetch_piece
        ret c
        ld a,(FETCH_ACTIVE)
        or a
        jr nz,.sread
        ld hl,$a000
        ld bc,8192
        ld de,0
.sum:   ld a,(hl)
        inc hl
        add a,e
        ld e,a
        jr nc,.nc
        inc d
.nc:    dec bc
        ld a,b
        or c
        jr nz,.sum
        ld a,(LOAD_PAGE)
        ld l,a
        ld h,0
        add hl,hl
        ld bc,SUMS
        add hl,bc
        ld a,(hl)
        cp e
        jp nz,bad
        inc hl
        ld a,(hl)
        cp d
        jp nz,bad
        ld a,(LOAD_PAGE)
        cp 2
        jr c,.no_patch_validation
        call validate_page
        ret c
.no_patch_validation:
        ld hl,LOAD_PAGE
        inc (hl)
        ld a,(hl)
        cp 64
        jr nz,.sweep
        jp validate_index
make_name:
        ld hl,name_template
        ld de,FILE_NAME
        call str_copy
        ld a,(PROFILE)
        ld (FILE_NAME+2),a
        ld a,(LOAD_VOLUME)
        ld b,'0'
.tens:  cp 10
        jr c,.units
        sub 10
        inc b
        jr .tens
.units: add a,'0'
        ld (FILE_NAME+5),a
        ld a,b
        ld (FILE_NAME+4),a
        ret
; CODE header and data, exact length required, checksum verified.
read_code:
        ld a,'H'
        ld (D_STAGE),a
        ld (LEGACY_CAP),bc
        ld (LEGACY_DEST),de
        ld de,NAME_BUFFER
        ld bc,17
        xor a
        call legacy_read_block
        ret c
        call check_cancel
        ret c
        ld a,(NAME_BUFFER)
        cp 3
        jp nz,bad
        ld hl,(NAME_BUFFER+11)
        ld de,(LEGACY_CAP)
        or a
        sbc hl,de
        jp nz,bad
        ld a,'D'
        ld (D_STAGE),a
        ld a,$ff
        ld de,(LEGACY_DEST)
        ld bc,(LEGACY_CAP)
        call legacy_read_block
        ret c
        jp check_cancel
check_cancel:
        ld a,(STOP)
        or a
        ret z
        ld a,E_CANCEL
        scf
        ret
ensure_region:
        rrca
        rrca
        rrca
        and 7
        ld b,a
        ld a,(REGION)
        cp b
        ret z
        ld a,b
        jp select_region

; Read/write a mapped 256-byte span. Aliases bounce through stable HOME 5E00.
write_piece:
        ld a,(LOAD_PAGE)
        and 7
        add a,a
        add a,a
        add a,a
        add a,a
        add a,a
        ld b,a
        ld a,(FETCH_PIECE)
        add a,b
        ld d,a
        ld e,0
        ld a,(FETCH_PIECE)
        add a,$80
        ld h,a
        ld l,0
        ld a,(LOAD_PAGE)
        and 7
        ld b,a
        ld a,1
.mask:  dec b
        jp m,.got
        add a,a
        jr .mask
.got:   ld (FETCH_CHUNK),a
        cp $10
        jp nz,mapped_copy
        push de
        ld de,BOUNCE
        call copy256
        pop de
        ld hl,BOUNCE
        ld a,$10
        jp mapped_copy
fetch_begin:
        ld (FETCH_PAGE),a
        and 7
        ld b,a
        ld a,1
.mask:  dec b
        jp m,.got
        add a,a
        jr .mask
.got:   ld (FETCH_CHUNK),a
        xor a
        ld (FETCH_PIECE),a
        ld a,1
        ld (FETCH_ACTIVE),a
        ret
fetch_piece:
        ld a,(FETCH_PAGE)
        and 7
        add a,a
        add a,a
        add a,a
        add a,a
        add a,a
        ld b,a
        ld a,(FETCH_PIECE)
        add a,b
        ld h,a
        ld l,0
        ld a,(FETCH_SLOT)
        add a,a
        add a,a
        add a,a
        add a,a
        add a,a
        add a,$80
        ld b,a
        ld a,(FETCH_PIECE)
        add a,b
        ld d,a
        ld e,0
        ld a,h
        and $e0
        ld c,a
        ld a,d
        and $e0
        cp c
        jr nz,.direct
        push de
        ld de,BOUNCE
        ld a,(FETCH_CHUNK)
        call mapped_copy
        pop de
        ld hl,BOUNCE
        call copy256
        jr .copied
.direct:ld a,(FETCH_CHUNK)
        call mapped_copy
.copied:
        ld hl,FETCH_PIECE
        inc (hl)
        ld a,(hl)
        cp 32
        jr z,.complete
        or a
        ret
.complete:
        xor a
        ld (FETCH_ACTIVE),a
        ld a,(FETCH_SLOT)
        ld c,a
        ld b,0
        ld hl,CACHE_IDS
        add hl,bc
        ld a,(FETCH_PAGE)
        ld (hl),a
        ld a,c
        add a,a
        add a,a
        add a,a
        add a,a
        add a,a
        add a,$80
        ld h,a
        ld l,0
        ld de,page_magic
        ld b,4
.check: ld a,(de)
        cp (hl)
        jp nz,bad_header
        inc de
        inc hl
        djnz .check
        ld a,(FETCH_PAGE)
        cp (hl)
        jp nz,bad_header
        xor a
        ret
mapped_copy:
        cp $80
        jp z,$5b00
        out ($f4),a
        call copy256
        xor a
        out ($f4),a
        ret
copy256:
        ld bc,256
        ldir
        ret
bad_header:
        ld (D_EXPECT),a
        ld a,(hl)
        ld (D_ACTUAL),a
        ld a,l
        and 7
        ld (D_OFFSET),a
        xor a
        ld (D_OFFSET+1),a
        jp bad
bad_compare:
        ld (D_ACTUAL),a
        ld a,(hl)
        ld (D_EXPECT),a
        ld bc,$8000
        or a
        sbc hl,bc
        ld (D_OFFSET),hl
bad:    ld a,E_CHECKSUM
        scf
        ret

; Cache lookup: A=physical page, carry set if absent, C=slot if found.
lookup: ld hl,CACHE_IDS
        ld c,0
.loop:  cp (hl)
        ret z
        inc hl
        inc c
        ld b,a
        ld a,c
        cp 3
        ld a,b
        jr nz,.loop
        scf
        ret
page_next:
        inc a
        ld b,a
        ld a,(META+7)
        cp b
        ld a,b
        ret nc
        ld a,2
        ret
prepare_frame:
        ld hl,(FRAME_PTR)
        ld a,(hl)
        ld (NEED_FIRST),a
        ld (CURRENT_PAGE),a
        ld (WANT),a
        call page_next
        ld (WANT+1),a
        call page_next
        ld (WANT+2),a
        inc hl
        ld a,(hl)
        ld (CURRENT_BLOCK),a
        inc hl
        ld c,(hl)
        inc hl
        ld b,(hl)
        ld (BLOCKS_LEFT),bc
        ld hl,(BLOCKS_LEFT)
        ld a,(CURRENT_BLOCK)
        ld e,a
        ld d,0
        add hl,de
        dec hl
        ld a,(NEED_FIRST)
.last:  ld de,31
        or a
        sbc hl,de
        jr c,.last_done
        inc a
        jr .last
.last_done:
        ld (NEED_LAST),a
        ret
ready:  ld a,(NEED_FIRST)
.loop:  call lookup
        ret c
        ld b,a
        ld a,(NEED_LAST)
        cp b
        ld a,b
        ret z
        inc a
        jr .loop
; Only render when every source page for the complete frame is cached.
pump:   ld a,(PLAY)
        or a
        ret z
        ld a,(BUSY)
        or a
        ret nz
        call keys
        ld a,(PLAY)
        or a
        ret z
        ld a,(PAUSED)
        or a
        ret nz
        ld hl,(TICK)
        ld de,(TARGET)
        or a
        sbc hl,de
        bit 7,h
        ret nz
        call prepare_frame
        call ready
        ret c
        ld a,1
        ld (BUSY),a
        ld hl,(TICK)
        ld de,(TARGET)
        or a
        sbc hl,de
        ld a,h
        or l
        jr z,.ontime
        ld hl,(LATE)
        inc hl
        ld (LATE),hl
.ontime:
        ld hl,(TICK)
        ld a,(META+5)
        ld e,a
        ld d,0
        add hl,de
        ld (TARGET),hl
.blocks:
        ld a,(CURRENT_PAGE)
        call lookup
        ld a,c
        add a,a
        add a,a
        add a,a
        add a,a
        add a,a
        add a,$81
        ld b,a
        ld a,(CURRENT_BLOCK)
        add a,b
        ld h,a
        ld l,0
        ld (W_SOURCE),hl
        call ram_words64
        ld hl,CURRENT_BLOCK
        inc (hl)
        ld a,(hl)
        cp 31
        jr nz,.same_page
        xor a
        ld (hl),a
        ld hl,CURRENT_PAGE
        inc (hl)
.same_page:
        ld hl,(BLOCKS_LEFT)
        dec hl
        ld (BLOCKS_LEFT),hl
        ld a,h
        or l
        jr nz,.blocks
frame_done:
        ld hl,(SHOWN)
        inc hl
        ld (SHOWN),hl
        ld hl,(FRAME_PTR)
        ld de,4
        add hl,de
        ld (FRAME_PTR),hl
        ld de,(INDEX_END)
        or a
        sbc hl,de
        jr nz,.next
        ld hl,INDEX
        ld (FRAME_PTR),hl
        ld hl,(LOOPS)
        inc hl
        ld (LOOPS),hl
.next:  xor a
        ld (BUSY),a
        ret
keys:   ld a,(STOP)
        or a
        ret nz                       ; latch the first request until drained
        ld bc,$fbfe                 ; Q
        in a,(c)
        bit 0,a
        jr z,.quit
        ld bc,$7ffe                 ; Space
        in a,(c)
        bit 0,a
        jr z,.menu
        ld bc,$bffe                 ; Enter
        in a,(c)
        bit 0,a
        jr z,.menu
        ld bc,$fefe                 ; X retains the optional statistics screen
        in a,(c)
        bit 2,a
        ret nz
        ld a,3
        jr .request
.menu:  ld a,1
        jr .request
.quit:  ld a,2
.request:
        ld (STOP),a
        xor a
        ld (PLAY),a
        ret
prefetch:
        ld a,(FETCH_ACTIVE)
        or a
        jp nz,fetch_piece
        call prepare_frame
        ; Select the next region once every still-needed old-region page
        ; is cached. The FIFO polling hook keeps presenting cached frames.
        ld a,(NEED_FIRST)
        and 7
        cp 5
        jr c,.wanted
        ld a,(NEED_FIRST)
        rrca
        rrca
        rrca
        and 7
        ld b,a
        ld a,(REGION)
        cp b
        jr nz,.wanted
        ld a,(NEED_FIRST)
.check_tail:
        call lookup
        jr c,.wanted
        ld b,a
        and 7
        cp 7
        ld a,b
        jr z,.advance_region
        inc a
        jr .check_tail
.advance_region:
        ld a,(REGION)
        inc a
        and 7
        jp select_region
.wanted:
        ld a,(WANT)
        call lookup
        ld a,(WANT)
        jr c,.missing
        ld a,(WANT+1)
        call lookup
        ld a,(WANT+1)
        jr c,.missing
        ld a,(WANT+2)
        call lookup
        ld a,(WANT+2)
        ret nc
.missing:
        ld (FETCH_PAGE),a
        call ensure_region
        ret c
        ; Re-evaluate on the next pass: cached frames may have played while
        ; the region command was in flight, changing the desired pages.
        call prepare_frame
        ld a,(FETCH_PAGE)
        ld b,a
        ld a,(WANT)
        cp b
        jr z,.slot
        ld a,(WANT+1)
        cp b
        jr z,.slot
        ld a,(WANT+2)
        cp b
        jr z,.slot
        xor a
        ret
.slot:  ld c,0
.find:  ld b,0
        ld hl,CACHE_IDS
        add hl,bc
        ld b,(hl)
        ld a,(WANT)
        cp b
        jr z,.occupied
        ld a,(WANT+1)
        cp b
        jr z,.occupied
        ld a,(WANT+2)
        cp b
        jr nz,.free
.occupied:
        inc c
        ld a,c
        cp 3
        jr nz,.find
        xor a
        ret
.free:  ld a,c
        ld (FETCH_SLOT),a
        ld a,$ff
        ld (hl),a
        ld a,(FETCH_PAGE)
        call fetch_begin
        jp fetch_piece
begin_play:
        ld a,1
        ld (PARAM_MEM),a
        xor a
        call select_region
        ret c
        xor a
        ld (FETCH_SLOT),a
        call fetch_begin
.k0:    call fetch_piece
        ret c
        ld a,(FETCH_ACTIVE)
        or a
        jr nz,.k0
        ld hl,$8100
        ld de,$4000
        ld bc,6144
        ldir
        ld a,1
        ld (FETCH_SLOT),a
        call fetch_begin
.k1:    call fetch_piece
        ret c
        ld a,(FETCH_ACTIVE)
        or a
        jr nz,.k1
        ld hl,$a100
        ld de,$6000
        ld bc,6144
        ldir
        ld hl,INDEX
        ld (FRAME_PTR),hl
        ld a,$ff
        ld (CACHE_IDS),a
        ld (CACHE_IDS+1),a
        ld (CACHE_IDS+2),a
        xor a
        ld (SHOWN),a
        ld (SHOWN+1),a
        ld (LOOPS),a
        ld (LOOPS+1),a
        ld (LATE),a
        ld (LATE+1),a
        ld (B_COUNT),a
        ld (B_COUNT+1),a
        ld (B_TOTAL),a
        ld (B_TOTAL+1),a
        ld (B_MAX),a
        ld (B_MAX+1),a
        ld (STOP),a
        ld (PAUSED),a
        ld (BUSY),a
        call prepare_frame
.prime: call prefetch
        ret c
        call ready
        jr c,.prime
        ld a,2
        out ($ff),a
        ld a,1
        ld (PLAY),a
        ld (IRQ_ALLOW),a
        ld (KEY_OLD),a
        di
        ld hl,0
        ld (TICK),hl
        ld a,(META+5)
        ld l,a
        ld h,0
        ld (TARGET),hl
        ei
        xor a
        ret
; Validate table geometry and every expanded destination once, before play.
validate_index:
        ld hl,INDEX
        ld (FRAME_PTR),hl
.record:
        ld a,(hl)
        cp 2
        jp c,bad
        cp 64
        jp nc,bad
        inc hl
        ld a,(hl)
        cp 31
        jp nc,bad
        inc hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld a,d
        or a
        jp nz,bad
        ld a,e
        or a
        jp z,bad
        cp 94
        jp nc,bad
        push hl
        ld de,(INDEX_END)
        or a
        sbc hl,de
        pop hl
        jr nz,.record
        ld hl,INDEX
        ld (FRAME_PTR),hl
.geometry:
        call prepare_frame
        ld a,(NEED_LAST)
        cp 64
        jp nc,bad
        ld b,a
        ld a,(META+7)
        cp b
        jp c,bad
        ld a,(NEED_FIRST)
        add a,2
        cp b
        jp c,bad
        ld hl,(FRAME_PTR)
        ld de,4
        add hl,de
        ld (FRAME_PTR),hl
        ld de,(INDEX_END)
        or a
        sbc hl,de
        jr nz,.geometry
        xor a
        ret
validate_page:
        ld hl,$a100
        ld bc,1984
.record:
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        inc hl
        inc hl
        bit 0,e
        jp nz,bad
        ld a,d
        cp $40
        jp c,bad
        cp $58
        jr c,.ok
        cp $60
        jr nc,.attribute
        cp $58
        jp nz,bad
        ld a,e
        or a
        jp nz,bad
        jr .ok
.attribute:
        cp $78
        jp nc,bad
.ok:    dec bc
        ld a,b
        or c
        jr nz,.record
        xor a
        ret
; Receiver and command polling never accesses new SRAM while a command runs.
v2_rx_hook:
        push af
        push bc
        push de
        push hl
        call poll_pump
        ld a,(LOADING)
        or a
        call nz,keys
        pop hl
        pop de
        pop bc
        pop af
        ret
v2_pump equ pump
poll_pump:
        ld hl,(TICK)
        ld de,(LAST_HOOK_TICK)
        or a
        sbc hl,de
        ret z
        ld hl,(TICK)
        ld (LAST_HOOK_TICK),hl
        jp pump
video_settle:
        push bc
        push de
        push hl
        ld a,(PLAY)
        or a
        jr nz,.fast
        ld a,(BANK_CMD)
        or a
        jr nz,.slow
        ld a,(D_STAGE)
        cp 'C'
        jr z,.slow
        cp 'M'
        jr nz,.fast
.slow:  ld bc,0
.inner: dec bc
        ld a,b
        or c
        jr nz,.inner
        jr .done
.fast:  ld bc,1024
.loop:  push bc
        call poll_pump
        pop bc
        dec bc
        ld a,b
        or c
        jr nz,.loop
.done:  pop hl
        pop de
        pop bc
        ret
full_rx_payload:
        ld e,32
.byte:  in a,($0e)
        ld (hl),a
        inc hl
        xor d
        ld d,a
        push bc
        ld a,(FULL_FAST)
        or a
        ld b,14
        jr z,.delay
        ld b,1
.delay: djnz .delay
        pop bc
        dec bc
        ld a,b
        or c
        ret z
        dec e
        jr nz,.byte
        call v2_rx_hook
        ld e,32
        jr .byte

hexword:
        push hl
        ld a,h
        call screen_hex
        pop hl
        ld a,l
        jp screen_hex
        include "ram512_words.inc"
        include "ram512_transport.inc"
        include "ram512b_files.inc"
        include "display.asm"
root: db '/',0
memdock_text: db 'tpi:memdock',0
name_template: db 'SWF000.TAP',0
meta_magic: db 'R512'
page_magic: db 'RAMV'
title: db 'STAR WARS TRENCH / 512K',13,'ORIGINAL FIRMWARE 1.00',13,13,0
help: db 'SOURCE 44.5 TO 52.0 SECONDS',13
      db '1 256X108 ECM / 12 FPS TARGET',13
      db '  90 FRAMES / 7.50 SEC LOOP',13
      db '2 240X102 ECM / 15 FPS TARGET',13
      db '  113 FRAMES / 7.53 SEC LOOP',13
      db 13,'NATURAL COLOUR / 8X1 ECM',13
      db 'PRELOADS AND VERIFIES 512K',13
      db 'REPLACES SRAM CARTRIDGES',13
      db 'AND RAM DISKS - THEN LOOPS',13,13
      db 'SPACE/ENTER MENU  Q QUIT',13,0
volume_text: db 'LOADING VOLUME $',0
verify_text: db 'VERIFYING ALL 64 PAGES',0
loading_text: db 'PRELOAD AND VERIFY 512K SRAM',13,'SPACE/ENTER MENU  Q QUIT',13,'WAIT FOR CURRENT TRANSFER',13,'X STATS DURING PLAYBACK',13,0
done_text: db 'STOPPED - SHOWN $',0
loop_text: db 13,'LOOPS $',0
late_text: db 13,'LATE STARTS $',0
tick_text: db 13,'TICKS $',0
cmd_text: db 13,'PLAY BANK COMMANDS $',0
bank_ticks_text: db 13,'BANK TOTAL TICKS $',0
bank_max_text: db ' MAX $',0
error_text: db 'TRENCH VIDEO ERROR $',0
stage_text: db ' STG ',0
volume_diag: db 13,'VOL $',0
page_text: db ' LOAD $',0
fetch_diag: db ' FETCH $',0
phase_text: db 13,'PHASE $',0
function_diag: db ' FN $',0
status_diag: db ' STATUS $',0
crc_diag: db 13,'CRC $',0
flag_diag: db ' FLAG $',0
file_diag: db 13,'FILE: ',0
cmd_diag: db 13,'CMD: ',0
mismatch_diag: db 13,'OFFSET $',0
expected_diag: db ' E $',0
actual_diag: db ' A $',0
err_help: db 13,'STOPPED IN HOME RAM',13,'POWER RESET BEFORE RETRY',0
font: incbin '../build/font.bin'
program_end:
        assert program_end <= $f800
