; Retained colours: native00..0F/20..7F, terrain80..8F,
; enemy dictionary IDs0..111 ->90..FF, IDs112..127 ->10..1F.
        ORG $0E00
terrain_decode_colour:
        PUSH HL
        PUSH BC
        CALL full_colour_pointer
        JR NC,full_decode_done
        LD C,IYL
        LD B,0
        ADD HL,BC
        LD A,(HL)
full_decode_done:
        POP BC
        POP HL
        RET
        ASSERT $ <= $0E40
        DS $0E40-$,$FF
terrain_copy_colour:
        PUSH HL
        PUSH BC
        CALL full_colour_pointer
        SET 5,D
        JR NC,full_copy_native
        LD B,2
full_copy_palette:
        DUP 4
        LD A,(HL)
        INC HL
        LD (DE),A
        INC D
        EDUP
        DJNZ full_copy_palette
        JR full_copy_done
full_copy_native:
        DUP 8
        LD (DE),A
        INC D
        EDUP
full_copy_done:
        LD A,D
        SUB 8
        LD D,A
        RES 5,D
        POP BC
        POP HL
        RET
        ASSERT $ <= $0E78
        DS $0E78-$,$FF
full_colour_pointer:
        CP $90
        JR NC,full_enemy_low
        CP $10
        JR C,full_native_or_terrain
        CP $20
        JR NC,full_native_or_terrain
        ADD A,$60
        JR full_enemy_pointer
full_enemy_low:
        SUB $90
full_enemy_pointer:
        LD BC,$2000
        JR full_palette_pointer
full_native_or_terrain:
        OR A
        RET P
        AND $7F
        LD BC,$FBD0
full_palette_pointer:
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,BC
        SCF
        RET
        ASSERT $ <= $0EA0
        DS $0EF0-$,$FF ; music ownership overlays EA0..EEF
terrain_reverse_attribute:
        LD A,(HL)
        CP $80
        JR C,full_reverse_done
        CP $90
        JR NC,full_reverse_done
        OR $04
full_reverse_done:
        LD (DE),A
        INC E
        RET
        ASSERT $ <= $0F00
