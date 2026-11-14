from pathlib import Path
import sys,json,shutil,re,subprocess,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
from pack_optimal_r87 import pack_optimal as pack
from build_reviewed_r72 import phase_rows
from build_rocket_fix import code
B=R/'build/fullgame/highscore_r138';O=R/'build/fullgame/l7_all_choices_r140';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.json','.asm','.sym']:shutil.copy2(p,O/p.name)
b=bytearray((B/'level07_region.bin').read_bytes());old=bytes(b);walk=json.loads((B/'walker_runtime.json').read_text());w=next(q for q in walk if q['level']==7);metas=json.loads((B/'generic_manifest.json').read_text());meta=next(q for q in metas if q['level']==7);sy=w['extension'];cache=bytearray(6144);t=w['preload_table']
for k in range(b[t]):
 p=int.from_bytes(b[t+1+k*4:t+3+k*4],'little');d=int.from_bytes(b[t+3+k*4:t+5+k*4],'little')-0xc000;v=unpack(b[p:]);cache[d:d+len(v)]=v
cache=bytearray((R/'build/graphics/l7_final_inputs/cache.bin').read_bytes());raw=bytearray((R/'build/graphics/l7_final_inputs/raw.bin').read_bytes());base=0xb200;assets=json.loads((R/'build/graphics/l7_final_inputs/assets.json').read_text());newentries=sorted(json.loads((R/'build/graphics/l7_final_inputs/entries.json').read_text()),key=lambda q:q['id']);entries=[bytes([q['id'],128|q['width']//8,q['height']//8])+q['ptr'].to_bytes(2,'little')*4 for q in newentries]
# The fixed housing is drawn by the native background path, not the moving-actor hook.
# Give its eight native cells exact selected ECM rows; only unused native palette
# slots from retired compiled families may be reused.
lay=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'][6];mem=bytes(0xc000)+old[0xa000:0xe000];used=set();retired={11,12,13,14,15,16,17,18,19,20,21,22,25,26,27,28,29,30,31,32,35,37,41,42,43,44,45,51}
for ident in range(1,lay['enemy_descriptors']+1):
 at=lay['enemy_descriptors_start']+(ident-1)*4;ww,hh=mem[at:at+2];ptr=int.from_bytes(mem[at+2:at+4],'little')
 for _ in range(ww*hh):
  tag=mem[ptr];ptr+=1
  if tag!=54:
   if ident not in retired:used.add(tag&127)
   ptr+=8
free=iter(sorted(set(range(96,128))-used));housing=(R/'build/graphics/l7_final_inputs/wall_0.pairs').read_bytes()[128:];native=bytearray();palette_rows={}
for cy in range(4):
 for cx in range(2):
  key=bytes(housing[2*(cx*32+cy*8+y)+1]for y in range(8));bits=bytes(housing[2*(cx*32+cy*8+y)]for y in range(8))
  if key not in palette_rows:palette_rows[key]=next(free)
  tag=palette_rows[key];b[0x2000+tag*8:0x2000+tag*8+8]=key;native+=bytes([tag])+bits
assert len(native)==72;b[0xad91:0xadd9]=native
# Native dirty-cell/erase masks must follow the chosen silhouettes too.
# Pose17 repeats chosen white pose1, so alias it to15 and reuse its old81-byte
# source for cyan30. Repack31/32 into their original family span, without
# touching the cache packet ending atCB4E or the following35 source atCC31.
def authoring_mask(key,k,width,height):
 v=(R/f'build/graphics/l7_final_inputs/{key}_{k}.pairs').read_bytes();fullw=32 if key=='wall' else width;out=bytearray()
 for cy in range(height//8):
  for cx in range(width//8):
   rows=[]
   for yy in range(8):
    y=cy*8+yy;bits,attr=v[2*(cx*height+y):2*(cx*height+y)+2];ink=attr&7;paper=attr>>3&7;rows.append(sum(128>>j for j in range(8)if (ink if bits&(128>>j)else paper)))
   if not any(rows):out.append(54)
   else:out+=bytes([7])+bytes(rows)
 return out
mask_contract=[]
def install_mask(ident,key,k,ptr,limit):
 v=authoring_mask(key,k,24 if key in['white','cyan','round']else 16,32 if key=='wall'else 24 if key!='orb'else 16);assert ptr+len(v)<=limit
 b[ptr-0x2000:ptr-0x2000+len(v)]=v;at=lay['enemy_descriptors_start']+(ident-1)*4-0x2000;b[at+2:at+4]=ptr.to_bytes(2,'little');mask_contract.append(dict(id=ident,ptr=ptr,bytes=len(v)))
for ident,k,ptr in[(14,0,0xc6e7),(15,1,0xc738),(16,2,0xc789),(17,1,0xc738)]:install_mask(ident,'white',k,ptr,ptr+81)
install_mask(30,'cyan',0,0xc7da,0xc82b);install_mask(31,'cyan',1,0xcb4e,0xcb9f);install_mask(32,'cyan',2,0xcb9f,0xcc31)
install_mask(35,'orb',0,0xcc31,0xcc55);install_mask(37,'round',0,0xcc9e,0xccef)
arm_ptr=0xcdd9
for ident,k in zip(range(42,46),range(4)):
 install_mask(ident,'wall',k,arm_ptr,0xceb1);arm_ptr+=mask_contract[-1]['bytes']
(O/'native_mask_contract.json').write_text(json.dumps(dict(entries=mask_contract,arm_end=arm_ptr,housing_rows={str(v):k.hex()for k,v in palette_rows.items()}),indent=2))
# Repack existing three cache streams and add explicit native-ID entries.
# Select largest prefix fitting existing immutable external slot.
planar=raw[::2]+raw[1::2]+bytes(0xc000-0xb200-len(raw))+cache[::2]+cache[1::2];split=988;extra=524;ext=pack(planar[:split]);mid=pack(planar[split:split+extra]);rest=pack(planar[split+extra:]);assert len(ext)<=662 and len(mid)<=438;pretab=0x2400+len(rest);rawptr=pretab+13;rawpack=b'';imageptr=rawptr
source=(B/'L7_walker_extension.asm').read_text();source=source.replace(' LD HL,$2EE6\n LD DE,$B200\n CALL $DE4F',' LD A,$ED\n OUT ($F4),A\n XOR A\n LD ($E3F0),A\n NOP');source += '\npost_cache:\n LD A,$6F\n OUT ($F4),A\n LD DE,$C000\n LD BC,4863\n CALL unshuffle\n LD DE,$B200\n LD BC,3135\n CALL unshuffle\n LD A,$ED\n OUT ($F4),A\n RET\nunshuffle:\n LD (shuffle_base),DE\n LD (shuffle_mod),BC\n LD HL,1\nshuffle_outer:\n LD (shuffle_index),HL\nshuffle_walk:\n CALL shuffle_next\n LD DE,(shuffle_index)\n OR A\n SBC HL,DE\n JR C,shuffle_advance\n ADD HL,DE\n JR NZ,shuffle_walk\n LD HL,(shuffle_index)\n LD DE,(shuffle_base)\n ADD HL,DE\n LD A,(HL)\n LD (shuffle_value),A\n LD HL,(shuffle_index)\nshuffle_cycle:\n CALL shuffle_next\n LD (shuffle_current),HL\n LD DE,(shuffle_base)\n ADD HL,DE\n LD A,(HL)\n LD E,A\n LD A,(shuffle_value)\n LD (HL),A\n LD A,E\n LD (shuffle_value),A\n LD HL,(shuffle_current)\n LD DE,(shuffle_index)\n SBC HL,DE\n ADD HL,DE\n JR NZ,shuffle_cycle\nshuffle_advance:\n LD HL,(shuffle_index)\n INC HL\n LD DE,(shuffle_mod)\n OR A\n SBC HL,DE\n RET NC\n ADD HL,DE\n JR shuffle_outer\nshuffle_next:\n ADD HL,HL\n LD DE,(shuffle_mod)\n OR A\n SBC HL,DE\n RET NC\n ADD HL,DE\n RET\nshuffle_base: DW 0\nshuffle_mod: DW 0\nshuffle_index: DW 0\nshuffle_current: DW 0\nshuffle_value: DB 0\n ASSERT $ <= $A998\n';imageold=(B/'L7_runtime_image.bin').read_bytes();table=imageold[sy['sprite_table']-0xa000:sy['id_map']-0xa000];assert table[-1]==0;table=b''.join(table[k:k+11]for k in range(0,len(table)-1,11)if table[k]not in{q['id']for q in newentries})+b''.join(entries)+bytes([0]);a=source.index('sprite_table:\n');z=source.index('id_map:\n',a);source=source[:a]+'sprite_table:\n'+'\n'.join(' DB '+','.join(map(str,table[k:k+64]))for k in range(0,len(table),64))+'\n'+source[z:];p=O/'L7_walker_extension';p.with_suffix('.asm').write_text(source);exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';q=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
ns={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};assert ns['sprite_hook']==sy['sprite_hook']and ns['load_new_art']==sy['load_new_art'];image=imageold[:sy['restore_native_bank5']-0xa000]+p.with_suffix('.bin').read_bytes();ip=pack(image);end=imageptr+len(ip);print('capacity',hex(end),'limit3A00',len(rest),len(rawpack),len(ip),split,flush=True);assert end<=0x3a00
b[0xaeb1:0xaeb1+len(ext)]=ext;b[0xa998:0xa998+len(mid)]=mid;b[0x2400:0x3a00]=bytes(0x1600);b[0x2400:pretab]=rest;b[pretab:rawptr]=bytes([3])+bytes.fromhex('b1ae00b2')+bytes.fromhex('98a9')+(0xb200+split).to_bytes(2,'little')+bytes.fromhex('0024')+(0xb200+split+extra).to_bytes(2,'little');b[rawptr:imageptr]=rawpack;b[imageptr:end]=ip
cs=meta['cache_symbols'];a=b.find(b'\xdd\x21'+t.to_bytes(2,'little'),cs['preload'],cs['install_motion']);assert a>=0;b[a+2:a+4]=pretab.to_bytes(2,'little');a=b.find(b'\x21'+w['motion_ptr'].to_bytes(2,'little'),cs['install_motion'],0xdf30);assert a>=0;b[a+1:a+3]=imageptr.to_bytes(2,'little')
pos=b.find(bytes.fromhex('3eedd3f4c9'),cs['preload'],cs['install_motion']);assert pos>=0;b[pos:pos+5]=bytes([0xc3])+ns['post_cache'].to_bytes(2,'little')+bytes(2)
w.update(extension=ns,immutable_end=end,runtime_bytes=len(image),art_bytes=len(raw),preload_table=pretab,motion_ptr=imageptr);w['assets']+=assets;meta.update(motion_ptr=imageptr,motion_image_bytes=len(image),walker_extension=ns,preload_blocks=[[0xaeb1,0xb200],[0xa998,0xc000+split],[0x2400,0xc000+split+extra]])
for name,data in [('level07_region.bin',b),('L7_runtime_art.bin',raw),('L7_runtime_image.bin',image),('L7_expected_cache.bin',cache)]:(O/name).write_bytes(data)
w['native_descriptor_overrides']=newentries;w['preload_format']='Combined planar raw B200..BE3F, reserved gap, planar cache C000..D2FF; post_cache interleaves both';w['retired_cache_range']=[0xc980,0xcf80]
for a in w['assets']:
 if 'name'not in a:a['name']=f'L7_selected_{a["key"]}_{a["frame"]}'
meta['sprites']=[q for q in meta['sprites']if q['id']!=51];meta['fixed_overrides']=newentries;meta['preload_format']=w['preload_format'];meta['reserved_cache_ranges']=[dict(start=0xc980,end=0xcb30,owner='selected cyan walker'),dict(start=0xcb30,end=0xcf30,owner='selected assembled wall poses')]
(O/'walker_runtime.json').write_text(json.dumps(walk,indent=2));(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));(O/'l7_choices_contract.json').write_text(json.dumps(dict(assets=assets,split=split,rawptr=rawptr,imageptr=imageptr,end=end,native_walker_pose_order=[0,1,2,1],planar=True,extra=extra,cache_shuffle=ns['post_cache'],raw_shuffle=ns['post_cache'],wall_integrated=True,cyan_ids=[30,31,32],white_ids=[14,15,16,17]),indent=2))
for name in['LEVEL07.TAP','START07.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[k*8192+j*1024:k*8192+(j+1)*1024]for k in[0,1,4,5,6,7]for j in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
s=(R/'scripts/boss_motion_fixture_r138.mjs').read_text().replace('highscore_r138','l7_all_choices_r140');(R/'scripts/boss_motion_fixture_r140.mjs').write_text(s)


# Version-only labels in the common startup image; gameplay code unchanged.
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R138',b'R140'))
p=O/'rtype/rt.tap';src=p.read_bytes();v=bytearray();at=0
while at<len(src):
 length=int.from_bytes(src[at:at+2],'little');q=bytearray(src[at+2:at+2+length]).replace(b'R138',b'R140');q[-1]=0
 for x in q[:-1]:q[-1]^=x
 v+=len(q).to_bytes(2,'little')+q;at+=length+2
p.write_bytes(v)
