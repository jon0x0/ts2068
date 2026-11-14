from pathlib import Path
import sys,json,shutil,re,subprocess,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
from pack_optimal_r87 import pack_optimal as pack
from build_reviewed_r72 import phase_rows
from build_rocket_fix import code
B=R/'build/fullgame/highscore_r138';O=R/'build/fullgame/l7_choices_r139';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.json','.asm','.sym']:shutil.copy2(p,O/p.name)
b=bytearray((B/'level07_region.bin').read_bytes());old=bytes(b);walk=json.loads((B/'walker_runtime.json').read_text());w=next(q for q in walk if q['level']==7);metas=json.loads((B/'generic_manifest.json').read_text());meta=next(q for q in metas if q['level']==7);sy=w['extension'];cache=bytearray(6144);t=w['preload_table']
for k in range(b[t]):
 p=int.from_bytes(b[t+1+k*4:t+3+k*4],'little');d=int.from_bytes(b[t+3+k*4:t+5+k*4],'little')-0xc000;v=unpack(b[p:]);cache[d:d+len(v)]=v
cache=cache[:4864];S=R/'build/graphics/l7_wall_assembled/selected';raw=bytearray((B/'L7_runtime_art.bin').read_bytes());base=0xb200;entries=[];assets=[]
# Keep original native pose cadence; repeat the middle of three selected walking poses.
for key,ids,poses in [('walker',[14,15,16,17],[0,1,2,1]),('orb',[35],[0]),('round',[37],[0])]:
 ptrs={}
 for ident,k in zip(ids,poses):
  f=json.loads((S/key/'choices.json').read_text())['families']['walker']['frames'][k];v=(S/key/f'frame_{k:02d}.pairs.bin').read_bytes()
  if k not in ptrs:ptrs[k]=base+len(raw);raw+=v
  ptr=ptrs[k];entries.append(bytes([ident,128|f['width']//8,f['height']//8])+ptr.to_bytes(2,'little')*4);assets.append(dict(id=ident,key=key,frame=k,pointer=ptr,bytes=len(v),size=[f['width'],f['height']]))
assert base+len(raw)<=0xc000
f=S/'emergence';bits=np.frombuffer((f/'frame_00.bits.bin').read_bytes(),np.uint8);attrs=np.frombuffer((f/'frame_00.attrs.bin').read_bytes(),np.uint8);im=np.where(np.unpackbits(bits).reshape(48,24),np.repeat((attrs&7).reshape(48,3),8,1),np.repeat((attrs>>3&7).reshape(48,3),8,1)).astype('uint8')
for k,ptr in enumerate([0xc980,0xcb00,0xcc80,0xce00]):
 v=(f/'frame_00.pairs.bin').read_bytes()+bytes(96)if k==0 else phase_rows(im,k*2,spill=True,normal=True);assert len(v)==384;cache[ptr-0xc000:ptr-0xc000+384]=v
# Repack existing three cache streams and add explicit native-ID entries.
# Select largest prefix fitting existing immutable external slot.
best=None
for split in [752,1008,1280,1536]:
 ext=pack(cache[:split]);mid=pack(cache[split:split+256]);rest=pack(cache[split+256:]);
 if len(ext)<=0xb147-0xaeb1 and len(mid)<=0xab4e-0xa998:
  if best is None or len(rest)<len(best[3]):best=(split,ext,mid,rest)
assert best is not None
split,ext,mid,rest=best;pretab=0x2400+len(rest);rawptr=pretab+13;rawpack=pack(raw[2208:]);auxpack=pack(raw[:2208]);assert len(auxpack)<=0x500;imageptr=rawptr+len(rawpack)
source=(B/'L7_walker_extension.asm').read_text();source=source.replace(' LD HL,$2EE6',' LD HL,$D300').replace(' JP $A199',' JP load_tail');source += f'\nload_tail:\n LD HL,${rawptr:04X}\n LD DE,$BAA0\n CALL $DE4F\n JP $A199\n';imageold=(B/'L7_runtime_image.bin').read_bytes();table=imageold[sy['sprite_table']-0xa000:sy['id_map']-0xa000];assert table[-1]==0;table=table[:-1]+b''.join(entries)+bytes([0]);a=source.index('sprite_table:\n');z=source.index('id_map:\n',a);source=source[:a]+'sprite_table:\n'+'\n'.join(' DB '+','.join(map(str,table[k:k+64]))for k in range(0,len(table),64))+'\n'+source[z:];p=O/'L7_walker_extension';p.with_suffix('.asm').write_text(source);exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';q=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
ns={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};assert ns['sprite_hook']==sy['sprite_hook']and ns['load_new_art']==sy['load_new_art'];image=imageold[:sy['restore_native_bank5']-0xa000]+p.with_suffix('.bin').read_bytes();ip=pack(image);end=imageptr+len(ip);print('capacity',hex(end),'limit3A00',len(rest),len(rawpack),len(ip),split,flush=True);assert end<=0x3a00
b[0xd300:0xd300+len(auxpack)]=auxpack;b[0xaeb1:0xaeb1+len(ext)]=ext;b[0xa998:0xa998+len(mid)]=mid;b[0x2400:0x3a00]=bytes(0x1600);b[0x2400:pretab]=rest;b[pretab:rawptr]=bytes([3])+bytes.fromhex('b1ae00c0')+bytes.fromhex('98a9')+(0xc000+split).to_bytes(2,'little')+bytes.fromhex('0024')+(0xc000+split+256).to_bytes(2,'little');b[rawptr:imageptr]=rawpack;b[imageptr:end]=ip
cs=meta['cache_symbols'];a=b.find(b'\xdd\x21'+t.to_bytes(2,'little'),cs['preload'],cs['install_motion']);assert a>=0;b[a+2:a+4]=pretab.to_bytes(2,'little');a=b.find(b'\x21'+w['motion_ptr'].to_bytes(2,'little'),cs['install_motion'],0xdf30);assert a>=0;b[a+1:a+3]=imageptr.to_bytes(2,'little')
w.update(extension=ns,immutable_end=end,runtime_bytes=len(image),art_bytes=len(raw),preload_table=pretab,motion_ptr=imageptr);w['assets']+=assets;meta.update(motion_ptr=imageptr,motion_image_bytes=len(image),walker_extension=ns,preload_blocks=[[0xaeb1,0xc000],[0xa998,0xc000+split],[0x2400,0xc000+split+256]])
for name,data in [('level07_region.bin',b),('L7_runtime_art.bin',raw),('L7_runtime_image.bin',image),('L7_expected_cache.bin',cache)]:(O/name).write_bytes(data)
(O/'walker_runtime.json').write_text(json.dumps(walk,indent=2));(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));(O/'l7_choices_contract.json').write_text(json.dumps(dict(assets=assets,split=split,rawptr=rawptr,imageptr=imageptr,end=end,native_walker_pose_order=[0,1,2,1],aux_source=[0xd300,0xd300+len(auxpack)],aux_limit=0xd800,wall_unmodified=True,shading_variant_uninstalled=True),indent=2))
for name in['LEVEL07.TAP','START07.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[k*8192+j*1024:k*8192+(j+1)*1024]for k in[0,1,4,5,6,7]for j in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
s=(R/'scripts/boss_motion_fixture_r138.mjs').read_text().replace('highscore_r138','l7_choices_r139');(R/'scripts/boss_motion_fixture_r139.mjs').write_text(s)
