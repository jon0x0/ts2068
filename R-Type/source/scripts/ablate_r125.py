from pathlib import Path
import sys,json,shutil,subprocess,re
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
B=R/'build/fullgame/l2_complete_r124';O=R/'build/fullgame/l2_scroll_projectile_r125';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.json','.asm','.sym']and not any(s in p.name for s in ['validation','approach','probe','trace','mismatch','.home.','native_jump','final_l2']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level02_region.bin').read_bytes());ct=json.loads((B/'integration_contract.json').read_text());defs=f'row_palette EQU ${ct["kernel_symbols"]["row_palette"]:04X}\nrow_cache EQU ${ct["kernel_symbols"]["row_cache"]:04X}\n'
p=O/'scroll_projectile';p.with_suffix('.asm').write_text(defs+(R/'src/l2_scroll_projectile_r125.asm').read_text());exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';r=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr
# Assemble each disjoint ORG separately: no gap-filling over live code.
s=(R/'src/l2_scroll_projectile_r125.asm').read_text();sym={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
for i,section in enumerate(s.split('        ORG ')[1:]):
 src='        ORG '+section;addr=int(section.splitlines()[0].strip()[1:],16);q=O/f'patch{i}';q.with_suffix('.asm').write_text(defs+''.join(f'{k} EQU ${v:04X}\n'for k,v in sym.items()if k not in ['row_palette','row_cache']and f'{k}:'not in src)+src);r=subprocess.run([str(exe),f'--raw={q}.bin',str(q)+'.asm'],capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr;v=q.with_suffix('.bin').read_bytes();b[addr:addr+len(v)]=v
# Restore live global actor/projectile palette in verified L2-only DOCK6 gap.
old=(R/'build/fullgame/l2_integrated_r123/level02_region.bin').read_bytes();assert all(x==255 for x in b[0xd920:0xdc40])or b[0xd940:0xdc40]==old[0xd940:0xdc40]
b[0xd940:0xdc40]=old[0x1b20:0x1e20]
assert b[0x157a:0x157e]==bytes.fromhex('01201b09');b[0x157a:0x157e]=bytes.fromhex('01201b09')
(O/'level02_region.bin').write_bytes(b);(O/'scroll_projectile_contract.json').write_text(json.dumps({'symbols':sym,'global_palette':[0xd940,0xdc40],'helper':[0xd920,0xd940],'source_sha256':__import__('hashlib').sha256(old[0x1b20:0x1e20]).hexdigest(),'native_scratch_d910_preserved':True,'global_rows':96},indent=2))
for name in ['LEVEL02.TAP','START02.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R124 PREPARING  ',b'R125 PREPARING  '))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+n]).replace(b'R124 PREPARING  ',b'R125 PREPARING  ');check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+n]=block;at+=n+2
p.write_bytes(v)
for stem in ['boss_motion_fixture','verify_cold_l2_fire','verify_native_revisits','verify_l2_boss_revisits','verify_l2_decode','verify_l2_tiles','trace_l2_reveal','probe_l2_full']:
 p=R/f'scripts/{stem}_r124.mjs';s=p.read_text(encoding='utf-8-sig').replace('l2_complete_r124','l2_scroll_projectile_r125').replace('boss_motion_fixture_r124','boss_motion_fixture_r125');(R/f'scripts/{stem}_r125.mjs').write_text(s)
print('r125 built',sym)

