from pathlib import Path
import sys,shutil,json,re,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code;from pack_optimal_r87 import pack_optimal as pack
B=R/'build/fullgame/l2_pre_copy_r129';O=R/'build/fullgame/l2_star_guard_r130';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.json','.asm','.sym']and not any(s in p.name for s in ['validation','approach','trace','probe','mismatch','.home.','native_jump','final_l2','expected','actual','boss_ceasefire','boss_background','boss_stop','reveal_paint','release_manifest']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level02_region.bin').read_bytes());tc=json.loads((B/'integration_contract.json').read_text());ct=json.loads((B/'L2_actor_contract.json').read_text());image=bytearray((B/'L2_runtime_image.bin').read_bytes());meta=json.loads((B/'generic_manifest.json').read_text());m=next(v for v in meta if v['level']==2);exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
def asm(name,s):
 p=O/name;p.with_suffix('.asm').write_text(s);q=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy
params='dirty_tiles EQU $11C9\nrepair_mode EQU $11CC\nreveal_index EQU $11CD\nsnapshot_saved EQU $11CE\n'+f'REVEAL_COORDS EQU ${tc["kernel_symbols"]["REVEAL_COORDS"]:04X}\nforce_tile_draw EQU $0174\ndraw_background_copy EQU $0183\nreveal_return EQU $0177\n'
v,bs=asm('cached_boss',params+(R/'src/l2_boss_dirty_r129.asm').read_text());assert len(v)<=220;b[0xb002:0xb0de]=v.ljust(220,b'\0')
v,hs=asm('star_metadata',(R/'src/l2_star_metadata_r130.asm').read_text());assert len(v)<=21;b[0x11b4:0x11c9]=v.ljust(21,b'\0')
v,gs=asm('star_paths',(R/'src/l2_star_paths_r130.asm').read_text());assert len(v)<=25;b[0x10d7:0x10f0]=v.ljust(25,b'\0')
# No runtime image or asset relocation: use existing native loader padding.
core=(B/'tile_loader.asm').read_text()
core=core.replace('        JP $01F4','        JP $3836',1)
old='        LD A,$3A\n        LD ($868C),A\n        LD HL,$7A8A\n        LD ($868D),HL\n';assert old in core;core=core.replace(old,'')
core=core.replace('        POP DE\n        RET\nsave_native:', '        LD A,$4F\n        OUT ($F4),A\n        CALL $39F2\n        LD A,$6F\n        OUT ($F4),A\n        POP DE\n        RET\nsave_native:')
# Reverse helper ends3836; installer patching tail lives in its18byte padding.
core=core.replace('        DS $3848-$,0', '''
        ORG $3836
        LD HL,$10D7
        LD ($BF12),HL
        LD HL,$11BE
        LD ($BEEB),HL
        JP $39CB
        DS $3848-$,0''')
core=core.replace('        DS $39E0-$,0', '''
        ASSERT $ <= $39CB
        DS $39CB-$,0
        LD A,$CD
        LD ($BF11),A
        LD ($BEEA),A
        JP $01F4
        LD ($BF12),HL
        LD HL,$A70D
        LD ($BEEB),HL
        RET
        DS $39E0-$,0''')
core+='''
        ASSERT $ == $39F2
        LD A,$0A
        LD ($BF11),A
        LD ($BEEA),A
        LD HL,$C0A7
        JP $39D6
        ASSERT $ == $3A00
'''
v,ts=asm('tile_loader',core);assert len(v)==0x1e0;b[0x3820:0x3a00]=v
old=tc['tile_symbols'];b[0x1de:0x1e0]=ts['get_tile'].to_bytes(2,'little');b[0x157b:0x157d]=ts['global_palette'].to_bytes(2,'little');b[0xfa0:0xfa2]=ts['reverse_cache'].to_bytes(2,'little')
start=m['cache_symbols']['install_motion'];q=b.find(b'\xcd'+old['save_native'].to_bytes(2,'little'),start,0xdf30);assert q>=0;b[q+1:q+3]=ts['save_native'].to_bytes(2,'little');assert ts['restore_native']==old['restore_native'];tc['tile_symbols']=ts;(O/'integration_contract.json').write_text(json.dumps(tc,indent=2))
pal=json.loads((B/'palette_contract.json').read_text());pal['global_helper']=ts['global_palette'];(O/'palette_contract.json').write_text(json.dumps(pal,indent=2))
br=json.loads((B/'background_repair_contract.json').read_text());br.update(star_occlusion_columns=[8,31],star_condition_address=0x7a8e,star_paths=gs,copy_bytes=len((O/'cached_boss.bin').read_bytes()),mark=bs,entry={'reveal_hook':0x1160,'done':0x11a4},star_metadata=hs);(O/'background_repair_contract.json').write_text(json.dumps(br,indent=2))
b[0x8000:0x82b3]=b[0x8000:0x82b3].replace(b'R129 DEBUG',b'R130 DEBUG');(O/'level02_region.bin').write_bytes(b)
for name in ['LEVEL02.TAP','START02.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R129 PREPARING  ',b'R130 PREPARING  '))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+n]).replace(b'R129 PREPARING  ',b'R130 PREPARING  ');check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+n]=block;at+=n+2
p.write_bytes(v)
for stem in ['boss_motion_fixture','verify_cold_l2_fire','verify_native_revisits','verify_l2_boss_revisits','verify_l2_tiles','verify_l2_oriented_decode','verify_palette_missile','verify_debug_l2','verify_l2_visible_overlap','verify_l2_visible_ceasefire','verify_l2_overlap_planes']:
 p=R/f'scripts/{stem}_r129.mjs';s=p.read_text(encoding='utf-8-sig').replace('l2_pre_copy_r129','l2_star_guard_r130').replace('boss_motion_fixture_r129','boss_motion_fixture_r130');
 if stem=='boss_motion_fixture':s=s.replace('c.coreBefore.set([0xcd,0,0x14],0x289);','c.coreBefore.set([0x0a,0xa7,0xc0],0x3b11);c.coreBefore.set([0x0a,0x0d,0xa7],0x3aea);c.coreBefore.set([0xcd,0,0x14],0x289);')
 (R/f'scripts/{stem}_r130.mjs').write_text(s)
print(O,'copier',len((O/'cached_boss.bin').read_bytes()))
