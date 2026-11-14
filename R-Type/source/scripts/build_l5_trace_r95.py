from pathlib import Path
import json,re,subprocess,sys,shutil
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
B=R/'build/fullgame/boss_guard_r94';O=R/'build/fullgame/l5_trace_r95';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(x in p.name for x in ['.home.','failed','trace','scene_','jump_']):shutil.copy2(p,O/p.name)
def asm(name,s):
 p=O/(name+'.asm');p.write_text(s);v=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert v.returncode==0,v.stdout+v.stderr;symbols={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),symbols
core=(B/'core_pairs.bin').read_bytes();sphere=(B/'sphere_pairs.bin').read_bytes();assert len(core)==7040 and len(sphere)==2304
checker,checksy=asm('l5_cache_check',f''' ORG $E340
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 LD A,$DF
 OUT ($F4),A
 LD HL,$2400
 LD BC,7040
 CALL checksum
 LD HL,${sum(core)&65535:04X}
 OR A
 SBC HL,DE
 JR NZ,bad_core
 LD HL,$C000
 LD BC,2304
 CALL checksum
 LD HL,${sum(sphere)&65535:04X}
 OR A
 SBC HL,DE
 JR NZ,bad_spheres
 LD A,$DD
 OUT ($F4),A
 LD A,1
 LD ($E3F1),A
 POP HL
 POP DE
 POP BC
 POP AF
 RET
checksum:
 LD DE,0
sum_loop:
 LD A,E
 ADD A,(HL)
 LD E,A
 LD A,D
 ADC A,0
 LD D,A
 INC HL
 DEC BC
 LD A,B
 OR C
 JR NZ,sum_loop
 RET
bad_core:
 LD A,6
 JR integrity_stop
bad_spheres:
 LD A,7
integrity_stop:
 OUT ($FE),A
 DI
 LD (bad_colour),A
 LD A,$D3
 OUT ($F4),A
 LD HL,$4000
 LD DE,$4001
 LD BC,$17FF
 LD (HL),$FF
 LDIR
 LD A,(bad_colour)
 LD HL,$6000
 LD DE,$6001
 LD BC,$17FF
 LD (HL),A
 LDIR
halt_point:
 HALT
 JR halt_point
bad_colour: DB 0
 ASSERT $ <= $E3F0
''');assert len(checker)<=176
oldsy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/'motion.sym').read_text(),re.I)}
s=(B/'motion.asm').read_text();s=s.replace('entry:\n','entry:\n        LD A,1\n        OUT ($FE),A\n',1);s=s.replace('        CALL PREPARE_CELLS','        LD A,2\n        OUT ($FE),A\n        CALL PREPARE_CELLS\n        LD A,3\n        OUT ($FE),A',1)
s=s.replace('        CALL Z,INIT_CACHE','        CALL Z,INIT_CACHE\n        LD A,($E3F1)\n        OR A\n        CALL Z,$E340',1)
a=s.index('warmup:');s=s[:a]+s[a:].replace('        LD A,($E3F0)','        XOR A\n        LD ($E3F1),A\n        LD A,($E3F0)',1).replace('CALL Z,INIT_CACHE','CALL $DFC0',1);motion,ns=asm('motion',s);assert 0xdc50+len(motion)<=0xdf00
trace,ts=asm('l5_trace_helpers',''' ORG $890A
trace_select:
 PUSH AF
 LD A,4
 OUT ($FE),A
 POP AF
 JP $8C00
trace_copy:
 PUSH AF
 LD A,5
 OUT ($FE),A
 POP AF
 JP $1A6E
 ASSERT $ <= $8920
''');assert len(trace)==18
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());b=b.replace(b'R94 DEBUG',b'R95 DEBUG')
 if n==5:
  assert not any(b[0xe340:0xe3f0]);b[0xe340:0xe340+len(checker)]=checker
  b[0xdc50:0xdf00]=motion+bytes(0xdf00-0xdc50-len(motion))
  for label,start,end in [('warmup',0xdc0,0xdde),('restore_sources',0xd27,0xd2f)]:
   pat=b'\xc3'+oldsy[label].to_bytes(2,'little');q=b.find(pat,start,end);assert q>=0,(label,hex(oldsy[label]));b[q+1:q+3]=ns[label].to_bytes(2,'little')
  assert b[0x8907:0x890a]==bytes.fromhex('c32089');b[0x890a:0x890a+len(trace)]=trace
  for target,label in [(0x8c00,'trace_select'),(0x1a6e,'trace_copy')]:
   pat=b'\xcd'+target.to_bytes(2,'little');q=b.find(pat,0x8920,0x8a00);assert q>=0;b[q+1:q+3]=ts[label].to_bytes(2,'little')
  assert b[0x97b:0x986]==bytes.fromhex('3e84ed47af320090c9ffff');b[0x97b:0x986]=bytes.fromhex('3e84ed47afd3fe320090c9')
 p.write_bytes(b)
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[page*8192+t*1024:page*8192+(t+1)*1024],k)for k,(page,t)in enumerate((page,t)for page in[0,1,4,5,6,7]for t in range(8))))
old=b'R94 PREPARING   ';new=b'R95 TRACE TEST  ';assert len(old)==len(new)
for name in ['demand_loader.bin','launcher.bin']:
 p=O/name;v=p.read_bytes();assert v.count(old)==1;p.write_bytes(v.replace(old,new))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+n]).replace(old,new);crc=0
 for x in block[:-1]:crc^=x
 block[-1]=crc;v[at+2:at+2+n]=block;at+=n+2
p.write_bytes(v)
(O/'trace_legend.json').write_text(json.dumps({'0':'black: cell draw returned','1':'blue: actor phase selection','2':'red: visibility/clip planning','3':'magenta: planning returned','4':'green: cache selection or overlap blending','5':'cyan: native paired-row copy','6':'yellow: expanded core cache failed checksum','7':'white: sphere cache failed checksum','hardware_freeze_unresolved':True},indent=2))
for stem in ['boss_motion_fixture','verify_walker_game','verify_native_revisits','repro_l4_l5_boss','verify_l5_live_guard','profile_l5_active','repro_l5_low_charge']:
 p=R/f'scripts/{stem}_r94.mjs'
 if p.exists():
  t=p.read_text().replace('boss_guard_r94','l5_trace_r95').replace('boss_motion_fixture_r94','boss_motion_fixture_r95').replace('l5_active_r94','l5_active_r95').replace('l5_low_charge_r94','l5_low_charge_r95');(R/f'scripts/{stem}_r95.mjs').write_text(t)
print('R95 trace motion end',hex(0xdc50+len(motion)),'warmup',hex(ns['warmup']),'restore',hex(ns['restore_sources']))
