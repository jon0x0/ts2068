from pathlib import Path
import sys,json,shutil,subprocess,hashlib,base64,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from build_rocket_fix import code
B=R/'build/fullgame/l2_roles_restore_r127';O=R/'build/fullgame/l2_orientations_r128';G=R/'build/graphics/l2_orientations_r128';O.mkdir(exist_ok=True);G.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.json','.sym','.asm']and not any(s in p.name for s in ['validation','approach','trace','probe','mismatch','.home.','native_jump','final_l2','expected','actual','boss_ceasefire','boss_background','boss_stop','reveal_paint','release_manifest']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level02_region.bin').read_bytes());ct=json.loads((B/'L2_actor_contract.json').read_text());image=bytearray((B/'L2_runtime_image.bin').read_bytes());meta=json.loads((B/'generic_manifest.json').read_text());m=next(v for v in meta if v['level']==2)
captured=[0,2,1,2,1,3,3,3,2,0];normalize=[x^3 for x in captured];assert normalize==[3,1,2,1,2,0,0,0,1,3]
source=json.loads((R/'build/graphics/l2_review_r118/data.json').read_text())['scorpion']['sources'][0]['frames'];groups=[0,0,2,3,0,2,0,3,8,3]
def rgba(f):return np.frombuffer(base64.b64decode(f['rgba']),np.uint8).reshape(f['h'],f['w'],4)
def flip_rgba(a,n):return a[::-1 if n&2 else 1,::-1 if n&1 else 1].copy()
normal_source=[flip_rgba(rgba(f),n)for f,n in zip(source,normalize)]
for i,g in enumerate(groups):assert np.array_equal(normal_source[i],normal_source[g]),('Source orientation family mismatch',i,g)
assert np.array_equal(rgba(source[3])[::-1],rgba(source[9]))
def transform(v,n):
 a=np.frombuffer(v[:400],np.uint8).reshape(5,40,2).copy()
 if n&1:
  a=a[::-1].copy();a[:,:,0]=np.array([int(f'{int(x):08b}'[::-1],2)for x in a[:,:,0].ravel()],np.uint8).reshape(5,40)
 if n&2:a=a[:,::-1].copy()
 return a.tobytes()+v[400:]
changes=[]
for key in ['scorpion_base2','scorpion_delta5']:
 p=ct['pieces'][key];raw=transform(bytes.fromhex(p['raw']),3);v=pack(raw);assert len(v)<=p['bytes'];ptr=p['pointer'];b[ptr:ptr+p['bytes']]=v.ljust(p['bytes'],b'\0');changes.append(dict(key=key,address=ptr,old_bytes=p['bytes'],new_bytes=len(v)));p.update(raw=raw.hex(),bytes=len(v))
ct['scorpion_normalize_flips']=normalize
for a in ct['assets']:
 if a.get('key')=='scorpion':a['normalize_flip']=normalize[a['frame']]
helper=ct['extension']['snake_part'];p=O/'snake_roles';p.with_suffix('.asm').write_text(f'HELPER EQU ${helper:04X}\n'+(R/'src/l2_snake_roles_r128.asm').read_text());exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';q=subprocess.run([str(exe),f'--raw={p}.bin',str(p)+'.asm'],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
image=image[:helper-0xa000]+p.with_suffix('.bin').read_bytes();assert 0xa000+len(image)<=0xa7c0;v=pack(image);ip=ct['imageptr'];assert ip+len(v)<=0x3820,(hex(ip+len(v)),hex(ip));b[ip:0x3820]=v.ljust(0x3820-ip,b'\0');m['motion_image_bytes']=len(image)
ct['snake_body_order']=['spiny']*4+['round']*9;ct['runtime_image_end']=0xa000+len(image);(O/'L2_runtime_image.bin').write_bytes(image);(O/'L2_actor_contract.json').write_text(json.dumps(ct,indent=2));(O/'generic_manifest.json').write_text(json.dumps(meta,indent=2))
b[0x8000:0x82b3]=b[0x8000:0x82b3].replace(b'R127 DEBUG',b'R128 DEBUG');(O/'level02_region.bin').write_bytes(b)
for name in ['LEVEL02.TAP','START02.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R127 PREPARING  ',b'R128 PREPARING  '))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+n]).replace(b'R127 PREPARING  ',b'R128 PREPARING  ');check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+n]=block;at+=n+2
p.write_bytes(v)
contract=dict(user_direction_convention='FlipX false=head right; FlipY false=head down',captured_orientation_bits=captured,native_normalize_flips=normalize,canonical_native='head left/up before native runtime flips',changed_packets=changes,all10_exact_exports_retained=True,frame3_resolution='Frame3 is exact vertical flip of Frame9 in64x64 arcade source. With9 false/false,3 is false/true; duplicate false/false entry treated as typo.',source_family_flips_pixel_exact=True,source_zip_sha256=hashlib.sha256((R/'convref/rtype-l2-art-assets_v2.zip').read_bytes()).hexdigest(),snake_body_order=ct['snake_body_order'],head_tail_unchanged=True,separate_native_neck_role=4,head_to_tail_order='head / existing neck segment / four spiny body sections / nine round body sections / tail',runtime_image_end=0xa000+len(image),packed_runtime_end=ip+len(pack(image)),geometry_changed=False)
frames=json.loads((R/'build/graphics/l2_scorpion_all10_r119/orientation_contract.json').read_text())['frames']
for i,f in enumerate(frames):f.update(captured_flip_x=bool(captured[i]&1),captured_flip_y=bool(captured[i]&2),native_normalize_flip=normalize[i])
contract.update(frames=frames,user_confirmed_frame3=True,frame3_resolution='User confirmed FlipX=False,FlipY=True; source3 is also an exact vertical flip of source9.')
for d in [O,G]:(d/'orientation_contract.json').write_text(json.dumps(contract,indent=2))
for stem in ['boss_motion_fixture','verify_cold_l2_fire','verify_native_revisits','verify_l2_boss_revisits','verify_l2_tiles','verify_l2_decode_all','verify_palette_missile','verify_debug_l2','verify_l2_dirty_refresh','verify_l2_background_repair','verify_l2_ceasefire']:
 p=R/f'scripts/{stem}_r127.mjs';s=p.read_text(encoding='utf-8-sig').replace('l2_roles_restore_r127','l2_orientations_r128').replace('boss_motion_fixture_r127','boss_motion_fixture_r128');(R/f'scripts/{stem}_r128.mjs').write_text(s)
print('Changed scorpion packets:',changes);print('Runtimeend',hex(0xa000+len(image)),'packedend',hex(ip+len(pack(image))))
