; Native intro and compressed resource reader. Runs in DOCK chunk 1.
; Stack, flags and stream state stay in HOME chunk 7. Bytecode is HOME RAM.
ACTIVE EQU $FAC0
PHASE EQU $FAC1
LAST EQU $FAC2
READY EQU $FAC3
REFRESH EQU $FAC6
CACHE_BLOCK EQU $FAD0
STREAM_PTR EQU $FAE0
STREAM_VALUE EQU $FAE2
BUFFER_COUNT EQU $FAE3
BUFFER_POS EQU $FAE4
SNAP_VALID EQU $FAE5
SNAP_BASE EQU $FAE6
SNAP_ARRAY_LEN EQU $FAE8
SNAP_TABLE_LEN EQU $FAEA
SNAP_END EQU $FAEC

boot_init:
    call MEM_COLD_INIT
    call MEM_INIT
    xor a
    ld (PORT_FF_SHADOW),a
    ld (ACTIVE),a
    ld (SNAP_VALID),a
    ld ($F7D0),a
    ld a,3
    ld ($F7E2),a
    call EXT2_CLEAR_ALL
    call KBD_ISR_INIT
    im 1
    ei
    ld hl,CODE_SRC
    call stream_reset
    ld de,$8000
    call dzx0_standard
    ld hl,counts
    ld de,SYM_COUNTS
    ld bc,5
    ldir
    ld hl,PROG_AREA_START-SESS_GAP-1
    ld (SYM_END_V),hl
    ld hl,ARR2_BASE
    ld (PAS_END),hl
    call VM_INIT
    ld a,$FF
    ld (CACHE_BLOCK),a
    ld hl,trampolines
    ld de,$F800
    ld bc,27
    ldir
    ld hl,data_trampoline
    ld de,$F400
    ld bc,3
    ldir
    ld a,$18
    ld ($F6FE),a
    ld a,$FE
    ld ($F6FF),a
    ld a,7
    ld (CURRENT_PAPER),a
    call GFX_CLS
    ld hl,$8000
    ld (VM_IP),hl
    call VM_RUN
    jp $F6FE
counts:
; COUNTS_PLACEHOLDER
trampolines:
    jp tick
    jp start
    jp ready
    jp restart_intro
    jp native_dungeon
    jp native_monsters
    jp native_room_data
    jp native_glyphs
    jp crown_joystick
data_trampoline:
    jp data_byte

; Stock TS2068 player-1 joystick: AY register 14, A8 selected ($01F6).
; Return active-low contacts in HL for Leap USR; real hardware and TSRun
; use up/down/left/right at bits 0..3 and fire at bit 7.
crown_joystick:
    ld a,14
    out ($F5),a
    ld bc,$01F6
    in a,(c)
    ld l,a
    ld h,0
    ret

; Discard the finished VM invocation and rebuild the startup state cleanly.
restart_intro:
    di
    ld sp,$FF00
    call VM_INIT
    ld hl,(SNAP_BASE)
    ld de,$CA00
    ld bc,(SNAP_ARRAY_LEN)
    ldir
    ld de,(VARS_START)
    ld bc,(SNAP_TABLE_LEN)
    ldir
    ld de,$F180
    ld bc,168
    ldir
    ld de,$5B00
    ld bc,$25A
    ldir
    ld hl,(SNAP_END)
    ld (ARRAYS_END),hl
    call KBD_ISR_INIT
    ei
    call start
    call ready
    ld hl,RESUME_IP
    ld (VM_IP),hl
    call VM_RUN
    jp $F6FE

; Read one byte at a physical ROM offset, then restore all HOME RAM banks.
; Preserve flags as well as BC/DE/HL for the ZX0 bit reader.
stream_get:
    push hl
    push af
    ld a,(BUFFER_COUNT)
    or a
    jr nz,.have
    call stream_refill
.have:
    ld a,(BUFFER_COUNT)
    dec a
    ld (BUFFER_COUNT),a
    ld a,(BUFFER_POS)
    ld l,a
    ld h,$F9
    ld a,(hl)
    ld (STREAM_VALUE),a
    inc l
    ld a,l
    ld (BUFFER_POS),a
    pop af
    ld a,(STREAM_VALUE)
    pop hl
    ret

stream_reset:
    ld (STREAM_PTR),hl
    xor a
    ld (BUFFER_COUNT),a
    ret

stream_refill:
    push bc
    push de
    ld hl,(STREAM_PTR)
    ld bc,256
    ld a,h
    and $1F
    cp $1F
    jr nz,.length
    ld a,l
    or a
    jr z,.length
    neg
    ld c,a
    ld b,0
.length:
    ld a,c
    ld (BUFFER_COUNT),a
    xor a
    ld (BUFFER_POS),a
    ld a,h
    rlca
    rlca
    rlca
    and 7
    ld e,a
    ld d,0
    push hl
    ld hl,read_masks
    add hl,de
    ld a,(hl)
    pop hl
    ld de,$F900
    di
    cp $83
    jr z,.stack_bank
    out ($F4),a
    ldir
    ld a,3
    out ($F4),a
    jr .copied
.stack_bank:
    ; Chunk 7 hides both stack and cache: use the stack-free far-byte gate.
.byte:
    push bc
    push de
    push hl
    ld c,3
    ld a,$83
    call $3FF0
    ld a,l
    pop hl
    pop de
    pop bc
    ld (de),a
    inc hl
    inc de
    dec bc
    ld a,b
    or c
    jr nz,.byte
.copied:
    ld (STREAM_PTR),hl
    pop de
    pop bc
    ei
    ret
read_masks: db 3,3,7,11,19,35,67,131

; Logical DATA byte reader with one 512-byte decompression cache.
data_byte:
    push bc
    push de
    ld hl,($F7E0)
    inc hl
    ld ($F7E0),hl
    dec hl
    push hl
    ld a,h
    srl a
    ld b,a
    ld a,(CACHE_BLOCK)
    cp b
    jr z,.cached
    ld a,b
    ld (CACHE_BLOCK),a
    add a,a
    ld e,a
    ld d,0
    ld hl,asset_table
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de,hl
    call stream_reset
    ld de,$BE00
    call dzx0_standard
.cached:
    pop hl
    ld a,h
    and 1
    add a,$BE
    ld h,a
    ld l,(hl)
    ld h,0
    pop de
    pop bc
    ret

tick:
    push af
    push bc
    push de
    push ix
    ld a,(ACTIVE)
    or a
    jp z,tick_done
    ld a,(FRAMES)
    ld b,a
    ld a,(LAST)
    ld c,a
    ld a,b
    sub c
    cp 12
    jp c,tick_done
    ld a,b
    ld (LAST),a
    ld a,(PHASE)
    inc a
    and 7
    ld (PHASE),a
    add a,a
    ld e,a
    ld d,0
    ld hl,frame_table
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld a,d
    and $E0
    cp $80
    jr c,.buffered
    cp $E0
    jr nc,.buffered
    ; Chunks 4/5/6 leave both video planes, ISR state and stack visible.
    ld a,d
    rlca
    rlca
    rlca
    and 7
    ld l,a
    ld h,0
    push de
    ld de,read_masks
    add hl,de
    ld a,(hl)
    pop de
    out ($F4),a
    ld hl,$4000
    ld b,12
.direct_blocks:
    push bc
    push hl
    call direct_plane
    pop hl
    set 5,h
    push hl
    call direct_plane
.direct_pair_done:
    pop hl
    res 5,h
    inc h
    inc h
    pop bc
    djnz .direct_blocks
    ld a,3
    out ($F4),a
    jr .drawn
.buffered:
    ex de,hl
    call stream_reset
    ld hl,$4000
    ld b,12
.buffered_blocks:
    push bc
    push hl
    call hybrid_plane
.buffered_pair_done:
    pop hl
    set 5,h
    push hl
    call hybrid_plane
    pop hl
    res 5,h
    inc h
    inc h
    pop bc
    djnz .buffered_blocks
.drawn:
    ld hl,REFRESH
    inc (hl)
frame_decoded:
tick_done:
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0
    ret

start:
    push ix
    xor a
    ld (PHASE),a
    ld (READY),a
    ld (REFRESH),a
    inc a
    ld (ACTIVE),a
    ld hl,$5800
    ld bc,$300
    call MEM_FILL_ZERO
    ld hl,$6000
    ld bc,$1800
    call MEM_FILL_ZERO
    xor a
    out ($FE),a
    ld a,2
    ld (PORT_FF_SHADOW),a
    out ($FF),a
blackout_ready:
    ld hl,KEY_PIX
    call stream_reset
    ld de,$4000
    call dzx0_standard
bitmap_decoded:
    ld hl,KEY_ATR
    call stream_reset
    ld de,$6000
    call dzx0_standard
    ld a,(FRAMES)
    ld (LAST),a
key_decoded:
    pop ix
    ld hl,0
    ret

ready:
    ld a,(ACTIVE)
    or a
    jr nz,.active
    ld hl,0
    ret
.active:
    push ix
    ld a,(SNAP_VALID)
    or a
    call z,save_fresh_game
    ld a,1
    ld (READY),a
    ; 3x5 lettering, two lines beside Brian Walker; preserve the credit.
    ld ix,prompt_rows
    ld hl,prompt_pixels
    ld b,10
.prompt_row:
    push bc
    ld e,(ix+0)
    ld d,(ix+1)
    inc ix
    inc ix
    push de
    ld bc,5
    ldir
    pop de
    set 5,d
    ld a,2
    REPT 5
    ld (de),a
    inc e
    ENDR
    pop bc
    djnz .prompt_row
release:
    call tick
    halt
    call startup_input
    jr nz,release
wait_key:
    call tick
    halt
    call startup_input
    jr z,wait_key
release_after:
    halt
    call startup_input
    jr nz,release_after
    xor a
    ld (ACTIVE),a
    ld (PORT_FF_SHADOW),a
    out ($FF),a
    call KBD_ISR_INIT
    pop ix
    ld hl,0
    ret

; Any keyboard key or player-1 direction/fire starts the game. The same
; release/fresh-press/release gate prevents a held startup control leaking
; into the first room. Z means every input is released.
startup_input:
    ld bc,$00FE
    in a,(c)
    and $1F
    cp $1F
    ret nz
    call crown_joystick
    ld a,l
    and $8F
    cp $8F
    ret

; TSCodec hybrid transport, unchanged pixels/attributes are skipped.
hybrid_plane:
    call stream_get
    or a
    ret z
    jp p,.skip
    cp $C0
    jr z,.mask
    and $3F
    inc a
    ld b,a
.literal:
    call stream_get
    xor (hl)
    ld (hl),a
    inc hl
    djnz .literal
    jr hybrid_plane
.skip:
    ld c,a
    ld b,0
    add hl,bc
    jr hybrid_plane
.mask:
    call stream_get
    ld c,a
    ld b,8
.bits:
    sla c
    jr nc,.next
    call stream_get
    xor (hl)
    ld (hl),a
.next:
    inc hl
    djnz .bits
    jr hybrid_plane

; Reserve the snapshot in the unused array gap. Extending ARRAYS_END prevents
; subsequent allocations/control-stack frames from overwriting this region.
save_fresh_game:
    ld hl,(ARRAYS_END)
    ld (SNAP_BASE),hl
    ld de,$CA00
    or a
    sbc hl,de
    ld (SNAP_ARRAY_LEN),hl
    ld b,h
    ld c,l
    ld hl,$CA00
    ld de,(SNAP_BASE)
    ldir
    ld hl,$F100
    ld bc,(VARS_START)
    or a
    sbc hl,bc
    ld (SNAP_TABLE_LEN),hl
    ld b,h
    ld c,l
    ld hl,(VARS_START)
    ldir
    ld hl,$F180
    ld bc,168
    ldir
    ld hl,$5B00
    ld bc,$25A
    ldir
    ld (SNAP_END),de
    ld (ARRAYS_END),de
    ld a,1
    ld (SNAP_VALID),a
    ret
prompt_rows:
    INCLUDE "prompt_rows.inc"
prompt_pixels:
    INCBIN "prompt.pixels"

; Direct TSCodec hybrid decoder for streams wholly in safe ROM banks.
direct_plane:
    ld a,(de)
    inc de
    or a
    ret z
    jp p,.skip
    cp $C0
    jr z,.mask
    and $3F
    inc a
    ld b,a
.literal:
    ld a,(de)
    inc de
    xor (hl)
    ld (hl),a
    inc hl
    djnz .literal
    jr direct_plane
.skip:
    ld c,a
    ld b,0
    add hl,bc
    jr direct_plane
.mask:
    ld a,(de)
    inc de
    ld c,a
    ld b,8
.bits:
    sla c
    jr nc,.next
    ld a,(de)
    inc de
    xor (hl)
    ld (hl),a
.next:
    inc hl
    djnz .bits
    jr direct_plane
