from pathlib import Path
import json,shutil,sys,re,numpy as np
R=Path.cwd();B=R/'build/fullgame/plume_diameter_r103';O=R/'build/fullgame/full_plume_r104';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(v in p.name for v in ['.home.','ordinary_','validation','route','manifest']):shutil.copy2(p,O/p.name)
for n in ['generic_manifest.json','walker_runtime.json','global_tags.json']:shutil.copy2(B/n,O/n)
sys.path.insert(0,str(R/'scripts'));from build_reviewed_r72 import phase_rows;from pack_optimal_r87 import pack_optimal;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
meta=json.loads((B/'generic_manifest.json').read_text());m=next(x for x in meta if x['level']==3);walk=json.loads((B/'walker_runtime.json').read_text());w=next(x for x in walk if x['level']==3);raw=bytearray((B/'L3_runtime_art.bin').read_bytes());oldraw=bytes(raw);rawbase=w['assets'][0]['pointer'];checks=[]
for a in w['assets']:
 if a['key']!='exhaust':continue
 p=R/'build/graphics/full_plume_r104';name=a['name'];attrs=np.frombuffer((p/f'{name}.attrs').read_bytes(),np.uint8).reshape(16,6);bits=np.unpackbits(np.frombuffer((p/f'{name}.bits').read_bytes(),np.uint8)).reshape(16,48);idx=np.where(bits,np.repeat(attrs&7,8,1),np.repeat((attrs>>3)&7,8,1));v=bytearray(phase_rows(idx,spill=False,normal=True));off=a['pointer']-rawbase;assert len(v)==192
 rows=[]
 for y in range(16):
  bt,at=v[5*32+y*2:5*32+y*2+2];rows.append((at&7)if bt&1 else(at>>3)&7)
 assert all(rows),'Plume does not fill nozzle seam';raw[off:off+192]=v;checks.append(dict(frame=a['frame'],mouth_pixels=16,full_plume_replaced=True))
b=bytearray((B/'level03_region.bin').read_bytes());cs={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/'L3_cache.sym').read_text(),re.I)};oldimageptr=m['motion_ptr'];oldimage=(B/'L3_runtime_image.bin').read_bytes();assert unpack(b[oldimageptr:])==oldimage
# Preserve the complete loader/renderer image; only its compressed storage address can move.
loadsym={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/'L3_walker_extension.sym').read_text(),re.I)};org=loadsym['restore_native_bank5'];imageoff=loadsym['load_new_art']-0xa000;rawptr=int.from_bytes(oldimage[imageoff+5:imageoff+7],'little');assert oldimage[imageoff:imageoff+4]==bytes.fromhex('3e6fd3f4')and oldimage[imageoff+4]==0x21
packed=pack_optimal(raw);imageptr=max(oldimageptr,rawptr+len(packed));packet=pack_optimal(oldimage);end=imageptr+len(packet);assert end<=0x3a00
b[rawptr:0x3a00]=bytes(0x3a00-rawptr);b[rawptr:rawptr+len(packed)]=packed;b[imageptr:end]=packet
pat=b'\x21'+oldimageptr.to_bytes(2,'little');q=b.find(pat,cs['install_motion'],0xdf30);assert q>=0;b[q+1:q+3]=imageptr.to_bytes(2,'little');assert unpack(b[rawptr:])==raw and unpack(b[imageptr:])==oldimage
(O/'level03_region.bin').write_bytes(b);(O/'L3_runtime_art.bin').write_bytes(raw);w.update(motion_ptr=imageptr,immutable_end=end);m['motion_ptr']=imageptr;(O/'walker_runtime.json').write_text(json.dumps(walk,indent=2));(O/'generic_manifest.json').write_text(json.dumps(meta,indent=2))
for name in ['LEVEL03.TAP','START03.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[page*8192+t*1024:page*8192+(t+1)*1024]for page in[0,1,4,5,6,7]for t in range(8)]
 (O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
old=b'R103 PREPARING  ';new=b'R104 PREPARING  '
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(old,new))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 size=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+size]).replace(old,new);c=0
 for x in block[:-1]:c^=x
 block[-1]=c;v[at+2:at+2+size]=block;at+=size+2
p.write_bytes(v)
(O/'diameter_contract.json').write_text(json.dumps(dict(passed=True,rawptr=rawptr,oldimageptr=oldimageptr,imageptr=imageptr,end=end,install_operand=q+1,checks=checks,runtime_art_size_unchanged=len(raw)==len(oldraw),runtime_image_unchanged=True),indent=2))
for stem in ['boss_motion_fixture','verify_photo_exhaust_state','verify_native_revisits','verify_cold_fire']:
 p=R/f'scripts/{stem}_r103.mjs';s=p.read_text().replace('plume_diameter_r103','full_plume_r104').replace('boss_motion_fixture_r103','boss_motion_fixture_r104');(R/f'scripts/{stem}_r104.mjs').write_text(s)
print('Complete48x16photo-derived plume; old checkered exhaust removed. Payload end',hex(end))
