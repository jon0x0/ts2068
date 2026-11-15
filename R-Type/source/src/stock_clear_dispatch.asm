; Called at restore_base. Native0/3 are empty; their palette tag is stale.
; Drop only this helper return so legacy restoration returns to the existing
; outer stock_restore wrapper. Preserve all registers, including BC/DE/HL.
 ORG $0F70
 OR A
 JR Z,empty
 CP 3
 RET NZ
empty:
 XOR A
 INC SP
 INC SP
 JP $162F
 ASSERT $ <= $0F80
