from pathlib import Path
R=Path.cwd();s=(R/'src/responsive_startup_r62.asm').read_text();s=s.replace('ACTUAL_BANK EQU $D61F','ACTUAL_BANK EQU $D61F\nSTART_ALL EQU $D623')
s=s.replace('        LD (BOOT_FLAG),A\n        INC A','        LD (BOOT_FLAG),A\n        LD (START_ALL),A\n        INC A',1)
s=s.replace('startup_poll:\n','''startup_poll:
        LD A,(START_ALL)
        OR A
        JR NZ,poll_level
        LD BC,$FEFE
        IN A,(C)
        AND 1
        JR NZ,poll_level
        LD B,$BF
        IN A,(C)
        AND 2
        JR NZ,poll_level
        LD A,1
        LD (START_ALL),A
        LD HL,all_queued
        LD DE,$4804
        CALL puts
poll_level:
''',1)
s=s.replace('        LD DE,$50E5','        LD DE,$5003',1)
s=s.replace('        LD A,(TARGET)\n        INC A\n        AND 7','        LD HL,prepare_message\n        LD DE,$5003\n        CALL puts\n        LD A,(TARGET)\n        INC A\n        AND 7',1)
s=s.replace('        LD HL,cold_start_image\n        LD DE,$5E00','        LD A,(START_ALL)\n        LD (cold_start_image+cold_all-cold_start+1),A\n        LD HL,cold_start_image\n        LD DE,$5E00',1)
s=s.replace('        LD ($FDA5),A\n        LD HL,$5B00','        LD ($FDA5),A\ncold_all:\n        LD A,0\n        LD ($FDA6),A\n        LD HL,$5B00',1)
s=s.replace("verify_message: DB 'VERIFYING MEMORY',0", "verify_message: DB 'VERIFYING MEMORY',0\nprepare_message: DB 'PREPARING GAME  ',0\nall_queued: DB 'LOAD ALL QUEUED ',0")
s=s.replace('        LD D,0\n        LD HL,logo_attributes\n        ADD HL,DE','        LD HL,logo_attributes',1)
a=s.index('        LD A,L\n        ADD A,32',s.index('start_restore_col:'));z=s.index('start_attr_nocarry:',a)+len('start_attr_nocarry:');s=s[:a]+'        INC HL\n'+s[z:]
(R/'src/responsive_startup_r66.asm').write_text(s)
s=(R/'src/level_hotkeys_r64.asm').read_text();s=s.replace('        PUSH IX\n        PUSH IY\n','').replace('        POP IY\n        POP IX\n','');s=s.replace('        LD BC,$BFFE\n','''        LD A,($FDA6)
        OR A
        JR Z,poll_l
        XOR A
        LD ($FDA6),A
        JP hot_preload
poll_l:
        LD BC,$BFFE
''',1);(R/'src/level_hotkeys_r66.asm').write_text(s)
# Exact 5x3 text in the existing 32x5 attribute-feedback display.
g={'P':['110','101','110','100','100'],'R':['110','101','110','101','101'],'E':['111','100','110','100','111'],'A':['010','101','111','101','101'],'M':['101','111','111','101','101'],' ':['000']*5}
rows=[''.join(g[c][y]+'0'for c in 'PREP RAM')for y in range(5)];bits=bytes(int(row[i:i+8],2) for row in rows for i in range(0,32,8));s=(R/'src/preload_feedback_r62.asm').read_text();s=s[:s.index('feedback_bits:')]+ 'feedback_bits: DB '+','.join(map(str,bits))+'\n';(R/'src/preload_feedback_r66.asm').write_text(s)
