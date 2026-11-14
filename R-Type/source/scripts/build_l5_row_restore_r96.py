from pathlib import Path
import json,re,subprocess,sys,shutil
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
B=R/'build/fullgame/l5_bank_guard_r93';O=R/'build/fullgame/l5_row_restore_r96';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(x in p.name for x in ['.home.','failed','trace','scene_','jump_']):shutil.copy2(p,O/p.name)
def asm(name,s):
 p=O/(name+'.asm');p.write_text(s);v=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert v.returncode==0,v.stdout+v.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy
oldcache=(R/'src/l5_preshift_cache.asm').read_text();current=(R/'src/l5_cell_plans.asm').read_text();cache_source=oldcache[:oldcache.index('init_cache:')]+current[current.index('init_cache:'):];cache,cs=asm('cache',cache_source);assert len(cache)<=0x300
oldsy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/'motion.sym').read_text(),re.I)}
s=(B/'motion.asm').read_text();s=s.replace('INIT_CACHE EQU $8DF7',f'INIT_CACHE EQU ${cs["init_cache"]:04X}');assert s.count('        CALL PREPARE_CELLS')==1;s=s.replace('        CALL PREPARE_CELLS','        ; Restored r58 selector computes each requested row at draw time.');motion,ms=asm('motion',s);assert 0xdc50+len(motion)<=0xdf00
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());b=b.replace(b'R38 DEBUG',b'R96 DEBUG')
 if n==5:
  q=b.find(bytes.fromhex('cdf61a'),0x897e,0x899d);assert q>=0;b[q:q+3]=bytes(3) # Empty row now skips metadata just as a preplanned54cell did.
  b[0x8c00:0x8f00]=cache+bytes(0x300-len(cache));b[0xdc50:0xdf00]=motion+bytes(0xdf00-0xdc50-len(motion))
  for label,start,end in [('warmup',0xdc0,0xdde),('restore_sources',0xd27,0xd2f)]:
   pat=b'\xc3'+oldsy[label].to_bytes(2,'little');q=b.find(pat,start,end);assert q>=0;b[q+1:q+3]=ms[label].to_bytes(2,'little')
 p.write_bytes(b)
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[page*8192+t*1024:page*8192+(t+1)*1024],k)for k,(page,t)in enumerate((page,t)for page in[0,1,4,5,6,7]for t in range(8))))
old=b'PREPARING GAME  ';new=b'R96 ROW RESTORE ';assert len(old)==len(new)
for name in ['demand_loader.bin','launcher.bin']:
 p=O/name;b=p.read_bytes();assert b.count(old)==1;p.write_bytes(b.replace(old,new))
p=O/'rtype/rt.tap';b=bytearray(p.read_bytes());at=0
while at<len(b):
 size=int.from_bytes(b[at:at+2],'little');v=bytearray(b[at+2:at+2+size]).replace(old,new);c=0
 for x in v[:-1]:c^=x
 v[-1]=c;b[at+2:at+2+size]=v;at+=size+2
p.write_bytes(b)
ref=(R/'build/fullgame/l5_preshift_r58/cache.bin').read_bytes();prefix_len=cs['init_cache']-0x8c00;assert cache[:prefix_len]==ref[:prefix_len],'Restored selector differs from r58'
(O/'row_restore.json').write_text(json.dumps(dict(prefix_identical_r58=True,prefix_bytes=prefix_len,cache_bytes=len(cache),init_cache=cs['init_cache'],motion_bytes=len(motion),warmup=ms['warmup'],restore_sources=ms['restore_sources'],no_prepare_cells_call=True,base='r93',graphics_unchanged=True),indent=2))
for stem in ['boss_motion_fixture','verify_walker_game','verify_native_revisits','stress_l5_boss','repro_l4_l5_boss','profile_l5_active','repro_l5_low_charge']:
 p=R/f'scripts/{stem}_r93.mjs'
 if not p.exists():p=R/f'scripts/{stem}_r94.mjs'
 if p.exists():
  s=p.read_text().replace('l5_bank_guard_r93','l5_row_restore_r96').replace('boss_guard_r94','l5_row_restore_r96').replace('boss_motion_fixture_r93','boss_motion_fixture_r96').replace('boss_motion_fixture_r94','boss_motion_fixture_r96').replace('l5_active_r93','l5_active_r96').replace('l5_low_charge_r94','l5_low_charge_r96');(R/f'scripts/{stem}_r96.mjs').write_text(s)
print('Restored r58 prefix',prefix_len,'cache',len(cache),'motion',len(motion),{k:hex(ms[k])for k in ['warmup','restore_sources']})
