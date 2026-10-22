; Protocol selected once by the cold loader. 1=FIFO, 2=status-register.
; This byte lies outside the TPA and all transport workspaces.
DUAL_PROTOCOL equ $eff3
dual_ready:
    push bc
    ld bc,0
.poll:
    in a,($0f)
    bit 6,a
    jr nz,.ok
    dec bc
    ld a,b
    or c
    jr nz,.poll
    pop bc
    ld a,E_TIMEOUT
    scf
    ret
.ok:
    pop bc
    or a
    ret
dual_reset:
    push bc
    ld bc,0
.idle:
    in a,($0f)
    and $48
    cp $48
    jr z,.sync
    dec bc
    ld a,b
    or c
    jr nz,.idle
    pop bc
    scf
    ret
.sync:
    xor a
    out ($0f),a
    call dual_ready
    pop bc
    ret c
    call tpi_rx
    cp 1
    ret z
    scf
    ret
