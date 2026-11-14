from pathlib import Path
import sys,json,re,subprocess,shutil
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/l1_blue_boost_r116';A=R/'build/graphics/l2_integrate_r119';O=R/'build/fullgame/l2_actors_r119';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']and not any(v in p.name for v in ['.home.','validation','expected_','actual_','timing','gameplay']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level02_region.bin').read_bytes());metas=json.loads((B/'generic_manifest.json').read_text());meta=next(x for x in metas if x['level']==2);cs=meta['cache_symbols'];motion=bytearray(b[meta['motion_ptr']:meta['motion_ptr']+meta['motion_image_bytes']]);oldlen=len(motion);entries=[];payload=bytearray();ptrmap={}
# Two exact selected heads plus native mirror flags replace four redundant stores.
import zipfile,numpy as np
from PIL import Image
from build_reviewed_r72 import phase_rows
zipart=zipfile.ZipFile(R/'convref/rtype-l2-art-assets_v2.zip')
for native,frame in [(3,0),(4,1)]:
 bits=np.frombuffer(zipart.read(f'emergence/frame_{frame:02d}.bits.bin'),np.uint8).reshape(40,5);attrs=np.frombuffer(zipart.read(f'emergence/frame_{frame:02d}.attrs.bin'),np.uint8).reshape(40,5);im=np.where(np.unpackbits(bits,axis=1),np.repeat(attrs&7,8,axis=1),np.repeat((attrs>>3)&7,8,axis=1)).astype('uint8');ptrs=[]
 for shift in [0,2,4,6]:
  ptrs.append(0x2400+len(payload));v=phase_rows(im,shift=shift,spill=True,normal=True);payload.extend(pack(v[::2]+v[1::2]))
 entries.append(bytes([native,5,5])+b''.join(v.to_bytes(2,'little')for v in ptrs))
print('head phase bytes',len(payload));backptr=0;rawptr=0x2400+len(payload);raw=bytearray();assets=json.loads((A/'actor_assets.json').read_text());mapping=bytearray(39)
for a in assets:
 v=(A/a['file']).read_bytes();a['pointer']=0xa7e0+len(raw);a['bytes']=len(v);raw.extend(v);w,h=a['size'];entries.append(bytes([a['id'],128|w//8,h//8])+a['pointer'].to_bytes(2,'little')*4)
 for ident in a['original']:mapping[ident]=a['id']
for i in [19,20]:mapping[i]=184
for i in [34,35,36,37,38]:mapping[i]=188
loadtable=[];source_ranges=[];bins=[[0xe84c,0xeb76],[0xebc7,0xeeae]]
for a in sorted(assets,key=lambda a:len(pack((A/a['file']).read_bytes()[::2]+(A/a['file']).read_bytes()[1::2])),reverse=True):
 v=(A/a['file']).read_bytes();packet=pack(v[::2]+v[1::2]);slot=next((q for q in bins if q[1]-q[0]>=len(packet)),None)
 if slot:
  ptr=slot[0];slot[0]+=len(packet);b[ptr:ptr+len(packet)]=packet;source_ranges.append(dict(address=ptr,bytes=len(packet),id=a['id']))
 else:ptr=0x2400+len(payload);payload.extend(packet)
 loadtable.append((ptr,a['pointer'],len(v)))
ip=0x2400+len(payload)
tabletext=','.join(map(str,b''.join(entries)+bytes([0])))
source=f''' ORG $A4B0
restore_native_bank5:
 PUSH DE
 LD A,$2D
 OUT ($F4),A
 LD HL,${0xc000+oldlen:04X}
 LD DE,${0xa000+oldlen:04X}
 LD BC,${0x187c-oldlen:04X}
 LDIR
 LD A,$ED
 OUT ($F4),A
 POP DE
 RET
sprite_hook:
 PUSH BC
 PUSH DE
 LD A,($DF3E)
 CP 5
 JR Z,mirror_head5
 CP 6
 JR NZ,head_done
 LD B,3
 JR mirror_head
mirror_head5:
 LD B,4
mirror_head:
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
 LD ($DF3E),A
head_done:
 LD A,($DF3E)
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
 CP 184
 JR Z,three_poses
 CP 188
 JR NZ,store
 LD A,IYL
 AND 63
 LD E,A
 LD HL,actor_phases
 ADD HL,DE
 LD A,(HL)
 INC (HL)
 AND 3
 ADD A,B
 JR store
three_poses:
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
store:
 LD ($DF3E),A
done:
 POP DE
 POP BC
 LD HL,sprite_table
 RET
head_planar:
 LD BC,480
 JP planar
planar:
 PUSH DE
 PUSH BC
 LD DE,$C000
 LD A,H
 CP $E0
 JR C,source_ready
 LD A,$EF
 OUT ($F4),A
source_ready:
 CALL $DE4F
 LD A,$6F
 OUT ($F4),A
 POP BC
 POP DE
 PUSH HL
 PUSH DE
 PUSH BC
 LD HL,$C000
 LD DE,$C200
 LDIR
 POP BC
 POP DE
 SRL B
 RR C
 PUSH IX
 PUSH IY
 LD IX,$C200
 LD HL,$C200
 ADD HL,BC
 PUSH HL
 POP IY
planar_loop:
 LD A,(IX+0)
 LD (DE),A
 INC DE
 LD A,(IY+0)
 LD (DE),A
 INC DE
 INC IX
 INC IY
 DEC BC
 LD A,B
 OR C
 JR NZ,planar_loop
 POP IY
 POP IX
 POP HL
 RET
load_new_art:
 LD A,$6F
 OUT ($F4),A
 LD ($C4D2),SP
 LD SP,$C4D0
 PUSH IX
 LD IX,load_table
 LD A,17
load_loop:
 PUSH AF
 LD L,(IX+0)
 LD H,(IX+1)
 LD E,(IX+2)
 LD D,(IX+3)
 LD C,(IX+4)
 LD B,(IX+5)
 CALL planar
 LD BC,6
 ADD IX,BC
 POP AF
 DEC A
 JR NZ,load_loop
 POP IX
 LD SP,($C4D2)
 JP $A1B2
load_table:
 DB {','.join(map(str,b''.join(x.to_bytes(2,'little')for row in loadtable for x in row)))}
sprite_table:
 DB {tabletext}
id_map:
 DB {','.join(map(str,mapping))}
actor_phases:
 DS 64,0
 ASSERT $ <= $A7E0
'''
lines=[]
for line in source.splitlines():
 if line.strip().startswith('DB '):
  v=line.strip()[3:].split(',');lines.extend(' DB '+','.join(v[i:i+64])for i in range(0,len(v),64))
 else:lines.append(line)
p=O/'L2_actor_extension';p.with_suffix('.asm').write_text('\n'.join(lines));r=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
pat=bytes.fromhex('cd4fde');at=motion.find(pat);assert at>=0;motion[at:at+3]=b'\xcd'+sy['head_planar'].to_bytes(2,'little')
pat=bytes.fromhex('2150e3');at=motion.find(pat);assert at>=0;motion[at:at+3]=b'\xcd'+sy['sprite_hook'].to_bytes(2,'little')
pat=bytes.fromhex('21f2a411f2c40144013e2fd3f4edb03e6fd3f4');at=motion.find(pat);assert at>=0;replacement=bytes.fromhex('21f2e411f2c40144013eefd3f4edb03e6fd3f4');motion[at:at+len(pat)]=replacement.ljust(len(pat),b'\0')
pat=bytes.fromhex('3eedd3f4af32f0e3');at=motion.find(pat);assert at>=0;motion[at:at+4]=b'\xcd'+sy['restore_native_bank5'].to_bytes(2,'little')+b'\0'
image=motion+bytes(0x4b0-len(motion))+p.with_suffix('.bin').read_bytes();print('image packet',len(pack(image)));payload.extend(pack(image));end=0x2400+len(payload);assert end<=0x3848,(hex(end),len(raw));b[0x2400:0x3848]=payload.ljust(0x1448,b'\0')
inst=cs['install_motion'];at=b.find(b'\x21'+meta['motion_ptr'].to_bytes(2,'little'),inst,0xdf30);assert at>=0;b[at+1:at+3]=ip.to_bytes(2,'little');pat=b'\x01'+oldlen.to_bytes(2,'little')+bytes.fromhex('edb0');at=b.find(pat,inst,0xdf30);assert at>=0;b[at:at+5]=bytes.fromhex('cd4fde0000');pat=bytes.fromhex('c3b2a1');at=b.find(pat,inst,0xdf30);assert at>=0;b[at+1:at+3]=sy['load_new_art'].to_bytes(2,'little')
assert unpack(b[ip:])==image
for ptr,dest,size in loadtable:
 v=unpack(b[ptr:]);assert len(v)==size;inter=bytes(x for pair in zip(v[:size//2],v[size//2:])for x in pair);assert inter==raw[dest-0xa7e0:dest-0xa7e0+size];meta.update(motion_ptr=ip,motion_image_bytes=len(image),motion_compressed=True,backup_ptr=backptr,actor_extension=sy);helper=bytes.fromhex('3e23d3f4')
for lo,hi in [(0xc84c,0xcb76),(0xcbc7,0xceae)]:helper+=b'\x21'+(lo-0x2000).to_bytes(2,'little')+b'\x11'+lo.to_bytes(2,'little')+b'\x01'+(hi-lo).to_bytes(2,'little')+bytes.fromhex('edb0')
helper+=bytes.fromhex('3e63d3f4c9');b[0x37e0:0x37e0+len(helper)]=helper
install=bytes.fromhex('f33e63d3f4cde037')+b'\x21'+ip.to_bytes(2,'little')+bytes.fromhex('1100a0cd4fde3e69d3f4c3')+sy['load_new_art'].to_bytes(2,'little');assert len(install)<0xdf30-inst;b[inst:inst+len(install)]=install
(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));(O/'level02_region.bin').write_bytes(b);(O/'L2_runtime_image.bin').write_bytes(image);(O/'L2_runtime_art.bin').write_bytes(raw);(O/'L2_actor_contract.json').write_text(json.dumps(dict(assets=assets,mapping=list(mapping),head_phase_ptr_map=ptrmap,rawptr=rawptr,imageptr=ip,end=end,extension=sy,backup_ptr=backptr,native_restore_start=0xa000+oldlen,native_restore_end=0xb87c,art_base=0xa7e0,art_end=0xa7e0+len(raw),load_table=loadtable,source_ranges=source_ranges),indent=2))
for name in ['LEVEL02.TAP','START02.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_l1_fire']:
 s=(R/f'scripts/{stem}_r116.mjs').read_text(encoding='utf-8-sig').replace('l1_blue_boost_r116','l2_actors_r119').replace('boss_motion_fixture_r116','boss_motion_fixture_r119');(R/f'scripts/{stem}_r119.mjs').write_text(s,encoding='utf-8')
print('actor packet end',hex(end),'art end',hex(0xa7e0+len(raw)),'image end',hex(0xa000+len(image)))
