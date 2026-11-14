from pathlib import Path
import json,subprocess,sys,shutil,re
R=Path.cwd(); B=R/'build/fullgame/l2_art_r121'; O=R/'build/fullgame/l2_art_r122';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.bin','.json','.asm','.sym'] and '.home.' not in p.name:shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
b=bytearray((B/'level02_region.bin').read_bytes());inks=json.loads((R/'build/graphics/l2_integrate_r119/selected_row_inks.json').read_text())
s=''' ORG $1B20
entry:
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 PUSH IX
 PUSH IY
 LD A,I
 LD A,0
 JP PO,iff_saved
 INC A
iff_saved:
 LD (saved_iff),A
 LD A,($7AA4)
 OR A
 JP Z,done
 LD A,($7A84)
 CP 59
 JR NC,boss
 XOR A
 LD (state),A
 LD (mode),A
 LD (row_y),A
 LD A,160
 LD (rows_left),A
 LD A,1
 LD (start_x),A
 LD HL,terrain_inks
 JR prepare
boss:
 CP 64
 JR NC,stopped
 LD A,1
 LD (state),A
 LD (mode),A
 LD A,($7A84)
 LD C,A
 LD A,64
 SUB C
 ADD A,A
 ADD A,A
 ADD A,8
 LD C,A
 LD A,($7A83)
 LD B,A
 LD A,C
 SUB B
 LD C,A
 LD A,($7A82)
 OR A
 LD A,C
 JR Z,coarse
 DEC A
coarse:
 CP 31
 JP NC,done
 OR A
 JR NZ,left_ok
 INC A
left_ok:
 LD (start_x),A
 JR boss_rows
stopped:
 LD A,(state)
 OR A
 JP Z,done
 CP 3
 JP Z,done
 CP 1
 JR NZ,fade_started
 XOR A
 LD (fade),A
 LD A,2
 LD (state),A
fade_started:
 LD A,2
 LD (mode),A
 LD A,8
 LD (start_x),A
boss_rows:
 LD A,56
 LD (row_y),A
 LD A,104
 LD (rows_left),A
 LD HL,boss_inks
prepare:
 LD (table_ptr),HL
row:
 LD A,(row_y)
 LD C,A
 AND 7
 OR $40
 LD B,A
 LD A,C
 AND $C0
 RRCA
 RRCA
 RRCA
 OR B
 LD H,A
 LD A,C
 AND $38
 RLCA
 RLCA
 LD L,A
 LD A,(start_x)
 ADD A,L
 LD L,A
 PUSH HL
 POP IX
 LD BC,$6000
 ADD HL,BC
 PUSH HL
 POP IY
 LD HL,(table_ptr)
 LD A,(HL)
 INC HL
 LD (table_ptr),HL
 LD (ink),A
 LD A,(start_x)
 LD (column),A
cell:
 LD C,(IY+0)
 PUSH IY
 POP HL
 SET 5,H
 LD B,(HL)
 AND A
 LD A,B
 AND $38
 JR Z,paper_black
 LD A,B
 AND 7
 LD A,C
 JR Z,invert
 LD A,$FF
 JR union_done
invert:
 CPL
 JR union_done
paper_black:
 LD A,B
 AND 7
 LD A,C
 JR NZ,union_done
 XOR A
union_done:
 OR A
 JR Z,next_cell
 LD E,A
 DI
 LD A,(mode)
 CP 2
 JR Z,dissolve
 LD A,(IX+0)
 CP C
 JR NZ,next_cell
 PUSH IX
 POP HL
 SET 5,H
 LD A,(HL)
 CP B
 JR NZ,next_cell
 LD A,E
 LD (IX+0),A
 LD A,(ink)
 LD (HL),A
 JR next_cell
dissolve:
 LD A,(row_y)
 LD D,A
 LD A,(column)
 ADD A,D
 AND 3
 LD D,A
 LD A,(fade)
 CP D
 JR NZ,next_cell
 LD A,(IX+0)
 CP E
 JR NZ,next_cell
 PUSH IX
 POP HL
 SET 5,H
 LD A,(ink)
 CP (HL)
 JR NZ,next_cell
 LD (IX+0),C
 LD (HL),B
next_cell:
 LD A,(saved_iff)
 OR A
 JR Z,no_ei
 EI
no_ei:
 INC IX
 INC IY
 LD A,(column)
 INC A
 LD (column),A
 CP 31
 JP C,cell
 LD A,(row_y)
 INC A
 LD (row_y),A
 LD A,(rows_left)
 DEC A
 LD (rows_left),A
 JP NZ,row
 LD A,(mode)
 CP 2
 JR NZ,done
 LD A,(fade)
 INC A
 LD (fade),A
 CP 4
 JR C,done
 LD A,3
 LD (state),A
done:
 POP IY
 POP IX
 POP HL
 POP DE
 POP BC
 POP AF
 LD A,($7A8A)
 RET
undo:
 LD A,$3A
 LD ($868C),A
 LD HL,$7A8A
 LD ($868D),HL
 RET
saved_iff: DB 0
state: DB 0
fade: DB 0
mode: DB 0
row_y: DB 0
rows_left: DB 0
start_x: DB 0
column: DB 0
ink: DB 0
table_ptr: DW 0
terrain_inks:
 DB TERRAIN
boss_inks:
 DB BOSS
 ASSERT $ <= $1E20
'''.replace('TERRAIN','n DB '.replace('n',chr(10)).join(','.join(map(str,inks['terrain'][i:i+64])) for i in range(0,160,64))).replace('BOSS',','.join(map(str,inks['boss'])))
p=O/'l2_scroll_palette';p.with_suffix('.asm').write_text(s);exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';r=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
v=p.with_suffix('.bin').read_bytes();assert b[0x468c:0x468f]==bytes.fromhex('3a8a7a');# HOME core is installed per level, rather than patching an unused DOCK copy.
b[0x1b20:0x1e20]=v.ljust(768,b'\0');sy={k:int(v,16) for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
inst=next(x for x in json.loads((B/'generic_manifest.json').read_text()) if x['level']==2)['cache_symbols']['install_motion'];end=b.index(bytes.fromhex('c3b2a1'),inst);hook=bytes.fromhex('3ecd328c8621201b228d86');b[end:end+len(hook)+3]=hook+bytes.fromhex('c3b2a1');assert end+len(hook)+3<0xdf30
end=b.index(bytes.fromhex('d1c9'),0x3940,0x3980);b[end:end+5]=b'\xcd'+sy['undo'].to_bytes(2,'little')+bytes.fromhex('d1c9');assert end+5<=0x3980
(O/'level02_region.bin').write_bytes(b)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
for name in ['LEVEL02.TAP','START02.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for stem in ['boss_motion_fixture','probe_l2_full','probe_l2_short','verify_cold_l2_fire','verify_l2_revisits','verify_native_revisits']:
 p=R/f'scripts/{stem}_r121.mjs';s=p.read_text(encoding='utf-8-sig').replace('l2_art_r121','l2_art_r122').replace('boss_motion_fixture_r121','boss_motion_fixture_r122')
 if stem=='boss_motion_fixture':
  s=s.replace('if(!Buffer.from(m.dock[0]).equals(expectedCode[c.region]))',f'if(!Buffer.from(m.dock[0]).map((v,i)=>c.region===1&&i>={sy["saved_iff"]}&&i<{sy["terrain_inks"]}?expectedCode[c.region][i]:v).equals(expectedCode[c.region]))')
 (R/f'scripts/{stem}_r122.mjs').write_text(s,encoding='utf-8')
print('overlay bytes',len(v))



