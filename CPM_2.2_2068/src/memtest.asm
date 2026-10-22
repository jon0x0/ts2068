    org $100
    ld a,$a5
    ld ($4000),a
    cpl
    ld ($6000),a
    ld de,message
    ld c,9
    call 5
    ld a,($4000)
    cp $a5
    jr nz,fail
    ld a,($6000)
    cp $5a
    jr nz,fail
    ld de,ok
    jr print
fail:
    ld de,bad
print:
    ld c,9
    call 5
    ret
message: db '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!?',13,10,'$'
ok: db 'Screen shadow RAM PASS',13,10,'$'
bad: db 'Screen shadow RAM FAIL',13,10,'$'
