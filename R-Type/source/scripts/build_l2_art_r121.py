from pathlib import Path
import sys,json,zipfile,re,subprocess,shutil,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_reviewed_r72 import phase_rows;from build_rocket_fix import code
B=R/'build/fullgame/l1_blue_boost_r116';O=R/'build/fullgame/l2_art_r121';A=R/'build/graphics/l2_integrate_r119';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']and not any(v in p.name for v in ['.home.','validation','expected_','actual_','timing','gameplay']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level02_region.bin').read_bytes());metas=json.loads((B/'generic_manifest.json').read_text());meta=next(v for v in metas if v['level']==2);cs=meta['cache_symbols'];motion=bytearray(b[meta['motion_ptr']:meta['motion_ptr']+meta['motion_image_bytes']]);z=zipfile.ZipFile(R/'convref/rtype-l2-art-assets_v2.zip');choices=json.loads(z.read('choices.json'));payload=bytearray();external=[];bins=[[0xa84c,0xab76],[0xabc7,0xaeae]];pieces={}
def packet(key,raw,ext=True):
 v=pack(raw);slot=next((s for s in bins if s[1]-s[0]>=len(v)),None)if ext else None
 if slot:ptr=slot[0];slot[0]+=len(v);b[ptr:ptr+len(v)]=v;external.append(dict(key=key,address=ptr,bytes=len(v)))
 else:ptr=0x2400+len(payload);payload.extend(v)
 pieces[key]=dict(pointer=ptr,bytes=len(v),rawbytes=len(raw),raw=bytes(raw).hex());return ptr
# Native head sources remain intact. Horizontal movement follows original8px
# coordinates; existing2px vertical smoothing remains active.
entries=[];assets=[]
for native,frame in [(3,0),(4,1)]:
 v=z.read(f'emergence/frame_{frame:02d}.pairs.bin')+bytes(80);ptr=packet(f'head{native}',v,False);entries.append(dict(id=native,width=0x85,height=5,ptrs=[ptr]*4));assets.append(dict(key='emergence',frame=frame,id=native,size=[40,40],source=ptr))
# Preserve all ten exact conversions, normalized only by legal whole-image flips.
flip=[3,1,1,1,2,3,0,0,1,3];base=[0,0,2,3,0,2,0,3,8,3];normalized=[]
def transform(v,flag):
 a=np.frombuffer(v,np.uint8).reshape(5,40,2).copy()
 if flag&1:
  a=a[::-1].copy();a[:,:,0]=np.array([int(f'{int(n):08b}'[::-1],2)for n in a[:,:,0].ravel()],np.uint8).reshape(5,40)
 if flag&2:a=a[:,::-1].copy()
 return a.tobytes()+bytes(80)
for i in range(10):normalized.append(transform(z.read(f'scorpion/frame_{i:02d}.pairs.bin'),flip[i]))
baseptr={i:packet(f'scorpion_base{i}',normalized[i])for i in [0,2,3,8]};records=[]
for i in range(10):
 delta=0 if base[i]==i else packet(f'scorpion_delta{i}',bytes(a^c for a,c in zip(normalized[i],normalized[base[i]])));records.append((baseptr[base[i]],delta));entries.append(dict(id=180+i,width=0x85,height=5,record=i));assets.append(dict(key='scorpion',frame=i,id=180+i,size=[40,40],normalize_flip=flip[i],exact_export_before_flip=True))
mapids=bytearray(39)
for a in json.loads((A/'actor_assets.json').read_text()):
 if a['key']=='scorpion':continue
 ident=a['id']+6;w,h=a['size'];raw=(A/a['file']).read_bytes()+bytes(h*2);ptr=packet(f'actor{ident}',raw);entries.append(dict(id=ident,width=128|w//8,height=h//8,ptrs=[ptr]*4));assets.append(dict(**{k:v for k,v in a.items()if k!='id'},id=ident,source=ptr))
 for n in a['original']:mapids[n]=ident
for n in [19,20]:mapids[n]=190
for n in [34,35,36,37,38]:mapids[n]=194
backptr=packet('native_plan_backup',bytes.fromhex(meta['backup']),False)
# Exact subset packing prevents small fragments wasting retired source slots.
items=[(k,pack(bytes.fromhex(v['raw'])))for k,v in pieces.items()if k!='native_plan_backup'];remaining=set(range(len(items)));chosen=[]
for capacity in [810,743]:
 dp={0:0}
 for i in sorted(remaining):
  n=len(items[i][1])
  for total,mask in sorted(list(dp.items()),reverse=True):
   if total+n<=capacity and total+n not in dp:dp[total+n]=mask|(1<<i)
 best=max(dp);mask=dp[best];group=[i for i in remaining if mask>>i&1];remaining.difference_update(group);chosen.append(group)
b=bytearray((B/'level02_region.bin').read_bytes());payload=bytearray();external=[];remap={}
for start,group in zip([0xa84c,0xabc7],chosen):
 for i in group:
  k,v=items[i];old=pieces[k]['pointer'];remap[old]=start;pieces[k]['pointer']=start;b[start:start+len(v)]=v;external.append(dict(key=k,address=start,bytes=len(v)));start+=len(v)
for k,v in pieces.items():
 if k in {x['key']for x in external}:continue
 old=v['pointer'];ptr=0x2400+len(payload);remap[old]=ptr;v['pointer']=ptr;payload.extend(pack(bytes.fromhex(v['raw'])))
for e in entries:
 if 'ptrs'in e:e['ptrs']=[remap[p]for p in e['ptrs']]
records=[(remap[a],remap[d]if d else 0)for a,d in records]
for a in assets:
 if 'source'in a:a['source']=remap[a['source']]
backptr=remap[backptr];ip=0x2400+len(payload)
print('externalpacked',sum(x['bytes']for x in external))
source=f''' ORG $A4B0
restore_native_bank5 EQU $3920
sprite_hook:
 PUSH BC
 PUSH DE
 LD A,($DF3E)
 CP 5
 JR Z,head5
 CP 6
 JR NZ,scorpion_check
 LD B,3
 JR mirror
head5:
 LD B,4
mirror:
 LD A,$6D
 OUT ($F4),A
 LD HL,($DF3A)
 INC HL
 INC HL
 INC HL
 LD A,(HL)
 XOR 1
 LD (HL),A
 LD A,$ED
 OUT ($F4),A
 LD A,B
 JR store_id
scorpion_check:
 CP 32
 JR Z,scorpion
 CP 33
 JR NZ,ordinary
scorpion:
 LD A,IYL
 AND 63
 LD E,A
 LD D,0
 LD HL,actor_phases
 ADD HL,DE
 LD A,(HL)
 CP 10
 JR C,scorpion_ready
 XOR A
scorpion_ready:
 LD E,A
 INC A
 LD (HL),A
 LD HL,scorpion_order
 ADD HL,DE
 LD A,(HL)
 ADD A,180
 JR store_id
ordinary:
 CP 39
 JR NC,done
 LD E,A
 LD D,0
 LD HL,id_map
 ADD HL,DE
 LD A,(HL)
 OR A
 JR Z,done
 LD B,A
 CP 190
 JR Z,three
 CP 194
 JR NZ,store_id
 LD A,IYL
 AND 63
 LD E,A
 LD HL,actor_phases
 ADD HL,DE
 LD A,(HL)
 INC (HL)
 AND 3
 ADD A,B
 JR store_id
three:
 LD A,IYL
 AND 63
 LD E,A
 LD HL,actor_phases
 ADD HL,DE
 LD A,(HL)
 INC A
 CP 3
 JR C,three_ready
 XOR A
three_ready:
 LD (HL),A
 ADD A,B
store_id:
 LD ($DF3E),A
done:
 POP DE
 POP BC
 LD HL,sprite_table
 RET
fetch_frame:
 DI
 LD A,($DF3E)
 CP 180
 JR C,decode
 CP 190
 JR NC,decode
 ; HL points to a unique4byte base/delta record, also the cache identity.
 LD C,(HL)
 INC HL
 LD B,(HL)
 INC HL
 LD E,(HL)
 INC HL
 LD D,(HL)
 PUSH DE
 LD H,B
 LD L,C
 LD DE,$C000
 CALL decode
 POP HL
 LD A,H
 OR L
 RET Z
 LD DE,$C200
 CALL decode
 LD HL,$C000
 LD DE,$C200
 LD BC,480
xor_loop:
 LD A,(DE)
 XOR (HL)
 LD (HL),A
 INC HL
 INC DE
 DEC BC
 LD A,B
 OR C
 JR NZ,xor_loop
 RET
decode:
 JP $DE4F
repair_native_home:
 LD A,$23
 OUT ($F4),A
 LD HL,$A84C
 LD DE,$C84C
 LD BC,$032A
 LDIR
 LD HL,$ABC7
 LD DE,$CBC7
 LD BC,$02E7
 LDIR
 LD A,$63
 OUT ($F4),A
 RET
sprite_table:
TABLE_PLACEHOLDER
scorpion_records:
 DB {','.join(map(str,b''.join(x.to_bytes(2,'little')for row in records for x in row)))}
id_map:
 DB {','.join(map(str,mapids))}
scorpion_order:
 DB 6,2,7,8,9,5,1,3,0,4
actor_phases:
 DS 64,0
 ASSERT $ <= $A84C
'''
def asm(s):
 lines=[]
 for line in s.splitlines():
  if line.strip().startswith('DB '):
   v=line.strip()[3:].split(',');lines.extend(' DB '+','.join(v[i:i+64])for i in range(0,len(v),64))
  else:lines.append(line)
 p=O/'L2_actor_extension';p.with_suffix('.asm').write_text('\n'.join(lines));q=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr;return p.with_suffix('.bin').read_bytes(),{k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
def table(rec):
 out=bytearray()
 for e in entries:
  ptrs=[rec+e['record']*4]*4 if 'record'in e else e['ptrs'];out.extend(bytes([e['id'],e['width'],e['height']])+b''.join(p.to_bytes(2,'little')for p in ptrs))
 return ' DB '+','.join(map(str,out+bytes([0])))
_,sy=asm(source.replace('TABLE_PLACEHOLDER',table(0)));ext,sy=asm(source.replace('TABLE_PLACEHOLDER',table(sy['scorpion_records'])))
for pat,target in [(bytes.fromhex('2150e3'),'sprite_hook'),(bytes.fromhex('cd4fde'),'fetch_frame')]:
 at=motion.find(pat);assert at>=0;motion[at:at+3]=b'\xcd'+sy[target].to_bytes(2,'little')
pat=bytes.fromhex('21f2a411f2c40144013e2fd3f4edb03e6fd3f4');at=motion.find(pat);assert at>=0;v=b'\x21'+backptr.to_bytes(2,'little')+bytes.fromhex('11f2c4cd43decd2039');motion[at:at+len(pat)]=v.ljust(len(pat),b'\0')
pat=bytes.fromhex('3e6dd3f42100e01100c0017c18edb0');at=motion.find(pat);assert at>=0;motion[at:at+len(pat)]=bytes(len(pat))
image=bytearray(motion+bytes(0x4b0-len(motion))+ext);trailer_at=b.find(bytes.fromhex('ed733adff53e3c322d88'),0x3848,0x3a00);assert trailer_at>=0;image[0x480:0x49f]=b[trailer_at:trailer_at+31];payload.extend(pack(image));end=0x2400+len(payload);assert end<=0x3848,(hex(end),len(image));b[0x2400:0x3848]=payload.ljust(0x1448,b'\0')
# Both cold and repeated installers can repair native HOME from the untouched
# bank5 native sources: compiled cache is C000, never overlaid on these ranges.
inst=cs['install_motion'];install=bytes.fromhex('f3f53e63d3f4')+b'\x21'+ip.to_bytes(2,'little')+bytes.fromhex('1100a0cd4fdecd')+sy['repair_native_home'].to_bytes(2,'little')+bytes.fromhex('f13e69d3f4c3b2a1');b[inst:inst+len(install)]=install
# Save the original native prefix before any expanded runtime overwrites it.
# C700..CA9B is unused during gameplay; the native restore overwrites it only
# after copying this snapshot back to bank5.
native_helper=bytes.fromhex('d53e6fd3f42100c711b0a4019c03edb03e2fd3f421f2a411f2c4014401edb03e6fd3f42100e01100c0017c18edb021b0a411b0c4019c03edb02158c41158a4015800edb0af32f0c6d1c9');assert len(native_helper)<=0x60;b[0x3920:0x3920+len(native_helper)]=native_helper
save_helper=bytes.fromhex('3af0c6fea5c821b0a41100c7019c03edb03ea532f0c6c9');b[0x3980:0x3980+len(save_helper)]=save_helper
# Reinstall compressed code while preserving the original entry flags.
install=bytes.fromhex('f3f53e63d3f4cd8039')+b'\x21'+ip.to_bytes(2,'little')+bytes.fromhex('1100a0cd4fdecd')+sy['repair_native_home'].to_bytes(2,'little')+bytes.fromhex('f13e69d3f4c3b2a1');b[inst:inst+len(install)]=install
meta.update(motion_ptr=ip,motion_image_bytes=len(image),motion_compressed=True,backup_ptr=backptr,actor_extension=sy);(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));(O/'level02_region.bin').write_bytes(b);(O/'L2_runtime_image.bin').write_bytes(image);(O/'L2_actor_contract.json').write_text(json.dumps(dict(assets=assets,entries=entries,extension=sy,pieces=pieces,source_ranges=external,bank4_unchanged=True,bank5_native_descriptors_unchanged=True,bank5_retired_sources_reused=True,scorpion_records=records,scorpion_normalize_flips=flip,all10=True,backup_ptr=backptr,imageptr=ip,end=end,horizontal_head_native_step=True,vertical_head_2px=True),indent=2));(O/'selected_l2_choices.json').write_text(json.dumps(choices,indent=2))
for name in ['LEVEL02.TAP','START02.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_l1_fire']:
 s=(R/f'scripts/{stem}_r116.mjs').read_text(encoding='utf-8-sig').replace('l1_blue_boost_r116','l2_art_r121').replace('boss_motion_fixture_r116','boss_motion_fixture_r121');(R/f'scripts/{stem}_r121.mjs').write_text(s,encoding='utf-8')
s=(R/'scripts/probe_l2_short_r119.mjs').read_text().replace('boss_motion_fixture_r119','boss_motion_fixture_r121').replace('l2_actors_r119','l2_art_r121');(R/'scripts/probe_l2_short_r121.mjs').write_text(s)
print('all10deltas end',hex(end),'imageend',hex(0xa000+len(image)),'external',sum(x['bytes']for x in external))
