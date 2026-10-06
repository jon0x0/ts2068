; Boot-only ROM3 code. Stack in HOME BFFF; interrupts disabled throughout.
 INCLUDE "../build/title-equ.asm"
 ORG title_source
title_entry:
 ld hl,title_data
 ld de,$4000
title_run:
 ld a,(hl)
 inc hl
 or a
 jr z,title_wait
 ld b,a
 bit 7,a
 jr nz,title_repeat
title_literal:
 ld a,(hl)
 inc hl
 ld (de),a
 inc de
 djnz title_literal
 jr title_run
title_repeat:
 res 7,b
 ld a,(hl)
 inc hl
title_byte:
 ld (de),a
 inc de
 djnz title_byte
 jr title_run
title_wait:
 ld bc,$7ffe
 in a,(c)
 bit 0,a
 jp z,title_return
 ld a,14
 out ($f5),a
 ld bc,$01f6
 in a,(c)
 bit 7,a
 jr nz,title_wait
 jp title_return
title_data:
 INCBIN "../build/title-rle.bin"
