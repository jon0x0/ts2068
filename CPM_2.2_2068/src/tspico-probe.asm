; Conservative modern-only probe. No OUT $0F until a framed preheader ACK
; and the distinct modern MID status have both been received. Legacy $40,
; busy $00, floating $FF and stale ACK with idle status are not sufficient.
tsp_probe:
    in a,($0f)
    cp $ff
    jr nz,tsp_no_device
    ld hl,tsp_probe_header
    ld b,10
    ld d,0
tsp_probe_send:
    ld a,(hl)
    inc hl
    call tpi_tx
    djnz tsp_probe_send
    call tpi_rx
    cp 1
    jr nz,tsp_no_device
    ; Wait boundedly for READY; require MID and RECOVERED, not idle/floating.
    ld bc,0
tsp_probe_wait:
    in a,($0f)
    cp $f7
    jr z,tsp_probe_ok
    dec bc
    ld a,b
    or c
    jr nz,tsp_probe_wait
tsp_no_device:
    scf
    ret
tsp_probe_ok:
    ; The validated modern preheader can now be safely aborted by SYNC.
    jp tpi_reset
; B command preheader for a harmless short command, nine bytes plus XOR.
tsp_probe_header: db $42,0,$ff,0,0,0,0,7,0,$ba
