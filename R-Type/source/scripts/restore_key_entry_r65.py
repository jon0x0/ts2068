from pathlib import Path
p=Path('src/ui_controls_r65.asm');s=p.read_text().replace('        JP Z,done\n        LD BC,$DFFE','        JP Z,title_keys\n        LD BC,$DFFE',1);s+='''
        ORG KEY_ORIGIN
title_keys:
        LD BC,$BFFE
        IN A,(C)
        AND 1
        JP NZ,done
        LD HL,key_return
        PUSH HL
        XOR A
        PUSH AF
        LD HL,$0E11
        PUSH HL
        LD A,UI_MAP
        PUSH AF
        LD HL,$0E13
        PUSH HL
        LD HL,$BF99
        PUSH HL
        XOR A
        PUSH AF
        LD A,9
        JP $0E10
key_return:
        DI
        JP done
        ASSERT $ <= KEY_ORIGIN+64
''';p.write_text(s)
p=Path('scripts/build_ui_r65.py');s=p.read_text();s=s.replace("mapping=0x19 if special else 0x0b", "mapping=0x19 if special else 0x0b;key_origin=0x8f40 if special else 0x3f80")
s=s.replace("UI_MAP EQU ${mapping:02X}\\n", "UI_MAP EQU ${mapping:02X}\\nKEY_ORIGIN EQU ${key_origin:04X}\\n")
s=s.replace("assert origin+len(ui)<= (0x9ff0 if special else f),(len(ui),hex(origin))", "main_len=us['ui_end']-origin;key_len=len(ui)-main_len;assert main_len<=336 and key_len<=64")
s=s.replace('b[origin:origin+len(ui)]=ui;', "b[origin:origin+main_len]=ui[:main_len];b[key_origin:key_origin+key_len]=ui[main_len:];assert b[0x1b03]==0xf5 and b[0x1b12]==0xf1;b[0x1b03]=0xf3;b[0x1b12]=0;")
s=s.replace("'bytes':len(ui)","'bytes':main_len,'key_origin':key_origin,'key_bytes':key_len")
p.write_text(s)
