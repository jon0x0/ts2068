from pathlib import Path
import sys,json,shutil,re,subprocess,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/l1_head32_r110';O=R/'build/fullgame/l1_ghost_r113';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(s in p.name for s in ['l1_','.home.','validation','route','native_jump']):shutil.copy2(p,O/p.name)
for name in ['generic_manifest.json','walker_runtime.json','global_tags.json']:shutil.copy2(B/name,O/name)
metas=json.loads((B/'generic_manifest.json').read_text());meta=next(x for x in metas if x['level']==1);walk=json.loads((B/'walker_runtime.json').read_text());w=next(x for x in walk if x['level']==1);oldsy=w['extension'];oldimage=(B/'L1_runtime_image.bin').read_bytes();raw=bytearray((B/'L1_runtime_art.bin').read_bytes());base=w['assets'][0]['pointer'];A=R/'build/graphics/walker_choice_r90'
# The original pre-expanded cache only held IDs21..25,201..204. Every one is
# redirected by the runtime's id_map and every active table pointer uses bank5 art.
# Keep a zero-filled preload block of identical3024byte size for initialization;
# no active sprite points into it. Preserve original packet for audit/recovery.
b=bytearray((B/'level01_region.bin').read_bytes());oldbytes=bytes(b);table=w['preload_table'];assert b[table]==1;oldcacheptr=int.from_bytes(b[table+1:table+3],'little');oldcache=unpack(b[oldcacheptr:]);assert len(oldcache)==w['original_preload_bytes']==3024
oldmaps=oldimage[oldsy['id_map']-0xa000:oldsy['id_map']-0xa000+256];assert all(oldmaps[i]for i in [21,22,23,24,25,201,202,203,204]);assert all(0xa900<=a['pointer']<0xc000 for a in w['assets'])
(O/'unused_original_cache.bin').write_bytes(oldcache)
import zipfile,hashlib
z=zipfile.ZipFile(R/'convref/rtype-l1-ghost-assets.zip');assert z.testzip() is None;choice=json.loads(z.read('choices.json'));assert choice['families']['ghost']['source']['id']=='arcade';assert choice['families']['ghost']['settings']['width']==choice['families']['ghost']['settings']['height']==32
(O/'selected_ghost_choices.json').write_text(json.dumps(choice,indent=2));oldbase=base;base=0xa870
for a in w['assets']:a['pointer']+=base-oldbase
for i in range(3):
 v=z.read(f'ghost/frame_{i:02d}.pairs.bin');assert len(v)==256 and all(a&192==0 for a in v[1::2]);ptr=base+len(raw);raw.extend(v);w['assets'].append(dict(level=1,key='ghost32',frame=i,id=180+i,name=f'L1_ghost32_{i}',size=[32,32],pointer=ptr,bytes=256,source=f'arcade{450+i*2}palette6',choice='exact user ZIP'))
assert base+len(raw)<=0xc000
zero=pack(bytes(len(oldcache)));backup=pack(bytes.fromhex(meta['backup']));start=0x2400;backptr=start+len(zero);pretab=backptr+len(backup);rawptr=pretab+5
s=(B/'L1_walker_extension.asm').read_text().replace(' LD DE,$A900',' LD DE,$A870').replace(' ASSERT $ <= $A900',' ASSERT $ <= $A870');entries=[bytes([a['id'],128|a['size'][0]//8,a['size'][1]//8])+a['pointer'].to_bytes(2,'little')*4 for a in w['assets']];mapping=bytearray(oldmaps)
for i in range(3):mapping[35+i]=180+i
s=re.sub(r'sprite_table:\n.*?id_map:', 'sprite_table:\n DB '+','.join(map(str,b''.join(entries)+b'\0'))+'\nid_map:',s,flags=re.S);s=re.sub(r'id_map:\n.*?actor_phases:', 'id_map:\n DB '+','.join(map(str,mapping))+'\nactor_phases:',s,flags=re.S);oldrawptr=int.from_bytes(oldimage[oldsy['load_new_art']-0xa000+5:oldsy['load_new_art']-0xa000+7],'little');s=s.replace(f' LD HL,${oldrawptr:04X}',f' LD HL,${rawptr:04X}')
lines=[]
for line in s.splitlines():
 if line.strip().startswith('DB '):
  vals=line.strip()[3:].split(',');lines.extend(' DB '+','.join(vals[k:k+64])for k in range(0,len(vals),64))
 else:lines.append(line)
p=O/'L1_walker_extension';p.with_suffix('.asm').write_text('\n'.join(lines));exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';r=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
motion=oldimage[:oldsy['restore_native_bank5']-0xa000];pat=b'\x21'+meta['backup_ptr'].to_bytes(2,'little');assert motion.count(pat)==1;motion=motion.replace(pat,b'\x21'+backptr.to_bytes(2,'little'));assert sy['sprite_hook']==oldsy['sprite_hook'];image=motion+p.with_suffix('.bin').read_bytes();guard_start=0xa000+len(image);assert guard_start<=base;guard=bytes([0xa7])*(base-guard_start);image+=guard;packed=pack(raw);ip=rawptr+len(packed);packet=pack(image);end=ip+len(packet);assert end<=0x3a00
b[start:0x3a00]=bytes(0x3a00-start);b[start:backptr]=zero;b[backptr:pretab]=backup;b[pretab:rawptr]=bytes([1])+start.to_bytes(2,'little')+bytes.fromhex('00c0');b[rawptr:ip]=packed;b[ip:end]=packet
cs=meta['cache_symbols'];q=b.find(b'\xdd\x21'+table.to_bytes(2,'little'),cs['preload'],cs['install_motion']);assert q>=0;b[q+2:q+4]=pretab.to_bytes(2,'little');q2=b.find(b'\x21'+meta['motion_ptr'].to_bytes(2,'little'),cs['install_motion'],0xdf30);assert q2>=0;b[q2+1:q2+3]=ip.to_bytes(2,'little');q3=b.find(b'\xc3'+oldsy['load_new_art'].to_bytes(2,'little'),cs['install_motion'],0xdf30);assert q3>=0;b[q3+1:q3+3]=sy['load_new_art'].to_bytes(2,'little');assert unpack(b[rawptr:])==raw and unpack(b[ip:])==image and unpack(b[backptr:])==bytes.fromhex(meta['backup'])
(O/'level01_region.bin').write_bytes(b);(O/'L1_runtime_art.bin').write_bytes(raw);(O/'L1_runtime_image.bin').write_bytes(image);meta.update(motion_ptr=ip,motion_image_bytes=len(image),backup_ptr=backptr,walker_extension=sy);w.update(extension=sy,motion_ptr=ip,immutable_end=end,runtime_bytes=len(image),art_bytes=len(raw),preload_table=pretab);w['groups'].append(dict(level=1,key='ghost32',original=[35,36,37],base=180,count=3,size=[32,32],native_pose_order=True));(O/'walker_runtime.json').write_text(json.dumps(walk,indent=2));(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));(O/'ghost_contract.json').write_text(json.dumps(dict(guard_start=guard_start,guard_bytes=len(guard),artbase=base,source_zip_sha256=hashlib.sha256((R/'convref/rtype-l1-ghost-assets.zip').read_bytes()).hexdigest(),end=end,rawptr=rawptr,imageptr=ip,artend=base+len(raw),imageend=0xa000+len(image),zero_cache_bytes=len(oldcache),unreferenced_cache_ids=[21,22,23,24,25,201,202,203,204],backup_ptr=backptr,preload_table_operand=q+2,install_operand=q2+1,warmup_operand=q3+1,native_source_unchanged=b[0xa000:0xc000]==oldbytes[0xa000:0xc000]),indent=2))
for name in ['LEVEL01.TAP','START01.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in [0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
oldlabel=b'R110 PREPARING  ';new=b'R113 PREPARING  '
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(oldlabel,new))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 size=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+size]).replace(oldlabel,new);check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+size]=block;at+=size+2
p.write_bytes(v)
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_l1_fire','verify_l1_nofire']:
 s=(R/f'scripts/{stem}_r110.mjs').read_text().replace('l1_head32_r110','l1_ghost_r113').replace('boss_motion_fixture_r110','boss_motion_fixture_r113');(R/f'scripts/{stem}_r113.mjs').write_text(s)
print('Exact chosen3pose ghost32; packedend',hex(end),'artbase',hex(base),'artend',hex(base+len(raw)),'guard',len(guard),'bytes')
