from pathlib import Path
import sys,json,shutil,re,subprocess,hashlib
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/l2_star_guard_r130';O=R/'build/fullgame/l4_shared_r131';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(s in p.name for s in ['validation','profile','trace','probe','.home.','boss_visible','boss_ceasefire','expected','actual','release_manifest']):shutil.copy2(p,O/p.name)
walk=json.loads((B/'walker_runtime.json').read_text());w=next(x for x in walk if x['level']==4);source=next(x for x in walk if x['level']==1);metas=json.loads((B/'generic_manifest.json').read_text());meta=next(x for x in metas if x['level']==4);b=bytearray((B/'level04_region.bin').read_bytes());old=bytes(b);cs=meta['cache_symbols'];oldsy=w['extension'];oldimage=(B/'L4_runtime_image.bin').read_bytes();oldraw=(B/'L4_runtime_art.bin').read_bytes();src=(B/'L1_runtime_art.bin').read_bytes();base=0xb280;oldbase=w['assets'][0]['pointer'];srcbase=source['assets'][0]['pointer'];raw=bytearray(oldraw)
for a in w['assets']:
 off=a['pointer']-oldbase
 if a['key']=='round':
  s=next(v for v in source['assets']if v['key']=='round'and v['frame']==a['frame']);raw[off:off+a['bytes']]=src[s['pointer']-srcbase:s['pointer']-srcbase+s['bytes']];a['source']='exact chosen L1 walker ZIP'
 a['pointer']=base+off
for key,ids,first in [('shell32',[5,6,7,8,9],176),('ghost32',[19,20,21],180)]:
 items=[v for v in source['assets']if v['key']==key]
 for a in items:
  v=src[a['pointer']-srcbase:a['pointer']-srcbase+a['bytes']];ptr=base+len(raw);raw.extend(v);w['assets'].append(dict(**{k:v for k,v in a.items()if k not in['level','pointer','name']},level=4,pointer=ptr,name=f'L4_{key}_{a["frame"]}',source_level=1,source_sha256=hashlib.sha256(v).hexdigest()))
 w['groups'].append(dict(level=4,key=key,original=ids,base=first,count=len(items),size=items[0]['size'],native_pose_order=True))
assert base+len(raw)==0xbfe0
# Repartition the unchanged expanded boss cache to reclaim packed storage.
t=w['preload_table'];cache=bytearray(6144)
for k in range(old[t]):
 p=int.from_bytes(old[t+1+4*k:t+3+4*k],'little');d=int.from_bytes(old[t+3+4*k:t+5+4*k],'little')-0xc000;v=unpack(old[p:]);cache[d:d+len(v)]=v
cache=cache[:w['original_preload_bytes']];split=0x1000;ext=pack(cache[:split]);rest=pack(cache[split:]);assert len(ext)<=0xb450-0xa9c7
# Newly redirected native head source C4E9..C65D stores a second art stream.
rawsplit=2688;aux=pack(raw[rawsplit:]);assert len(aux)<=0xa65e-0xa4e9;main=pack(raw[:rawsplit]);b[0xa4e9:0xa4e9+len(aux)]=aux;b[0xa9c7:0xa9c7+len(ext)]=ext
pretab=0x2800+len(rest);rawptr=pretab+9;s=(B/'L4_walker_extension.asm').read_text();mapping=bytearray(oldimage[oldsy['id_map']-0xa000:oldsy['id_map']-0xa000+256])
for i,k in zip([5,6,7,8,9],[176,176,177,178,179]):mapping[i]=k
for i in range(3):mapping[19+i]=180+i
entries=[]
for k in range(0xe350,0xe3f0,11):
 if not old[k]:break
 if old[k]not in {a['id']for a in w['assets']}:entries.append(old[k:k+11])
entries.extend(bytes([a['id'],128|a['size'][0]//8,a['size'][1]//8])+a['pointer'].to_bytes(2,'little')*4 for a in w['assets']);assert len({e[0]for e in entries})==len(entries)
s=re.sub(r'sprite_table:\n.*?id_map:','sprite_table:\n DB '+','.join(map(str,b''.join(entries)+b'\0'))+'\nid_map:',s,flags=re.S);s=re.sub(r'id_map:\n.*?actor_phases:','id_map:\n DB '+','.join(map(str,mapping))+'\nactor_phases:',s,flags=re.S)
a=s.index('load_new_art:');z=s.index(' LD HL,actor_phases',a)
s=s[:a]+f'''load_new_art:
 LD HL,0
 ADD HL,SP
 LD A,$6F
 OUT ($F4),A
 LD SP,$5CF0
 PUSH HL
 PUSH IX
 LD A,$ED
 OUT ($F4),A
 LD A,($E3F0)
 OR A
 CALL Z,$DEAE
 POP IX
 POP HL
 LD A,$2F
 OUT ($F4),A
 LD SP,HL
art_after_preload:
 LD HL,$C4E9
 LD DE,${base:04X}
 LD BC,{len(aux)}
 LDIR
 LD A,$6F
 OUT ($F4),A
 LD HL,${base:04X}
 LD DE,${base+rawsplit:04X}
 CALL $DE4F
 LD HL,${rawptr:04X}
 LD DE,${base:04X}
 CALL $DE4F
'''+s[z:]
exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';p=O/'L4_walker_extension';lines=[]
for line in s.splitlines():
 if line.strip().startswith('DB '):
  vals=line.strip()[3:].split(',');lines.extend(' DB '+','.join(vals[k:k+64])for k in range(0,len(vals),64))
 else:lines.append(line)
p.with_suffix('.asm').write_text('\n'.join(lines));q=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
motion=bytearray(oldimage[:oldsy['restore_native_bank5']-0xa000]);assert motion.count(bytes.fromhex('ccaede'))==1;motion=motion.replace(bytes.fromhex('ccaede'),bytes(3));assert sy['restore_native_bank5']==oldsy['restore_native_bank5'] and sy['sprite_hook']==oldsy['sprite_hook']
for name in ['fast_synth_entry']:
 pat=b'\xc3'+oldsy[name].to_bytes(2,'little');assert motion.count(pat)==1;motion=motion.replace(pat,b'\xc3'+sy[name].to_bytes(2,'little'))
for name,op in [('fast_visibility',0xcd),('fast_same_pair',0xc3)]:
 lo,hi=(0xdc50,0xdf50)if name=='fast_visibility'else(0xdf50,0xe000);pat=bytes([op])+oldsy[name].to_bytes(2,'little');q=b.find(pat,lo,hi);assert q>=0,(name,hex(lo));b[q+1:q+3]=sy[name].to_bytes(2,'little')
image=motion+p.with_suffix('.bin').read_bytes();assert 0xa000+len(image)<=0xa9c7;ip=rawptr+len(main);packet=pack(image);end=ip+len(packet);assert end<=0x3a00,(hex(end),len(main),len(aux),len(packet))
b[0x2800:0x3a00]=bytes(0x1200);b[0x2800:pretab]=rest;b[pretab:rawptr]=bytes([2])+bytes.fromhex('c7a900c0')+bytes.fromhex('0028')+(0xc000+split).to_bytes(2,'little');b[rawptr:ip]=main;b[ip:end]=packet
q=b.find(b'\xdd\x21'+t.to_bytes(2,'little'),cs['preload'],cs['install_motion']);assert q>=0;b[q+2:q+4]=pretab.to_bytes(2,'little');q2=b.find(b'\x21'+meta['motion_ptr'].to_bytes(2,'little'),cs['install_motion'],0xdf30);assert q2>=0;b[q2+1:q2+3]=ip.to_bytes(2,'little')
assert unpack(b[0x2800:])==cache[split:] and unpack(b[0xa9c7:])==cache[:split] and unpack(b[rawptr:])==raw[:rawsplit] and unpack(b[0xa4e9:])==raw[rawsplit:]
meta.update(motion_ptr=ip,motion_image_bytes=len(image),walker_extension=sy,preload_blocks=[[0xa9c7,0xc000],[0x2800,0xd000]]);w.update(extension=sy,motion_ptr=ip,immutable_end=end,runtime_bytes=len(image),art_bytes=len(raw),preload_table=pretab)
(O/'L4_runtime_image.bin').write_bytes(image);(O/'L4_runtime_art.bin').write_bytes(raw);(O/'L4_expected_cache.bin').write_bytes(cache);(O/'level04_region.bin').write_bytes(b);(O/'walker_runtime.json').write_text(json.dumps(walk,indent=2));(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2))
for name in ['LEVEL04.TAP','START04.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
contract=dict(level=4,rawbase=base,rawend=base+len(raw),rawsplit=rawsplit,aux_file_source=0xa4e9,aux_home_backup=0xc4e9,aux_bytes=len(aux),main_compressed=len(main),native_cache_split=split,external_source=0xa9c7,external_end=0xa9c7+len(ext),bank1_end=end,code_end=0xa000+len(image),pretab=pretab,rawptr=rawptr,imageptr=ip,groups=w['groups'],native_cache_unchanged=True,reused_native_sources={'head':[5,6,7,8,9],'round':[28,29,30,31]},first_head_pose='Native5 has no L1 counterpart; uses approved first head pose,6..9 preserve the four matching native pose slots.',aux_order='Copy HOME backup C4E9 stream to B280 scratch; expand tail to BD00; then expand main prefix over temporary stream.',runtime_source_lifetimes='External boss preload finishes before art overwrites B280..B3C7; native restore snapshot retains recycled packets. Only redirected native sources changed.')
(O/'l4_shared_contract.json').write_text(json.dumps(contract,indent=2))
for name in ['launcher.bin','demand_loader.bin']:(O/name).write_bytes((O/name).read_bytes().replace(b'R130 PREPARING  ',b'R131 PREPARING  '))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+n]).replace(b'R130 PREPARING  ',b'R131 PREPARING  ');block[-1]=0
 for x in block[:-1]:block[-1]^=x
 v[at+2:at+2+n]=block;at+=n+2
p.write_bytes(v)
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_l2_fire','verify_l2_boss_revisits']:
 s=(R/f'scripts/{stem}_r130.mjs').read_text().replace('l2_star_guard_r130','l4_shared_r131').replace('boss_motion_fixture_r130','boss_motion_fixture_r131');(R/f'scripts/{stem}_r131.mjs').write_text(s)
print(O,hex(end),len(image),len(main),len(aux),hex(base+len(raw)))
