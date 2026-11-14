from pathlib import Path
import json,sys,shutil,re,subprocess,zipfile,hashlib
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/boss_targets_r132';O=R/'build/fullgame/launcher_r133';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(t in p.name for t in ['validation','probe','trace','audit','.home.','expected','actual','release_manifest']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level04_region.bin').read_bytes());old=bytes(b);raw=(B/'L4_runtime_art.bin').read_bytes();image=(B/'L4_runtime_image.bin').read_bytes();wmeta=json.loads((B/'walker_runtime.json').read_text());w=next(x for x in wmeta if x['level']==4);metas=json.loads((B/'generic_manifest.json').read_text());meta=next(x for x in metas if x['level']==4);oldsy=w['extension'];ct=json.loads((B/'l4_shared_contract.json').read_text());z=zipfile.ZipFile(R/'build/graphics/l4_launcher_selected_r133/selected_assets.zip');art=b''.join(z.read(f'launcher/frame_{i:02d}.pairs.bin')for i in range(3));assert len(art)==432;launch=pack(art);first=pack(raw[:256]);main=pack(raw[256:ct['rawsplit']]);assert len(launch)<=0xa8e4-0xa72e and len(first)<=0xb738-0xb64d
b[0xa72e:0xa72e+len(launch)]=launch;b[0xb64d:0xb64d+len(first)]=first
s=(B/'L4_walker_extension.asm').read_text();a=s.index('art_after_preload:');end=s.index(' LD HL,actor_phases',a)
s=s[:a]+f'''art_after_preload:
 LD HL,$C72E
 LD DE,$B0C0
 LD BC,{len(launch)}
 CALL decode_home_packet
 LD HL,$D64D
 LD DE,$B280
 LD BC,{len(first)}
 CALL decode_home_packet
 LD HL,$C4E9
 LD DE,$BD00
 LD BC,{ct['aux_bytes']}
 CALL decode_home_packet
 LD A,$6F
 OUT ($F4),A
 LD HL,${ct['rawptr']:04X}
 LD DE,$B380
 CALL $DE4F
'''+s[end:]
s+='''
decode_home_packet:
 PUSH DE
 LD DE,$B380
 LDIR
 POP DE
 LD A,$6F
 OUT ($F4),A
 LD HL,$B380
 CALL $DE4F
 LD A,$2F
 OUT ($F4),A
 RET
'''
a=s.index('sprite_table:');end=s.index('id_map:',a);table=s[a:end];table=table.rstrip();assert table.endswith(',0');table=table[:-2]+','+','.join(str(x)for i in range(3)for x in bytes([184+i,131,3])+(0xb0c0+i*144).to_bytes(2,'little')*4)+',0\n';s=s[:a]+table+s[end:]
a=s.index('id_map:');end=s.index('actor_phases:',a);mapping=bytearray(image[oldsy['id_map']-0xa000:oldsy['id_map']-0xa000+256]);mapping[52:55]=bytes([184,185,186]);s=s[:a]+'id_map:\n DB '+','.join(map(str,mapping))+'\n'+s[end:]
exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
def asm(name,s):
 lines=[]
 for l in s.splitlines():
  if l.strip().startswith('DB '):
   v=l.strip()[3:].split(',');lines.extend(' DB '+','.join(v[k:k+64])for k in range(0,len(v),64))
  else:lines.append(l)
 p=O/name;p.with_suffix('.asm').write_text('\n'.join(lines));q=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy
ext,sy=asm('L4_walker_extension',s);prefix=bytearray(image[:oldsy['restore_native_bank5']-0xa000]);assert sy['restore_native_bank5']==oldsy['restore_native_bank5']
for name in ['fast_synth_entry']:
 pat=b'\xc3'+oldsy[name].to_bytes(2,'little');assert prefix.count(pat)==1;prefix=prefix.replace(pat,b'\xc3'+sy[name].to_bytes(2,'little'))
for name,op,lo,hi in [('fast_visibility',0xcd,0xdc50,0xdf50),('fast_same_pair',0xc3,0xdf50,0xe000)]:
 pat=bytes([op])+oldsy[name].to_bytes(2,'little');q=b.find(pat,lo,hi);assert q>=0;b[q+1:q+3]=sy[name].to_bytes(2,'little')
vis_entry=0xa000+len(prefix)+len(ext);vsource=(B/'L4_weakpoint_visibility.asm').read_text();vsource=re.sub(r'ORG \$[0-9A-Fa-f]+',f'ORG ${vis_entry:04X}',vsource,count=1);vis,_=asm('L4_weakpoint_visibility',vsource);coord_entry=vis_entry+len(vis);csource=(B/'L4_weakpoint_coordinates.asm').read_text();csource=re.sub(r'ORG \$[0-9A-Fa-f]+',f'ORG ${coord_entry:04X}',csource,count=1);coord,_=asm('L4_weakpoint_coordinates',csource)
oldcoord=int(re.search(r'ORG \$([0-9A-Fa-f]+)',(B/'L4_weakpoint_coordinates.asm').read_text())[1],16);pat=b'\xcd'+oldcoord.to_bytes(2,'little');assert prefix.count(pat)==1;prefix=prefix.replace(pat,b'\xcd'+coord_entry.to_bytes(2,'little'));newimage=bytes(prefix)+ext+vis+coord;assert 0xa000+len(newimage)<=0xa9c7
ip=ct['rawptr']+len(main);packed=pack(newimage);assert ip+len(packed)<=0x3a00,(hex(ip+len(packed)),len(packed));b[ct['rawptr']:0x3a00]=main+packed+bytes(0x3a00-ip-len(packed));cs=meta['cache_symbols'];pat=b'\x21'+ct['imageptr'].to_bytes(2,'little');p=b.find(pat,cs['install_motion'],0xdf30);assert p>=0;b[p+1:p+3]=ip.to_bytes(2,'little');b[0xa01:0xa03]=vis_entry.to_bytes(2,'little')
assert unpack(b[0xa72e:])==art and unpack(b[0xb64d:])==raw[:256] and unpack(b[ct['rawptr']:])==raw[256:ct['rawsplit']] and unpack(b[ip:])==newimage
(O/'level04_region.bin').write_bytes(b);(O/'L4_runtime_image.bin').write_bytes(newimage);(O/'L4_launcher_art.bin').write_bytes(art)
for i in range(3):w['assets'].append(dict(level=4,key='launcher',frame=i,id=184+i,size=[24,24],pointer=0xb0c0+i*144,bytes=144,name=f'L4_launcher_{i}',source='user choices rtype-l4-twin-launcher-choices.json'))
w['groups'].append(dict(level=4,key='launcher',original=[52,53,54],base=184,count=3,size=[24,24],native_pose_order=True));w.update(extension=sy,runtime_bytes=len(newimage),immutable_end=ip+len(packed),motion_ptr=ip,weakpoint_helper=vis_entry,weakpoint_coordinates=coord_entry);meta.update(walker_extension=sy,motion_ptr=ip,motion_image_bytes=len(newimage));ct.update(imageptr=ip,main_compressed=len(main),bank1_end=ip+len(packed),code_end=0xa000+len(newimage));(O/'walker_runtime.json').write_text(json.dumps(wmeta,indent=2));(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));(O/'l4_shared_contract.json').write_text(json.dumps(ct,indent=2));(O/'launcher_contract.json').write_text(json.dumps(dict(native=[52,53,54],ids=[184,185,186],rawbase=0xb0c0,rawend=0xb270,launcher_packet=[0xa72e,0xa72e+len(launch)],prefix_packet=[0xb64d,0xb64d+len(first)],main_prefix_bytes=256,scratch=[0xb380,0xb4ee],weakpoint_helper=vis_entry,weakpoint_coordinates=coord_entry,code_end=ct['code_end'],packed_end=ct['bank1_end'],choices_sha256=hashlib.sha256((R/'convref/rtype-l4-twin-launcher-choices.json').read_bytes()).hexdigest()),indent=2))
for name in ['LEVEL04.TAP','START04.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_targets']:
 s=(R/f'scripts/{stem}_r132.mjs').read_text().replace('boss_targets_r132','launcher_r133').replace('boss_motion_fixture_r132','boss_motion_fixture_r133');(R/f'scripts/{stem}_r133.mjs').write_text(s)
print('code',hex(ct['code_end']),'packet',hex(ct['bank1_end']),'launcher',len(launch),'prefix',len(first))

ct.update(main_raw_start=0xb380,raw_prefix_bytes=256,aux_order='Copy launcher packet from HOME C72E to B380 scratch, expand B0C0; prefix from HOME D64D via B380 to B280; aux from HOME C4E9 via B380 to BD00; immutable main remainder expands B380..BD00 last.',runtime_source_lifetimes='Boss external preload completes before launcher output overwrites B0C0..B270. All three HOME backup packets survive native restores. B380 scratch is overwritten by the main remainder only after its packets are consumed.',reused_native_sources={'head':[5,6,7,8,9],'small':[14,15,16,17,18],'round':[28,29,30,31],'launcher':[52,53,54]})
w.update(art_bytes=len(raw)+len(art),asset_segments=[dict(file='L4_runtime_art.bin',base=0xb280,bytes=len(raw)),dict(file='L4_launcher_art.bin',base=0xb0c0,bytes=len(art))])
(O/'l4_shared_contract.json').write_text(json.dumps(ct,indent=2));(O/'walker_runtime.json').write_text(json.dumps(wmeta,indent=2))
