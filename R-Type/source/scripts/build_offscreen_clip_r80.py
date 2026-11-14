from pathlib import Path
import shutil,sys,json
R=Path.cwd();B=R/'build/fullgame/world_reset_r79';O=R/'build/fullgame/offscreen_clip_r80';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
meta=json.loads((B/'generic_manifest.json').read_text());report=[]
for n in[2,3,4,6,7,8]:
 rec=next(r for r in meta if r['level']==n);p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());start=rec['motion_ptr'];end=start+rec['motion_image_bytes'];patches=[]
 for old,new in [('3a3cdfcb7f280479f6e04f','3a3cdfe6e0b14f00000000'),('3a3ddfcb7f280478f6e047','3a3ddfe6e0b04700000000')]:
  old=bytes.fromhex(old);new=bytes.fromhex(new);assert len(old)==len(new);at=b.find(old,start,end);assert at>=0 and b.find(old,at+1,end)<0,(n,old.hex());b[at:at+len(old)]=new;patches.append(at)
 p.write_bytes(b);report.append({'level':n,'patches':patches,'size_unchanged':True})
 p=O/f'L{n}_motion.bin'
 if p.exists():p.write_bytes(b[start:start+p.stat().st_size])
 p=O/f'L{n}_motion.asm'
 if p.exists():
  s=p.read_text(encoding='utf-8-sig')
  for reg,addr,label in [('C','MAIN_BC','x_unsigned'),('B','MAIN_BC+1','y_unsigned')]:
   old=f'        LD A,({addr})\n        BIT 7,A\n        JR Z,{label}\n        LD A,{reg}\n        OR $E0\n        LD {reg},A\n'
   new=f'        LD A,({addr})\n        AND $E0\n        OR {reg}\n        LD {reg},A\n        DUP 4\n        NOP\n        EDUP\n';assert old in s;s=s.replace(old,new,1)
  p.write_text(s,encoding='utf-8')
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();(O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)));(O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))
(O/'clipping_patch.json').write_text(json.dumps(report,indent=2));s=(R/'scripts/boss_motion_fixture_r79.mjs').read_text(encoding='utf-8-sig').replace('world_reset_r79','offscreen_clip_r80');(R/'scripts/boss_motion_fixture_r80.mjs').write_text(s,encoding='utf-8')
for stem in ['trace_l3_fragment_actors','verify_boss_game','verify_world_jump','verify_preload_title']:
 s=(R/f'scripts/{stem}_r79.mjs').read_text(encoding='utf-8-sig').replace('boss_motion_fixture_r79','boss_motion_fixture_r80');(R/f'scripts/{stem}_r80.mjs').write_text(s,encoding='utf-8')
print(report)
