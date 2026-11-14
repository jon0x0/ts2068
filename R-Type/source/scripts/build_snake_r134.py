from pathlib import Path
import sys,json,re,shutil,subprocess,zipfile,hashlib
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/launcher_r133';O=R/'build/fullgame/snake_r134';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(t in p.name for t in ['validation','probe','trace','audit','.home.','expected','actual','release_manifest']):shutil.copy2(p,O/p.name)
z=zipfile.ZipFile(R/'convref/rtype-l4-snake-assets.zip');assert z.testzip()is None;choices=json.loads(z.read('choices.json'));frames=[z.read(f'snake/frame_{i:02d}.pairs.bin')for i in range(3)];assert all(len(f)==144 and all(a&192==0 for a in f[1::2])for f in frames)
# Original silver connectors: native33left,34lower-left,35down. Arcade views2left,1upper-left,0down.
f=frames[1];frames[1]=bytes(v for x in range(3)for y in range(23,-1,-1)for v in f[(x*24+y)*2:(x*24+y)*2+2]);raw=b''.join(frames);split=216;pa=pack(raw[:split]);pb=pack(raw[split:]);assert len(pa)<=0xa9c7-0xa8e4 and len(pb)<=0xb567-0xb474
b=bytearray((B/'level04_region.bin').read_bytes());b[0xa8e4:0xa8e4+len(pa)]=pa;b[0xb474:0xb474+len(pb)]=pb
image=(B/'L4_runtime_image.bin').read_bytes();wm=json.loads((B/'walker_runtime.json').read_text());w=next(v for v in wm if v['level']==4);oldsy=w['extension'];metas=json.loads((B/'generic_manifest.json').read_text());meta=next(v for v in metas if v['level']==4);ct=json.loads((B/'l4_shared_contract.json').read_text());s=(B/'L4_walker_extension.asm').read_text();needle='art_after_preload:\n';assert needle in s;s=s.replace(needle,needle+f''' LD HL,$C8E4
 LD DE,$DA00
 LD BC,{len(pa)}
 CALL decode_home_packet
 LD HL,$D474
 LD DE,${0xda00+split:04X}
 LD BC,{len(pb)}
 CALL decode_home_packet
''',1)
a=s.index('sprite_table:');e=s.index('id_map:',a);table=s[a:e].rstrip();assert table.endswith(',0');table=table[:-2]+','+','.join(str(v)for i in range(3)for v in bytes([187+i,131,3])+(0xda00+i*144).to_bytes(2,'little')*4)+',0\n';s=s[:a]+table+s[e:];mapping=bytearray(image[oldsy['id_map']-0xa000:oldsy['id_map']-0xa000+256]);mapping[33:36]=bytes([189,188,187]);a=s.index('id_map:');e=s.index('actor_phases:',a);s=s[:a]+'id_map:\n DB '+','.join(map(str,mapping))+'\n'+s[e:]
exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
def asm(name,source):
 lines=[]
 for l in source.splitlines():
  if l.strip().startswith('DB '):
   v=l.strip()[3:].split(',');lines.extend(' DB '+','.join(v[k:k+64])for k in range(0,len(v),64))
  else:lines.append(l)
 p=O/name;p.with_suffix('.asm').write_text('\n'.join(lines));q=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy
ext,sy=asm('L4_walker_extension',s);prefix=bytearray(image[:oldsy['restore_native_bank5']-0xa000])
for name in ['fast_synth_entry']:
 pat=b'\xc3'+oldsy[name].to_bytes(2,'little');assert prefix.count(pat)==1;prefix=prefix.replace(pat,b'\xc3'+sy[name].to_bytes(2,'little'))
for name,op,lo,hi in [('fast_visibility',0xcd,0xdc50,0xdf50),('fast_same_pair',0xc3,0xdf50,0xe000)]:
 p=b.find(bytes([op])+oldsy[name].to_bytes(2,'little'),lo,hi);assert p>=0;b[p+1:p+3]=sy[name].to_bytes(2,'little')
vis_entry=0xa000+len(prefix)+len(ext);vs=re.sub(r'ORG \$[0-9a-fA-F]+',f'ORG ${vis_entry:04X}',(B/'L4_weakpoint_visibility.asm').read_text(),count=1);vis,_=asm('L4_weakpoint_visibility',vs);coord_entry=vis_entry+len(vis);oldcoord=int(re.search(r'ORG \$([0-9A-Fa-f]+)',(B/'L4_weakpoint_coordinates.asm').read_text())[1],16);cs=re.sub(r'ORG \$[0-9a-fA-F]+',f'ORG ${coord_entry:04X}',(B/'L4_weakpoint_coordinates.asm').read_text(),count=1);coord,_=asm('L4_weakpoint_coordinates',cs);pat=b'\xcd'+oldcoord.to_bytes(2,'little');assert prefix.count(pat)==1;prefix=prefix.replace(pat,b'\xcd'+coord_entry.to_bytes(2,'little'));newimage=bytes(prefix)+ext+vis+coord;assert 0xa000+len(newimage)<=0xa9c7
packet=pack(newimage);ip=ct['imageptr'];assert ip+len(packet)<=0x3a00,(hex(ip+len(packet)),len(packet));b[ip:0x3a00]=packet+bytes(0x3a00-ip-len(packet));b[0xa01:0xa03]=vis_entry.to_bytes(2,'little');assert unpack(b[0xa8e4:])==raw[:split] and unpack(b[0xb474:])==raw[split:]
(O/'level04_region.bin').write_bytes(b);(O/'L4_runtime_image.bin').write_bytes(newimage);(O/'L4_snake_art.bin').write_bytes(raw)
for i in range(3):w['assets'].append(dict(level=4,key='snake',frame=i,id=187+i,size=[24,24],pointer=0xda00+i*144,bytes=144,name=f'L4_snake_{i}',flipY=i==1,source='convref/rtype-l4-snake-assets.zip'))
w['groups'].append(dict(level=4,key='snake',original=[33,34,35],base=187,count=3,size=[24,24],native_pose_order=[2,1,0],orientation_flipY=[False,True,False]));w.update(extension=sy,runtime_bytes=len(newimage),immutable_end=ip+len(packet),weakpoint_helper=vis_entry,weakpoint_coordinates=coord_entry,art_bytes=w['art_bytes']+432);w['asset_segments'].append(dict(file='L4_snake_art.bin',base=0xda00,bytes=432));meta.update(walker_extension=sy,motion_image_bytes=len(newimage));ct.update(bank1_end=ip+len(packet),code_end=0xa000+len(newimage));ct['reused_native_sources'].update(ghost=[19,20,21],snake=[33,34,35]);(O/'walker_runtime.json').write_text(json.dumps(wm,indent=2));(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));ct.update(snake_bank=6,snake_raw_start=0xda00,snake_raw_end=0xdbb0,aux_order='Boss preload then snake into DOCK6 DA00..DBB0; existing launcher/prefix/aux then main remainder last');(O/'l4_shared_contract.json').write_text(json.dumps(ct,indent=2));(O/'snake_contract.json').write_text(json.dumps(dict(native=[33,34,35],runtime=[189,188,187],source_frame=[2,1,0],flipY=[False,True,False],base=0xda00,end=0xdbb0,packets=[[0xa8e4,0xa8e4+len(pa)],[0xb474,0xb474+len(pb)]],split=split,code_end=ct['code_end'],packed_end=ct['bank1_end'],choices=choices['families']['snake']['settings'],package_sha256=hashlib.sha256((R/'convref/rtype-l4-snake-assets.zip').read_bytes()).hexdigest()),indent=2))
for name in ['LEVEL04.TAP','START04.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
(O/'L4_expected_cache.bin').write_bytes((B/'L4_expected_cache.bin').read_bytes())
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_launcher','probe_l4_damage','verify_launcher_runtime']:
 s=(R/f'scripts/{stem}_r133.mjs').read_text().replace('launcher_r133','snake_r134').replace('boss_motion_fixture_r133','boss_motion_fixture_r134');(R/f'scripts/{stem}_r134.mjs').write_text(s)
print(hex(ct['code_end']),hex(ct['bank1_end']),len(pa),len(pb))
