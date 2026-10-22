; Read-only PicoVideo diagnostics: only selects readable register indices.
    org $100
    ld bc,$bf3b
    in a,(c)
    ld (selector),a
    ld de,title
    call puts
    ld a,($eff5)
    call hex
    ld de,cap_label
    call puts
    ld a,($eff7)
    call hex
    ld de,nl
    call puts
    ld hl,indices
    ld b,4
.next:
    push bc
    push hl
    ld a,(hl)
    ld (index),a
    call hex
    ld e,'='
    call char
    ld a,(index)
    ld bc,$bf3b
    out (c),a
    ld b,64
.wait: djnz .wait
    ld b,$ff
    in a,(c)
    call hex
    ld de,nl
    call puts
    pop hl
    inc hl
    pop bc
    djnz .next
    ld a,(selector)
    ld bc,$bf3b
    out (c),a
    ld de,end_text
    jp puts
puts:
    ld c,9
    jp 5
hex:
    push af
    rrca
    rrca
    rrca
    rrca
    call digit
    pop af
digit:
    and 15
    add a,'0'
    cp '9'+1
    jr c,.out
    add a,7
.out:
    ld e,a
char:
    ld c,2
    jp 5
indices: db $7f,$40,$41,$43
selector: db 0
index: db 0
title: db 'VIDEO: active=', '$'
cap_label: db ' capability=', '$'
nl: db 13,10,'$'
end_text: db '7F=version, 40=enable, 41=mode, 43=mirror.',13,10
    db '10 matches older V4: no supported 80-column renderer.',13,10
    db '42 is the currently supported 80-column implementation.',13,10
    db 'COLUMNS 80 retries detection with a longer settling delay.',13,10,'$'
