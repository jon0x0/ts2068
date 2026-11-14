"""r86: four-pose presentation using load-time expanded ROM assets in bank5."""
from pathlib import Path
import sys,json,shutil,re,subprocess,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import pack,unpack
from build_reviewed_r72 import phase_rows
from build_rocket_fix import code
B=R/'build/fullgame/l1_machinery_r84';O=R/'build/fullgame/walkers_exhaust_r86';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']and not any(s in p.name for s in['.home','trace','actors','captures']):shutil.copy2(p,O/p.name)
A=R/'build/graphics/walker_runtime_r86';m=json.loads((A/'inputs.json').read_text());metas=json.loads((B/'generic_manifest.json').read_text());reports=[]
def asm(name,s):
 p=O/(name+'.asm');lines=[]
 for line in s.splitlines():
  if line.strip().startswith('DB '):
   vals=line.strip()[3:].split(',');lines.extend(' DB '+','.join(vals[k:k+64])for k in range(0,len(vals),64))
  else:lines.append(line)
 s='\n'.join(lines);p.write_text(s);r=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy
for n in[1,3,4,6,7]:
 meta=next(r for r in metas if r['level']==n);b=bytearray((B/f'level{n:02d}_region.bin').read_bytes());original=bytes(b);cs={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/f'L{n}_cache.sym').read_text(),re.I)};ms={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/f'L{n}_motion.sym').read_text(),re.I)}
 off=original.find(bytes.fromhex('dd21'),cs['preload']+0 if False else 0xde90,0xdedb);assert off>=0;nativetab=int.from_bytes(original[off+2:off+4],'little');expanded=bytearray(6144);used=0
 for k in range(original[nativetab]):
  p=int.from_bytes(original[nativetab+1+4*k:nativetab+3+4*k],'little');dest=int.from_bytes(original[nativetab+3+4*k:nativetab+5+4*k],'little');v=unpack(original[p:]);expanded[dest-0xc000:dest-0xc000+len(v)]=v;used=max(used,dest-0xc000+len(v))
 assert used<=6144
 start=0x2800 if n==4 else 0x2400;split=0xb00 if n==4 else (0x2f0 if n==7 else 0);external=pack(expanded[:split])if split else b'';oldpack=pack(expanded[split:used]);assert unpack(oldpack)==expanded[split:used];
 if external:
  extaddr=0xa9c7 if n==4 else 0xaeb1;extcap=0xd30c-0xc9c7 if n==4 else 0xd147-0xceb1;assert len(external)<=extcap,(n,len(external),extcap);b[extaddr:extaddr+len(external)]=external
 backup=pack(bytes.fromhex(meta['backup']))if meta['backup_ptr']else b'';backptr=start+len(oldpack)if backup else 0;pretab=start+len(oldpack)+len(backup);newptr=pretab+(9 if split else 5);rawbase=0xb400 if n==4 else (0xb200 if n==7 else 0xb000)
 raw=bytearray();entries=[];mapping=bytearray(256);masks=bytearray(256);newassets=[]
 groups=[g for g in m['groups']if g['level']==n];replaced={i for g in groups for i in g['original']}
 for at in range(0xe350,0xe3f0,11):
  if original[at]==0:break
  if original[at]not in replaced:entries.append(original[at:at+11])
 for g in groups:
  for ident in g['original']:mapping[ident]=g['base'];masks[ident]=g['count']-1
  for a in[a for a in m['assets']if a['level']==n and a['key']==g['key']]:
   w,h=a['size'];attrs=np.frombuffer((A/(a['name']+'.attrs')).read_bytes(),np.uint8).reshape(h,w//8);bits=np.unpackbits(np.frombuffer((A/(a['name']+'.bits')).read_bytes(),np.uint8)).reshape(h,w);im=np.where(bits,np.repeat(attrs&7,8,axis=1),np.repeat((attrs>>3)&7,8,axis=1)).astype('uint8');v=phase_rows(im,spill=False,normal=True);dest=rawbase+len(raw);raw.extend(v);entries.append(bytes([a['id'],0x80|w//8,h//8])+dest.to_bytes(2,'little')*4);newassets.append(dict(**a,pointer=dest,bytes=len(v)))
 assert rawbase+len(raw)<=0xc000,(n,len(raw));assert len({e[0]for e in entries})==len(entries),(n,'duplicate ids')
 motion=bytearray(original[meta['motion_ptr']:meta['motion_ptr']+meta['motion_image_bytes']]);oldlen=len(motion)
 if backup:
  pat=b'\x21'+meta['backup_ptr'].to_bytes(2,'little');assert motion.count(pat)==1;motion=motion.replace(pat,b'\x21'+backptr.to_bytes(2,'little'))
 tablebytes=b''.join(entries)+bytes([0]);org=0xa000+len(motion)
 source=f''' ORG ${org:04X}
sprite_hook:
 PUSH BC
 PUSH DE
 LD A,($DF3E)
 LD E,A
 LD D,0
 LD HL,id_map
 ADD HL,DE
 LD A,(HL)
 OR A
 JR Z,hook_done
 LD B,A
 LD C,0
 CP 200
 JR C,single_pose
 LD C,3
single_pose:
 LD A,IYL
 LD E,A
 LD HL,actor_phases
 ADD HL,DE
 LD A,(HL)
 INC (HL)
 AND C
 ADD A,B
 LD ($DF3E),A
hook_done:
 POP DE
 POP BC
 LD HL,sprite_table
 RET
load_new_art:
 LD A,$6F
 OUT ($F4),A
 LD HL,${newptr:04X}
 LD DE,${rawbase:04X}
 CALL ${cs['decompress']:04X}
 LD HL,actor_phases
 LD DE,actor_phases+1
 LD BC,255
 LD (HL),0
 LDIR
 JP ${ms['warmup']:04X}
sprite_table:
 DB {','.join(map(str,tablebytes))}
id_map:
 DB {','.join(map(str,mapping))}
actor_phases:
 DS 256,0
 ASSERT $ <= $B000
'''
 extension,sy=asm(f'L{n}_walker_extension',source);at=motion.find(bytes.fromhex('2150e3'));assert at>=0
 if n==1:motion[0x19:at]=bytes(at-0x19)
 motion[at:at+3]=bytes([0xcd])+sy['sprite_hook'].to_bytes(2,'little');image=bytes(motion)+extension;assert n!=4 or 0xa000+len(image)<=0xa9c7;packedraw=pack(raw);imageptr=newptr+len(packedraw);packedimage=pack(image);end=imageptr+len(packedimage);assert end<=0x3a00,(n,hex(end),len(oldpack),len(packedraw),len(packedimage));assert unpack(packedraw)==raw and unpack(packedimage)==image
 b[start:0x3a00]=bytes(0x3a00-start);b[start:start+len(oldpack)]=oldpack;b[start+len(oldpack):pretab]=backup;tabdata=(bytes([2])+extaddr.to_bytes(2,'little')+bytes.fromhex('00c0')+start.to_bytes(2,'little')+(0xc000+split).to_bytes(2,'little'))if split else(bytes([1])+start.to_bytes(2,'little')+bytes.fromhex('00c0'));b[pretab:pretab+len(tabdata)]=tabdata;b[newptr:imageptr]=packedraw;b[imageptr:end]=packedimage;b[off+2:off+4]=pretab.to_bytes(2,'little')
 inst=cs['install_motion'];q=b.find(b'\x21'+meta['motion_ptr'].to_bytes(2,'little'),inst,0xdf30);assert q>=0;b[q+1:q+3]=imageptr.to_bytes(2,'little');pat=b'\x01'+oldlen.to_bytes(2,'little')+bytes.fromhex('edb0');q=b.find(pat,inst,0xdf30);assert q>=0;b[q:q+5]=bytes([0xcd])+cs['decompress'].to_bytes(2,'little')+bytes(2);pat=b'\xc3'+ms['warmup'].to_bytes(2,'little');q=b.find(pat,inst,0xdf30);assert q>=0;b[q+1:q+3]=sy['load_new_art'].to_bytes(2,'little')
 (O/f'level{n:02d}_region.bin').write_bytes(b);(O/f'L{n}_runtime_image.bin').write_bytes(image);(O/f'L{n}_runtime_art.bin').write_bytes(raw);report=dict(level=n,extension=sy,groups=groups,assets=newassets,immutable_end=end,runtime_bytes=len(image),art_bytes=len(raw),original_preload_bytes=used,compressed_code=True,preload_table=pretab,motion_ptr=imageptr);reports.append(report);meta.update(motion_ptr=imageptr,motion_image_bytes=len(image),motion_compressed=True,backup_ptr=backptr,preload_blocks=([[extaddr,0xc000],[start,0xc000+split]]if split else[[start,0xc000]]),walker_extension=sy);print(n,'end',hex(end),'code',len(image),'art',len(raw),flush=True)
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();(O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)));(O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))
(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));(O/'walker_runtime.json').write_text(json.dumps(reports,indent=2));s=(R/'scripts/boss_motion_fixture_r84.mjs').read_text().replace('l1_machinery_r84','walkers_exhaust_r86');(R/'scripts/boss_motion_fixture_r86.mjs').write_text(s)
for stem,version in [('verify_boss_game',84),('verify_world_jump',80),('trace_l3_fragment_actors',82)]:
 s=(R/f'scripts/{stem}_r{version}.mjs').read_text().replace(f'boss_motion_fixture_r{version}','boss_motion_fixture_r86');(R/f'scripts/{stem}_r86.mjs').write_text(s)





