"""RAM veneers that expose HOME display RAM around graphics calls."""
WRAPPED = [
    'GFX_CLS','GFX_PAINT_ATTR','GFX_SCROLL_TEXT_UP','GFX_SCROLL_OUTPUT_UP','GFX_SCROLL_TEXT_DOWN',
    'GFX_PUTCHAR','GFX_PUTCHAR_OVER','GFX_PUTCHAR_BOLD','GFX_INVERT_ATTR','GFX_INVERT_ATTR_STATIC',
    'GFX_SET_ATTR','GFX_CLEAR_ROW','GFX_CLEAR_ROW_TEXT','GFX_WRITE_PIXEL','GFX_READ_PIXEL',
]
ADDRESSES={name:0xF4A0+14*i for i,name in enumerate(WRAPPED)}


def helper_assembly(symbols,wide,data_length):
    code=f'''helper_source:
    DISP $F400
; Read and increment the logical packed-DATA pointer. All workspace is HOME 7.
data_byte:
    di
    ld hl,($F7E0)
    ld de,1
    add hl,de
    ld ($F7E0),hl
    dec hl
    ld de,$1B50
    or a
    sbc hl,de
    jr nc,.upper
    add hl,de
    ld de,$84B0
    add hl,de
    ld e,$10
    jr .read
.upper:
    ld de,$2000
    or a
    sbc hl,de
    jr nc,.last
    add hl,de
    ld de,$A000
    add hl,de
    ld e,$20
    jr .read
.last:
    ld de,$E000
    add hl,de
    ld e,$80
.read:
    ld a,(${symbols['PORT_FF_SHADOW']:04X})
    ld ($F7E3),a
    and $7F
    out ($FF),a
    ld a,($F7E2)
    ld c,a
    or e
    call $3FF0
    ld a,($F7E3)
    out ($FF),a
    ld a,($F7E2)
    out ($F4),a
    ei
    ret
    ASSERT $ <= $F4A0
    DS $F4A0-$,0
'''
    if wide:
        for name in WRAPPED:
            if 'REAL_'+name not in symbols:
                code+='    DS 14,0\n'
                continue
            code+=f'''    ASSERT $ == ${ADDRESSES[name]:04X}
    push af
    call $F580
    pop af
    call ${symbols['REAL_'+name]:04X}
    push af
    call $F5B0
    pop af
    ret
'''
        code+='''    ASSERT $ <= $F580
    DS $F580-$,0
screen_in:
    ld a,($F7D0)
    inc a
    ld ($F7D0),a
    cp 1
    ret nz
    ld a,($F7E2)
    ld ($F7D1),a
    and $FB
    ld ($F7E2),a
    out ($F4),a
    ret
    ASSERT $ <= $F5B0
    DS $F5B0-$,0
screen_out:
    ld a,($F7D0)
    dec a
    ld ($F7D0),a
    ret nz
    ld a,($F7D1)
    ld ($F7E2),a
    out ($F4),a
    ret
'''
    code+='''    ASSERT $ <= $F600
    DS $F600-$,0
    ENT
helper_end:
'''
    return code
