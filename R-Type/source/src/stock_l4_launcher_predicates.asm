 ORG PREDICATE_CODE
 JP cell_owner
 JP neighbour_owner
cell_owner:
 LD A,(DE)
 CALL FILTER_CODE
 OR A
 RET NZ
 JP $8F0B
neighbour_owner:
 INC E
 LD A,(DE)
 DEC E
 JP FILTER_CODE
