; Called after the original RL terrain span, which includes one left spill cell.
terrain_after_pixel_scroll:
        PUSH DE
        LD H,B
        LD L,C
        PUSH AF
        LD A,L
        AND $1F
        CP 31
        JR NZ,terrain_visible_right
        DEC L
terrain_visible_right:
        CALL terrain_colour_core
        POP AF
        POP DE
        LD H,B
        LD L,E
        JP $8869
terrain_colour_core:
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
 IFNDEF ROM_ONLY
        LD A,$0B
        OUT ($F4),A
 ENDIF
        PUSH AF ; keep frame layout; IRQ-safe code leaves IFF unchanged
        ; Original RL code already found the left endpoint in DE. Reuse it;
        ; re-scanning every terrain ID would duplicate its hottest loop.
        LD B,H
        LD IXH,1
        LD A,E
        AND $1F
        JR NZ,terrain_span_ready
        INC E
        LD IXH,0
terrain_span_ready:
        LD A,L
        SUB E
        INC A
        LD C,A
        LD L,E
        LD A,D
        SUB $26
        LD H,A
        LD A,B
        LD D,A
        ; Native front-attribute copy excludes staging column31. Temporarily
        ; supply its actual incoming palette, never the stale black sentinel.
        LD A,L
        OR $1F
        LD L,A
        LD A,(HL)
        PUSH AF
        SET 5,H
        LD A,(HL)
        RES 5,H
        LD (HL),A
        LD L,E
        LD A,($7A82)
        AND 7
        LD IYH,A
        PUSH HL
        LD H,0
        LD L,A
        PUSH BC
        LD BC,terrain_left_masks
        ADD HL,BC
        LD A,(HL)
        POP BC
        LD B,A
        POP HL
        LD A,3
        OUT ($F4),A
        ; The spill cell already contains prior fine-shift pixels. Its legacy
        ; attribute belongs to sky/actors, so always inherit the entering terrain.
        LD A,IXH
        AND A
        JR Z,terrain_dispatch
        INC HL
        LD A,(HL)
        CALL terrain_flat_cell
        INC E
        DEC C
        JP Z,terrain_span_done
terrain_dispatch:
        LD A,IYH
        CP 7
        JR Z,terrain_cells_right
        AND A
        JR Z,terrain_cells_initial
terrain_span_cell:
        LD A,(HL)
        INC HL
        XOR (HL)
        JR Z,terrain_next_cell
        CALL terrain_boundary_cell
terrain_next_cell:
        INC E
        DEC C
        JR NZ,terrain_span_cell
        JR terrain_span_done
terrain_cells_initial:
        LD A,(HL)
        LD IXL,A
        INC HL
        LD A,(HL)
        CP IXL
        JR NZ,terrain_initial_boundary
        CALL terrain_flat_cell
        JR terrain_initial_next
terrain_initial_boundary:
        CALL terrain_boundary_cell
terrain_initial_next:
        INC E
        DEC C
        JR NZ,terrain_cells_initial
        JR terrain_span_done
terrain_cells_right:
        INC HL
        LD A,(HL)
        CALL terrain_flat_cell
        INC E
        DEC C
        JR NZ,terrain_cells_right
        JR terrain_span_done
terrain_flat_cell:
        JP $0E40
terrain_boundary_cell:
        DEC HL
        LD A,(HL)
        LD IXL,A
        INC HL
        LD A,(HL)
        LD IXH,A
        AND IXL
        JP M,$0100
        LD IYL,0
terrain_line:
        LD A,(DE)
        AND B
        LD A,IXL
        JR NZ,terrain_selected
        LD A,IXH
terrain_selected:
        CALL $0E00
        SET 5,D
        LD (DE),A
        RES 5,D
        INC D
        INC IYL
        LD A,IYL
        CP 8
        JR NZ,terrain_line
        LD A,D
        SUB 8
        LD D,A
        RET
terrain_span_done:
        LD A,L
        OR $1F
        LD L,A
        POP AF
        LD (HL),A
        LD A,(MODE_SHADOW)
        OUT ($FF),A
 IFDEF ROM_ONLY
        LD A,3
 ELSE
        LD A,9
 ENDIF
        OUT ($F4),A
        POP AF
terrain_span_no_ei:
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        RET
terrain_left_masks:
        DB $FE,$FC,$F8,$F0,$E0,$C0,$80,0
