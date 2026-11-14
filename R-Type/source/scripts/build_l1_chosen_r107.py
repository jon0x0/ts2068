from pathlib import Path
import json,zipfile,base64,shutil,re,subprocess,sys
import numpy as np
from PIL import Image
R=Path.cwd();sys.path.insert(0,str(R/'scripts'))
from pack_optimal_r87 import pack_optimal as pack
from boss_motion_assets_r60 import unpack
from build_rocket_fix import code
B=R/'build/fullgame/full_plume_r104';O=R/'build/fullgame/l1_chosen_r107';O.mkdir(exist_ok=True)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.bin','.asm','.sym','.json'] and not any(s in p.name for s in ['ordinary_','.home.','validation','route']):shutil.copy2(p,O/p.name)
z=zipfile.ZipFile(R/'convref/rtype-l1-walker-snake-assets.zip');assert z.testzip() is None
choices=json.loads(z.read('choices.json'));(O/'selected_choices.json').write_text(json.dumps(choices,indent=2))
walk=json.loads((B/'walker_runtime.json').read_text());w=next(x for x in walk if x['level']==1);metas=json.loads((B/'generic_manifest.json').read_text());meta=next(x for x in metas if x['level']==1)
oldimage=(B/'L1_runtime_image.bin').read_bytes();raw=bytearray((B/'L1_runtime_art.bin').read_bytes());oldbase=w['assets'][0]['pointer'];base=0xa900
for a in w['assets']:
 off=a['pointer']-oldbase
 if a['key']=='round':
  v=z.read(f"walker/frame_{a['frame']:02d}.pairs.bin");assert len(v)==a['bytes']==144;raw[off:off+144]=v
 a['pointer']=base+off
# Native four joint orientations and their two flip flags select actual captured poses.
# Match the open side of each joint using low-frequency occupancy, independent of palette.
d=json.loads((R/'build/graphics/l1_art_converter/data.json').read_text());source=[]
for f in d['snake']['sources'][1]['frames']:
 p=np.frombuffer(base64.b64decode(f['rgba']),np.uint8).reshape(f['h'],f['w'],4);source.append((p[:,:,:3].max(2)>0).astype(float))
def pixels(v):
 a=np.frombuffer(v,np.uint8).reshape(3,24,2);bt=np.unpackbits(a[:,:,0],axis=0).reshape(3,8,24).transpose(2,0,1).reshape(24,24);at=np.repeat(a[:,:,1].T,8,axis=1);return np.where(bt,at&7,(at>>3)&7)
def silhouette(im):
 # Radial sectors describe the gap/open side; rings remove the differing outer scales.
 yy,xx=np.indices((24,24));ang=np.arctan2(yy-11.5,xx-11.5);rad=np.hypot(yy-11.5,xx-11.5);return np.array([im[(rad>=lo)&(rad<hi)&(ang>=-np.pi+k*np.pi/8)&(ang<-np.pi+(k+1)*np.pi/8)].mean() for lo,hi in [(5,9),(9,12)] for k in range(16)])
frames=[z.read(f'snake/frame_{i:02d}.pairs.bin') for i in range(10)];masks=[pixels(v)>0 for v in frames];scores=[];mapping=[]
# Nearest open-side occupancy, reviewed in orientation_mapping.png before publication.
for native in range(4):
 for flip in range(4):
  im=source[native]
  if flip&1:im=im[:,::-1]
  if flip&2:im=im[::-1,:]
  score=[float(((silhouette(im)-silhouette(m))**2).mean()) for m in masks];idx=int(np.argmin(score));mapping.append(idx);scores.append(score)
print("mapping",mapping,flush=True)
for idx,v in enumerate(frames):
 if idx not in mapping:continue
 ident=160+idx;ptr=base+len(raw);raw.extend(v);w['assets'].append(dict(level=1,key='snake',frame=idx,id=ident,name=f'L1_snake_{idx}',size=[24,24],pointer=ptr,bytes=144,export_frame=idx))
assert base+len(raw)<=0xc000
entries=[]
for a in w['assets']:entries.append(bytes([a['id'],0x80|a['size'][0]//8,a['size'][1]//8])+a['pointer'].to_bytes(2,'little')*4)
assert len(set(e[0] for e in entries))==len(entries)
oldsy=w['extension'];s=(B/'L1_walker_extension.asm').read_text();needle=' LD A,($DF3E)\n LD E,A';assert needle in s
s=s.replace(needle,''' LD A,($DF3E)
 CP 16
 JR C,ordinary_hook
 CP 20
 JR NC,ordinary_hook
 SUB 16
 ADD A,A
 ADD A,A
 LD B,A
 LD A,$6D
 OUT ($F4),A
 LD HL,($DF3A)
 INC HL
 INC HL
 INC HL
 LD A,(HL)
 AND 3
 ADD A,B
 LD E,A
 LD A,(HL)
 AND $FC
 LD (HL),A
 LD A,$ED
 OUT ($F4),A
 LD D,0
 LD HL,snake_map
 ADD HL,DE
 LD A,(HL)
 LD ($DF3E),A
 JR hook_done
ordinary_hook:
 LD A,($DF3E)
 LD E,A''')
s=s.replace('sprite_table:', 'snake_map:\n DB '+','.join(str(160+x) for x in mapping)+'\nsprite_table:');s=s.replace(' LD DE,$B000',f' LD DE,${base:04X}');s=re.sub(r'sprite_table:\n.*?id_map:', 'sprite_table:\n DB '+','.join(map(str,b''.join(entries)+b'\0'))+'\nid_map:',s,flags=re.S);s=s.replace(' ASSERT $ <= $B000',f' ASSERT $ <= ${base:04X}')
# Art source stays put; compressed runtime follows the repacked art.
rawptr=int.from_bytes(oldimage[oldsy['load_new_art']-0xa000+5:oldsy['load_new_art']-0xa000+7],'little');packed=pack(raw)
# sjasmplus limits DB lines; split them.
lines=[]
for line in s.splitlines():
 if line.strip().startswith('DB '):
  vals=line.strip()[3:].split(',');lines.extend(' DB '+','.join(vals[k:k+64]) for k in range(0,len(vals),64))
 else:lines.append(line)
s='\n'.join(lines);(O/'L1_walker_extension.asm').write_text(s)
exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';p=O/'L1_walker_extension';r=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
motion=bytearray(oldimage[:oldsy['restore_native_bank5']-0xa000]);pat=b'\xcd'+oldsy['sprite_hook'].to_bytes(2,'little');assert motion.count(pat)==1;motion=motion.replace(pat,b'\xcd'+sy['sprite_hook'].to_bytes(2,'little'));image=bytes(motion)+p.with_suffix('.bin').read_bytes();assert 0xa000+len(image)<=base
packet=pack(image);ip=rawptr+len(packed);end=ip+len(packet);assert end<=0x3a00,(hex(end),len(packed));b=bytearray((B/'level01_region.bin').read_bytes());b[rawptr:0x3a00]=bytes(0x3a00-rawptr);b[rawptr:ip]=packed;b[ip:end]=packet
cs={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/'L1_cache.sym').read_text(),re.I)}
pat=b'\x21'+meta['motion_ptr'].to_bytes(2,'little');q=b.find(pat,cs['install_motion'],0xdf30);assert q>=0;b[q+1:q+3]=ip.to_bytes(2,'little')
pat=b'\xc3'+oldsy['load_new_art'].to_bytes(2,'little');q2=b.find(pat,cs['install_motion'],0xdf30);assert q2>=0;b[q2+1:q2+3]=sy['load_new_art'].to_bytes(2,'little')
assert unpack(b[rawptr:])==raw and unpack(b[ip:])==image
(O/'level01_region.bin').write_bytes(b);(O/'L1_runtime_art.bin').write_bytes(raw);(O/'L1_runtime_image.bin').write_bytes(image)
w.update(extension=sy,motion_ptr=ip,immutable_end=end,runtime_bytes=len(image),art_bytes=len(raw));w['groups'].append(dict(level=1,key='snake',original=[16,17,18,19],base=160,count=10,size=[24,24],orientation_not_gait=True));meta.update(motion_ptr=ip,motion_image_bytes=len(image),walker_extension=sy)
(O/'walker_runtime.json').write_text(json.dumps(walk,indent=2));(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2))
for name in ['LEVEL01.TAP','START01.TAP']:
 parts=[b[k*8192:(k+1)*8192] for k in range(8)]if name.startswith('LEVEL')else[b[page*8192+t*1024:page*8192+(t+1)*1024] for page in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k) for k,v in enumerate(parts)))
old=b'R104 PREPARING  ';new=b'R107 PREPARING  '
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(old,new))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 size=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+size]).replace(old,new);check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+size]=block;at+=size+2
p.write_bytes(v)
(O/'integration_contract.json').write_text(json.dumps(dict(rawptr=rawptr,imageptr=ip,end=end,artbase=base,artend=base+len(raw),imageend=0xa000+len(image),install_operand=q+1,warmup_operand=q2+1,mapping=mapping,scores=scores),indent=2))
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_fire']:
 s=(R/f'scripts/{stem}_r104.mjs').read_text().replace('full_plume_r104','l1_chosen_r107').replace('boss_motion_fixture_r104','boss_motion_fixture_r107');(R/f'scripts/{stem}_r107.mjs').write_text(s)
print('layout',hex(0xa000+len(image)),hex(base),hex(base+len(raw)),hex(end),'mapping',mapping)
