; HOME resident byte loop. Patched immediates are title-owned RAM only.
        DS $FC80-$,$FF
title_delta_cells:
        LD A,C
delta_base: SUB 0
        CP 7
        LD A,0
        JR NC,delta_no_moving
        LD A,(HL)
        INC HL
delta_no_moving:
        EX AF,AF'
        LD A,C
delta_prefix: CP 0
        JR NC,delta_no_prefix
        EX AF,AF'
        OR (IX+0)
        JR delta_store_pixel
delta_no_prefix:
        EX AF,AF'
delta_store_pixel:
        LD (DE),A
        LD A,C
delta_colour_base: CP 0
        JR NC,delta_shared_colour
        LD A,IXH
        ADD A,6
        LD IXH,A
        LD A,(IX+0)
        EX AF,AF'
        LD A,IXH
        SUB 6
        LD IXH,A
        EX AF,AF'
        JR delta_store_colour
delta_shared_colour:
        LD A,C
delta_colour_offset: SUB 0
        CP 4
        LD A,$47
        JR C,delta_store_colour
        LD A,$45
delta_store_colour:
        SET 5,D
        LD (DE),A
        RES 5,D
        INC DE
        INC IX
        INC C
        DJNZ title_delta_cells
        RET
        ASSERT $ <= $FD20
