; Boot-only ROM3 code. Stack in HOME BFFF; interrupts disabled throughout.
 INCLUDE "../build/title-equ.asm"
 ORG title_source
title_entry:
 ld hl,title_data
 ld de,$a000
title_run:
 ld a,(hl)
 inc hl
 or a
 jr z,title_transpose
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
title_transpose:
 ld de,$a000
 ld bc,0
title_column:
 call offset
 set 6,h
 ld a,(de)
 ld (hl),a
 inc de
 inc b
 ld a,b
 cp 192
 jr nz,title_column
 ld b,0
 inc c
 ld a,c
 cp 32
 jr nz,title_column
title_wait:
 ld a,$98
 out ($f4),a
 jp effects_origin+15
title_data:
 INCBIN "../build/title-rle.bin"

 INCLUDE "frontend-title.asm"
