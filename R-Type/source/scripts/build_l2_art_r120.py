from pathlib import Path
import json,sys,zipfile,shutil,re,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/l1_blue_boost_r116';A=R/'build/graphics/l2_integrate_r119';O=R/'build/fullgame/l2_art_r120';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']and not any(v in p.name for v in ['.home.','validation','expected_','actual_','timing','gameplay']):shutil.copy2(p,O/p.name)
z=zipfile.ZipFile(R/'convref/rtype-l2-art-assets_v2.zip');choices=json.loads(z.read('choices.json'));b=bytearray((B/'level02_region.bin').read_bytes());metas=json.loads((B/'generic_manifest.json').read_text());meta=next(x for x in metas if x['level']==2);cs=meta['cache_symbols'];motion=bytearray(b[meta['motion_ptr']:meta['motion_ptr']+meta['motion_image_bytes']]);oldlen=len(motion);entries=[];payload=bytearray();assets=[];raw=bytearray();mapping=bytearray(39)
# Keep original eight-bit native sources intact. New source bank4 is used only
# during an interrupt-masked copy, then raw rendering uses the existing C000cache.
for i in range(10):
 v=z.read(f'scorpion/frame_{i:02d}.pairs.bin');ptr=0x8500+len(raw);raw.extend(v);assets.append(dict(key='scorpion',frame=i,id=180+i,size=[40,40],pointer=ptr,bytes=len(v)))
for a in json.loads((A/'actor_assets.json').read_text()):
 if a['key']=='scorpion':continue
 q=dict(a);q['id']=a['id']+6;q['pointer']=0x8500+len(raw);v=(A/a['file']).read_bytes();raw.extend(v);q['bytes']=len(v);assets.append(q)
for a in assets:
 w,h=a['size'];entries.append(bytes([a['id'],128|w//8,h//8])+a['pointer'].to_bytes(2,'little')*4)
 for native in a.get('original',[]):mapping[native]=a['id']
for i in [19,20]:mapping[i]=190
for i in [34,35,36,37,38]:mapping[i]=194
assert len(raw)==6160 and 0x8500+len(raw)==0x9d10
b[0x8500:0x9d10]=raw
# Selected rolling heads retain every two-pixel shift phase.
import numpy as np
from build_reviewed_r72 import phase_rows
for native,frame in [(3,0),(4,1)]:
 bits=np.frombuffer(z.read(f'emergence/frame_{frame:02d}.bits.bin'),np.uint8).reshape(40,5);attrs=np.frombuffer(z.read(f'emergence/frame_{frame:02d}.attrs.bin'),np.uint8).reshape(40,5);im=np.where(np.unpackbits(bits,axis=1),np.repeat(attrs&7,8,axis=1),np.repeat((attrs>>3)&7,8,axis=1)).astype('uint8');ptrs=[]
 for shift in [0,2,4,6]:ptrs.append(0x2400+len(payload));payload.extend(pack(phase_rows(im,shift=shift,spill=True,normal=True)))
 entries.insert(native-3,bytes([native,5,5])+b''.join(v.to_bytes(2,'little')for v in ptrs))
backptr=0x2400+len(payload);payload.extend(pack(bytes.fromhex(meta['backup'])));ip=0x2400+len(payload);tabletext=','.join(map(str,b''.join(entries)+bytes([0])));flip=[3,1,1,1,2,3,0,0,1,3];order=[6,2,7,8,9,5,1,3,0,4]
s=f''' ORG $A4B0
restore_native_bank5:
 PUSH DE
 LD A,$2D
 OUT ($F4),A
 LD HL,$C458
 LD DE,$A458
 LD BC,$1424
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
 JR Z,head5
 CP 6
 JR NZ,check_scorpion
 LD B,3
 JR mirror_head
head5:
 LD B,4
mirror_head:
 LD C,1
 JR change_flip
check_scorpion:
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
 JR C,count_ready
 XOR A
count_ready:
 LD E,A
 INC A
 LD (HL),A
 LD HL,scorpion_order
 ADD HL,DE
 LD E,(HL)
 LD A,E
 ADD A,180
 LD B,A
 LD HL,scorpion_flips
 ADD HL,DE
 LD C,(HL)
change_flip:
 LD A,$6D
 OUT ($F4),A
 LD HL,($DF3A)
 INC HL
 INC HL
 INC HL
 LD A,(HL)
 XOR C
 LD (HL),A
 LD A,$ED
 OUT ($F4),A
 LD A,B
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
 LD A,H
 CP $A0
 JP NC,$DE4F
 CP $80
 JP C,$DE4F
 ; Source is raw paired bytes in bank4. Copy before EI, restore normal map.
 PUSH HL
 LD A,($DF38)
 LD B,A
 LD A,($DF39)
 ADD A,A
 LD E,A
 LD D,0
 LD HL,0
size_loop:
 ADD HL,DE
 DJNZ size_loop
 LD B,H
 LD C,L
 POP HL
 LD DE,$C000
 DI
 LD A,$7F
 OUT ($F4),A
 LDIR
 LD A,$6F
 OUT ($F4),A
 RET
sprite_table:
 DB {tabletext}
id_map:
 DB {','.join(map(str,mapping))}
scorpion_order:
 DB {','.join(map(str,order))}
scorpion_flips:
 DB {','.join(map(str,flip))}
actor_phases:
 DS 64,0
 ASSERT $ <= $A900
'''
lines=[]
for line in s.splitlines():
 if line.strip().startswith('DB '):
  v=line.strip()[3:].split(',');lines.extend(' DB '+','.join(v[k:k+64])for k in range(0,len(v),64))
 else:lines.append(line)
p=O/'L2_actor_extension';p.with_suffix('.asm').write_text('\n'.join(lines));q=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
for pat,target in [(bytes.fromhex('2150e3'),'sprite_hook'),(bytes.fromhex('cd4fde'),'fetch_frame')]:
 at=motion.find(pat);assert at>=0;motion[at:at+3]=b'\xcd'+sy[target].to_bytes(2,'little')
pat=bytes.fromhex('21f2a411f2c40144013e2fd3f4edb03e6fd3f4');at=motion.find(pat);assert at>=0;v=b'\x21'+backptr.to_bytes(2,'little')+bytes.fromhex('11f2c4cd43de');motion[at:at+len(pat)]=v.ljust(len(pat),b'\0')
pat=bytes.fromhex('3eedd3f4af32f0e3');at=motion.find(pat);assert at>=0;motion[at:at+4]=b'\xcd'+sy['restore_native_bank5'].to_bytes(2,'little')+b'\0'
image=motion+bytes(0x4b0-len(motion))+p.with_suffix('.bin').read_bytes();payload.extend(pack(image));end=0x2400+len(payload);assert end<=0x3848;assert unpack(payload[ip-0x2400:])==image;b[0x2400:0x3848]=payload.ljust(0x1448,b'\0');inst=cs['install_motion'];at=b.find(b'\x21'+meta['motion_ptr'].to_bytes(2,'little'),inst,0xdf30);assert at>=0;b[at+1:at+3]=ip.to_bytes(2,'little');at=b.find(b'\x01'+oldlen.to_bytes(2,'little')+bytes.fromhex('edb0'),inst,0xdf30);assert at>=0;b[at:at+5]=bytes.fromhex('cd4fde0000')
meta.update(motion_ptr=ip,motion_image_bytes=len(image),motion_compressed=True,backup_ptr=backptr,actor_extension=sy);(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));(O/'level02_region.bin').write_bytes(b);(O/'L2_runtime_image.bin').write_bytes(image);(O/'L2_bank4_art.bin').write_bytes(raw);(O/'L2_actor_contract.json').write_text(json.dumps(dict(assets=assets,extension=sy,art_base=0x8500,art_end=0x9d10,source_bank=4,source_ranges=[],mapping=list(mapping),head_phase_bytes=backptr-0x2400,backup_ptr=backptr,imageptr=ip,end=end,scorpion_order=order,scorpion_flip_normalization=flip,all10=True),indent=2));(O/'selected_l2_choices.json').write_text(json.dumps(choices,indent=2))
for name in ['LEVEL02.TAP','START02.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_l1_fire']:
 s=(R/f'scripts/{stem}_r116.mjs').read_text(encoding='utf-8-sig').replace('l1_blue_boost_r116','l2_art_r120').replace('boss_motion_fixture_r116','boss_motion_fixture_r120');(R/f'scripts/{stem}_r120.mjs').write_text(s,encoding='utf-8')
print('All10scorpions; bank4 raw',len(raw),'image',hex(0xa000+len(image)),'packed',hex(end))
