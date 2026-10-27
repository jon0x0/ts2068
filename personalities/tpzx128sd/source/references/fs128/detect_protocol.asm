; Extracted from CP/M cold loader; workspace relocation by build_fs128_probe.py.
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
