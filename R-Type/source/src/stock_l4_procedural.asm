; Exact L4 phase reconstruction. All mutable state is explicitly allocated RAM.
 ORG PROC_CODE
 JP construct
 JP reset
 JP proc_row
 JP proc_attr
 JP clear_cell
reset:
 XOR A
 LD HL,PS
 LD DE,PS+1
 LD BC,145
 LD (HL),A
 LDIR
 LD A,$FF
 LD (PS+7),A
 JP invalidate_caches
; Constructor descriptor stream.
get_desc:
 DI
 PUSH HL
 LD HL,(PS+86)
 LD A,(PS+88)
 CALL READ_BYTE
 INC HL
 LD (PS+86),HL
 POP HL
 PUSH AF
 LD A,(PS+138)
 OR A
 JR Z,desc_keep_di
 POP AF
 EI
 RET
desc_keep_di:
 POP AF
 RET
construct:
 XOR A
 LD (PS+138),A
 LD A,1
 LD (PS+134),A
 LD A,(IX+2)
 LD (PS+132),A
 LD A,(IX+3)
 LD (PS+133),A
 LD A,(IX+9)
 AND 3
 LD (PS+117),A
 LD A,(FLAGS+13)
 LD (PS+135),A
 LD A,2
 LD (FLAGS+13),A
 LD (PS+86),HL
 LD A,C
 LD (PS+88),A
 CALL get_desc
 LD (PS+94),A
 CALL get_desc
 LD (PS+90),A
 CALL get_desc
 LD (PS+91),A
 CALL get_desc
 LD (PS+92),A
 CALL get_desc
 LD (PS+93),A
 ; Parent metadata is sixteen bytes, including the packed index high plane.
 LD A,(PS+94)
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,PARENT_TABLE
 ADD HL,DE
 LD DE,PS+96
 LD B,16
 LD C,PARENT_MASK
parent_descriptor:
 LD A,C
 CALL READ_BYTE
 LD (DE),A
 INC HL
 INC DE
 DJNZ parent_descriptor
 LD HL,(PS+110)
 LD (PS+136),HL
 ; Reject whole hidden parts before decompressing their base bitmap.
 LD HL,(PS+86)
 LD (PS+126),HL
 LD A,(PS+91)
 LD C,A
 LD A,(PS+92)
 LD B,A
 XOR A
pre_count:
 ADD A,C
 DJNZ pre_count
 LD (PS+122),A
 XOR A
 LD (PS+114),A
 LD (PS+115),A
 LD (PS+116),A
pre_cell:
 LD A,(PS+114)
 AND 7
 JR NZ,pre_mask
 CALL get_desc
 LD (PS+119),A
pre_mask:
 LD A,(PS+119)
 RRCA
 LD (PS+119),A
 JR NC,pre_next
 CALL cell_visible
 JR C,part_visible
pre_next:
 CALL advance_cell
 JR NZ,pre_cell
 LD HL,(PS+126)
 LD (PS+86),HL
 JP prepare_output
part_visible:
 LD HL,(PS+126)
 LD (PS+86),HL
 ; Decode one of the three original base bitmaps into the separate dense buffer.
 LD HL,(PS+102)
 LD A,(PS+101)
 LD DE,DENSE
 LD (PS+120),SP
 LD SP,CACHE-2
 CALL $000A
 LD SP,(PS+120)
 LD A,(CTX_IFF)
 LD (PS+138),A
 OR A
 JR Z,constructor_keep_di
 EI
constructor_keep_di:
 LD A,(PS+100)
 OR A
 JR Z,shift_finished
 PUSH IY
 LD HL,PS+124
 LD B,8
 XOR A
shift_zero:
 LD (HL),A
 INC HL
 DJNZ shift_zero
 LD A,(PS+99)
 DEC A
 LD (PS+116),A
shift_y:
 LD A,(PS+98)
 DEC A
 LD (PS+115),A
shift_x:
 LD A,(PS+115)
 LD C,A
 LD A,(PS+98)
 LD E,A
 LD A,(PS+116)
 CALL cell_address
 LD DE,7
 ADD HL,DE
 PUSH HL
 POP IY
 LD A,(PS+115)
 DEC A
 CALL shift_source_pointer
 PUSH HL
 POP IX
 LD A,(PS+115)
 CALL shift_source_pointer
 LD E,8
shift_raster:
 LD A,(PS+100)
 CP 4
 LD C,(IX)
 LD A,(HL)
 JR Z,shift_four
 JR C,shift_two
 SRL C
 RRA
 SRL C
 RRA
shift_four:
 SRL C
 RRA
 SRL C
 RRA
shift_two:
 SRL C
 RRA
 SRL C
 RRA
 LD (IY),A
 DEC HL
 DEC IX
 DEC IY
 DEC E
 JR NZ,shift_raster
 LD HL,PS+115
 DEC (HL)
 JP P,shift_x
 LD HL,PS+116
 DEC (HL)
 JP P,shift_y
 POP IY
shift_finished:
 ; Apply the bounded correction stream with one ROM mapping, using a visible
 ; private stack; the short mapped loop is atomic, then normal IRQs resume.
 DI
 LD (PS+120),SP
 LD SP,CACHE-2
 LD HL,(PS+105)
 LD A,(PS+104)
 OUT ($F4),A
patch_next:
 LD E,(HL)
 INC HL
 LD D,(HL)
 INC HL
 LD A,D
 AND E
 INC A
 JR Z,patch_finished
 PUSH HL
 LD HL,DENSE
 ADD HL,DE
 EX DE,HL
 POP HL
 LD B,(HL)
 INC HL
patch_bytes:
 LD A,(HL)
 LD (DE),A
 INC HL
 INC DE
 DJNZ patch_bytes
 JR patch_next
patch_finished:
 LD A,3
 OUT ($F4),A
 LD SP,(PS+120)
 LD A,(CTX_IFF)
 OR A
 JR Z,patch_keep_di
 EI
patch_keep_di:
prepare_output:
 LD A,(PS+91)
 LD (CACHE),A
 LD C,A
 LD A,(PS+92)
 LD (CACHE+1),A
 LD B,A
 XOR A
count_cells:
 ADD A,C
 DJNZ count_cells
 LD (PS+122),A
 LD A,(PS+93)
 CP 55
 JR C,no_dummy_palette
 INC A
no_dummy_palette:
 LD (CACHE+2),A
 LD L,A
 LD H,0
 ADD HL,HL
 LD DE,CACHE+3
 ADD HL,DE
 LD (PS+112),HL
 LD (PS+110),DE
 XOR A
 LD (PS+114),A
 LD (PS+115),A
 LD (PS+116),A
 LD (PS+118),A
construct_cell:
 LD A,(PS+114)
 AND 7
 JR NZ,mask_available
 CALL get_desc
 LD (PS+119),A
mask_available:
 LD A,(PS+119)
 RRCA
 LD (PS+119),A
 JR NC,invisible_cell
 CALL palette_token
 CALL cell_visible
 JR C,opaque_cell
invisible_cell:
 LD A,54
 CALL emit
 JP cell_complete
opaque_cell:
 LD HL,(PS+110)
 LD A,(PS+118)
 CP 54
 JR NZ,header_cell
 XOR A
 LD (HL),A
 INC HL
 LD (HL),A
 INC HL
 LD A,55
 LD (PS+118),A
header_cell:
 LD DE,(PS+144)
 LD (HL),E
 INC HL
 LD (HL),D
 INC HL
 LD (PS+110),HL
 LD A,(PS+118)
 CALL emit
 LD HL,PS+118
 INC (HL)
 LD A,(PS+115)
 LD C,A
 LD A,(PS+98)
 LD E,A
 LD A,(PS+116)
 CALL cell_address
 LD (PS+124),HL
 LD DE,(PS+112)
 LD A,(PS+90)
 OR A
 JR Z,copy_lower_rows
 LD B,A
 LD A,(PS+116)
 OR A
 JR Z,upper_rows_blank
 LD A,(PS+98)
 ADD A,A
 ADD A,A
 ADD A,A
 LD C,A
 LD A,8
 SUB C
 LD C,A
 LD A,(PS+90)
 LD L,A
 LD A,C
 SUB L
 LD C,A
 LD B,$FF
 LD HL,(PS+124)
 ADD HL,BC
 LD A,(PS+90)
 LD C,A
 LD B,0
 LDIR
 JR copy_lower_rows
upper_rows_blank:
 XOR A
upper_zero:
 LD (DE),A
 INC DE
 DJNZ upper_zero
copy_lower_rows:
 LD A,(PS+90)
 LD C,A
 LD A,8
 SUB C
 LD C,A
 LD B,0
 LD A,(PS+116)
 LD H,A
 LD A,(PS+99)
 CP H
 JR Z,lower_rows_blank
 JR C,lower_rows_blank
 LD HL,(PS+124)
 LDIR
 JR vertical_rows_done
lower_rows_blank:
 LD B,C
 XOR A
lower_zero:
 LD (DE),A
 INC DE
 DJNZ lower_zero
vertical_rows_done:
 LD (PS+112),DE
cell_complete:
 CALL advance_cell
 JP NZ,construct_cell
 DI
 XOR A
 LD (CTX_IFF+1),A
 LD A,(PS+135)
 LD (FLAGS+13),A
 JP CACHED_FRAME
advance_cell:
 LD HL,PS+115
 INC (HL)
 LD A,(PS+91)
 CP (HL)
 JR NZ,next_cell
 LD (HL),0
 LD HL,PS+116
 INC (HL)
next_cell:
 LD HL,PS+114
 INC (HL)
 LD A,(PS+122)
 CP (HL)
 RET
cell_visible:
 LD A,(PS+117)
 AND 1
 LD A,(PS+115)
 JR Z,visible_x
 LD C,A
 LD A,(PS+91)
 DEC A
 SUB C
visible_x:
 LD C,A
 LD A,(PS+132)
 ADD A,C
 OR A
 RET Z
 CP 31
 RET NC
 LD C,A
 LD A,(PS+117)
 AND 2
 LD A,(PS+116)
 JR Z,visible_y
 LD E,A
 LD A,(PS+92)
 DEC A
 SUB E
visible_y:
 LD E,A
 LD A,(PS+133)
 ADD A,E
 CP 20
 RET NC
 LD E,A
 AND 7
 RRCA
 RRCA
 RRCA
 ADD A,C
 LD L,A
 LD A,E
 RRCA
 RRCA
 RRCA
 AND 3
 ADD A,$7E
 LD H,A
 LD A,(HL)
 OR A
 RET NZ
 SCF
 RET
emit:
 LD DE,(PS+112)
 LD (DE),A
 INC DE
 LD (PS+112),DE
 RET
; A=cell y, C=cell x, E=row width; return dense cell pointer.
cell_address:
 LD B,A
 LD D,E
 XOR A
 INC B
 JR cell_multiply_test
cell_multiply:
 ADD A,D
cell_multiply_test:
 DJNZ cell_multiply
 ADD A,C
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,DENSE
 ADD HL,DE
 RET
shift_source_pointer:
 LD C,A
 LD A,(PS+96)
 CP C
 JR Z,shift_source_blank
 JR C,shift_source_blank
 LD E,A
 LD A,(PS+116)
 CALL cell_address
 LD DE,7
 ADD HL,DE
 RET
shift_source_blank:
 LD HL,PS+131
 RET
palette_token:
 DI
 LD A,(PS+114)
 LD B,A
 LD E,A
 LD D,0
 LD HL,(PS+108)
 ADD HL,DE
 LD DE,(PS+136)
 LD A,(PS+107)
 OUT ($F4),A
 LD C,(HL)
 LD H,D
 LD L,E
 LD A,B
 RRCA
 RRCA
 AND 63
 LD E,A
 LD D,0
 ADD HL,DE
 LD D,(HL)
 LD A,B
 AND 3
 ADD A,A
 LD B,A
 JR Z,token_high_done
token_high_shift:
 SRL D
 DJNZ token_high_shift
token_high_done:
 LD A,D
 AND 3
 LD H,A
 LD L,C
 ADD HL,HL
 ADD HL,HL
 INC H
 LD A,3
 OUT ($F4),A
 LD A,(PS+90)
 SRL A
 OR L
 LD L,A
 LD (PS+144),HL
 LD A,(PS+138)
 OR A
 JR Z,token_keep_di
 EI
token_keep_di:
 RET
; Permanent ID = 256 + 4 * adjacent-quad recipe + vertical pair phase.
; The low two ID bits are the vertical phase. Fold them into the recipe
; before indexing: raw ID modulo156 would use only39 slots per phase.
key_hash:
 LD A,E
 AND 3
 RRCA
 RRCA
 LD C,A
 SRL D
 RR E
 SRL D
 RR E
 LD A,E
 XOR C
 LD C,A
 LD E,D
 LD D,0
 LD HL,HASH_MOD
 ADD HL,DE
 LD A,(HL)
 ADD A,C
 JR NC,hash_fold
 ADD A,100
hash_fold:
 CP 156
 RET C
 SUB 168
 RET
ensure_palette:
 LD A,(PS+77)
 OR A
 JR Z,row_miss
 LD HL,(PS+75)
 OR A
 SBC HL,DE
 LD HL,(PS+72)
 RET Z
row_miss:
 LD (PS+75),DE
 CALL key_hash
 LD (PS+49),A
 LD L,A
 LD H,0
 ADD HL,HL
 LD DE,PAIR_KEYS
 ADD HL,DE
 LD (PS+46),HL
 LD DE,(PS+75)
 LD A,(HL)
 CP E
 JR NZ,pair_cache_miss
 INC HL
 LD A,(HL)
 CP D
 JR NZ,pair_cache_miss
 LD A,(PS+49)
 CALL pair_address
 JR expanded_ready
pair_cache_miss:
 CALL decode_recipe
 LD A,(PS+49)
 CALL pair_address
 LD (PS+44),HL
 EX DE,HL
 LD BC,PAIR_BASE
expand_pair:
 LD A,(PS+40)
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,BC
 LD A,(HL)
 LD (DE),A
 INC DE
 INC HL
 LD A,(HL)
 LD (DE),A
 INC DE
 LD A,(PS+41)
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,BC
 LD A,(HL)
 LD (DE),A
 INC DE
 INC HL
 LD A,(HL)
 LD (DE),A
 INC DE
 LD A,(PS+42)
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,BC
 LD A,(HL)
 LD (DE),A
 INC DE
 INC HL
 LD A,(HL)
 LD (DE),A
 INC DE
 LD A,(PS+43)
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,BC
 LD A,(HL)
 LD (DE),A
 INC DE
 INC HL
 LD A,(HL)
 LD (DE),A
 INC DE
 LD HL,(PS+46)
 LD DE,(PS+75)
 LD (HL),E
 INC HL
 LD (HL),D
 LD HL,(PS+44)
expanded_ready:
 LD (PS+72),HL
 LD A,1
 LD (PS+77),A
 RET
pair_address:
 CP 80
 JR NC,pair_glyph
 LD DE,$5800
 JR row_address
pair_glyph:
 SUB 80
 CP 56
 JR NC,pair_keys_tail
 LD DE,$7B08
 JR row_address
pair_keys_tail:
 SUB 56
 CP 17
 JR NC,pair_free_tail
 LD DE,PAIR_KEYS+312
 JR row_address
pair_free_tail:
 SUB 17
 LD DE,EXTRA_ROWS
row_address:
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 ADD HL,DE
 RET
decode_recipe:
 LD DE,(PS+75)
 DEC D
 LD A,E
 AND 3
 ADD A,A
 LD (PS+9),A
 SRL D
 RR E
 SRL D
 RR E
 LD H,D
 LD L,E
 LD BC,RECIPE_DEFAULTS
 OR A
 SBC HL,BC
 JR NC,exception_recipe
 LD (PS+26),DE
 LD A,E
 AND 7
 LD (PS+2),A
 LD H,D
 LD L,E
 SRL D
 RR E
 SRL D
 RR E
 SRL D
 RR E
 ADD HL,DE
 LD DE,RECIPE_TABLE
 ADD HL,DE
 LD A,RECIPE_MASK
 OUT ($F4),A
 LD E,(HL)
 INC HL
 LD D,(HL)
 LD A,3
 OUT ($F4),A
 LD A,(PS+2)
 OR A
 JR Z,default_shifted
 LD B,A
default_shift:
 SRL D
 RR E
 DJNZ default_shift
default_shifted:
 LD A,D
 AND 1
 LD H,A
 LD L,E
 LD (PS+22),HL
 JP recipe_quads_ready
exception_recipe:
 EX DE,HL
 LD A,E
 AND 3
 ADD A,A
 LD (PS+2),A
 LD H,D
 LD L,E
 ADD HL,HL
 SRL D
 RR E
 SRL D
 RR E
 ADD HL,DE
 LD DE,RECIPE_EXTRA
 ADD HL,DE
 LD A,RECIPE_MASK
 OUT ($F4),A
 LD E,(HL)
 INC HL
 LD D,(HL)
 INC HL
 LD C,(HL)
 LD A,3
 OUT ($F4),A
 LD A,(PS+2)
 OR A
 JR Z,recipe_shifted
 LD B,A
recipe_shift:
 SRL C
 RR D
 RR E
 DJNZ recipe_shift
recipe_shifted:
 LD L,E
 LD A,D
 AND 1
 LD H,A
 LD (PS+22),HL
 SRL C
 RR D
 LD L,D
 LD A,C
 AND 1
 LD H,A
 LD (PS+26),HL
recipe_quads_ready:
 LD A,(PS+9)
 OR A
 JR Z,only_lower
 SRL A
 LD B,A
 LD A,4
 SUB B
 LD C,A
 LD HL,(PS+22)
 LD DE,PS+40
 CALL copy_pairs
 JR lower_tail
only_lower:
 LD DE,PS+40
lower_tail:
 LD A,(PS+9)
 SRL A
 LD C,A
 LD A,4
 SUB C
 LD B,A
 LD C,0
 LD HL,(PS+26)
 JP copy_pairs
copy_pairs:
 ADD HL,HL
 ADD HL,HL
 PUSH DE
 LD DE,QUAD_BASE
 ADD HL,DE
 LD E,C
 LD D,0
 ADD HL,DE
 POP DE
 LD C,B
 LD B,0
 LD A,QUAD_MASK
 OUT ($F4),A
 LDIR
 LD A,3
 OUT ($F4),A
 RET
proc_row:
 LD A,I
 PUSH AF
 DI
 CALL ensure_palette
 LD DE,TEMP
 DUP 8
 LDI
 EDUP
 POP AF
 JP PO,proc_row_di
 EI
proc_row_di:
 POP AF
 LD HL,TEMP
 RET
proc_attr:
 LD A,I
 PUSH AF
 DI
 PUSH BC
 CALL ensure_palette
 POP BC
 LD E,B
 LD D,0
 ADD HL,DE
 LD C,(HL)
 POP AF
 JP PO,attr_di
 EI
attr_di:
 LD A,C
 RET
invalidate_caches:
 LD HL,PAIR_KEYS
 LD DE,PAIR_KEYS+1
 LD BC,311
 LD (HL),$FF
 LDIR
 RET
clear_cell:
 PUSH AF
 PUSH DE
 PUSH HL
 LD A,H
 AND $18
 RRCA
 RRCA
 RRCA
 ADD A,$81
 LD D,A
 LD E,L
 LD A,(DE)
 BIT 5,A
 JR Z,clear_done
 XOR A
 LD (DE),A
 LD A,D
 SUB 9
 LD D,A
 LD A,7
 LD (DE),A
clear_done:
 POP HL
 POP DE
 POP AF
 RET
 ASSERT $ <= PROC_CODE+3000
