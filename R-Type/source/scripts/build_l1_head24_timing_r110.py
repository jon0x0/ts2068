from pathlib import Path
import sys,json,shutil,re,subprocess,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/l1_chosen_r107';O=R/'build/fullgame/l1_head24_timing_r110';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(s in p.name for s in ['l1_','.home.','validation','route','native_jump']):shutil.copy2(p,O/p.name)
for name in ['generic_manifest.json','walker_runtime.json','global_tags.json']:shutil.copy2(B/name,O/name)
metas=json.loads((B/'generic_manifest.json').read_text());meta=next(x for x in metas if x['level']==1);walk=json.loads((B/'walker_runtime.json').read_text());w=next(x for x in walk if x['level']==1);oldsy=w['extension'];oldimage=(B/'L1_runtime_image.bin').read_bytes();raw=bytearray((B/'L1_runtime_art.bin').read_bytes());base=w['assets'][0]['pointer'];A=R/'build/graphics/l1_head_c_r109'
# The original pre-expanded cache only held IDs21..25,201..204. Every one is
# redirected by the runtime's id_map and every active table pointer uses bank5 art.
# Keep a zero-filled preload block of identical3024byte size for initialization;
# no active sprite points into it. Preserve original packet for audit/recovery.
b=bytearray((B/'level01_region.bin').read_bytes());oldbytes=bytes(b);table=w['preload_table'];assert b[table]==1;oldcacheptr=int.from_bytes(b[table+1:table+3],'little');oldcache=unpack(b[oldcacheptr:]);assert len(oldcache)==w['original_preload_bytes']==3024
oldmaps=oldimage[oldsy['id_map']-0xa000:oldsy['id_map']-0xa000+256];assert all(oldmaps[i]for i in [21,22,23,24,25,201,202,203,204]);assert all(0xa900<=a['pointer']<0xc000 for a in w['assets'])
(O/'unused_original_cache.bin').write_bytes(oldcache)
for i in range(4):
 attrs=np.frombuffer((A/f'L1_head_{i}.attrs').read_bytes(),np.uint8).reshape(24,3);bits=np.frombuffer((A/f'L1_head_{i}.bits').read_bytes(),np.uint8).reshape(24,3);assert not np.any(attrs&192);v=np.stack([bits.T,attrs.T],axis=2).tobytes();assert len(v)==144;ptr=base+len(raw);raw.extend(v);w['assets'].append(dict(level=1,key='shell32',frame=i,id=176+i,name=f'L1_shell32_{i}',size=[24,24],pointer=ptr,bytes=144,source=f'L6_head_{i}',choice='C exact saved32x32'))
assert base+len(raw)<=0xc000
zero=pack(bytes(len(oldcache)));backup=pack(bytes.fromhex(meta['backup']));start=0x2400;backptr=start+len(zero);pretab=backptr+len(backup);rawptr=pretab+5
s=(B/'L1_walker_extension.asm').read_text();entries=[bytes([a['id'],128|a['size'][0]//8,a['size'][1]//8])+a['pointer'].to_bytes(2,'little')*4 for a in w['assets']];mapping=bytearray(oldmaps)
for i in range(4):mapping[30+i]=176+i
s=re.sub(r'sprite_table:\n.*?id_map:', 'sprite_table:\n DB '+','.join(map(str,b''.join(entries)+b'\0'))+'\nid_map:',s,flags=re.S);s=re.sub(r'id_map:\n.*?actor_phases:', 'id_map:\n DB '+','.join(map(str,mapping))+'\nactor_phases:',s,flags=re.S);oldrawptr=int.from_bytes(oldimage[oldsy['load_new_art']-0xa000+5:oldsy['load_new_art']-0xa000+7],'little');s=s.replace(f' LD HL,${oldrawptr:04X}',f' LD HL,${rawptr:04X}')
lines=[]
for line in s.splitlines():
 if line.strip().startswith('DB '):
  vals=line.strip()[3:].split(',');lines.extend(' DB '+','.join(vals[k:k+64])for k in range(0,len(vals),64))
 else:lines.append(line)
p=O/'L1_walker_extension';p.with_suffix('.asm').write_text('\n'.join(lines));exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';r=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
motion=oldimage[:oldsy['restore_native_bank5']-0xa000];pat=b'\x21'+meta['backup_ptr'].to_bytes(2,'little');assert motion.count(pat)==1;motion=motion.replace(pat,b'\x21'+backptr.to_bytes(2,'little'));assert sy['sprite_hook']==oldsy['sprite_hook'];image=motion+p.with_suffix('.bin').read_bytes();assert 0xa000+len(image)<=base;packed=pack(raw);ip=rawptr+len(packed);packet=pack(image);end=ip+len(packet);assert end<=0x3a00
b[start:0x3a00]=bytes(0x3a00-start);b[start:backptr]=zero;b[backptr:pretab]=backup;b[pretab:rawptr]=bytes([1])+start.to_bytes(2,'little')+bytes.fromhex('00c0');b[rawptr:ip]=packed;b[ip:end]=packet
cs=meta['cache_symbols'];q=b.find(b'\xdd\x21'+table.to_bytes(2,'little'),cs['preload'],cs['install_motion']);assert q>=0;b[q+2:q+4]=pretab.to_bytes(2,'little');q2=b.find(b'\x21'+meta['motion_ptr'].to_bytes(2,'little'),cs['install_motion'],0xdf30);assert q2>=0;b[q2+1:q2+3]=ip.to_bytes(2,'little');q3=b.find(b'\xc3'+oldsy['load_new_art'].to_bytes(2,'little'),cs['install_motion'],0xdf30);assert q3>=0;b[q3+1:q3+3]=sy['load_new_art'].to_bytes(2,'little');assert unpack(b[rawptr:])==raw and unpack(b[ip:])==image and unpack(b[backptr:])==bytes.fromhex(meta['backup'])
(O/'level01_region.bin').write_bytes(b);(O/'L1_runtime_art.bin').write_bytes(raw);(O/'L1_runtime_image.bin').write_bytes(image);meta.update(motion_ptr=ip,motion_image_bytes=len(image),backup_ptr=backptr,walker_extension=sy);w.update(extension=sy,motion_ptr=ip,immutable_end=end,runtime_bytes=len(image),art_bytes=len(raw),preload_table=pretab);w['groups'].append(dict(level=1,key='shell32',original=[30,31,32,33],base=176,count=4,size=[24,24],native_pose_order=True));(O/'walker_runtime.json').write_text(json.dumps(walk,indent=2));(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));(O/'head32_contract.json').write_text(json.dumps(dict(end=end,rawptr=rawptr,imageptr=ip,artend=base+len(raw),imageend=0xa000+len(image),zero_cache_bytes=len(oldcache),unreferenced_cache_ids=[21,22,23,24,25,201,202,203,204],backup_ptr=backptr,preload_table_operand=q+2,install_operand=q2+1,warmup_operand=q3+1,native_data_unchanged=b[0xa000:0xe000]==oldbytes[0xa000:0xe000]),indent=2))
for name in ['LEVEL01.TAP','START01.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in [0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
oldlabel=b'R107 PREPARING  ';new=b'R110 PREPARING  '
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(oldlabel,new))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 size=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+size]).replace(oldlabel,new);check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+size]=block;at+=size+2
p.write_bytes(v)
print('24x24 timing comparator built')
