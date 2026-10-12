; Optional CRC32 code. Low-ROM label addresses supplied by the suite assembler.
 INCLUDE "../build/symbols.txt"
 ORG $8000
; Preserve the proven native high-anchor handoff stub.
 di
 ld a,$11
 out ($f4),a
 jp entry
 DS $8020-$,255
home_crc:
 di
 ld a,$10
 out ($f4),a
 ld hl,0
 ld ix,$4000
 ld bc,$ffff
 ld de,$ffff
home_crc_byte:
 ld a,(hl)
 xor e
 ld e,a
 ld a,8
 ld i,a
home_crc_bit:
 srl b
 rr c
 rr d
 rr e
 jp nc,home_crc_no_poly
 ld a,b
 xor $ed
 ld b,a
 ld a,c
 xor $b8
 ld c,a
 ld a,d
 xor $83
 ld d,a
 ld a,e
 xor $20
 ld e,a
home_crc_no_poly:
 ld a,i
 dec a
 ld i,a
 jp nz,home_crc_bit
 inc hl
 dec ix
 ld a,ixh
 or ixl
 jp nz,home_crc_byte
 ld a,b
 cpl
 ld b,a
 ld a,c
 cpl
 ld c,a
 ld a,d
 cpl
 ld d,a
 ld a,e
 cpl
 ld e,a
 ld a,$11
 out ($f4),a
 jp crc_home_return
 DS $8100-$,255
 DISP $c000
exrom_gateway:
 di
 ld a,$c0
 out ($ff),a
 ld a,1
 out ($f4),a
 ld hl,0
 ld ix,$2000
 ld bc,$ffff
 ld de,$ffff
exrom_crc_byte:
 ld a,(hl)
 xor e
 ld e,a
 ld a,8
 ld i,a
exrom_crc_bit:
 srl b
 rr c
 rr d
 rr e
 jp nc,exrom_crc_no_poly
 ld a,b
 xor $ed
 ld b,a
 ld a,c
 xor $b8
 ld c,a
 ld a,d
 xor $83
 ld d,a
 ld a,e
 xor $20
 ld e,a
exrom_crc_no_poly:
 ld a,i
 dec a
 ld i,a
 jp nz,exrom_crc_bit
 inc hl
 dec ix
 ld a,ixh
 or ixl
 jp nz,exrom_crc_byte
 ld a,b
 cpl
 ld b,a
 ld a,c
 cpl
 ld c,a
 ld a,d
 cpl
 ld d,a
 ld a,e
 cpl
 ld e,a
 ld a,$40
 out ($ff),a
 jp crc_exrom_return
 ENT
 DS $8200-$,255
