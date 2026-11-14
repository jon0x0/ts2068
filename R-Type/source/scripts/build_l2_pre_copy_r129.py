from pathlib import Path
import sys,shutil,json,re,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code;from pack_optimal_r87 import pack_optimal as pack
B=R/'build/fullgame/l2_orientations_r128';O=R/'build/fullgame/l2_pre_copy_r129';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.json','.asm','.sym']and not any(s in p.name for s in ['validation','approach','trace','probe','mismatch','.home.','native_jump','final_l2','expected','actual','boss_ceasefire','boss_background','boss_stop','reveal_paint','release_manifest']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level02_region.bin').read_bytes());tc=json.loads((B/'integration_contract.json').read_text());ct=json.loads((B/'L2_actor_contract.json').read_text());image=bytearray((B/'L2_runtime_image.bin').read_bytes());meta=json.loads((B/'generic_manifest.json').read_text());m=next(v for v in meta if v['level']==2);exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
def asm(name,s):
 p=O/name;p.with_suffix('.asm').write_text(s);q=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy
params='dirty_tiles EQU $11C9\nrepair_mode EQU $11CC\nreveal_index EQU $11CD\nsnapshot_saved EQU $11CE\n'+f'REVEAL_COORDS EQU ${tc["kernel_symbols"]["REVEAL_COORDS"]:04X}\nforce_tile_draw EQU $0174\ndraw_background_copy EQU $0183\nreveal_return EQU $0177\n'
v,bs=asm('cached_boss',params+(R/'src/l2_boss_dirty_r129.asm').read_text());assert len(v)<=220;b[0xb002:0xb0de]=v.ljust(220,b'\0')
v,ss=asm('repair_service',params+f'front_done EQU ${bs["front_done"]:04X}\n'+(R/'src/l2_background_repair_service_r129.asm').read_text());assert len(v)<=132;b[0x106c:0x10f0]=v.ljust(132,b'\0');b[0xf80:0xf83]=b'\xcd'+ss['damage_lookup'].to_bytes(2,'little');check,chs=asm('front_check',f'next_cell EQU ${bs["next_cell"]:04X}\n'+(R/'src/l2_front_check_r129.asm').read_text());b[0xa807:0xa816]=check.ljust(15,b'\0')
core=(B/'tile_loader.asm').read_text();old='        LD ($868C),A\n        LD HL,reveal_hook\n        LD ($868D),HL';new=f'        LD ($8689),A\n        LD HL,${ss["precopy"]:04X}\n        LD ($868A),HL';assert old in core;core=core.replace(old,new,1)
old='        LD ($868D),HL\n        POP DE';new='        LD ($868D),HL\n        LD A,$CD\n        LD ($8689),A\n        LD HL,$1400\n        LD ($868A),HL\n        POP DE';assert old in core;core=core.replace(old,new,1)
v,ts=asm('tile_loader',core);assert len(v)<=0x1e0;b[0x3820:0x3a00]=v.ljust(0x1e0,b'\0');b[0x1de:0x1e0]=ts['get_tile'].to_bytes(2,'little');b[0x157b:0x157d]=ts['global_palette'].to_bytes(2,'little');b[0xfa0:0xfa2]=ts['reverse_cache'].to_bytes(2,'little')
old=tc['tile_symbols'];pat=b'\xcd'+old['restore_native'].to_bytes(2,'little');assert image.count(pat)==1;image=image.replace(pat,b'\xcd'+ts['restore_native'].to_bytes(2,'little'));start=m['cache_symbols']['install_motion'];q=b.find(b'\xcd'+old['save_native'].to_bytes(2,'little'),start,0xdf30);assert q>=0;b[q+1:q+3]=ts['save_native'].to_bytes(2,'little');tc['tile_symbols']=ts;ct['extension']['restore_native_bank5']=ts['restore_native']
ip=ct['imageptr'];v=pack(image);assert ip+len(v)<=0x3820;b[ip:0x3820]=v.ljust(0x3820-ip,b'\0');(O/'L2_runtime_image.bin').write_bytes(image);(O/'L2_actor_contract.json').write_text(json.dumps(ct,indent=2));(O/'integration_contract.json').write_text(json.dumps(tc,indent=2));pal=json.loads((B/'palette_contract.json').read_text());pal['global_helper']=ts['global_palette'];(O/'palette_contract.json').write_text(json.dumps(pal,indent=2));br=json.loads((B/'background_repair_contract.json').read_text());br.update(mark=bs,service=ss,precopy_hook=0x8689,original_poll=0x868c,dirty_only=True,copy_bytes=len((O/'cached_boss.bin').read_bytes()));(O/'background_repair_contract.json').write_text(json.dumps(br,indent=2))
b[0x8000:0x82b3]=b[0x8000:0x82b3].replace(b'R128 DEBUG',b'R129 DEBUG');(O/'level02_region.bin').write_bytes(b)
for name in ['LEVEL02.TAP','START02.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R128 PREPARING  ',b'R129 PREPARING  '))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+n]).replace(b'R128 PREPARING  ',b'R129 PREPARING  ');check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+n]=block;at+=n+2
p.write_bytes(v)
for stem in ['boss_motion_fixture','verify_cold_l2_fire','verify_native_revisits','verify_l2_boss_revisits','verify_l2_tiles','verify_l2_oriented_decode','verify_palette_missile','verify_debug_l2','verify_l2_anatomy_gameplay','verify_l2_ceasefire']:
 p=R/f'scripts/{stem}_r128.mjs';s=p.read_text(encoding='utf-8-sig').replace('l2_orientations_r128','l2_pre_copy_r129').replace('boss_motion_fixture_r128','boss_motion_fixture_r129')
 if stem in ['verify_l2_anatomy_gameplay','verify_l2_ceasefire']:s=s.replace("if(didRepair)assert.equal(m.dock[3][cellAt],tag,'Native cell attribute after repair');",'')
 if stem=='boss_motion_fixture':s=s.replace('c.coreBefore.set([0x3a,0x8a,0x7a],0x28c);','c.coreBefore.set([0xcd,0,0x14],0x289);c.coreBefore.set([0x3a,0x8a,0x7a],0x28c);')
 # Export comparison images remain the approved r128 choices.
 s=s.replace('build/graphics/l2_pre_copy_r129','build/graphics/l2_orientations_r128');(R/f'scripts/{stem}_r129.mjs').write_text(s)
print(O,'copier',len((O/'cached_boss.bin').read_bytes()),'precopy',hex(ss['precopy']),'global',hex(ts['global_palette']))
