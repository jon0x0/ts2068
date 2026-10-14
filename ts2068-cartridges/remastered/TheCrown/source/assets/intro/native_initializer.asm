; Crown-specific array setup. DIM and scalar setup retain the Leap ABI.
; Scratch $FAEE-$FAF8 stays outside intro/stream state and all arenas.
NI_ITEMS EQU $FAEE
NI_LEVEL EQU $FAF0
NI_ROOM EQU $FAF1
NI_LEFT EQU $FAF2
NI_KIND EQU $FAF3
NI_AMOUNT EQU $FAF4

native_dungeon:
    push ix
    ; DIM initially zeroes arrays; replay must also clear every numeric array.
    ld hl,ni_clear_slots
    ld b,11
.clear:
    push bc
    ld a,(hl)
    inc hl
    push hl
    ld c,0
    call ARR_SLOT
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de,hl
    inc hl
    ld c,(hl)
    inc hl
    ld b,(hl)
    inc hl
    sla c
    rl b
    call MEM_FILL_ZERO
    pop hl
    pop bc
    djnz .clear
    call tick
    ld hl,(ni_item_resource)
    call ni_load
    ld a,NATIVE_QA40
    ld c,0
    call ARR_SLOT
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc de
    inc de
    inc de
    ld (NI_ITEMS),de
    ld a,1
    ld (NI_ROOM),a
.base_rooms:
    ld de,100
    call ni_random
    ld a,l
    cp 33
    jr c,.next_room
    ld de,10
    call ni_random
    inc l
    ld a,l
    ld (NI_KIND),a
    ld de,120
    call ni_random
    push hl
    ld a,(NI_ROOM)
    ld e,a
    ld d,0
    call ni_random
    pop de
    add hl,de
    ld de,40
    call MATH_DIVIDE16
    inc l
    ld a,l
    ld (NI_AMOUNT),a
    call ni_put_room
.next_room:
    ld hl,NI_ROOM
    inc (hl)
    ld a,(hl)
    cp 121
    jr c,.base_rooms
    call tick
    ld de,120
    call ni_random
    inc l
    ld a,l
    ld (NI_ROOM),a
    ld a,23
    ld (NI_KIND),a
    ld a,1
    ld (NI_AMOUNT),a
    call ni_put_room
    xor a
    ld (NI_LEVEL),a
.level:
    ld a,24
    ld (NI_KIND),a
    ld a,5
    ld (NI_LEFT),a
.gold:
    call ni_pick
    ld de,7
    call ni_random
    inc l
    ld a,l
    ld (NI_AMOUNT),a
    call ni_put_room
    ld hl,NI_LEFT
    dec (hl)
    jr nz,.gold
    ld a,25
    ld (NI_KIND),a
    ld a,5
    ld (NI_LEFT),a
.potions:
    call ni_pick
    ld de,3
    call ni_random
    inc l
    ld a,l
    ld (NI_AMOUNT),a
    call ni_put_room
    ld hl,NI_LEFT
    dec (hl)
    jr nz,.potions
    ld a,(NI_LEVEL)
    or a
    jr z,.keys
    ld a,21
    ld (NI_KIND),a
    call ni_pick
    ld de,5
    call ni_random
    srl l
    ld a,(NI_LEVEL)
    add a,l
    ld (NI_AMOUNT),a
    call ni_put_room
.keys:
    call ni_pick
    ld a,(NI_LEVEL)
    add a,11
    ld (NI_KIND),a
    ld a,1
    ld (NI_AMOUNT),a
    call ni_put_room
    ld a,1
    ld (NI_LEFT),a
.equipment:
    call ni_pick
    call ni_room_addr
    ld a,(hl)
    or a
    jr nz,.equipment_next
    ld a,(NI_LEFT)
    add a,15
    ld (NI_KIND),a
    ld a,(NI_LEVEL)
    add a,2
    ld (NI_AMOUNT),a
    call ni_put_room
.equipment_next:
    ld hl,NI_LEFT
    inc (hl)
    ld a,(hl)
    cp 5
    jr c,.equipment
    call ni_pick_empty
    ld a,(NI_LEVEL)
    add a,11
    ld (NI_KIND),a
    ld a,1
    ld (NI_AMOUNT),a
    call ni_put_room
    call ni_pick_empty
    ld a,(NI_LEVEL)
    add a,20
    ld (NI_KIND),a
    call ni_put_room
    call tick
    ld hl,NI_LEVEL
    inc (hl)
    ld a,(hl)
    cp 3
    jp c,.level
    ld a,120
    ld (NI_ROOM),a
    ld a,15
    ld (NI_KIND),a
    ld a,1
    ld (NI_AMOUNT),a
    call ni_put_room
    pop ix
    ld hl,0
    ret

ni_random:
    ex de,hl
    jp MATH_RND16
ni_pick:
    ld de,40
    call ni_random
    ld a,(NI_LEVEL)
    ld e,a
    add a,a
    add a,a
    add a,e
    add a,a
    add a,a
    add a,a ; level * 40
    add a,l
    inc a
    ld (NI_ROOM),a
    ret
ni_pick_empty:
    call ni_pick
    ld a,(NI_ROOM)
    cp 120
    jr z,ni_pick_empty
    call ni_room_addr
    ld a,(hl)
    or a
    jr nz,ni_pick_empty
    ret
ni_room_addr:
    ld a,(NI_ROOM)
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    dec hl
    dec hl ; room 1 => array element 1
    ld de,(NI_ITEMS)
    add hl,de
    ret
ni_put_room:
    call ni_room_addr
    ld a,(NI_KIND)
    ld (hl),a
    inc hl
    ld (hl),0
    inc hl
    ld a,(NI_AMOUNT)
    ld (hl),a
    inc hl
    ld (hl),0
    ret

native_monsters:
    call native_room_data
    ld a,NATIVE_QA12
    ld c,0
    call ARR_SLOT
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de,hl
    ld de,5
    add hl,de
    ld (NI_ITEMS),hl
    ld a,40
    ld (NI_LEFT),a
.loop:
    ld de,100
    call ni_random
    ld a,l
    cp 33
    ld hl,0
    jr nc,.store
    ld de,10
    call ni_random
    inc l
.store:
    ld de,(NI_ITEMS)
    ld a,l
    ld (de),a
    inc de
    xor a
    ld (de),a
    inc de
    ld (NI_ITEMS),de
    ld hl,NI_LEFT
    dec (hl)
    jr nz,.loop
    call tick
    ld hl,0
    ret

native_room_data:
    push ix
    ld hl,(RT_SYMTAB_PTR)
    ld de,NATIVE_QV23*3+1
    add hl,de
    ld a,(hl)
    dec a
    add a,a
    ld e,a
    ld d,0
    ld hl,ni_level_resources
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de,hl
    call ni_load
    call tick
    pop ix
    ld hl,0
    ret

; Compressed fixed tables expand into the DATA cache. Each record holds
; array slot, kind, byte length and element-1 payload; $FF terminates.
ni_load:
    call stream_reset
    ld de,$BE00
    call dzx0_standard
    ld a,$FF
    ld (CACHE_BLOCK),a
    ld ix,$BE00
.record:
    ld a,(ix+0)
    cp $FF
    ret z
    ld c,(ix+1)
    push bc
    call ARR_SLOT
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de,hl
    inc hl
    inc hl
    inc hl
    pop bc
    bit 0,c
    jr nz,.string
    inc hl
    inc hl
    jr .destination
.string:
    ld e,(hl)
    ld d,0
    inc hl
    add hl,de
.destination:
    ex de,hl
    ld c,(ix+2)
    ld b,(ix+3)
    inc ix
    inc ix
    inc ix
    inc ix
    push ix
    pop hl
    ldir
    push hl
    pop ix
    jr .record
ni_clear_slots:
    DB NATIVE_QA40,NATIVE_QA41,NATIVE_QA42,NATIVE_QA12,NATIVE_QA27,NATIVE_QA21,NATIVE_QA17,NATIVE_QA38,NATIVE_QA39,NATIVE_QA16,NATIVE_QA11


native_glyphs:
    ld hl,(RT_SYMTAB_PTR)
    ld de,NATIVE_QV23*3+1
    add hl,de
    ld a,(hl)
    dec a
    add a,a
    ld e,a
    ld d,0
    ld hl,ni_glyph_resources
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de,hl
    call stream_reset
    ld de,$F180
    call dzx0_standard
    ld a,$FF
    ld (CACHE_BLOCK),a
    call tick
    ld hl,0
    ret
