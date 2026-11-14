from pathlib import Path
import sys,json,zipfile,shutil,re,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code;from build_reviewed_r72 import frames
B=R/'build/fullgame/l1_ghost_r114';O=R/'build/fullgame/l1_blue_boost_r116';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(s in p.name for s in ['l1_','.home.','validation','route','native_jump','ghost_timing','ghost_gameplay']):shutil.copy2(p,O/p.name)
for name in ['generic_manifest.json','walker_runtime.json','global_tags.json','L1_runtime_art.bin']:shutil.copy2(B/name,O/name)
z=zipfile.ZipFile(R/'convref/rtype-l1-blue-enemy-assets.zip');assert z.testzip()is None;choices=json.loads(z.read('choices.json'));ch=choices['families']['blue'];assert ch['source']['id']=='action' and ch['settings']['width']==ch['settings']['height']==40;(O/'selected_blue_choices.json').write_text(json.dumps(choices,indent=2));blue=b''.join(z.read(f'blue/frame_{i:02d}.pairs.bin')for i in range(2));assert len(blue)==800 and all(a&192==0 for a in blue[1::2]);packedblue=pack(blue);assert len(packedblue)<=512
metas=json.loads((B/'generic_manifest.json').read_text());meta=next(x for x in metas if x['level']==1);walk=json.loads((B/'walker_runtime.json').read_text());w=next(x for x in walk if x['level']==1);sy0=w['extension'];image0=(B/'L1_runtime_image.bin').read_bytes();b=bytearray((B/'level01_region.bin').read_bytes());old=bytes(b);used=set(range(16))|{t&127 for d in frames(b,1)for _,t,_ in d['cells']if t!=54};free=sorted(set(range(128))-used);source_len=min(len(packedblue),len(free)*8);tail=packedblue[source_len:];assert len(tail)<=3;chunks=[];left=source_len;at=0
for row in free:
 if not left:break
 n=min(8,left)
 if chunks and row*8+0x2000==chunks[-1]['address']+chunks[-1]['bytes'] and chunks[-1]['bytes']+n<=255:chunks[-1]['bytes']+=n
 else:chunks.append(dict(address=0x2000+row*8,bytes=n))
 b[0x2000+row*8:0x2000+row*8+n]=packedblue[at:at+n];at+=n;left-=n
assert not left
loader_source='BLUE_CHUNKS EQU '+str(len(chunks))+'\nBLUE_TAIL EQU '+str(len(tail))+'\n'+(R/'src/l1_blue_art_load.asm').read_text();(O/'blue_load.asm').write_text(loader_source)
exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';p=O/'blue_load';r=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(O/'blue_load.asm')],capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr
oldtable=w['preload_table'];oldcacheptr=int.from_bytes(b[oldtable+1:oldtable+3],'little');cache=bytearray(unpack(b[oldcacheptr:]));assert len(cache)==768;assert cache[0x200:0x2e0]==bytes(0xe0);loader=p.with_suffix('.bin').read_bytes();cache[0x200:0x200+len(loader)]=loader;chunk_table=bytes(v for ch in chunks for v in [(ch['address']-0x2000)//8,ch['bytes']]);assert 0x260+len(chunk_table)<=0x2e0;cache[0x260:0x260+len(chunk_table)]=chunk_table;cache[0x25d:0x25d+len(tail)]=tail
# Existing bank5 sprite bytes and pointers remain exact; new boost frames use the
# adjacent unused bank6 cache space, after helper variables, before sprite scratch.
for i in range(2):w['assets'].append(dict(level=1,key='blue_boost',frame=i,id=184+i,name=f'L1_blue_boost_{i}',size=[40,40],pointer=0xc300+i*400,bytes=400,bank=6,source=f'arcade{260+i*2}',choice='exact user ZIP'))
oldmaps=image0[sy0['id_map']-0xa000:sy0['id_map']-0xa000+256];assert oldmaps[205:]==bytes(51);mapping=bytearray(oldmaps[:205]);mapping[41]=184
oldrawptr=int.from_bytes(image0[sy0['load_new_art']-0xa000+5:sy0['load_new_art']-0xa000+7],'little');raw=(B/'L1_runtime_art.bin').read_bytes();prefix=pack(cache);backup=pack(bytes.fromhex(meta['backup']));backptr=0x2400+len(prefix);table=backptr+len(backup);rawptr=table+5;s=(B/'L1_walker_extension.asm').read_text();s=s.replace(' LD A,($DF3E)\n CP 16',' LD A,($DF3E)\n CP 205\n JR NC,hook_done\n CP 16',1);s=s.replace(' LD C,0\n CP 200',' LD C,0\n CP 184\n JR NZ,ordinary_count\n LD C,1\n JR single_pose\nordinary_count:\n CP 200',1)
entries=[bytes([a['id'],128|a['size'][0]//8,a['size'][1]//8])+a['pointer'].to_bytes(2,'little')*4 for a in w['assets']];s=re.sub(r'sprite_table:\n.*?id_map:', 'sprite_table:\n DB '+','.join(map(str,b''.join(entries)+b'\0'))+'\nid_map:',s,flags=re.S);s=re.sub(r'id_map:\n.*?actor_phases:', 'id_map:\n DB '+','.join(map(str,mapping))+'\nactor_phases:',s,flags=re.S);s=s.replace(f' LD HL,${oldrawptr:04X}',f' LD HL,${rawptr:04X}');needle=' CALL $DE4F\n LD HL,actor_phases';assert needle in s;s=s.replace(needle,' CALL $DE4F\n LD ($C7F2),SP\n LD SP,$C7F0\n CALL $DEAE\n CALL $C200\n LD SP,($C7F2)\n LD HL,actor_phases',1)
clear=' LD HL,actor_phases\n LD DE,actor_phases+1\n LD BC,255\n LD (HL),0\n LDIR\n';assert clear in s;s=s.replace(clear,'')
lines=[]
for line in s.splitlines():
 if line.strip().startswith('DB '):
  vals=line.strip()[3:].split(',');lines.extend(' DB '+','.join(vals[k:k+64])for k in range(0,len(vals),64))
 else:lines.append(line)
p=O/'L1_walker_extension';p.with_suffix('.asm').write_text('\n'.join(lines));r=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
motion=image0[:sy0['restore_native_bank5']-0xa000];pat=b'\x21'+meta['backup_ptr'].to_bytes(2,'little');assert motion.count(pat)==1;motion=motion.replace(pat,b'\x21'+backptr.to_bytes(2,'little'));assert sy['sprite_hook']==sy0['sprite_hook'];image=motion+p.with_suffix('.bin').read_bytes();guardstart=0xa000+len(image);assert guardstart<=0xa870;image+=bytes([0xa7])*(0xa870-guardstart);packedraw=pack(raw);ip=rawptr+len(packedraw);packet=pack(image);end=ip+len(packet);assert end<=0x3a00,(hex(end),len(packedblue),len(chunks),len(prefix));b[0x2400:0x3a00]=bytes(0x1600);b[0x2400:backptr]=prefix;b[backptr:table]=backup;b[table:rawptr]=bytes([1])+bytes.fromhex('002400c0');b[rawptr:ip]=packedraw;b[ip:end]=packet
cs=meta['cache_symbols'];q=b.find(b'\xdd\x21'+oldtable.to_bytes(2,'little'),cs['preload'],cs['install_motion']);assert q>=0;b[q+2:q+4]=table.to_bytes(2,'little');q2=b.find(b'\x21'+meta['motion_ptr'].to_bytes(2,'little'),cs['install_motion'],0xdf30);assert q2>=0;b[q2+1:q2+3]=ip.to_bytes(2,'little');q3=b.find(b'\xc3'+sy0['load_new_art'].to_bytes(2,'little'),cs['install_motion'],0xdf30);assert q3>=0;b[q3+1:q3+3]=sy['load_new_art'].to_bytes(2,'little');assert unpack(b''.join(b[x['address']:x['address']+x['bytes']]for x in chunks)+tail)==blue;assert unpack(b[rawptr:])==raw;assert unpack(b[ip:])==image
(O/'level01_region.bin').write_bytes(b);(O/'L1_runtime_image.bin').write_bytes(image);(O/'L1_blue_art.bin').write_bytes(blue);(O/'L1_preload_cache.bin').write_bytes(cache);w.update(extension=sy,preload_table=table,motion_ptr=ip,immutable_end=end,runtime_bytes=len(image));w['groups'].append(dict(level=1,key='blue_boost',original=[41],base=184,count=2,size=[40,40],two_pose_action_cycle=True));meta.update(motion_ptr=ip,motion_image_bytes=len(image),backup_ptr=backptr,walker_extension=sy);(O/'walker_runtime.json').write_text(json.dumps(walk,indent=2));(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));(O/'blue_contract.json').write_text(json.dumps(dict(source_zip_sha256=__import__('hashlib').sha256((R/'convref/rtype-l1-blue-enemy-assets.zip').read_bytes()).hexdigest(),end=end,rawptr=rawptr,imageptr=ip,guard_start=guardstart,guard_bytes=0xa870-guardstart,artbase=0xa870,artend=0xc000,bluebase=0xc300,blueend=0xc620,source_ranges=chunks,source_tail=list(tail),aux_bytes=len(packedblue),source_rows_unused=sorted(free),native_restore_end=0xf87c,cache_source=0x2400,cache_bytes=len(cache),backup_ptr=backptr,preload_table_operand=q+2,install_operand=q2+1,warmup_operand=q3+1),indent=2))
for name in ['LEVEL01.TAP','START01.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in [0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
oldlabel=b'R114 PREPARING  ';new=b'R116 PREPARING  '
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(oldlabel,new))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 size=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+size]).replace(oldlabel,new);check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+size]=block;at+=size+2
p.write_bytes(v)
for stem in ['boss_motion_fixture']:
 s=(R/f'scripts/{stem}_r114.mjs').read_text().replace('l1_ghost_r114','l1_blue_boost_r116').replace('boss_motion_fixture_r114','boss_motion_fixture_r116');(R/f'scripts/{stem}_r116.mjs').write_text(s)
print('Boost40x40 exacttwoframes; source',len(packedblue),'bytes in unused palette slots; payload',hex(end),'guard',0xa870-guardstart,'newartC300..C61F')
