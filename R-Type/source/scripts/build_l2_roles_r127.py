from pathlib import Path
import sys,json,shutil,subprocess,re,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from build_rocket_fix import code
B=R/'build/fullgame/l2_snake_parts_r126';O=R/'build/fullgame/l2_roles_restore_r127';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.json','.sym','.asm']and not any(s in p.name for s in ['validation','approach','trace','probe','mismatch','.home.','native_jump','final_l2']):shutil.copy2(p,O/p.name)
ct=json.loads((B/'L2_actor_contract.json').read_text());image=bytearray((B/'L2_runtime_image.bin').read_bytes());b=bytearray((B/'level02_region.bin').read_bytes());meta=json.loads((B/'generic_manifest.json').read_text());m=next(v for v in meta if v['level']==2);oldip=m['motion_ptr'];ip=ct['backup_ptr'];raw=bytes.fromhex(ct['pieces']['native_plan_backup']['raw']);assert raw==b[0xa4f2:0xa4f2+len(raw)]
pat=b'\x21'+ip.to_bytes(2,'little')+bytes.fromhex('11f2c4cd43de');at=image.find(pat);assert at>=0;image[at:at+len(pat)]=bytes(len(pat))
# Expanded prefix restore already restores this exact plan, removing duplicate packet.
helper=0xa000+len(image);p=O/'snake_roles';p.with_suffix('.asm').write_text(f'HELPER EQU ${helper:04X}\n'+(R/'src/l2_snake_roles_r127.asm').read_text());exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';q=subprocess.run([str(exe),f'--raw={p}.bin',str(p)+'.asm'],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr;image.extend(p.with_suffix('.bin').read_bytes());assert 0xa000+len(image)<=0xa84c
ordinary=ct['extension']['ordinary']-0xa000;done=ct['extension']['done'];assert image[ordinary:ordinary+5]==bytes([0xfe,39,0x30,(done-(0xa000+ordinary+4))&255,0x5f]);image[ordinary:ordinary+5]=b'\xcd'+helper.to_bytes(2,'little')+bytes([0x30,(done-(0xa000+ordinary+5))&255]);image[ct['extension']['id_map']-0xa000+22]=198
# Route the four native emerging boss-mouth poses through the existing masked
# ECM compositor, retaining their original pixels and per-scanline colours.
layout=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'][1];packets=[];external=0xaeae;new_entries=[];mouths=[]
# Immutable upgraded background under the fixed native mouth rectangle x152/y64.
inputs=json.loads((B/'tile_inputs.json').read_text());body=json.loads((R/'build/graphics/l2_integrated_r67/manifest.json').read_text());background=np.zeros((160,256,3),np.int32);pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],np.int32)
for tile_id,t in enumerate(body['tiles'],34):
 rawtile=bytes.fromhex(inputs['tiles'][tile_id]);x0=t['tx']*32;y0=t['ty']*32
 for cell in range(16):
  tag=rawtile[cell*9];pi=tag+96 if tag<32 else tag-144
  if tag==7:continue
  for y in range(8):
   attr=b[0x2000+pi*8+y];bits=rawtile[cell*9+1+y]
   for x in range(8):background[y0+(cell//4)*8+y,x0+(cell%4)*8+x]=pal[(attr&7)if bits&(128>>x)else(attr>>3)&7]
mouth_base=background[64:88,152:184].copy()
for n in range(41,45):
 q=layout['enemy_descriptors_start']-0x2000+(n-1)*4;w,h=b[q:q+2];p0=int.from_bytes(b[q+2:q+4],'little')-0x2000;pos=p0;arr=np.zeros((w,h*8,2),np.uint8)
 for cy in range(h):
  for cx in range(w):
   tag=b[pos];pos+=1
   if tag==54:continue
   for y in range(8):arr[cx,cy*8+y]=[b[pos+y],b[0x2000+(tag&127)*8+y]]
   pos+=8
 # Native black is transparency; precompose against the upgraded boss base.
 comp=mouth_base.copy()
 for xcell in range(w):
  for y in range(h*8):
   bits,attr=map(int,arr[xcell,y]);ink=attr&7;paper=(attr>>3)&7
   for x in range(8):
    col=ink if bits&(128>>x)else paper
    if col:comp[y,xcell*8+x]=pal[col]
 for xcell in range(w):
  for y in range(h*8):
   pixels=comp[y,xcell*8:xcell*8+8];err=((pixels[:,None,:]-pal[None,:,:])**2).sum(axis=2);best=None
   for paper in range(8):
    for ink in range(8):
     use=err[:,ink]<err[:,paper];score=int(np.minimum(err[:,ink],err[:,paper]).sum());cand=(score,paper,ink,use)
     if best is None or cand[:3]<best[:3]:best=cand
   _,paper,ink,use=best;arr[xcell,y]=[sum((128>>x)for x in range(8)if use[x]),ink|(paper<<3)]
 raw=arr.tobytes();raw+=bytes(480-len(raw));packet=pack(raw);packets.append((n,w,h,raw,packet))
base42=0;delta43=0
for n,w,h,raw,packet in packets:
 if n==43:packet=pack(bytes(x^y for x,y in zip(raw,packets[1][3])))
 if n<43:
  ptr=external;b[ptr:ptr+len(packet)]=packet;external+=len(packet)
 else:
  ptr=ip;b[ptr:ptr+len(packet)]=packet;ip+=len(packet)
 if n==42:base42=ptr
 if n==43:delta43=ptr
 new_entries.extend(bytes([n,0x80|w,h])+ptr.to_bytes(2,'little')*4);mouths.append(dict(id=n,width=w*8,height=h*8,pointer=ptr,raw=raw.hex(),packed=len(packet)))
assert external<=0xb0de
# Reassemble the extension so adding four table entries relocates its data safely,
# rather than appending a duplicate table into the following packed actor sources.
src=(B/'L2_actor_extension.asm').read_text();src=src.replace(' LD BC,$02E7',' LD BC,$0517');src=src.replace(' CP 39\n JR NC,done\n LD E,A',' CALL snake_part\n JR NC,done')
begin=src.index('sprite_table:');end=src.index('scorpion_records:',begin);src=src[:begin]+'sprite_table:\n TABLE_PLACEHOLDER\n'+src[end:];src=src.replace(' ; HL points to a unique4byte','fetch_delta:\n ; HL points to a unique4byte');src+=f'\nmouth_record: DW {base42},{delta43}\n';src+='\n'+(R/'src/l2_snake_roles_r127.asm').read_text().replace('        ORG HELPER','')
def table(rec,mouthrec):
 rows=bytearray()
 for e in ct['entries']:
  ptrs=[rec+e['record']*4]*4 if 'record'in e else e['ptrs'];rows.extend(bytes([e['id'],e['width'],e['height']])+b''.join(p.to_bytes(2,'little')for p in ptrs))
 extra=bytearray(new_entries)
 for off in range(0,len(extra),11):
  if extra[off]==43:extra[off+3:off+11]=base42.to_bytes(2,'little')*4
 return '\n'.join(' DB '+','.join(map(str,(rows+extra+bytes([0]))[i:i+64]))for i in range(0,len(rows)+len(extra)+1,64))
def assemble(rec,mouthrec=0):
 p=O/'L2_actor_extension';p.with_suffix('.asm').write_text(src.replace('TABLE_PLACEHOLDER',table(rec,mouthrec)));q=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy
_,sy=assemble(0);ext,sy=assemble(sy['scorpion_records'],sy['mouth_record']);image=image[:0x4b0]+ext;assert 0xa000+len(image)<=0xa84c
assert sy['sprite_hook']==ct['extension']['sprite_hook'] and sy['fetch_frame']==ct['extension']['fetch_frame']
ct['extension'].update(sy);helper=sy['snake_part'];newtable=sy['sprite_table']
# Preserve the full diagnostic RAM capture, show sixteen essential fields, and
# use only the removed display text/table space for tile pointers.
base_contract=json.loads((B/'integration_contract.json').read_text());scratch=base_contract['kernel_symbols']['SCRATCH'];coords=base_contract['kernel_symbols']['REVEAL_COORDS']
def assemble_file(name,text):
 p=O/name;p.with_suffix('.asm').write_text(text);q=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr;sy2={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy2
debug=(R/'src/debug_ram_screen.asm').read_text().replace('R38 DEBUG','R127 DEBUG').replace('font: INCBIN "assets/fullgame_preloader_font.bin"','font EQU $3D00').replace('LD A,28','LD A,16');remove=['input_label','music_label','seq_label','st0','st1','st2','st3','decoder_label','attr_label','draw_label','sfx_label','timer_label']
for label in remove:debug=re.sub(r'^'+label+r':.*\n','',debug,flags=re.M)
a=debug.index('fields:');z=debug.index('sources:',a);debug=debug[:a]+"""fields:
 DW pc_label,$7C0E,sp_label,$7C20,af_label,$7C0C,bc_label,$7C0A
 DW de_label,$7C08,hl_label,$7C04,ix_label,$7C02,iy_label,$7C00
 DW map_label,$7C22,level_label,$7C40,world_label,$7C48,object_label,$7C4A
 DW cache_label,$7C50,joy_label,$7C60,game_label,$7C46,valid_label,$7C52
"""+debug[z:];dv,ds=assemble_file('debug_compact',debug);table=(0x8000+len(dv)+1)&~1;assert table+104<=scratch;b[0x8000:scratch]=dv.ljust(scratch-0x8000,b'\0');pointers=json.loads((B/'tile_inputs.json').read_text())['ptrs'];b[table:table+104]=b''.join(p.to_bytes(2,'little')for p in pointers)
params='dirty_tiles EQU $11C9\nrepair_mode EQU $11CC\nreveal_index EQU $11CD\nsnapshot_saved EQU $11CE\n'+f'REVEAL_COORDS EQU ${coords:04X}\nforce_tile_draw EQU ${base_contract["kernel_symbols"]["force_tile_draw"]:04X}\ndraw_background_copy EQU ${base_contract["kernel_symbols"]["draw_background_copy"]:04X}\nreveal_return EQU ${base_contract["kernel_symbols"]["reveal_return"]:04X}\n'
b[0x2338:0x2340]=bytes(8)
mark,marks=assemble_file('cached_boss',params+(R/'src/l2_boss_cached_r127.asm').read_text());b[external:external+len(mark)]=mark;attr_entry=external;attrs,ats=assemble_file('capture_boss',params+f'SCRATCH EQU ${scratch:04X}\n'+(R/'src/l2_boss_capture_r127.asm').read_text());b[0xa7cc:0xa7cc+len(attrs)]=attrs
service,ss=assemble_file('repair_service',params+f'ATTR_ENTRY EQU ${attr_entry:04X}\n'+(R/'src/l2_background_repair_service_r127.asm').read_text());entry,es=assemble_file('repair_entry',params+f'paint_body_tile EQU ${ss["paint_body_tile"]:04X}\ntake_dirty EQU ${ss["take_dirty"]:04X}\n'+(R/'src/l2_background_repair_entry_r127.asm').read_text());b[0x106c:0x10f0]=service.ljust(132,b'\0');b[0x1160:0x11c9]=entry.ljust(105,b'\0');b[0x11c9:0x11d0]=bytes(7);assert b[0xf80:0xf83]==bytes.fromhex('7cfec7');b[0xf80:0xf83]=b'\xcd'+ss['damage_lookup'].to_bytes(2,'little')
gateway,gs=assemble_file('dirty_gateway',f'MARK_ENTRY EQU ${external:04X}\n'+(R/'src/l2_dirty_gateway_r127.asm').read_text());b[0x3820:0x3848]=gateway.ljust(40,b'\0');b[0xfb8:0xfc3]=(B/'level02_region.bin').read_bytes()[0xfb8:0xfc3];assert base_contract['kernel_symbols']['INTERLEAVE']+len((B/'interleave.bin').read_bytes())<=0x1e18;b[0x1e18:0x1e20]=bytes.fromhex('d3f4fbc9d3f4c900')
core=(B/'tile_loader.asm').read_text();core=re.sub(r'^reveal_hook EQU .*$', 'reveal_hook EQU $1160',core,flags=re.M);core=re.sub(r'^snapshot_saved EQU .*$', 'snapshot_saved EQU $11CE',core,flags=re.M);core=core.replace('tile_table EQU $1160',f'tile_table EQU ${table:04X}').replace('        DS $3998-$,0','');core=core.replace('        LD ($FF81),A','        LD ($FF81),A\n');core=core.replace('restore_native:\n','restore_native:\n        CALL $A7C0\n')
core=core.replace('        ASSERT $ <= $3998','');ra=core.index('reverse_cache:');rz=core.index('global_palette:',ra);reverse=core[ra:rz];core=core[:ra]+core[rz:];core=core.replace('        ORG $3848','        ORG $3820\n'+reverse+'        DS $3848-$,0\n        ORG $3848',1);core=core.replace('global_palette:\n','global_palette:\n        LD A,1\n        LD ($11CF),A\n');tilecode,ts2=assemble_file('tile_loader',core);assert len(tilecode)<=0x1e0;b[0x3820:0x3a00]=tilecode.ljust(0x1e0,b'\0');b[0x1de:0x1e0]=ts2['get_tile'].to_bytes(2,'little');b[0x157b:0x157d]=ts2['global_palette'].to_bytes(2,'little');assert b[0xf9f:0xfa2]==bytes.fromhex('c47d39');b[0xfa0:0xfa2]=ts2['reverse_cache'].to_bytes(2,'little')
oldrestore=base_contract['tile_symbols']['restore_native'];pat=b'\xcd'+oldrestore.to_bytes(2,'little');assert image.count(pat)==1;image=image.replace(pat,b'\xcd'+ts2['restore_native'].to_bytes(2,'little'));oldsave=base_contract['tile_symbols']['save_native'];inst=m['cache_symbols']['install_motion'];at=b.find(b'\xcd'+oldsave.to_bytes(2,'little'),inst,0xdf30);assert at>=0;b[at+1:at+3]=ts2['save_native'].to_bytes(2,'little');ct['extension']['restore_native_bank5']=ts2['restore_native'];base_contract['tile_symbols']=ts2;base_contract['reveal_symbols'].update(reveal_hook=0x1160,reveal_index=0x11cd,snapshot_saved=0x11ce);(O/'integration_contract.json').write_text(json.dumps(base_contract,indent=2));pal=json.loads((B/'palette_contract.json').read_text());pal['global_helper']=ts2['global_palette'];pal['table']=table;(O/'palette_contract.json').write_text(json.dumps(pal,indent=2))
# This tail belongs to retired native head6, before the untouched projectile16 data.
b[0xa7c0:0xa7cc]=bytes.fromhex('21c5d522fd8c3ed932ff8cc9')
(O/'background_repair_contract.json').write_text(json.dumps(dict(tile_table=table,dirty_flags=[0x11c9,0x11cc],repair_mode=0x11cc,mark=marks,gateway=gs,service=ss,entry=es,debug_fields_displayed=16,debug_full_capture_preserved=True,unpatch=0xa7c0),indent=2))
v=pack(image);assert ip+len(v)<=0x3820,(hex(ip),len(v),hex(ip+len(v)));b[ip:0x3820]=v.ljust(0x3820-ip,b'\0');inst=m['cache_symbols']['install_motion'];pat=b'\x21'+oldip.to_bytes(2,'little')+bytes.fromhex('1100a0');pos=b.find(pat,inst,0xdf30);assert pos>=0;b[pos+1:pos+3]=ip.to_bytes(2,'little');m['motion_ptr']=ip;m['motion_image_bytes']=len(image);ct['imageptr']=ip;ct['extension']['snake_part']=helper;ct['redundant_plan_packet_removed']=True
for pose in mouths:
 if pose['id']==43:
  pose['raw']=next(v['raw']for v in mouths if v['id']==42);pose['pointer']=base42;pose['source_alias']=42
(O/'boss_mouth_mask_contract.json').write_text(json.dumps(dict(poses=mouths,source_range=[0xaeae,external],mouth_record=sy['mouth_record'],base42=base42,delta43=delta43,compositor_address=external,extra_source=[ptr,ptr+len(packet)],sprite_table=newtable,original_native_geometry=True,collision_AI_unchanged=True,precomposed_background_rect=[152,64,32,24]),indent=2))
(O/'L2_runtime_image.bin').write_bytes(image);(O/'generic_manifest.json').write_text(json.dumps(meta,indent=2));(O/'L2_actor_contract.json').write_text(json.dumps(ct,indent=2));b[0x8000:0x82b3]=b[0x8000:0x82b3].replace(b'R126 DEBUG',b'R127 DEBUG');(O/'level02_region.bin').write_bytes(b)
for name in ['LEVEL02.TAP','START02.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R126 PREPARING  ',b'R127 PREPARING  '))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+n]).replace(b'R126 PREPARING  ',b'R127 PREPARING  ');check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+n]=block;at+=n+2
p.write_bytes(v)
for stem in ['boss_motion_fixture','verify_cold_l2_fire','verify_native_revisits','verify_l2_boss_revisits','verify_l2_decode','verify_l2_tiles','trace_l2_reveal','verify_palette_missile']:
 p=R/f'scripts/{stem}_r126.mjs';s=p.read_text(encoding='utf-8-sig').replace('l2_snake_parts_r126','l2_roles_restore_r127').replace('boss_motion_fixture_r126','boss_motion_fixture_r127');
 if stem=='verify_l2_boss_revisits':s=s.replace('frame<100000','frame<250000')
 if stem=='boss_motion_fixture':s=s.replace('c.coreBefore.set([0x3a,0x8a,0x7a],0x28c);','{c.coreBefore.set([0x3a,0x8a,0x7a],0x28c);c.coreBefore.set([0xc5,0xd5,0xd9],0x8fd);}') ;s=s.replace('||i===7656','||(i>=4553&&i<4560)||i===7656')
 (R/f'scripts/{stem}_r127.mjs').write_text(s)
print('Snake roles by native chain ordinal: 9 round then4 spiny; helper',hex(helper),'sourceend',hex(ip+len(pack(image))))




