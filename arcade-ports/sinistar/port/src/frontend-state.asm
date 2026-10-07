; Two thirty-entry session tables, in units of five points.
; HOME 5ED4..5FFF is retained; radar publication now uses E000..E15E.
front_scores EQU $5ed4
front_today_scores EQU $5f6a
front_entry_two EQU $5e6a
front_magic EQU $5e77
front_score EQU $5e79
front_demo EQU $5e7b
front_finished EQU $7bf0
front_end_tick EQU $7bf1
front_entry EQU $5e7c
 INCLUDE "../build/frontend-font.asm"
