    org $100
    ld de,message
    ld c,9
    call 5
    ret
message: db 'HELLO from a .COM on the TS2068 Z80!',13,10,'$'
