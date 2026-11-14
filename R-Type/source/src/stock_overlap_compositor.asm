; L5 front-to-back ECM overlap, matching the TAP Bellmite compositor.
 ORG COMPOSITOR_CODE
 JP overlap_predicate
 JP reset_pool
 JP read_dynamic_attr
 JP read_dynamic_row
 JP clear_dynamic_cell
 JP invalidate_references
invalidate_references:
 XOR A
 LD (WS+58),A
 RET
reset_pool:
 XOR A
 LD (WS),A
 LD (WS+1),A
 LD (WS+2),A
 LD (WS+58),A
 LD HL,HEAD_VALID
 LD DE,HEAD_VALID+1
 LD BC,31
 LD (HL),A
 LDIR
 RET
; Backend input: C palette slot, B raster. Caller saves BC/DE/HL.
read_dynamic_attr:
 LD L,C
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,POOL
 ADD HL,DE
 LD E,B
 LD D,0
 ADD HL,DE
 LD A,(HL)
 RET
; palette_read has already pushed the caller AF. DE=0400+slot.
read_dynamic_row:
 LD A,I
 PUSH AF
 DI
 LD L,E
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,POOL
 ADD HL,DE
 LD DE,TEMP
 LD BC,8
 LDIR
 POP AF
 JP PO,row_keep_di
 EI
row_keep_di:
 POP AF
 LD HL,TEMP
 RET
; Zero-owner erase must retire a composed cell, not leave its coloured paper.
clear_dynamic_cell:
 PUSH AF
 PUSH BC
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
 AND $30
 CP $30
 JR NZ,erase_done
 XOR A
 LD (DE),A
 LD A,D
 SUB 9
 LD D,A
 LD A,7
 LD (DE),A
erase_done:
 POP HL
 POP DE
 POP BC
 POP AF
 RET
; Candidate WS+24..31. Return slot A, carry only on exhausted live pool.
find_pattern:
 LD HL,WS+24
 LD B,8
 XOR A
hash_next:
 RLCA
 ADD A,(HL)
 XOR B
 INC HL
 DJNZ hash_next
 LD (WS+56),A
 CALL bucket_head
 JP C,allocate_slot
search_slot:
 LD E,A
 LD D,0
 PUSH DE
 LD L,E
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD BC,POOL
 ADD HL,BC
 LD DE,WS+24
 LD B,8
compare_pattern:
 LD A,(DE)
 CP (HL)
 JR NZ,pattern_mismatch
 INC DE
 INC HL
 DJNZ compare_pattern
 POP DE
 LD A,(WS+58)
 OR A
 JR Z,matched_untracked
 LD A,E
 CALL mark_reference
matched_untracked:
 LD A,E
 OR A
 RET
pattern_mismatch:
 POP DE
 LD HL,LINKS
 ADD HL,DE
 LD A,(HL)
 CP $FF
 JR NZ,search_slot
allocate_slot:
 LD HL,(WS)
 LD A,H
 OR A
 JR NZ,reclaim_slot
 IF POOL_SLOTS < 256
 LD A,L
 CP POOL_SLOTS
 JR NC,reclaim_slot
 ENDIF
 LD A,L
 INC HL
 LD (WS),HL
 JR store_pattern
reclaim_slot:
 XOR A
 LD (WS+59),A
 LD A,(WS+58)
 OR A
 JR NZ,references_ready
refresh_references:
 CALL scan_references
 LD A,1
 LD (WS+58),A
references_ready:
 LD HL,REFS
 LD C,0
find_free_byte:
 LD A,(HL)
 CP $FF
 JR NZ,find_free_bit
 INC HL
 LD A,C
 ADD A,8
 LD C,A
 IF POOL_SLOTS < 256
 CP POOL_SLOTS
 ENDIF
 JR NZ,find_free_byte
 LD A,(WS+59)
 OR A
 JR NZ,pool_exhausted
 INC A
 LD (WS+59),A
 JR refresh_references
pool_exhausted:
 LD A,(WS+2)
 CP $FF
 JR Z,overflow_recorded
 INC A
 LD (WS+2),A
overflow_recorded:
 SCF
 RET
find_free_bit:
 LD B,8
free_bit:
 RRCA
 JR NC,free_found
 INC C
 DJNZ free_bit
free_found:
 LD A,C
 LD (WS+57),A
 CALL unlink_pattern
 LD A,(WS+57)
store_pattern:
 LD (WS+57),A
 LD A,(WS+57)
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,POOL
 ADD HL,DE
 EX DE,HL
 LD HL,WS+24
 LD BC,8
 LDIR
 CALL link_pattern
 LD A,(WS+58)
 OR A
 JR Z,new_untracked
 LD A,(WS+57)
 CALL mark_reference
new_untracked:
 LD A,(WS+57)
 OR A
 RET
; Hash buckets retain all256 slots. SlotFF is always a bucket head;
; a separate head-valid bitmap distinguishes it from an empty bucket.
bucket_head:
 LD C,A
 AND 7
 LD L,A
 LD H,0
 LD DE,bit_masks
 ADD HL,DE
 LD B,(HL)
 LD A,C
 RRCA
 RRCA
 RRCA
 AND 31
 LD L,A
 LD H,0
 LD DE,HEAD_VALID
 ADD HL,DE
 LD A,(HL)
 AND B
 JR Z,bucket_empty
 LD L,C
 LD H,0
 LD DE,HASHES
 ADD HL,DE
 LD A,(HL)
 OR A
 RET
bucket_empty:
 SCF
 RET
mark_bucket:
 LD A,(WS+56)
 CALL bucket_bit
 LD A,(HL)
 OR B
 LD (HL),A
 RET
clear_bucket:
 LD A,(WS+60)
 CALL bucket_bit
 LD A,B
 CPL
 AND (HL)
 LD (HL),A
 RET
bucket_bit:
 LD C,A
 AND 7
 LD L,A
 LD H,0
 LD DE,bit_masks
 ADD HL,DE
 LD B,(HL)
 LD A,C
 RRCA
 RRCA
 RRCA
 AND 31
 LD L,A
 LD H,0
 LD DE,HEAD_VALID
 ADD HL,DE
 RET
link_pattern:
 LD A,(WS+56)
 CALL bucket_head
 JR C,link_empty
 LD C,A
 LD A,(WS+57)
 CP $FF
 JR Z,link_prepend
 LD A,C
 CP $FF
 JR NZ,link_prepend
 LD A,(WS+57)
 LD E,A
 LD D,0
 LD HL,LINKS+255
 LD A,(HL)
 LD (HL),E
 LD C,A
 LD HL,LINKS
 ADD HL,DE
 LD (HL),C
 RET
link_empty:
 LD C,$FF
link_prepend:
 LD A,(WS+57)
 LD E,A
 LD D,0
 LD HL,LINKS
 ADD HL,DE
 LD (HL),C
 LD C,E
 LD A,(WS+56)
 LD E,A
 LD HL,HASHES
 ADD HL,DE
 LD (HL),C
 CALL mark_bucket
 RET
unlink_pattern:
 LD A,(WS+57)
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,POOL
 ADD HL,DE
 LD B,8
 XOR A
old_hash:
 RLCA
 ADD A,(HL)
 XOR B
 INC HL
 DJNZ old_hash
 LD (WS+60),A
 CALL bucket_head
 RET C
 LD C,A
 LD A,(WS+57)
 CP C
 JR Z,unlink_head
 LD A,C
unlink_walk:
 LD E,A
 LD D,0
 LD HL,LINKS
 ADD HL,DE
 LD A,(HL)
 CP $FF
 JR Z,chain_error
 LD C,A
 LD A,(WS+57)
 CP C
 JR Z,unlink_after
 LD A,C
 JR unlink_walk
unlink_after:
 PUSH HL
 LD E,A
 LD D,0
 LD HL,LINKS
 ADD HL,DE
 LD A,(HL)
 POP HL
 LD (HL),A
 RET
unlink_head:
 LD A,(WS+57)
 LD E,A
 LD D,0
 LD HL,LINKS
 ADD HL,DE
 LD A,(HL)
 CP $FF
 JP Z,clear_bucket
 LD C,A
 LD A,(WS+60)
 LD E,A
 LD HL,HASHES
 ADD HL,DE
 LD (HL),C
 RET
chain_error:
 LD A,$FF
 LD (WS+2),A
 RET
scan_references:
 LD HL,REFS
 LD DE,REFS+1
 LD BC,REF_BYTES-1
 LD (HL),0
 LDIR
 LD HL,$7800
 LD DE,$8100
 LD BC,640
scan_grid:
 LD A,(DE)
 AND $30
 CP $30
 JR NZ,grid_next
 LD A,(HL)
 CALL mark_reference
grid_next:
 INC DE
 INC HL
 DEC BC
 LD A,B
 OR C
 JR NZ,scan_grid
 IF SNAPSHOT_CELLS > 0
 LD HL,SNAPSHOT
 LD B,SNAPSHOT_CELLS
scan_snapshot:
 LD C,(HL)
 INC HL
 LD A,(HL)
 AND $30
 CP $30
 JR NZ,snapshot_next
 LD A,C
 CALL mark_reference
snapshot_next:
 INC HL
 DJNZ scan_snapshot
 ENDIF
 RET
mark_reference:
 PUSH BC
 PUSH DE
 PUSH HL
 LD C,A
 AND 7
 LD L,A
 LD H,0
 LD DE,bit_masks
 ADD HL,DE
 LD B,(HL)
 LD A,C
 RRCA
 RRCA
 RRCA
 AND 31
 LD L,A
 LD H,0
 LD DE,REFS
 ADD HL,DE
 LD A,(HL)
 OR B
 LD (HL),A
 POP HL
 POP DE
 POP BC
 RET
bit_masks: DB 1,2,4,8,16,32,64,128
overlap_predicate:
 LD A,(DE)
 OR A
 JR Z,unowned
 CP $DC
 RET NC
 LD A,(CTX+25)
 OR A
 RET NZ
 LD A,(CTX+24)
 CP 8
 JR Z,compose_cell
 CP 30
 JR C,occupied
 CP 34
 JR C,compose_cell
occupied:
 OR A
 RET
unowned:
 SCF
 RET
compose_cell:
 PUSH HL
 LD A,D
 ADD A,3
 LD H,A
 LD L,E
 LD A,(HL)
 AND $60
 CP $60
 POP HL
 JR NZ,compose_visible
 OR A
 RET
compose_visible:
 PUSH BC
 PUSH DE
 PUSH HL
 PUSH IX
 PUSH IY
 LD A,I
 PUSH AF
 DI
 LD (WS+6),HL
 LD (WS+8),DE
 LD A,(FLAGS+13)
 LD (WS+3),A
 LD A,1
 LD (FLAGS+13),A
 LD IX,0
 ADD IX,SP
 LD A,(IX+14)
 CP $8C
 JR Z,mirror_cell
 CP $F8
 JR Z,invert_cell
 CP $52
 JR Z,reverse_cell
 XOR A
 JR flip_ready
mirror_cell:
 LD A,1
 JR flip_ready
invert_cell:
 LD A,2
 JR flip_ready
reverse_cell:
 LD A,3
flip_ready:
 LD (WS+5),A
 CALL read_old_row
 CALL foreground_opaque
 JP C,opaque_foreground
 LD HL,(WS+6)
 CALL STOCK_COLOUR
 PUSH HL
 POP IY
 LD A,(WS+5)
 OR A
 JR NZ,source_oriented
 LD A,($8EB1)
 AND $3F
 JR NZ,source_oriented
 LD DE,WS+16
 LD BC,8
 LDIR
 LD HL,(WS+6)
 INC HL
 LD DE,WS+32
 LD BC,8
 LDIR
 JR source_complete
source_oriented:
 LD HL,(WS+6)
 INC HL
 LD A,(WS+5)
 AND 2
 JR Z,source_ready
 LD DE,7
 ADD HL,DE
 ADD IY,DE
source_ready:
 LD IX,WS+16
 LD B,8
source_row:
 LD A,($8EB1)
 AND $3F
 JR NZ,source_attribute
 LD A,(IY)
source_attribute:
 LD (IX),A
 LD A,(WS+5)
 AND 1
 LD A,(HL)
 JR Z,source_bits
 PUSH HL
 LD L,A
 LD H,$5D
 LD A,(HL)
 POP HL
source_bits:
 LD (IX+16),A
 LD A,(WS+5)
 AND 2
 JR NZ,source_back
 INC HL
 INC IY
 JR source_next
source_back:
 DEC HL
 DEC IY
source_next:
 INC IX
 DJNZ source_row
source_complete:
 LD DE,(WS+8)
 LD A,D
 SUB $7E
 RLCA
 RLCA
 RLCA
 ADD A,$A6
 LD D,A
 LD (WS+10),DE
 XOR A
 LD (WS+4),A
 LD (WS+12),A
 INC A
 LD (WS+13),A
compose_row:
 DI
 LD HL,(WS+10)
 LD A,(HL)
 LD (WS+48),A
 LD (WS+52),A
 LD A,(WS+12)
 LD E,A
 LD D,0
 LD HL,WS+64
 ADD HL,DE
 LD A,(HL)
 LD (WS+49),A
 LD (WS+53),A
 LD A,(WS+12)
 LD E,A
 LD D,0
 LD HL,WS+16
 ADD HL,DE
 LD A,(HL)
 LD (WS+51),A
 LD HL,WS+32
 ADD HL,DE
 LD A,(HL)
 LD (WS+50),A
 EI
 CALL blend_row
 LD A,(WS+13)
 OR A
 JR Z,opacity_ready
 LD A,(WS+53)
 AND $38
 JR Z,opaque_black_paper
 LD A,(WS+53)
 AND 7
 JR NZ,opacity_ready
 LD A,(WS+52)
 OR A
 JR Z,opacity_ready
 JR not_opaque
opaque_black_paper:
 LD A,(WS+53)
 AND 7
 JR Z,not_opaque
 LD A,(WS+52)
 CP $FF
 JR Z,opacity_ready
not_opaque:
 XOR A
 LD (WS+13),A
opacity_ready:
 LD A,(WS+12)
 LD E,A
 LD D,0
 LD HL,WS+24
 ADD HL,DE
 LD A,(WS+53)
 LD (HL),A
 LD C,A
 LD A,(WS+49)
 XOR C
 LD C,A
 LD A,(WS+4)
 OR C
 LD (WS+4),A
 LD HL,WS+40
 ADD HL,DE
 LD A,(WS+52)
 LD (HL),A
 LD HL,WS+11
 INC (HL)
 LD HL,WS+12
 INC (HL)
 LD A,(HL)
 CP 8
 JP NZ,compose_row
 LD A,(WS+4)
 OR A
 JR Z,preserve_pair
 CALL find_pattern
 JP C,compose_done
 LD HL,(WS+8)
 LD C,A
 LD A,H
 SUB 6
 LD H,A
 LD (HL),C
 ADD A,9
 LD H,A
 LD (HL),$31
 JR publish_bits
preserve_pair:
 LD HL,(WS+8)
 LD A,H
 ADD A,3
 LD H,A
 SET 0,(HL)
publish_bits:
 LD A,(WS+13)
 OR A
 JR Z,opacity_published
 SET 6,(HL)
opacity_published:
 LD DE,(WS+10)
 LD A,D
 SUB 8
 LD D,A
 LD HL,WS+40
 LD B,8
output_row:
 LD A,(HL)
 LD (DE),A
 INC HL
 INC D
 DJNZ output_row
compose_done:
 DI
 LD A,(WS+3)
 LD (FLAGS+13),A
 POP AF
 JP PO,compose_keep_di
 EI
compose_keep_di:
 POP IY
 POP IX
 POP HL
 POP DE
 POP BC
 OR A
 RET
; A newly painted foreground cell may already hide every rear pixel.
; Check its actual row masks before resolving/copying the source frame.
foreground_opaque:
 LD DE,(WS+8)
 LD A,D
 SUB $7E
 RLCA
 RLCA
 RLCA
 ADD A,$A6
 LD D,A
 LD HL,WS+64
 LD B,8
foreground_opaque_row:
 LD A,(HL)
 AND 7
 JR Z,foreground_black_ink
 LD A,(HL)
 AND $38
 JR NZ,foreground_next
 LD A,(DE)
 CP $FF
 JR NZ,foreground_visible
 JR foreground_next
foreground_black_ink:
 LD A,(HL)
 AND $38
 JR Z,foreground_visible
 LD A,(DE)
 OR A
 JR NZ,foreground_visible
foreground_next:
 INC HL
 INC D
 DJNZ foreground_opaque_row
 SCF
 RET
foreground_visible:
 OR A
 RET
opaque_foreground:
 LD HL,(WS+8)
 LD A,H
 ADD A,3
 LD H,A
 BIT 5,(HL)
 JR Z,opaque_not_dictionary
 SET 6,(HL)
opaque_not_dictionary:
 JP compose_done
; Resolve the foreground pair once per cell. No shared temporary survives
; STOCK_COLOUR; this private eight-byte row is protected by the actor guard.
read_old_row:
 LD HL,(WS+8)
 LD A,H
 ADD A,3
 LD H,A
 LD A,(HL)
 LD B,A
 LD A,H
 SUB 9
 LD H,A
 LD C,(HL)
 BIT 5,B
 JR NZ,old_dictionary
 BIT 6,B
 JR NZ,old_terrain
 LD A,C
 AND $7F
 LD HL,WS+64
 LD B,8
old_flat:
 LD (HL),A
 INC HL
 DJNZ old_flat
 RET
old_dictionary:
 LD A,B
 AND $1C
 RRCA
 RRCA
 LD D,A
 LD E,C
 PUSH BC
 CALL PALETTE_READ
 POP BC
 JR old_copy
old_terrain:
 LD A,C
 AND $7F
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,$FBD0
 ADD HL,DE
old_copy:
 LD DE,WS+64
 LD A,B
 AND $A0
 CP $A0
 JR Z,old_reverse
 LD BC,8
 LDIR
 RET
old_reverse:
 LD BC,7
 ADD HL,BC
 LD B,8
old_reverse_loop:
 LD A,(HL)
 LD (DE),A
 DEC HL
 INC DE
 DJNZ old_reverse_loop
 RET
; Exact normal/black pair rules from the TAP Bellmite compositor.
blend_row:
 ; Equal pairs are frequent between adjacent Bellmite spheres. Preserve the
 ; exact TAP result, including its redundant full-coverage colour pair.
 LD A,(WS+49)
 LD C,A
 LD A,(WS+51)
 CP C
 JR NZ,blend_different
 LD A,C
 AND $38
 JR Z,equal_black_paper
 LD A,C
 AND 7
 RET NZ
 LD A,(WS+48)
 OR A
 RET Z
 CP $FF
 JP Z,replace_row
 LD A,(WS+50)
 LD B,A
 LD A,(WS+48)
 AND B
 LD (WS+52),A
 OR A
 RET NZ
 LD A,(WS+48)
 CPL
 LD (WS+52),A
 LD A,C
 RRCA
 RRCA
 RRCA
 AND 7
 JR equal_full_colour
equal_black_paper:
 LD A,C
 AND 7
 JP Z,replace_row
 LD A,(WS+48)
 CP $FF
 RET Z
 OR A
 JP Z,replace_row
 LD A,(WS+50)
 LD B,A
 LD A,(WS+48)
 OR B
 CP $FF
 JR Z,equal_full_ink
 LD (WS+52),A
 RET
equal_full_ink:
 LD A,C
 AND 7
equal_full_colour:
 LD C,A
 RLCA
 RLCA
 RLCA
 OR C
 LD (WS+53),A
 RET
blend_different:
 LD A,(WS+49)
 AND $38
 JR Z,old_black_paper
 LD A,(WS+49)
 AND 7
 RET NZ
 LD A,(WS+49)
 RRCA
 RRCA
 RRCA
 AND 7
 LD (WS+54),A
 LD A,(WS+48)
 CPL
 LD (WS+55),A
 JR foreground_ready
old_black_paper:
 LD A,(WS+49)
 AND 7
 JP Z,replace_row
 LD (WS+54),A
 LD A,(WS+48)
 LD (WS+55),A
foreground_ready:
 LD A,(WS+55)
 OR A
 JP Z,replace_row
 CP $FF
 RET Z
 CALL source_mask
 LD (WS+15),A
 LD C,A
 LD A,(WS+55)
 OR C
 CP $FF
 JR Z,combined_pair
 LD A,(WS+49)
 AND $38
 JR Z,fill_ink
 LD A,(WS+15)
 CPL
 LD C,A
 LD A,(WS+48)
 AND C
 LD (WS+52),A
 RET
fill_ink:
 LD A,(WS+48)
 OR C
 LD (WS+52),A
 RET
combined_pair:
 LD A,(WS+51)
 AND $38
 JR Z,back_ink
 LD A,(WS+51)
 AND 7
 JR Z,back_paper
 LD A,(WS+50)
 LD C,A
 LD A,(WS+55)
 OR C
 CP $FF
 JR Z,back_ink
back_paper:
 LD A,(WS+51)
 RRCA
 RRCA
 RRCA
 AND 7
 JR back_colour_ready
back_ink:
 LD A,(WS+51)
 AND 7
back_colour_ready:
 RLCA
 RLCA
 RLCA
 LD C,A
 LD A,(WS+54)
 OR C
 LD (WS+53),A
 LD A,(WS+55)
 LD (WS+52),A
 RET
replace_row:
 LD A,(WS+50)
 LD (WS+52),A
 LD A,(WS+51)
 LD (WS+53),A
 RET
source_mask:
 LD A,(WS+51)
 AND $38
 JR Z,source_black_paper
 LD A,(WS+51)
 AND 7
 LD A,$FF
 RET NZ
 LD A,(WS+50)
 CPL
 RET
source_black_paper:
 LD A,(WS+51)
 AND 7
 RET Z
 LD A,(WS+50)
 RET
 ASSERT $ <= COMPOSITOR_CODE+2048
