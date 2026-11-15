"""L1 current actor-art cache on a true-ROM stock HOME layout. Experimental."""
from pathlib import Path
import json,subprocess,re,hashlib,sys,os
from stock_tap_motion_config import enabled as tap_motion_enabled, composition_enabled, procedural_enabled
from pack_optimal_r87 import pack_optimal
from boss_motion_assets_r60 import unpack
R=Path.cwd();level=int(sys.argv[1]);assert 1<=level<=8;O=R/f'build/cartridges/integration_work/level{level:02d}';base=(O/'compressed_kernel_base.rom').read_bytes();b=bytearray(base);layout=json.loads((O/'compressed_kernel_layout.json').read_text());j=json.loads((O.parent/f'L{level}_written_stock_frames.json').read_text());foundation=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'][level-1];descriptor_end=foundation['enemy_descriptors_start'];exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
capture_contract=j.get('captureContract',{})
assert capture_contract.get('version')==2 and all(capture_contract.get(k)for k in ('clearedNativeOwnersAndFlags','selectorAndPainterWrites','returnedOrigin')),'Regenerate actor art with the clean native-write capture contract'
motion_enabled=tap_motion_enabled(level)
proc_enabled=procedural_enabled(level)
overlap_enabled=composition_enabled(level)
if not overlap_enabled:(O/'overlap_contract.json').unlink(missing_ok=True)
irq_decode_enabled=os.environ.get('STOCK_IRQ_DECODE')=='1'
if not irq_decode_enabled:(O/'decode_irq_contract.json').unlink(missing_ok=True)
# BRIGHT applies to both colors on the real video path: reserve normal black.
black_normalized=0
for row in j['palette']:
 for i,a in enumerate(row):
  if a&64 and(not a&7 or not a&56):row[i]=a&~64;black_normalized+=1
# L4 IDs64..95 are destructible background chain grow/erase fragments.
# Their blank cells must overwrite the previous world pixels, not act as
# transparent actor padding. Keep separate frame copies for this family.
if level==4:
 blank=[7]*8
 if blank not in j['palette']:j['palette'].append(blank)
 blank_pi=j['palette'].index(blank);converted={}
 for variant in j['variants']:
  if not 64<=variant['id']<=95 or variant['frame']<0:continue
  old_index=variant['frame']
  if old_index not in converted:
   original=j['frames'][old_index]
   if -1 not in original['rows']:converted[old_index]=old_index
   else:
    frame=dict(original);frame['rows']=[];frame['bits']=[];offset=0
    for pi in original['rows']:
     if pi<0:
      assert original['bits'][offset]==54;offset+=1
      frame['rows'].append(blank_pi);frame['bits'] += [7]+[0]*8
     else:
      frame['rows'].append(pi);frame['bits'] += original['bits'][offset:offset+9];offset+=9
    assert offset==len(original['bits'])
    converted[old_index]=len(j['frames']);j['frames'].append(frame)
  variant['frame']=converted[old_index]
# Shared HUD/effect frames use the same bounded HOME cache.
common=json.loads((O.parent/f'L{level}_common_direct_frames.json').read_text());j=json.loads(json.dumps(j));common_palette=[]
for row in common['palette']:
 for i,a in enumerate(row):
  if a&64 and(not a&7 or not a&56):row[i]=a&~64;black_normalized+=1
for row in common['palette']:
 if row not in j['palette']:j['palette'].append(row)
 common_palette.append(j['palette'].index(row))
common_frames=[]
for frame in common['frames']:
 frame=dict(frame);frame['rows']=[-1 if pi<0 else common_palette[pi]for pi in frame['rows']]
 key=(frame['w'],frame['h'],frame['bits'],frame['rows']);found=next((i for i,f in enumerate(j['frames'])if (f['w'],f['h'],f['bits'],f['rows'])==key),None)
 if found is None:found=len(j['frames']);j['frames'].append(frame)
 common_frames.append(found)
body_ids=[];body_coordinates=[]
if level==2:
 from stock_l2_body_assets import append_body
 body_ids,body_coordinates=append_body(R,j)
 j['boss_tiles']=[dict(frame=fi,coord=coord)for fi,coord in zip(body_ids,body_coordinates)]
motion_variants=[];motion_vertical={}
if motion_enabled:
 motion=json.loads((O.parent/f'L{level}_tap_motion_frames.json').read_text());pal=[];indices=[]
 for row in motion['palette']:
  row=[a&~64 if a&64 and(not a&7 or not a&56)else a for a in row]
  if row not in j['palette']:j['palette'].append(row)
  pal.append(j['palette'].index(row))
 for frame in motion['frames']:
  frame=dict(frame,rows=[pal[pi]if pi>=0 else -1 for pi in frame['rows']])
  found=next((i for i,f in enumerate(j['frames'])if all(f[k]==frame[k]for k in ('w','h','bits','rows'))),None)
  if found is None:found=len(j['frames']);j['frames'].append(frame)
  indices.append(found)
 motion_variants=[dict(v,frame=indices[v['frame']])for v in motion['variants']]
 j['motion_variants']=motion_variants
 if level in (2,4,5,7)and not proc_enabled:
  index={(v['id'],v['anim'],v['px'],v['py'],v['flip']):v for v in motion_variants}
  for v in motion_variants:
   if not v['py']:continue
   parent=index[(v['id'],v['anim'],v['px'],0,v['flip'])]['frame'];dy=(8-v['py']*2)%8 if v['flip']&2 else v['py']*2
   spec=(parent,dy)
   assert v['frame']not in motion_vertical or motion_vertical[v['frame']]==spec
   motion_vertical[v['frame']]=spec

if motion_enabled:
 active={v['id']for v in motion_variants};zero={(v['id'],v['anim'],v['flip']):v['frame']for v in motion_variants if not v['px']and not v['py']}
 periods={ident:1+max(v['anim']for v in motion_variants if v['id']==ident)for ident in active}
 for v in j['variants']:
  if v['id']in active:v['frame']=zero[(v['id'],v['phase']%periods[v['id']],v['flip'])]
 used={v['frame']for v in j['variants']+motion_variants if v['frame']>=0}|set(common_frames)|set(body_ids)
 remap={old:i for i,old in enumerate(sorted(used))};j['frames']=[j['frames'][old]for old in sorted(used)]
 for v in j['variants']+motion_variants:
  if v['frame']>=0:v['frame']=remap[v['frame']]
 common_frames=[remap[i]for i in common_frames];body_ids=[remap[i]for i in body_ids]
 if 'boss_tiles'in j:
  for v in j['boss_tiles']:v['frame']=remap[v['frame']]
 motion_vertical={remap[k]:(remap[v[0]],v[1])for k,v in motion_vertical.items()}
 j['motion_variants']=motion_variants
 used_palette=sorted({pi for frame in j['frames']for pi in frame['rows']if pi>=0});pmap={old:i for i,old in enumerate(used_palette)}
 j['palette']=[j['palette'][i]for i in used_palette]
 for frame in j['frames']:frame['rows']=[pmap[pi]if pi>=0 else -1 for pi in frame['rows']]
assert len(j['frames'])<255
common_variant_bytes=bytes(255 if v['frame']<0 else common_frames[v['frame']]for v in common['variants'])
assert all(len(set(common_variant_bytes[i:i+4]))==1 for i in range(0,len(common_variant_bytes),4))
common_variant_bytes=common_variant_bytes[::4]
j['normal_black_policy']={'normalized_attributes':black_normalized,'policy':'Clear BRIGHT when either ECM color is black'}
j['common_variants']=[dict(v,frame=-1 if v['frame']<0 else common_frames[v['frame']])for v in common['variants']]
actor_variant_bytes=len(j['variants'])
proc=None
if proc_enabled:
 from stock_l4_procedural_assets import prepare
 proc=prepare(j)
 proc['oracle']['hardware_palette']=proc['hardware']
 (O/'combined_frames.json').write_text(json.dumps(proc['oracle']))
else:(O/'combined_frames.json').write_text(json.dumps(j))
b[0x2000:0x4000]=bytes([255])*8192
b[0x0200:0x0480]=bytes([255])*(0x0480-0x0200)
b[0x0d00]=0xc9 # old orb callback targets retired native graphics
for lo,hi in ((0x0c00,0x0d00),(0x0d30,0x0e00),(0x1000,0x10f0),(0x1b20,0x1e20)):b[lo:hi]=bytes([255])*(hi-lo)
# Normal black in ECM empty cells and mirrored native HUD; standard-mode
# score palette keeps its native colour animation with normal-black paper.
assert b[0x16c5:0x16c9]==bytes.fromhex('3e47e647')
b[0x16c6]=7;b[0x16c8]=7
# Flat native restoration can inherit bright black even with a normal cache.
# Use the fixed unused ROM0 title padding; no cache/palette allocations move.
p=O/'stock_normal_black.asm';p.write_text((R/'src/stock_normal_black.asm').read_text())
q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
data=p.with_suffix('.bin').read_bytes();assert all(v==255 for v in b[0xf50:0xf50+len(data)])
b[0xf50:0xf50+len(data)]=data
assert b[0x164e:0x1650]==bytes.fromhex('287b') and b[0x16c9:0x16cd]==bytes.fromhex('1800e67f')
b[0x164f]=0x79 # JR Z restore_uniform now enters the two retired JR bytes
b[0x16c9:0x16cd]=bytes.fromhex('cd500f00')
(O/'normal_black_restore_contract.json').write_text(json.dumps(dict(entry=0xf50,bytes=len(data),call=0x16c9,source='Actual legacy native flat attribute; no palette IDs',policy='Clear BRIGHT only when a colour endpoint is black; preserve two-nonblack pairs')))

assert b[0x145a:0x145d]==bytes.fromhex('7ee67f')
b[0x145c]=0x3f
b[0x18f7:0x18f9]=bytes.fromhex("a7c9")
score_address=0xc15 if level==2 else 0xc06
b[score_address:score_address+12]=bytes.fromhex('cdcbbcaf3200bed3ffc390bc')
b[0xd30:0xdd0]=bytes([255])*0xa0
ram_layout=json.loads((O/'player_ram_layout.json').read_text());ram=ram_layout['allocations'];ctx=ram['context_and_stack'][0];cache=ram['sprite_cache'][0];phase_mask=ram_layout['actor_slot_hash_proof']['mask']
pickup_template=f'PLAYER_STATE EQU ${ram["player_state"][0]:04X}\nPLAYER_FLAGS EQU ${ram_layout["clock_flags"][0]:04X}\n'+(R/'src/stock_pickup_contact.asm').read_text()
p=O/'stock_pickup_contact.asm';p.write_text('PICKUP_CODE EQU 0\n'+pickup_template)
q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
pickup_address=0x0c21
assert pickup_address+len(p.with_suffix('.bin').read_bytes())<=0x0d00
p.write_text(f'PICKUP_CODE EQU ${pickup_address:04X}\n'+pickup_template)
q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
data=p.with_suffix('.bin').read_bytes();b[pickup_address:pickup_address+len(data)]=data
(O/'pickup_contact_contract.json').write_text(json.dumps(dict(address=pickup_address,bytes=len(data),scope='Native pickup contact fallback; no early player ownership publication')))
# Rebuild the HOME8000 image after installing its native selector hook.
p=next(p for p in layout['packets']if p['bank']==2);home=bytearray(unpack(base[0x4000:0x4000+p['bytes']]));assert len(home)==8192
home[0xe85:0xe8c]=bytes.fromhex('c3002000000000')
home[0xe8c:0xe92]=bytes.fromhex('c30320000000')
assert home[0x1172:0x1175]==bytes.fromhex('cd858e')
home[0x1172:0x1175]=bytes.fromhex('cd0920')
if overlap_enabled:
 assert home[0xed6:0xed9]==bytes.fromhex('1aa728')
 home[0xed6:0xedb]=bytes.fromhex('cd0c20c900')
assert home[0x1885:0x1888]==bytes.fromhex('3a957a')
home[0x1885:0x1888]=bytes([0xcd])+pickup_address.to_bytes(2,'little')
assert home[0x17f9:0x17fc]==bytes.fromhex('3a957a')
home[0x17f9:0x17fc]=bytes([0xcd])+(pickup_address+3).to_bytes(2,'little')
pkt=pack_optimal(home);assert len(pkt)<8192;b[0x4000:0x6000]=bytes([255])*8192;b[0x4000:0x4000+len(pkt)]=pkt
segments=[s.copy()for s in layout['free_segments']if s[0]//8192 in (2,3,5,6,7)];segments=[([0x4000+len(pkt),0x6000]if s[0]//8192==2 else s)for s in segments]
segments += [[0x80D0,0x862F],[0x8634,0x8800],[0x2D80,0x4000],[pickup_address+len(data),0x0d00]]
def put(data,banks=None,prefer_safe=False):
 def priority(segment):
  bank=segment[0]//8192
  return (0 if bank in (2,3,5,6)else 1 if bank in (4,7)else 2)if prefer_safe else bank!=6
 seg=next((s for s in sorted(segments,key=priority) if s[1]-s[0]>=len(data)and(banks is None or s[0]//8192 in banks)),None);assert seg is not None,(len(data),segments)
 a=seg[0];seg[0]+=len(data);b[a:a+len(data)]=data;return a
body_address=None;body_masks=[];body_template=''
if level==2:
 old_rom=(R/'build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r24.rom').read_bytes()
 for fi in body_ids:
  frame=j['frames'][fi];mask=0
  for c,pi in enumerate(frame['rows']):
   bits=frame['bits'][c*9+1:c*9+9];row=j['palette'][pi]
   if any(((a&7)!=0 and bit!=0)or((a&56)!=0 and bit!=255)for a,bit in zip(row,bits)):mask|=1<<c
  body_masks.append(mask)
 body_template=(R/'src/stock_l2_body.asm').read_text().replace('NATIVE_GETTER',','.join(str(v)for v in old_rom[0x482d:0x4842])).replace('FRAME_IDS',','.join(map(str,body_ids))).replace('BODY_COORDS',','.join(map(str,body_coordinates))).replace('BODY_MASKS',','.join(map(str,body_masks)))
 body_state=ram.get('l2_body_workspace',ram_layout['free_segments'][0])[0]
 assert ram.get('l2_body_workspace',ram_layout['free_segments'][0])[1]-body_state>=320
 (O/'l2_body_ram_contract.json').write_text(json.dumps(dict(state=[body_state,body_state+32],tickets=[body_state+32,body_state+320],source_free_segment=ram.get('l2_body_workspace',ram_layout['free_segments'][0]))))
 defs=f'PLAYER_FLAGS EQU ${ram_layout["clock_flags"][0]:04X}\nSTATE EQU ${body_state:04X}\nTICKETS EQU ${body_state+32:04X}\nCTX EQU ${ctx:04X}\nCACHE EQU ${cache:04X}\nPALPTR EQU CTX+4\nBITS EQU CTX+6\n'
 p=O/'stock_l2_body_size.asm';p.write_text('BODY_CODE EQU $3000\nPALETTE_READ EQU $2100\n'+defs+body_template)
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 body_bytes=len(p.with_suffix('.bin').read_bytes());body_address=put(bytes([255])*body_bytes,[1])
 body_template=defs+body_template
# Title atlas is generated in borrowed HOME C700..DBFF from ROM4's logo.
title_address=put(bytes([255])*512,[1])
title_source=f'TITLE_CODE EQU ${title_address:04X}\n'+(R/'src/stock_title_lifetime.asm').read_text()
p=O/'stock_title_lifetime.asm';p.write_text(title_source)
q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
data=p.with_suffix('.bin').read_bytes();assert len(data)<=512;b[title_address:title_address+len(data)]=data
segments.append([title_address+len(data),title_address+512])
b[0xc00:0xc03]=bytes([0xc3])+title_address.to_bytes(2,'little')
assert b[0x1435:0x1438]==bytes.fromhex('cdc386')
b[0x1435:0x1438]=bytes([0xcd])+(title_address+3).to_bytes(2,'little')
old_sources=b''.join(a.to_bytes(2,'little')for a in [0xe400,0xe940,0xebe0,0xee80,0xf120,0xf3c0,0xf660])
at=b.find(old_sources,0x9d10,0x9ea0);assert at>=0
b[at:at+14]=b''.join(a.to_bytes(2,'little')for a in [0xc700,0xcc40,0xcee0,0xd180,0xd420,0xd6c0,0xd960])
at=b.find(bytes.fromhex('3e93d3f4'),0x9d10,0x9ea0);assert at>=0;b[at+1]=0x13
# Pause and boss preview/recovery run only on the native main loop.
control_address=put(bytes([255])*512,[1])
native=bytes(16384)+(R/f'build/fullgame/foundation/level{level:02d}.raw').read_bytes();start_column=[99,63,9,74,73,8,61,32][level-1]
event=foundation['map_end'];prior_setting=0
while native[event]!=255 and native[event]<start_column:
 if native[event+2:event+4]==bytes([99,4]):prior_setting=native[event+4]
 event+=5
assert native[event]!=255 and native[event]>=start_column
assert ram['sprite_cache'][1]-cache>=99
(O/'pause_ram_contract.json').write_text(json.dumps(dict(pixels=[cache,cache+96],ay=[cache+96,cache+99],borrowed_from=ram['sprite_cache'],frame_valid=ctx+17,scope='Main-loop pause only; DI during borrow; invalidate decoded frame before EI; native font untouched')))
control_source=f'PAUSE_PIXELS EQU ${cache:04X}\nPAUSE_AY EQU ${cache+96:04X}\nFRAME_VALID EQU ${ctx+17:04X}\nCONTROL_CODE EQU ${control_address:04X}\nLEVEL_NUM EQU {level}\nEVENT_PTR EQU ${event:04X}\nSTART_COLUMN EQU {max(0,start_column-9)}\nPRIOR_SETTING EQU {prior_setting}\n'+(R/'src/stock_controls.asm').read_text()
p=O/'stock_controls.asm';p.write_text(control_source)
q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
data=p.with_suffix('.bin').read_bytes();assert len(data)<=512;b[control_address:control_address+len(data)]=data
segments.append([control_address+len(data),control_address+512])
assert b[0x1ff8:0x1ffb]==bytes([255])*3
b[0x1ff8:0x1ffb]=bytes([0xc3])+control_address.to_bytes(2,'little')
# Small completion message, no automatic media insertion or tape loading.
font=(R/'assets/fullgame_preloader_font.bin').read_bytes();picture=bytearray(6144)
for cy,text in [(9,f'LEVEL {level} COMPLETE'),(11,'RESET FOR ANOTHER CARTRIDGE'),(13,'FIRE TO REPLAY')]:
 x=(32-len(text))//2
 for c,ch in enumerate(text):
  for y in range(8):
   yy=cy*8+y;offset=((yy&192)<<5)|((yy&7)<<8)|((yy&56)<<2)
   picture[offset+x+c]=font[(ord(ch)-32)*8+y]
(O/'completion_bitmap.bin').write_bytes(picture)
completion_source=put(pack_optimal(picture),[3,4,5])
completion_address=put(bytes([255])*160,[0,1])
completion_text=f'COMPLETE_CODE EQU ${completion_address:04X}\nCOMPLETE_SOURCE EQU ${completion_source:04X}\nCOMPLETE_MASK EQU ${3|(1<<(completion_source//8192)):02X}\nFLAGS EQU ${ram_layout["clock_flags"][0]:04X}\n'+(R/'src/stock_completion.asm').read_text()
p=O/'stock_completion.asm';p.write_text(completion_text)
q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
data=p.with_suffix('.bin').read_bytes();assert len(data)<=160;b[completion_address:completion_address+len(data)]=data
segments.append([completion_address+len(data),completion_address+160])
b[0xc03:0xc06]=bytes([0xc3])+completion_address.to_bytes(2,'little')
# Permanent compact group table: recomputed against exact current tile pixels.
groups=(O/'terrain/groups.bin').read_bytes();group_meta=json.loads((O/'terrain/contract.json').read_text())
segments.append([0x0A08,0x0BC0])
l2_row_palette=None
if level==2:
 region=(R/'build/fullgame/visible_hits_r145/level02_region.bin').read_bytes()
 assert region[0x13a:0x13d]==bytes.fromhex('214383')
 inks=region[0x8343:0x83e3]+region[0x83e3:0x844b]
 patterns=[];row_map=[]
 for i in range(0,len(inks),8):
  row=inks[i:i+8]
  if row not in patterns:patterns.append(row)
  row_map.append(patterns.index(row))
 assert len(patterns)==17 and len(row_map)==33
 data=b''.join(patterns)+bytes(row_map)+b''.join(row[::-1]for row in patterns)
 l2_row_palette=put(data,[0]);group_address=l2_row_palette
 (O/'l2_row_palette_contract.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(region).hexdigest(),source_ranges=[[0x8343,0x83e3],[0x83e3,0x844b]],palette=l2_row_palette,patterns=len(patterns),row_map=row_map,bytes=len(data))))
else:
 group_address=put(groups,[0]if len(groups)<=0x1b8 else [1])
group_source=(R/'src/terrain_groups_full.asm').read_text().replace('LD HL,$0200','LD HL,GROUP_RUNS')
start=foundation['terrain_start'];end=foundation['map_start']
group_source=group_source.replace('CP $D9',f'CP ${start>>8:02X}').replace('CP $E6',f'CP ${(end>>8)+1:02X}')
if level==2:
 group_source=group_source.replace('        LD A,H\n        CP $D4','        LD A,(${ctx+25:04X})\n        CP 3\n        JR Z,initial_cache_tile\n        LD A,H\n        CP $D4')
 group_source=group_source.replace('        LD A,D\n        AND 3','initial_cache_tile:\n        LD A,D\n        AND 3',1)
 group_source=group_source.replace('${ctx+25:04X}',f'${ctx+25:04X}')
if level==2:
 group_source=f'ROW_MAP EQU ${l2_row_palette+136:04X}\nBOSS_MAP EQU ${l2_row_palette+156:04X}\nBODY_CONTEXT EQU ${ctx+25:04X}\nTILE_START_HI EQU ${start>>8:02X}\nTILE_END_HI EQU ${(end>>8)+1:02X}\n'+(R/'src/stock_l2_row_terrain.asm').read_text()
group_source=f'GROUP_RUNS EQU ${group_address:04X}\nGROUP_DICTIONARY EQU ${group_address+group_meta["dictionary"]:04X}\n'+group_source
pgroup=O/'stock_terrain_groups.asm';pgroup.write_text(group_source)
q=subprocess.run([str(exe),f'--raw={pgroup.with_suffix(".bin")}',str(pgroup)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
data=pgroup.with_suffix('.bin').read_bytes();assert len(data)==0x148;b[0x8c0:0xa08]=data
lookup=(R/'src/restore_terrain_palette.asm').read_text().replace('$D9',f'${start>>8:02X}').replace('$E6',f'${(end>>8)+1:02X}').replace('$E5',f'${end>>8:02X}').replace('CP $11',f'CP ${start&255:02X}').replace('CP $71',f'CP ${end&255:02X}')
if level==2:
 lookup=lookup.replace('terrain_lookup_row:\n        PUSH BC','terrain_lookup_row:\n        PUSH BC\n        LD A,(${ctx+25:04X})\n        CP 3\n        JR Z,terrain_check_marker')
 lookup=lookup.replace('${ctx+25:04X}',f'${ctx+25:04X}')
 lookup=lookup.replace('LD A,(HL)\n        AND $F7\n        LD C,A','LD C,0')
 lookup=lookup.replace('AND 8\n        OR C','AND $7F')
 lookup=lookup.replace('$FBD0',f'${l2_row_palette:04X}')
 a=lookup.index('terrain_check_marker:');z=lookup.index('terrain_not_found:',a)
 lookup=lookup[:a]+f'''terrain_check_marker:
        BIT 7,(HL)
        JR Z,terrain_not_found
        PUSH DE
        LD E,(IX+8)
        LD D,(IX+9)
        LD A,D
        AND 3
        RLCA
        RLCA
        RLCA
        LD C,A
        LD A,E
        AND $E0
        RLCA
        RLCA
        RLCA
        OR C
        CALL $08F0
        LD C,A
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        CALL $15EC
        OR A
        LD DE,${l2_row_palette:04X}
        JR Z,l2_direct_palette_ready
        LD DE,${l2_row_palette+169:04X}
l2_direct_palette_ready:
        ADD HL,DE
        LD A,C
        POP DE
        POP BC
        SCF
        RET
'''+lookup[z:]

plook=O/'stock_terrain_lookup.asm';plook.write_text(lookup)
q=subprocess.run([str(exe),f'--raw={plook.with_suffix(".bin")}',str(plook)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
data=plook.with_suffix('.bin').read_bytes();assert len(data)<=0x100
# F20 is a live native title/input bridge; update only the terrain lookup body.
last=data.index(bytes.fromhex('c1a7c9'),0x80)+3
b[0xf80:0xf00+last]=data[0x80:last]
# Palette in one ROM5 window: temporary bank reads never hide HOME6000 or stack.
phase_packet=pack_optimal((O/'stock_player_phases.bin').read_bytes());phase_source=put(phase_packet,[1])
pair_palette=bool(motion_vertical)or level==6 or proc_enabled;paged_palette=bool(pair_palette and(len(j['palette'])>512 or proc_enabled));palette_pointer=None
if pair_palette:
 pairs=list(dict.fromkeys(tuple(row[i:i+2])for row in j['palette']for i in range(0,8,2)));assert len(pairs)<=256
 if proc_enabled:pairs=proc['pairs']
 row_pairs=bytes(pairs.index(tuple(row[i:i+2]))for row in j['palette']for i in range(0,8,2));pair_bytes=bytes(a for pair in pairs for a in pair)
 if paged_palette:
  pair_base=put(pair_bytes,[1]);pages=[]
  for i in range(0,len(row_pairs),1024):
   address=put(row_pairs[i:i+1024],[2,3,4,5]);pages.append((3|(1<<(address//8192)),address))
  palette=pages[0][1];page_directory=put(b''.join(bytes([mask])+address.to_bytes(2,'little')for mask,address in pages),[1]);p=O/'stock_palette_page_pointer.asm';pointer_template=(R/'src/stock_palette_page_pointer.asm').read_text();p.write_text(f'PALETTE_POINTER_CODE EQU 0\nPALETTE_PAGE_DIRECTORY EQU ${page_directory:04X}\n'+pointer_template)
  q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
  pointer_data=p.with_suffix('.bin').read_bytes();palette_pointer=put(bytes(len(pointer_data)),[1]);p.write_text(f'PALETTE_POINTER_CODE EQU ${palette_pointer:04X}\nPALETTE_PAGE_DIRECTORY EQU ${page_directory:04X}\n'+pointer_template)
  q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
  data=p.with_suffix('.bin').read_bytes();assert len(data)==len(pointer_data);b[palette_pointer:palette_pointer+len(data)]=data
  (O/'palette_page_contract.json').write_text(json.dumps(dict(directory=page_directory,pointer=palette_pointer,pages=pages,rows_per_page=256,maximum_rows=2048,stack_and_context_visible=True)))
 else:palette=put(row_pairs+pair_bytes,[5]);pair_base=palette+len(row_pairs)
 (O/'palette_pair_contract.json').write_text(json.dumps(dict(palette=palette,pairs=pair_base,pair_count=len(pairs),rows=len(j['palette']),raw_bytes=8*len(j['palette']),packed_bytes=len(row_pairs)+len(pair_bytes),lossless=True,paged=paged_palette)))
else:palette=put(bytes(v for row in j['palette']for v in row),[5])
assert len(j['palette'])<=(2048 if paged_palette else 512)
actor_variants=bytes(255 if v['frame']<0 else v['frame']for v in j['variants'])
row_size=64 if level==2 else 16;original_variant_bytes=len(actor_variants)
rows=[actor_variants[i:i+row_size]for i in range(0,len(actor_variants),row_size)];unique=list(dict.fromkeys(rows))
directory=bytearray();encoded=bytearray();base=len(rows)+2*len(unique)
for row in unique:
 period=next(p for p in (1,2,4,8,16,32,64)if p<=row_size and all(row[k]==row[k%p]for k in range(row_size)))
 directory+=(base+len(encoded)).to_bytes(2,'little');encoded+=bytes([period-1])+row[:period]
actor_variants=bytes(unique.index(row)for row in rows)+directory+encoded;actor_variant_bytes=len(actor_variants)
for ident,row in enumerate(rows):
 at=len(rows)+2*actor_variants[ident];pointer=int.from_bytes(actor_variants[at:at+2],'little');mask=actor_variants[pointer]
 assert bytes(actor_variants[pointer+1+(k&mask)]for k in range(row_size))==row
(O/'variant_period_contract.json').write_text(json.dumps(dict(original_bytes=original_variant_bytes,packed_bytes=len(actor_variants),rows=len(rows),unique_rows=len(unique),lossless=True)))
motion_address=None;motion_defs='';motion_template=''
if motion_enabled:
 ids=sorted(set(v['id']for v in motion_variants));map_size=max(ids)+1;idmap=bytearray([255])*map_size;motion_rows=[]
 for ident in ids:
  variants_id=[v for v in motion_variants if v['id']==ident];period=1+max(v['anim']for v in variants_id);entry={(v['anim'],v['py'],v['px'],v['flip']):v['frame']for v in variants_id};row=bytes(entry[(a%period,y,0 if level in (2,3) or(level==7 and ident==51)else x,f)]for a in range(4)for y in range(4)for x in range(4)for f in range(4))
  if row not in motion_rows:motion_rows.append(row)
  idmap[ident]=motion_rows.index(row)
 directory=bytearray();encoded=bytearray();table_base=len(idmap)+len(motion_rows)*2
 for row in motion_rows:
  period=next(p for p in (1,2,4,8,16,32,64,128,256)if all(row[k]==row[k%p]for k in range(256)))
  directory+=(table_base+len(encoded)).to_bytes(2,'little');encoded+=bytes([period-1])+row[:period]
 motion_table=put(bytes(idmap)+directory+encoded);motion_mask=3|(1<<(motion_table//8192));motion_state=ram['boss_motion_state'][0]
 motion_defs=f'CTX EQU ${ctx:04X}\nPHASES EQU $C4CE\nPHASE_MASK EQU {phase_mask}\nMOTION_STATE EQU ${motion_state:04X}\nSTATE_BYTES EQU {128 if level==4 else 64}\nMULTIPART_KEYS EQU {int(level==4)}\nMOTION_TABLE EQU ${motion_table:04X}\nMOTION_MAP_SIZE EQU {map_size}\nMOTION_MASK EQU {motion_mask}\nLOCK_X EQU {int(level in (2,3))}\nMIXED_LOCK_X EQU {int(level==7)}\n'
 motion_template=(R/'src/stock_tap_motion.asm').read_text();p=O/'stock_tap_motion.asm';p.write_text('MOTION_CODE EQU 0\nREAD_BYTE EQU 0\n'+motion_defs+motion_template)
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 motion_bytes=len(p.with_suffix('.bin').read_bytes());motion_address=put(bytes([255])*motion_bytes,[1])
 (O/'tap_motion_contract.json').write_text(json.dumps(dict(table=motion_table,map_size=map_size,rows=len(motion_rows),state=[motion_state,motion_state+(128 if level==4 else 64)],code=motion_address,source_sha256=hashlib.sha256((O.parent/f'L{level}_tap_motion_frames.json').read_bytes()).hexdigest(),frames=motion_variants)))
palette_delta_address=None
if level==6 or proc_enabled:
 delta=O/'stock_palette_deltas.asm';template=(R/'src/stock_palette_deltas.asm').read_text();delta.write_text(f'PALETTE_DELTA_CODE EQU 0\nCACHE EQU ${cache:04X}\n'+template)
 q=subprocess.run([str(exe),f'--raw={delta.with_suffix(".bin")}',str(delta)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 palette_delta_address=put(bytes(len(delta.with_suffix('.bin').read_bytes())),[0])
 delta.write_text(f'PALETTE_DELTA_CODE EQU ${palette_delta_address:04X}\nCACHE EQU ${cache:04X}\n'+template)
 q=subprocess.run([str(exe),f'--raw={delta.with_suffix(".bin")}',str(delta)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 data=delta.with_suffix('.bin').read_bytes();b[palette_delta_address:palette_delta_address+len(data)]=data
vertical_address=None;vertical_template='';vertical_defs=''
if motion_vertical:
 palette_delta_address=None
 if level==5:
  delta=O/'stock_palette_deltas.asm';template=(R/'src/stock_palette_deltas.asm').read_text();delta.write_text(f'PALETTE_DELTA_CODE EQU 0\nCACHE EQU ${cache:04X}\n'+template)
  q=subprocess.run([str(exe),f'--raw={delta.with_suffix(".bin")}',str(delta)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
  palette_delta_address=put(bytes(len(delta.with_suffix('.bin').read_bytes())),[0])
  delta.write_text(f'PALETTE_DELTA_CODE EQU ${palette_delta_address:04X}\nCACHE EQU ${cache:04X}\n'+template)
  q=subprocess.run([str(exe),f'--raw={delta.with_suffix(".bin")}',str(delta)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
  data=delta.with_suffix('.bin').read_bytes();b[palette_delta_address:palette_delta_address+len(data)]=data
 vertical_defs=f'CTX EQU ${ctx:04X}\nCACHE EQU ${cache:04X}\nBITS EQU CTX+6\nDENSE_PARENT EQU ${ram["motion_dense_parent"][0]:04X}\n'
 vertical_template=(R/'src/stock_vertical_frame.asm').read_text()
 if palette_delta_address is not None:vertical_template=vertical_template.replace(' CALL UNPACK_FRAME\n',f' CALL UNPACK_FRAME\n CALL ${palette_delta_address:04X}\n',1)
 p=O/'stock_vertical_frame.asm';p.write_text('VERTICAL_CODE EQU 0\nREAD_STREAM_BYTE EQU 0\nDIRECT_FRAME EQU 0\nUNPACK_FRAME EQU 0\nCACHED_FRAME EQU 0\n'+vertical_defs+vertical_template)
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 vertical_bytes=len(p.with_suffix('.bin').read_bytes());vertical_address=put(bytes([255])*vertical_bytes,[1])
overlap_address=None
if overlap_enabled:
 assert len(j['palette'])<1024,'Dynamic IDs reserve1024..1279'
 pool_slots=(ram['dynamic_palette_rows'][1]-ram['dynamic_palette_rows'][0])//8
 overlap_defs=f'POOL_SLOTS EQU {pool_slots}\nREF_BYTES EQU {(pool_slots+7)//8}\nSNAPSHOT_CELLS EQU {80 if ram["backing_attributes"][1]-ram["backing_attributes"][0]==160 else 0}\nLINKS EQU ${ram["dynamic_palette_links"][0]:04X}\nHEAD_VALID EQU ${ram["dynamic_palette_head_valid"][0]:04X}\nPOOL EQU ${ram["dynamic_palette_rows"][0]:04X}\nHASHES EQU ${ram["dynamic_palette_hashes"][0]:04X}\nREFS EQU ${ram["dynamic_palette_refs"][0]:04X}\nWS EQU ${ram["dynamic_palette_state"][0]:04X}\nSNAPSHOT EQU ${ram["backing_attributes"][0]:04X}\nFLAGS EQU ${ram_layout["clock_flags"][0]:04X}\nCTX EQU ${ctx:04X}\nTEMP EQU CTX+8\n'
 overlap_template=(R/'src/stock_overlap_compositor.asm').read_text()
 # Keep the pure row blender in a separate permanent-ROM0 fragment so restored
 # ordinary artwork cannot squeeze the full compositor out of ROM1.
 split=overlap_template.index('; Exact normal/black pair rules')
 overlap_helper=overlap_template[split:].split(' ASSERT $ <= COMPOSITOR_CODE+2048')[0]
 helper=O/'stock_overlap_blend.asm';helper.write_text(' ORG 0\n'+overlap_defs+overlap_helper)
 q=subprocess.run([str(exe),f'--raw={helper.with_suffix(".bin")}',str(helper)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 helper_address=put(bytes(len(helper.with_suffix('.bin').read_bytes())),[0])
 helper.write_text(f' ORG ${helper_address:04X}\n'+overlap_defs+overlap_helper)
 q=subprocess.run([str(exe),f'--raw={helper.with_suffix(".bin")}',str(helper)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 helper_data=helper.with_suffix('.bin').read_bytes();b[helper_address:helper_address+len(helper_data)]=helper_data
 overlap_template=overlap_template[:split].replace('CALL blend_row','CALL BLEND_ROW')+'\n ASSERT $ <= COMPOSITOR_CODE+2048\n'
 overlap_defs+=f'BLEND_ROW EQU ${helper_address:04X}\n'
 p=O/'stock_overlap_compositor.asm';p.write_text('COMPOSITOR_CODE EQU 0\nSTOCK_COLOUR EQU 0\nPALETTE_READ EQU 0\n'+overlap_defs+overlap_template)
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 overlap_bytes=len(p.with_suffix('.bin').read_bytes());overlap_address=put(bytes(overlap_bytes),[1])
 (O/'overlap_contract.json').write_text(json.dumps(dict(enabled=True,code=overlap_address,rows=ram['dynamic_palette_rows'],hashes=ram['dynamic_palette_hashes'],references=ram['dynamic_palette_refs'],state=ram['dynamic_palette_state'],dynamic_id_base=1024,slots=pool_slots,publish_ready=False)))
proc_address=None
if not proc_enabled:
 for stale in ['l4_palette_pool_contract.json','rom_font_contract.json','l4_procedural_contract.json','l4_procedural_validation.json','l4_constructor_irq_validation.json','l4_stable_tokens.json','stock_l4_procedural.sym','stock_l4_procedural.bin','stock_l4_procedural.asm']:
  (O/stale).unlink(missing_ok=True)
if proc_enabled:
 locations={}
 def location(data,banks=None):
  key=(bytes(data),None if banks is None else tuple(banks))
  if key in locations:return locations[key]
  address=put(data,banks);result=bytes([3|(1<<(address//8192))if address//8192>1 else 3])+address.to_bytes(2,'little');locations[key]=result;return result
 base_locations={key:location(value['packed'],[2,3,4,5])for key,value in proc['bases'].items()}
 quad_location=location(proc['quads'],[2,3,5])
 parents=[]
 for parent in proc['parents']:
  base_info=proc['bases'][parent['base']]
  directory=parent['colour_ids']
  colour_location=location(directory);high=int.from_bytes(colour_location[1:],'little')+parent['w']*(parent['h']+1)
  parents.append(bytes([base_info['w'],base_info['h'],parent['w'],parent['h'],parent['dx']])+base_locations[parent['base']]+location(parent['patch'],[2,3,5,7])+colour_location+high.to_bytes(2,'little'))
 parent_table=put(b''.join(parents));parent_mask=3|(1<<(parent_table//8192))if parent_table//8192>1 else 3
 quad_mask=quad_location[0];quad_address=int.from_bytes(quad_location[1:],'little')
 descriptor_locations={fi:location(data)for fi,data in proc['descriptors'].items()}
 recipe_location=location(proc['recipe_data'],[2,3,5,7]);recipe_table=int.from_bytes(recipe_location[1:],'little');recipe_mask=recipe_location[0]
 high_directory=0;popcount=0

 hash_mod=put(bytes((d*256)%156 for d in range(16)),[0])
 proc_defs=f'RECIPE_DEFAULTS EQU {proc["recipe_defaults"]}\nRECIPE_EXTRA EQU ${recipe_table+proc["recipe_extra_offset"]:04X}\nRECIPE_MASK EQU ${recipe_mask:02X}\nHASH_MOD EQU ${hash_mod:04X}\nEXTRA_ROWS EQU ${ram["l4_expanded_row_tail"][0]:04X}\nPAIR_KEYS EQU ${ram["l4_pair_cache_keys"][0]:04X}\nSTATIC_ROWS EQU {proc["static_rows"]}\nRECIPE_TABLE EQU ${recipe_table:04X}\nHIGH_DIRECTORY EQU ${high_directory:04X}\nPOPCOUNT EQU ${popcount:04X}\nLASTPI EQU ${ctx+2:04X}\nWS EQU ${ram["l4_procedural_state"][0]:04X}\nREFS EQU WS+8\nHEAD_VALID EQU WS+40\nHASHES EQU $7B88\nLINKS EQU $7BC8\nPOOL_SLOTS EQU 224\nREF_BYTES EQU 28\nSNAPSHOT_CELLS EQU 0\nEMPTY_QUAD EQU ${proc["empty_quad"]:04X}\nQUAD_MASK EQU ${quad_mask:02X}\nQUAD_BASE EQU ${quad_address:04X}\nPALETTE_POINTER EQU ${palette_pointer:04X}\nPAIR_BASE EQU ${pair_base:04X}\nCTX_IFF EQU ${ctx+16:04X}\nFLAGS EQU ${ram_layout["clock_flags"][0]:04X}\nCACHE EQU ${cache:04X}\nDENSE EQU ${ram["motion_dense_parent"][0]:04X}\nPS EQU ${ram["l4_procedural_state"][0]:04X}\nTEMP EQU ${ctx+8:04X}\nPARENT_TABLE EQU ${parent_table:04X}\nPARENT_MASK EQU ${parent_mask:02X}\n'
 proc_template=(R/'src/stock_l4_procedural.asm').read_text()
 p=O/'stock_l4_procedural.asm';p.write_text('RAW_PALETTE EQU 0\nPROC_CODE EQU 0\nREAD_BYTE EQU 0\nPALETTE_READ EQU 0\nCACHED_FRAME EQU 0\n'+proc_defs+proc_template)
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 proc_size=len(p.with_suffix('.bin').read_bytes());proc_address=put(bytes(proc_size),[1])
 (O/'l4_procedural_contract.json').write_text(json.dumps(dict(enabled=True,code=proc_address,bytes=proc_size,state=ram['l4_procedural_state'],dense=ram['motion_dense_parent'],maximum_cache=proc['max_cache'],frames=sorted(proc['frames']),hardware_palette=proc['hardware'],source='Exact r145 base bitmaps/horizontal sparse corrections; immutable adjacent-row recipes; all 2px phases',publish_ready=False)))
variants=actor_variants+common_variant_bytes;vaddr=put(variants);daddr=put(bytes(len(j['frames'])*3));pointers=[None]*len(j['frames']);maxraw=0;raws=[None]*len(j['frames'])
for fi,f in sorted(enumerate(j['frames']),key=lambda q:len(q[1]['bits']),reverse=True):
 if proc_enabled and fi in proc['frames']:
  raws[fi]=bytes([f['w'],f['h'],0]);maxraw=max(maxraw,proc['max_cache']);continue
 local=sorted(set(f['rows'])-{-1});assert len(local)<254
 mapping={pi:i+(i>=54) for i,pi in enumerate(local)};local=local[:54]+([0]+local[54:] if len(local)>54 else []);native=bytearray(f['bits']);offset=0
 for pi in f['rows']:
  if pi<0:assert native[offset]==54;offset+=1
  else:native[offset]=mapping[pi];offset+=9
 palette_values=local
 if level==6 or proc_enabled:
  previous=0;palette_values=[]
  for pi in local:palette_values.append((pi-previous)&65535);previous=pi
 raw=bytes([f['w'],f['h'],len(local)])+b''.join(pi.to_bytes(2,'little')for pi in palette_values)+native;maxraw=max(maxraw,len(raw));raws[fi]=raw
from stock_frame_packets import frame_packets
packets,delta_saved=frame_packets(raws,[(f['w'],f['h'])for f in j['frames']]);print('Sparse delta savings',delta_saved,sum(p['base']is not None for p in packets))
if motion_vertical:
 for p in packets:
  if p['base']in motion_vertical:p['base']=None
 for fi,p in enumerate(packets):
  if p['base']is None:p['data']=pack_optimal(raws[fi])
 for parent,dy in motion_vertical.values():packets[parent]=dict(base=None,data=pack_optimal(raws[parent]))
 for fi,(parent,dy)in motion_vertical.items():
  f=j['frames'][fi];assert f['w']==j['frames'][parent]['w']
  native=raws[fi];offset=3+2*native[2];raw=bytearray(native[:offset])
  for pi in f['rows']:
   raw.append(native[offset]);offset+=1 if pi<0 else 9
  assert offset==len(native)
  if level==5:
   previous=0
   for at in range(3,3+native[2]*2,2):
    value=int.from_bytes(raw[at:at+2],'little');raw[at:at+2]=((value-previous)&65535).to_bytes(2,'little');previous=value
  packets[fi]=dict(base=None,vertical=True,data=bytes([parent,dy])+pack_optimal(raw))
if proc_enabled:
 for fi,p in enumerate(packets):
  if p['base']in proc['frames']:packets[fi]=dict(base=None,data=pack_optimal(raws[fi]))
 for fi,data in proc['descriptors'].items():packets[fi]=dict(base=None,procedural=True,data=data)
(O/'packet_size_diagnostic.json').write_text(json.dumps([dict(frame=i,bytes=len(p['data']),base=p['base'],vertical=p.get('vertical',False))for i,p in enumerate(packets)]))
print('Frame storage budget',sum(len(p['data'])+int(bool(motion_vertical and p['base']is None and not p.get('vertical')and len(p['data'])<=200))for p in packets),sum(e-a for a,e in segments),flush=True)
for fi in sorted(range(len(packets)),key=lambda i:len(packets[i]['data']),reverse=True):
 p=packets[fi]
 if p.get('procedural'):
  address=descriptor_locations[fi];pointers[fi]=bytes([address[0]&~2])+address[1:];continue
 stage=bool(motion_vertical and p['base']is None and not p.get('vertical')and len(p['data'])<=200)
 payload=(bytes([len(p['data'])])+p['data'])if stage else p['data']
 a=put(payload,[0,1,2,3,4,5,6,7]if p['base']is not None or stage else[0,1,2,3,4,5,7],prefer_safe=irq_decode_enabled and p['base']is None)
 bank=a//8192
 if stage and bank!=6:a+=1
 mask=(1 if p.get('procedural')else 0 if p.get('vertical')else 3 if p['base']is None else 2)|((1<<bank)if bank>1 else 0);pointers[fi]=bytes([mask])+a.to_bytes(2,'little')
assert cache+maxraw<=ram['sprite_cache'][1] and ram['sprite_cache'][1]<=descriptor_end
b[daddr:daddr+len(pointers)*3]=b''.join(pointers)
# Small directory is copied to cache RAM on boot? Access it via a ROM window,
# keeping source and private stack visible. Direct ROM reads helper stores byte.
l2_helpers="""
snake_role:
 CP 22
 RET C
 CP 24
 RET NC
 PUSH IY
 POP HL
 LD DE,-4
 ADD HL,DE
 LD DE,-9
 LD B,0
snake_previous:
 LD A,(HL)
 CP 5
 JR NZ,snake_classify
 INC B
 ADD HL,DE
 JR snake_previous
snake_classify:
 LD A,B
 CP 9
 LD A,23
 RET C
 DEC A
 RET
next_phase:
 PUSH BC
 LD C,A
 LD B,4
 LD A,(CTX+24)
 CP 19
 JR Z,period_three
 CP 20
 JR Z,period_three
 CP 32
 JR Z,period_ten
 CP 33
 JR NZ,advance_phase
period_ten:
 LD B,10
 JR advance_phase
period_three:
 LD B,3
advance_phase:
 LD A,C
 INC A
 CP B
 JR C,phase_store
 XOR A
phase_store:
 LD (HL),A
 LD A,C
 POP BC
 RET
"""if level==2 else ''
draw_actor_gate=(R/'src/stock_actor_draw_gate.asm').read_text()
if level==4:
 assert home[0xed6:0xedb]==bytes.fromhex('1aa72831c9')and home[0xf0b:0xf0e]==bytes.fromhex('1c1a1d')
 draw_actor_gate=draw_actor_gate.replace(' LD A,E\n CALL stock_select',' LD A,E\n CALL $0C1B\n CALL stock_select').replace('actor_drawn:\n','actor_drawn:\n CALL $0C1E\n')
source=f''' ORG $2000
 JP stock_select
 JP common_select
 JP direct_frame
 JP draw_actor
{(" JP $%04X" % overlap_address)if overlap_enabled else ""}
PLAYER_FLAGS EQU ${ram_layout["clock_flags"][0]:04X}
CTX EQU ${ctx:04X}
OLDSP EQU CTX
LASTPI EQU CTX+2
PALPTR EQU CTX+4
BITS EQU CTX+6
TEMP EQU CTX+8
PHASES EQU $C4CE
CACHE EQU ${cache:04X}
direct_frame:
 PUSH BC
 PUSH IX
 LD IX,0
 ADD IX,SP
 JP select_frame_index
stock_select:
 PUSH AF
 XOR A
 LD (CTX+25),A
 POP AF
 JR select_entry
common_select:
 PUSH AF
 LD A,(PLAYER_FLAGS+13)
 CP 2
 JR NZ,common_ready
 POP AF
 JP return_blank
common_ready:
 POP AF
 LD ($7A9C),A
 PUSH AF
 LD A,1
 LD (CTX+25),A
 POP AF
select_entry:
 PUSH AF
 LD A,($BE00)
 OR $40
 OUT ($FF),A
 LD A,I
 PUSH AF
 POP DE
 LD A,E
 AND 4
 LD (CTX+16),A
 POP AF
 DI
 CALL select_inner
 LD A,($BE00)
 OUT ($FF),A
 LD A,(CTX+16)
 OR A
 RET Z
 EI
 RET
select_inner:
 PUSH BC
 PUSH IX
 LD IX,0
 ADD IX,SP
{(" LD E,A"+chr(10)+" LD A,(CTX+25)"+chr(10)+" OR A"+chr(10)+" LD A,E"+chr(10)+" CALL Z,snake_role"+chr(10))if level==2 else ""} LD (CTX+24),A
 LD E,A
 LD D,0
 DEC E
 LD L,E
 LD H,0
 ADD HL,HL
 ADD HL,HL
 LD A,(CTX+25)
 OR A
 JR Z,actor_index
 LD BC,{actor_variant_bytes}
 ADD HL,BC
 LD A,(IX+9)
 AND 3
 LD C,A
 LD B,0
 ADD HL,BC
 JR lookup_index
actor_index:
 ADD HL,HL
 ADD HL,HL
{(' ADD HL,HL'+chr(10)+' ADD HL,HL')if level==2 else ''}
 LD A,IYL
 AND {phase_mask}
 LD C,A
 LD B,0
 PUSH HL
 LD HL,PHASES
 ADD HL,BC
 LD A,(HL)
{(" CALL next_phase" if level==2 else " INC (HL)")}
 AND {15 if level==2 else 3}
 ADD A,A
 ADD A,A
 LD C,A
 LD A,(IX+9)
 AND 3
 ADD A,C
 LD C,A
 POP HL
 ADD HL,BC
lookup_index:
 LD BC,${vaddr:04X}
 ADD HL,BC
 LD A,${3|(1<<(vaddr//8192)):02X}
 CALL read_byte
 CP 255
 JR Z,empty
select_frame_index:
 LD E,A
 LD A,(CTX+17)
 CP $A5
 JR NZ,decode_frame
 LD A,(CTX+18)
 CP E
 JR Z,cached_frame
decode_frame:
 LD A,$A5
 LD (CTX+17),A
 LD A,E
 LD (CTX+18),A
 CALL frame_pointer
 BIT 0,C
 JR NZ,full_frame
 LD A,C
 LD (CTX+26),A
 CALL read_stream_byte
 LD (CTX+28),HL
 CALL frame_pointer
 CALL unpack_frame
 LD HL,(CTX+28)
delta_next:
 CALL read_stream_byte
 LD E,A
 CALL read_stream_byte
 LD D,A
 AND E
 INC A
 JR Z,cached_frame
 PUSH HL
 LD HL,CACHE
 ADD HL,DE
 EX DE,HL
 POP HL
 CALL read_stream_byte
 LD B,A
delta_bytes:
 CALL read_stream_byte
 LD (DE),A
 INC DE
 DJNZ delta_bytes
 JR delta_next
full_frame:
 CALL unpack_frame
cached_frame:
 LD HL,CACHE
 LD E,(HL)
 INC HL
 LD D,(HL)
 INC HL
 LD A,(HL)
 INC HL
 LD (PALPTR),HL
 ADD A,A
 LD C,A
 LD B,0
 ADD HL,BC
 LD (BITS),HL
 POP IX
 POP BC
 RET
empty:
 LD DE,$0101
 LD HL,draw_blank
 POP IX
 POP BC
 RET
frame_pointer:
 LD L,A
 LD H,0
 LD D,H
 LD E,L
 ADD HL,HL
 ADD HL,DE
 LD DE,${daddr:04X}
 ADD HL,DE
 LD A,${3|(1<<(daddr//8192)):02X}
 OUT ($F4),A
 LD C,(HL)
 INC HL
 LD E,(HL)
 INC HL
 LD H,(HL)
 LD L,E
 LD A,3
 OUT ($F4),A
 RET
unpack_frame:
 LD A,C
 LD DE,CACHE
 LD (OLDSP),SP
 LD SP,${cache-2:04X}
 CALL $000A
 LD SP,(OLDSP)
 RET
read_stream_byte:
 LD A,(CTX+26)
 CALL read_byte
 INC HL
 RET
read_byte:
 PUSH BC
 OR 1
 OUT ($F4),A
 LD B,(HL)
 LD A,3
 OUT ($F4),A
 LD A,B
 POP BC
 RET
stock_colour:
 PUSH BC
 PUSH DE
 PUSH HL
 LD BC,CACHE
 OR A
 SBC HL,BC
 POP HL
 JR C,old_colour
 PUSH HL
 LD BC,${descriptor_end:04X}
 OR A
 SBC HL,BC
 POP HL
 JR NC,old_colour
 LD A,(HL)
 LD L,A
 LD H,0
 ADD HL,HL
 LD BC,(PALPTR)
 ADD HL,BC
 LD E,(HL)
 INC HL
 LD D,(HL)
 LD (LASTPI),DE
 CALL palette_read
 POP DE
 POP BC
 SCF
 RET
old_colour:
 POP DE
 POP BC
 JP $18F7
palette_read:
 PUSH AF
 LD A,($BE00)
 OR $40
 OUT ($FF),A
 LD A,I
 PUSH AF
 DI
 LD H,D
 LD L,E
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD BC,${palette:04X}
 ADD HL,BC
 LD DE,TEMP
 LD BC,8
 LD A,$23
 OUT ($F4),A
 LDIR
 LD A,3
 OUT ($F4),A
 LD A,($BE00)
 OUT ($FF),A
 POP AF
 JP PO,palette_no_ei
 EI
palette_no_ei:
 POP AF
 LD HL,TEMP
 RET
stock_background:
 CALL stock_colour
 JP NC,$15B3
 LD A,H
 CP ${(ctx+8)>>8:02X}
 JP NZ,$15A6
 LD HL,(LASTPI)
 LD A,L
 LD (DE),A
 CALL $15EC
 LD C,A
 LD A,H
 ADD A,A
 ADD A,A
 OR C
 OR $20
 LD C,A
 JP $15B9
stock_restore:
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 PUSH IX
 PUSH IY
 LD C,A
 LD A,($BE00)
 OR $40
 OUT ($FF),A
 LD A,I
 PUSH AF
 DI
 LD A,C
 CALL restore_base
 CALL $0209
 LD A,($BE00)
 OUT ($FF),A
 POP AF
 JP PO,restore_no_ei
 EI
restore_no_ei:
 POP IY
 POP IX
 POP HL
 POP DE
 POP BC
 POP AF
 RET
restore_base:
 OR A
 JP Z,$162F
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 LD A,H
 AND $18
 RRCA
 RRCA
 RRCA
 ADD A,$81
 LD D,A
 LD E,L
 LD A,(DE)
 BIT 5,A
 JR Z,restore_legacy
 LD C,A
 AND 4
 RRCA
 RRCA
 LD H,A
 LD A,D
 SUB 9
 LD D,A
 LD A,(DE)
 LD E,A
 LD D,H
 PUSH BC
 CALL palette_read
 POP BC
 POP DE
 PUSH DE
 SET 5,D
 BIT 7,C
 JR Z,normal
 LD A,D
 ADD A,7
 LD D,A
 LD B,8
reverse:
 LD A,(HL)
 LD (DE),A
 INC HL
 DEC D
 DJNZ reverse
 JR restored
normal:
 LD B,8
line:
 LD A,(HL)
 LD (DE),A
 INC HL
 INC D
 DJNZ line
restored:
 POP HL
 POP DE
 POP BC
 POP AF
 RET
restore_legacy:
 POP HL
 POP DE
 POP BC
 POP AF
 JP $162F
copy_front:
 LD BC,30
 PUSH AF
 LD A,($BE00)
 OR A
 JR NZ,copy_tokens
 POP AF
 LDDR
 JP $8859
copy_tokens:
 PUSH IX
 LD IXL,30
copy_cell:
 ; The legacy horizontal colour interpolator reads adjacent standard cells.
 ; Never publish dictionary indices there as if they were raw attributes.
 PUSH HL
 LD A,H
 ADD A,9
 LD H,A
 BIT 5,(HL)
 POP HL
 LD A,7
 JR NZ,emit
 LD A,(HL)
 BIT 7,A
 JR Z,emit
 LD C,A
 PUSH HL
 LD A,H
 ADD A,9
 LD H,A
 LD A,(HL)
 AND $60
 POP HL
 LD A,C
 JR NZ,emit
 PUSH HL
 AND $7F
 CALL $15D6
 LD A,(HL)
 POP HL
emit:
 LD (DE),A
 DEC HL
 DEC DE
 DEC IXL
 JR NZ,copy_cell
 POP IX
 POP AF
 LD BC,0
 JP $8859
{l2_helpers}
{draw_actor_gate}
 ASSERT $ <= $2400
'''
old_common=f''' LD BC,{actor_variant_bytes}
 ADD HL,BC
 LD A,(IX+9)
 AND 3
 LD C,A
 LD B,0
 ADD HL,BC
 JR lookup_index'''
new_common=f''' SRL H
 RR L
 SRL H
 RR L
 LD BC,{actor_variant_bytes}
 ADD HL,BC
 JR lookup_index'''
assert old_common in source;source=source.replace(old_common,new_common)
if True:
 old=f'lookup_index:\n LD BC,${vaddr:04X}\n ADD HL,BC\n LD A,${3|(1<<(vaddr//8192)):02X}\n CALL read_byte'
 replacement=f'''lookup_index:
 LD A,(CTX+25)
 OR A
 JR NZ,common_lookup
 LD A,L
 AND {row_size-1}
 LD E,A
 LD D,0
 DUP {6 if level==2 else 4}
 SRL H
 RR L
 EDUP
 LD BC,${vaddr:04X}
 ADD HL,BC
 LD A,${3|(1<<(vaddr//8192)):02X}
 CALL read_byte
 LD L,A
 LD H,0
 ADD HL,HL
 LD BC,${vaddr+len(rows):04X}
 ADD HL,BC
 LD A,${3|(1<<(vaddr//8192)):02X}
 CALL read_byte
 LD C,A
 INC HL
 LD A,${3|(1<<(vaddr//8192)):02X}
 CALL read_byte
 LD H,A
 LD L,C
 LD BC,${vaddr:04X}
 ADD HL,BC
 LD A,${3|(1<<(vaddr//8192)):02X}
 CALL read_byte
 AND E
 LD E,A
 LD D,0
 INC HL
 ADD HL,DE
 JR table_read
common_lookup:
 LD BC,${vaddr:04X}
table_lookup:
 ADD HL,BC
table_read:
 LD A,${3|(1<<(vaddr//8192)):02X}
 CALL read_byte'''
 assert old in source;source=source.replace(old,replacement)
if pair_palette:
 start=source.index(' LD H,D',source.index('palette_read:'));end=source.index(' LD A,3\n OUT ($F4),A',start)
 source=source[:start]+f''' LD H,D
 LD L,E
 ADD HL,HL
 ADD HL,HL
 LD BC,${palette:04X}
 ADD HL,BC
 LD DE,TEMP
 LD B,4
 LD A,$23
 OUT ($F4),A
palette_pair_next:
 LD A,(HL)
 INC HL
 PUSH HL
 LD L,A
 LD H,0
 ADD HL,HL
 PUSH BC
 LD BC,${pair_base:04X}
 ADD HL,BC
 POP BC
 LD A,(HL)
 LD (DE),A
 INC HL
 INC DE
 LD A,(HL)
 LD (DE),A
 INC DE
 POP HL
 DJNZ palette_pair_next
'''+source[end:]
if paged_palette:
 start=source.index('palette_read:');end=source.index('stock_background:',start)
 q=source[start:end];a=q.index(' LD H,D');z=q.index('palette_pair_next:')
 q=q[:a]+f''' LD H,D
 LD L,E
 CALL ${palette_pointer:04X}
 OUT ($F4),A
 LD DE,TEMP
 LD B,4
'''+q[z:]
 source=source[:start]+q+source[end:]
 start=source.index('restore_base:');end=source.index('copy_front:',start)
 source=source[:start]+source[start:end].replace(' AND 4\n RRCA',' AND $1C\n RRCA')+source[end:]
 old=' OR $20\n LD C,A\n JP $15B9'
 new=''' OR $20
 LD C,A
 LD A,D
 ADD A,9
 LD D,A
 LD A,(DE)
 AND 3
 OR C
 LD (DE),A
 JP $15C2'''
 assert old in source;source=source.replace(old,new)
if motion_vertical:
 source=source.replace('unpack_frame:\n LD A,C',f'''unpack_frame:
 BIT 6,C
 JR Z,unpack_source_ready
 LD A,C
 CALL read_byte
 INC HL
 LD B,A
 LD DE,${ram["motion_dense_parent"][0]:04X}
stage_source_byte:
 LD A,C
 CALL read_byte
 INC HL
 LD (DE),A
 INC DE
 DJNZ stage_source_byte
 LD HL,${ram["motion_dense_parent"][0]:04X}
 LD C,3
unpack_source_ready:
 LD A,C''')
if irq_decode_enabled:
 # Native FD20 saves F4, maps3 for the complete IRQ and restores F4 on return.
 # ROM4 would hide the84xx vector; ROM7 would hide handler/native stack.
 # The reentrant input-only busy path cannot touch the partially decoded cache.
 marker='unpack_frame:\n'
 start=source.index(marker)+len(marker)
 if motion_vertical:start=source.index('unpack_source_ready:',start)+len('unpack_source_ready:\n')
 source=source[:start]+f''' LD A,(CTX+16)
 OR A
 JR Z,unpack_atomic
 LD A,C
 AND $90
 JR NZ,unpack_atomic
 LD A,(${ram_layout["clock_flags"][0]+13:04X})
 PUSH AF
 LD A,1
 LD (${ram_layout["clock_flags"][0]+13:04X}),A
 LD A,C
 LD DE,CACHE
 EI
 CALL $000A
 DI
 POP AF
 LD (${ram_layout["clock_flags"][0]+13:04X}),A
 RET
unpack_atomic:
'''+source[start:]
 (O/'decode_irq_contract.json').write_text(json.dumps(dict(enabled=True,excluded_source_banks=[4,7],native_vector_page=[0x8400,0x8501],native_handler=0xfd20,source_stack='Native main stack remains visible; private decoder stack used only for atomic sources',input_guard=ram_layout['clock_flags'][0]+13,scope='Experimental interrupt-safe full-packet decode; source mapping restored by native IRQ wrapper; tests required')))
if motion_vertical:
 source=source.replace(' BIT 0,C\n JR NZ,full_frame',f' BIT 1,C\n JP Z,${vertical_address:04X}\n BIT 0,C\n JR NZ,full_frame').replace(' OR 1\n OUT ($F4),A',' OR 3\n OUT ($F4),A')
if motion_enabled:
 old=' LD (CTX+24),A\n LD E,A'
 assert source.count(old)==1
 source=source.replace(old,f' LD (CTX+24),A\n CALL ${motion_address:04X}\n JP C,select_frame_index\n LD E,A')
if proc_enabled:
 # Keep the normal scrolling mirror until the boss pool first allocates.
 old_copy=source[source.index('copy_front:'):source.index(' JP $8859',source.index('emit:',source.index('copy_front:')))+len(' JP $8859')]
 new_copy=old_copy.replace(' JR NZ,copy_tokens',' JR NZ,copy_decide',1).replace('copy_tokens:',f"""copy_decide:
 LD A,(${ram['l4_procedural_state'][0]+134:04X})
 OR A
 JR Z,copy_tokens
 OR A
 SBC HL,BC
 EX DE,HL
 OR A
 SBC HL,BC
 EX DE,HL
 POP AF
 LD BC,0
 JP $8859
copy_tokens:""",1)
 source=source.replace(old_copy,new_copy,1)
if proc_enabled:
 source=source.replace(' OR 1\n OUT ($F4),A',' OR 3\n OUT ($F4),A')
 source=source.replace(' CALL frame_pointer\n BIT 0,C',' CALL frame_pointer\n LD A,C\n AND 3\n DEC A\n JP Z,$%04X\n BIT 0,C'%proc_address,1)
 source=source.replace('palette_read:\n PUSH AF',f'palette_read:\n PUSH AF\n LD A,D\n OR A\n JP NZ,${proc_address+6:04X}\n LD A,E\n CP {proc["static_rows"]}\n JP NC,${proc_address+6:04X}\npalette_uncached:',1)
 source=source.replace('restore_base:\n OR A','restore_base:\n OR A\n JR NZ,restore_not_procedural\n CALL $%04X\nrestore_not_procedural:\n OR A'%(proc_address+12),1)
 start=source.index('restore_base:');end=source.index('copy_front:',start)
 source=source[:start]+source[start:end].replace(' LD D,H\n PUSH BC\n CALL palette_read',' LD D,H\n BIT 6,C\n JR Z,restore_generation_ready\n SET 3,D\nrestore_generation_ready:\n PUSH BC\n CALL palette_read',1)+source[end:]
if proc_enabled:
 source=source.replace(' LD A,H\n ADD A,A\n ADD A,A\n OR C\n OR $20', """ PUSH HL
 LD A,H
 AND 8
 RLCA
 RLCA
 RLCA
 LD L,A
 LD A,H
 AND 7
 ADD A,A
 ADD A,A
 OR L
 OR C
 OR $20
 POP HL""",1)
if level==6 or proc_enabled:
 source=source.replace(' INC A\n JR Z,cached_frame\n PUSH HL',' INC A\n JR Z,decoded_frame\n PUSH HL',1)
 source=source.replace('full_frame:\n CALL unpack_frame\ncached_frame:',f'full_frame:\n CALL unpack_frame\ndecoded_frame:\n CALL ${palette_delta_address:04X}\ncached_frame:',1)
if overlap_enabled:
 source=source.replace('palette_read:\n PUSH AF','palette_read:\n PUSH AF\n LD A,D\n CP 4\n JP Z,$%04X'%(overlap_address+9),1)
 source=source.replace('restore_base:\n OR A','restore_base:\n OR A\n JR NZ,restore_not_dynamic_empty\n CALL $%04X\nrestore_not_dynamic_empty:\n OR A'%(overlap_address+12),1)
if proc_enabled:
 font=(O.parent/'L4_native_font.bin').read_bytes();assert len(font)==512 and b[0x8ae8:0x8ce8]==font
 (O/'rom_font_contract.json').write_text(json.dumps(dict(ram_reclaimed=[0x7b08,0x7cc8],rom_font=[0x8ae8,0x8ce8],reader=0x23c0,native_sites=[0xc0b4,0xc0db,0x8c6c],bytes=512,scope='Native glyph reads use existing read-only ROM4 copy; preserve glyphs, cursor and IFF; RAM becomes active-game palette cache')))
 source+='''
 ASSERT $ <= $23AC
 DS $23AC-$,$FF
launcher_grid_pointer:
 LD A,B
 AND 7
 RRCA
 RRCA
 RRCA
 ADD A,C
 LD L,A
 LD A,B
 RRCA
 RRCA
 RRCA
 AND 3
 ADD A,$7E
 LD H,A
 RET
 ASSERT $ <= $23C0
 DS $23C0-$,$FF
font_load:
 PUSH BC
 LD A,I
 PUSH AF
 DI
 PUSH HL
 LD A,H
 ADD A,$10
 LD H,A
 LD A,$13
 OUT ($F4),A
 LD B,(HL)
 LD A,3
 OUT ($F4),A
 POP HL
 POP AF
 JP PO,font_di
 EI
font_di:
 LD A,B
 POP BC
 RET
 DS $23E0-$,$FF
font_byte:
 CALL font_load
 LD (DE),A
 INC D
 RET
 DS $23E8-$,$FF
font_hud:
 CALL font_load
 LD HL,$7AFB
 RET
 ASSERT $ <= $2400
'''
p=O/'stock_actor_kernel.asm';p.write_text(source);q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
sym={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9A-Fa-f]+)',p.with_suffix('.sym').read_text())};code=p.with_suffix('.bin').read_bytes();b[0x2000:0x2000+len(code)]=code
if proc_enabled:
 p=O/'stock_l4_procedural.asm';p.write_text(f'RAW_PALETTE EQU ${sym["palette_uncached"]:04X}\nPROC_CODE EQU ${proc_address:04X}\nREAD_BYTE EQU ${sym["read_byte"]:04X}\nPALETTE_READ EQU ${sym["palette_read"]:04X}\nCACHED_FRAME EQU ${sym["cached_frame"]:04X}\n'+proc_defs+proc_template)
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 data=p.with_suffix('.bin').read_bytes();assert len(data)==proc_size;b[proc_address:proc_address+len(data)]=data
 (O/'l4_palette_pool_contract.json').unlink(missing_ok=True)
 (O/'l4_stable_tokens.json').write_text(json.dumps(dict(codec=proc['codec'],static_rows=proc['static_rows'],token_count=proc['token_count'],recipes=proc['recipes'],cache_entries=156,keys=[ram['l4_pair_cache_keys'][0],ram['l4_pair_cache_keys'][0]+312],expanded_rows=[[0x5800,0x5a80],[0x7b08,0x7cc8],[ram['l4_pair_cache_keys'][0]+312,ram['l4_pair_cache_keys'][1]],ram['l4_expanded_row_tail']],immutable=True)))
if overlap_enabled:
 p=O/'stock_overlap_compositor.asm';p.write_text(f'COMPOSITOR_CODE EQU ${overlap_address:04X}\nSTOCK_COLOUR EQU ${sym["stock_colour"]:04X}\nPALETTE_READ EQU ${sym["palette_read"]:04X}\n'+overlap_defs+overlap_template)
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 data=p.with_suffix('.bin').read_bytes();assert len(data)==overlap_bytes;b[overlap_address:overlap_address+len(data)]=data
if motion_vertical:
 p=O/'stock_vertical_frame.asm';p.write_text(f'VERTICAL_CODE EQU ${vertical_address:04X}\nREAD_STREAM_BYTE EQU ${sym["read_stream_byte"]:04X}\nDIRECT_FRAME EQU ${sym["direct_frame"]:04X}\nUNPACK_FRAME EQU ${sym["unpack_frame"]:04X}\nCACHED_FRAME EQU ${sym["cached_frame"]:04X}\n'+vertical_defs+vertical_template)
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 data=p.with_suffix('.bin').read_bytes();assert len(data)==vertical_bytes;b[vertical_address:vertical_address+len(data)]=data
 (O/'vertical_frame_contract.json').write_text(json.dumps(dict(code=vertical_address,bytes=vertical_bytes,frames={str(k):dict(parent=v[0],dy=v[1])for k,v in motion_vertical.items()},dense_ram=ram['motion_dense_parent'])))
if motion_enabled:
 p=O/'stock_tap_motion.asm';p.write_text(f'MOTION_CODE EQU ${motion_address:04X}\nREAD_BYTE EQU ${sym["read_byte"]:04X}\n'+motion_defs+motion_template)
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 data=p.with_suffix('.bin').read_bytes();assert len(data)==motion_bytes;b[motion_address:motion_address+len(data)]=data
if level==2:
 p=O/'stock_l2_body.asm';p.write_text(f'BODY_CODE EQU ${body_address:04X}\nPALETTE_READ EQU ${sym["palette_read"]:04X}\n'+body_template)
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 data=p.with_suffix('.bin').read_bytes();assert len(data)==body_bytes;b[body_address:body_address+len(data)]=data
 b[0xc06:0xc09]=bytes([0xc3])+body_address.to_bytes(2,'little');b[0xc09:0xc0c]=bytes([0xc3])+(body_address+3).to_bytes(2,'little');b[0xc12:0xc15]=bytes([0xc3])+(body_address+6).to_bytes(2,'little')
 star_source=(R/'src/stock_l2_star_guard.asm').read_text()
 p=O/'stock_l2_star_guard.asm';p.write_text(f' ORG ${0x2000+len(code):04X}\n'+star_source+'\n ASSERT $ <= $2400\n')
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 ss={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};data=p.with_suffix('.bin').read_bytes();b[0x2000+len(code):0x2000+len(code)+len(data)]=data
 b[0xc0c:0xc0f]=bytes([0xc3])+ss['cleanup_guard'].to_bytes(2,'little');b[0xc0f:0xc12]=bytes([0xc3])+ss['draw_guard'].to_bytes(2,'little')


for a in (0x1550,):b[a:a+3]=bytes([0xcd])+sym['stock_colour'].to_bytes(2,'little')
b[0x15a3:0x15a6]=bytes([0xc3])+sym['stock_background'].to_bytes(2,'little')
for a in (0x160d,0x1615):b[a+1:a+3]=sym['stock_restore'].to_bytes(2,'little')
b[0x1703:0x1706]=bytes([0xc3])+sym['copy_front'].to_bytes(2,'little')
for lo,hi in ((0x1614,0x162f),(0x16e5,0x16ee),(0x1745,0x1790)):
 for a in range(lo,hi):
  if b[a:a+2]==bytes.fromhex('e6c0'):b[a+1]=0xe4
  elif b[a:a+2]==bytes.fromhex('e63f'):b[a+1]=0x1b
for a in range(0x15b9,0x15c2):
 if b[a:a+2]==bytes.fromhex('e63f'):b[a+1]=0x1b
if paged_palette:
 for lo,hi in ((0x1614,0x162f),(0x16e5,0x16ee),(0x1745,0x1771)):
  for address in range(lo,hi-1):
   if b[address:address+2]==bytes.fromhex('e6e4'):b[address+1]=0xfc
   elif b[address:address+2]==bytes.fromhex('e61b'):b[address+1]=3
a=b.find(bytes.fromhex('e61f5f1600'),0x1a00,0x1a6e);assert a>=0;b[a+1]=0x8f
a=b.find(bytes.fromhex('cb632802cbe2'),0x1a00,0x1a6e);assert a>=0;b[a+1]=0x7b
backend=f'PALETTE_BASE EQU ${palette:04X}\nPLAYER_STATE EQU ${ram["player_state"][0]:04X}\nCLOCK_FLAGS EQU ${ram_layout["clock_flags"][0]:04X}\n'+(R/'src/stock_player_backend.asm').read_text()
if pair_palette:
 start=backend.index('dictionary_forward:');end=backend.index('terrain_attribute:',start)
 backend=backend[:start]+f'''dictionary_forward:
 LD A,D
 AND 4
 RRCA
 RRCA
 LD H,A
 LD L,C
 ADD HL,HL
 ADD HL,HL
 LD DE,${palette:04X}
 ADD HL,DE
 LD A,B
 AND 1
 LD C,A
 SRL B
 LD E,B
 LD D,0
 ADD HL,DE
 LD A,$23
 OUT ($F4),A
 LD A,(HL)
 LD L,A
 LD H,0
 ADD HL,HL
 LD DE,${pair_base:04X}
 ADD HL,DE
 LD E,C
 LD D,0
 ADD HL,DE
 LD A,(HL)
 PUSH AF
 LD A,3
 OUT ($F4),A
 POP AF
 JR attribute_done
'''+backend[end:]
if paged_palette:
 start=backend.index('dictionary_forward:');end=backend.index('terrain_attribute:',start)
 q=backend[start:end].replace(' AND 4\n RRCA',' AND $1C\n RRCA')
 a=q.index(' ADD HL,HL');z=q.index(' LD A,B\n AND 1',a)
 q=q[:a]+f''' CALL ${palette_pointer:04X}
 LD E,A
'''+q[z:]
 # Preserve the page mask until mapping; the parity bit stays in C.
 q=q.replace(' LD E,A\n LD A,B\n AND 1', ' PUSH AF\n LD A,B\n AND 1')
 q=q.replace(' LD A,$23\n OUT ($F4),A',' POP AF\n OUT ($F4),A')
 backend=backend[:start]+q+backend[end:]
if level==2:
 start_backend=backend.index('terrain_attribute:')
 end_backend=backend.index('attribute_done:',start_backend)
 backend=backend[:start_backend]+f'''terrain_attribute:
 LD A,D
 SUB $81
 RLCA
 RLCA
 RLCA
 LD H,A
 LD A,E
 AND $E0
 RRCA
 RRCA
 RRCA
 RRCA
 RRCA
 OR H
 CALL $08F0
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,${l2_row_palette:04X}
 ADD HL,DE
 LD E,B
 LD D,0
 ADD HL,DE
 LD A,(HL)
'''+backend[end_backend:]
if proc_enabled:
 backend=backend.replace('dictionary_forward:\n',f"""dictionary_forward:
 LD A,D
 AND $1C
 RRCA
 RRCA
 LD H,A
 LD A,D
 AND $40
 RRCA
 RRCA
 RRCA
 OR H
 LD D,A
 LD E,C
 OR A
 JR NZ,body_attribute
 LD A,E
 CP {proc['static_rows']}
 JR C,dictionary_static
body_attribute:
 CALL ${proc_address+9:04X}
 JR attribute_done
dictionary_static:
""",1)
if overlap_enabled:
 assert backend.count('dictionary_forward:\n')==1
 backend=backend.replace('dictionary_forward:\n','dictionary_forward:\n BIT 4,D\n JR Z,dictionary_static\n CALL $%04X\n JR attribute_done\ndictionary_static:\n'%(overlap_address+6),1)
compact_snapshot=ram['backing_attributes'][1]-ram['backing_attributes'][0]==160
if compact_snapshot:
 backend=backend.replace(' JP merge_player_attributes\n',' JP merge_player_attributes\n JP snapshot_attribute\n JP snapshot_capture\n',1).replace(' BIT 5,A\n JR NZ,dictionary_attribute','attribute_dispatch:\n BIT 5,A\n JR NZ,dictionary_attribute',1)
 backend=backend.replace(' ASSERT $ <= $0400','')
 backend=f'SNAPSHOT_BASE EQU ${ram["backing_attributes"][0]:04X}\nBACKING_PIXELS EQU ${ram["backing_pixels"][0]:04X}\n'+backend+(R/'src/stock_compact_snapshot.asm').read_text()+'\n ASSERT $ <= $0480\n'
 (O/'compact_snapshot_contract.json').write_text(json.dumps(dict(attributes=ram['backing_attributes'],pixels=ram['backing_pixels'],rows=64,columns=10,cells=80,format='interleaved token/flag bytes; exact palette resolution on read',bytes_saved=480)))
pback=O/'stock_player_backend.asm';pback.write_text(backend)
q=subprocess.run([str(exe),f'--raw={pback.with_suffix(".bin")}',str(pback)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
backcode=pback.with_suffix('.bin').read_bytes();assert 0x200+len(backcode)<=(0x480 if compact_snapshot else 0x400);b[0x200:0x200+len(backcode)]=backcode
if proc_enabled:segments.append([0x200+len(backcode),0x400])
# The global refresh still visits every cell. Resolve dictionary cells using
# their per-raster pairs instead of treating the palette ID as a raw attribute.
def legacy_assemble(name,source):
 p=O/(name+'.asm');p.write_text(source)
 q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 return p.with_suffix('.bin').read_bytes()
legacy_source=(R/'src/stock_legacy_palette.asm').read_text()
if level==2:legacy_source=legacy_source.replace('$FBD0',f'${l2_row_palette:04X}')
dictionary_source=(R/'src/stock_legacy_dictionary.asm').read_text()
if proc_enabled:
 dictionary_source=dictionary_source.replace('ordinary:\n POP AF\n POP HL\n OR A\n RET',f"""ordinary:
 LD A,($BE00)
 CP 2
 JR NZ,legacy_input
 LD A,(${ram['l4_procedural_state'][0]+134:04X})
 OR A
 JR Z,legacy_input
 POP AF
 PUSH BC
 LD A,(HL)
 AND $60
 LD B,A
 LD A,H
 SUB 9
 LD H,A
 LD A,(HL)
 BIT 7,A
 JR Z,clean_input
 LD C,A
 LD A,B
 OR A
 LD A,C
 JR NZ,clean_input
 AND $7F
 CALL $15D6
 LD A,(HL)
clean_input:
 POP BC
 POP HL
 OR A
 RET
legacy_input:
 POP AF
 POP HL
 OR A
 RET""").replace('DICT_CODE+40','DICT_CODE+96')
if level==2:dictionary_source=dictionary_source.replace('BIT 5,(HL)','LD A,(HL)\n AND $60')
legacy_bulk_source=None
if proc_enabled:
 at=legacy_source.index('bulk:')
 legacy_bulk_source='dictionary_cell EQU DICT_CODE\n ORG LEGACY_CODE\n'+legacy_source[at:]
 legacy_source=legacy_source[:at]
probe=legacy_assemble('stock_legacy_palette','LEGACY_CODE EQU 0\nDICT_CODE EQU 0\n'+legacy_source)
legacy_address=put(bytes([255])*len(probe),[0,1])
if proc_enabled:
 split=dictionary_source.index('ordinary:')
 helper_source=dictionary_source[split:dictionary_source.index(' ASSERT',split)] if ' ASSERT' in dictionary_source[split:] else dictionary_source[split:]
 helper_source=helper_source.split('ASSERT')[0]
 helper_data=legacy_assemble('stock_l4_ordinary_helper',' ORG 0\n'+helper_source)
 helper_address=put(helper_data,[0,1])
 helper_data=legacy_assemble('stock_l4_ordinary_helper',f' ORG ${helper_address:04X}\n'+helper_source)
 b[helper_address:helper_address+len(helper_data)]=helper_data
 dictionary_source=dictionary_source[:split]+f'ordinary:\n JP ${helper_address:04X}\n'
probe=legacy_assemble('stock_legacy_dictionary','DICT_CODE EQU 0\n'+dictionary_source)
dictionary_address=put(bytes([255])*len(probe),[0,1])
legacy=legacy_assemble('stock_legacy_palette',f'LEGACY_CODE EQU ${legacy_address:04X}\nDICT_CODE EQU ${dictionary_address:04X}\n'+legacy_source)
dictionary=legacy_assemble('stock_legacy_dictionary',f'DICT_CODE EQU ${dictionary_address:04X}\n'+dictionary_source)
b[legacy_address:legacy_address+len(legacy)]=legacy
if legacy_bulk_source:
 probe=legacy_assemble('stock_legacy_bulk','LEGACY_CODE EQU 0\nDICT_CODE EQU 0\n'+legacy_bulk_source)
 legacy_bulk_address=put(bytes(len(probe)),[0,1])
 data=legacy_assemble('stock_legacy_bulk',f'LEGACY_CODE EQU ${legacy_bulk_address:04X}\nDICT_CODE EQU ${dictionary_address:04X}\n'+legacy_bulk_source)
 b[legacy_bulk_address:legacy_bulk_address+len(data)]=data

b[dictionary_address:dictionary_address+len(dictionary)]=dictionary
if proc_enabled:
 guard=f""" ORG 0
 PUSH AF
 LD HL,$7800
 LD DE,$5800
 LD BC,$280
 LD A,(${ram['l4_procedural_state'][0]+134:04X})
 OR A
 JR Z,copy_initial
 LD HL,$7A80
 LD DE,$5A80
 LD BC,0
 POP AF
 RET
copy_initial:
 LDIR
 POP AF
 RET
"""
 data=legacy_assemble('stock_l4_mirror_guard',guard);address=put(data,[0,1]);b[0xc18:0xc1b]=bytes([0xc3])+address.to_bytes(2,'little')

if level==4:
 layer_source=(R/'src/stock_l4_launcher_layers.asm').read_text()
 filter_source=(R/'src/stock_l4_launcher_filter.asm').read_text()
 predicate_source=(R/'src/stock_l4_launcher_predicates.asm').read_text()
 mask_source=(R/'src/stock_l4_launcher_mask.asm').read_text();mask_defs=f'PS EQU ${ram["l4_procedural_state"][0]:04X}\n'
 layer_defs=f'CTX EQU ${ctx:04X}\nMASK_CODE EQU 0\n'+mask_defs
 probe=legacy_assemble('stock_l4_launcher_layers','LAYER_CODE EQU 0\n'+layer_defs+layer_source);layer_address=put(bytes(len(probe)),[0,1])
 probe=legacy_assemble('stock_l4_launcher_mask','MASK_CODE EQU 0\n'+mask_defs+mask_source);mask_address=put(bytes(len(probe)),[0,1])
 data=legacy_assemble('stock_l4_launcher_mask',f'MASK_CODE EQU ${mask_address:04X}\n'+mask_defs+mask_source);b[mask_address:mask_address+len(data)]=data
 layer_defs=f'CTX EQU ${ctx:04X}\nMASK_CODE EQU ${mask_address:04X}\n'+mask_defs
 probe=legacy_assemble('stock_l4_launcher_filter','FILTER_CODE EQU 0\n'+layer_defs+filter_source);filter_address=put(bytes(len(probe)),[0,1])
 predicate_defs=f'FILTER_CODE EQU ${filter_address:04X}\n'
 probe=legacy_assemble('stock_l4_launcher_predicates','PREDICATE_CODE EQU 0\n'+predicate_defs+predicate_source);predicate_address=put(bytes(len(probe)),[0,1])
 for stem,defs,source,address in [('stock_l4_launcher_layers',f'LAYER_CODE EQU ${layer_address:04X}\n'+layer_defs,layer_source,layer_address),('stock_l4_launcher_filter',predicate_defs+layer_defs,filter_source,filter_address),('stock_l4_launcher_predicates',f'PREDICATE_CODE EQU ${predicate_address:04X}\n'+predicate_defs,predicate_source,predicate_address)]:
  data=legacy_assemble(stem,defs+source);b[address:address+len(data)]=data
 for gateway,target in [(0xc12,predicate_address),(0xc15,predicate_address+3),(0xc1b,layer_address),(0xc1e,layer_address+3)]:b[gateway:gateway+3]=bytes([0xc3])+target.to_bytes(2,'little')
 (O/'launcher_layer_contract.json').write_text(json.dumps(dict(native_ids=[52,53,54],projectile_owner=250,layer_code=layer_address,filter_code=filter_address,predicate_code=predicate_address,temporary_native_sites=[0x8ed6,0x8f0b],scope='Launcher visual foreground over projectile cells only; saved projectile collision ownership restored after every draw; native object records, terrain and other actor occlusion unchanged; native predicates restored')))

legacy_bulk=legacy_bulk_address if legacy_bulk_source else int(re.search(r'^bulk: EQU 0x([0-9A-Fa-f]+)',(O/'stock_legacy_palette.sym').read_text(),re.M)[1],16)
b[0xe00:0xe03]=bytes([0xc3])+legacy_address.to_bytes(2,'little');b[0xe40:0xe43]=bytes([0xc3])+legacy_bulk.to_bytes(2,'little')

engine_files=[('stock_player_engine.bin',0x2400,0x2d80),('stock_player_damage.bin',0x1e20,0x1f20),('stock_projectile_engine.bin',0x1b20,0x1da0),('stock_visible_owner.bin',0x1db0,0x1dd0),('stock_projectile_shims.bin',0xd30,0xd90),('stock_projectile_glyphs.bin',0x1dd0,0x1e20),('stock_projectile_gateway.bin',0xd90,0xdd0)]
for filename,at,limit in engine_files:
 data=(O/filename).read_bytes();assert at+len(data)<=limit
 assert all(v==255 for v in b[at:at+len(data)]),(filename,'engine overlaps allocated bytes')
 b[at:at+len(data)]=data
# Complete stock lifecycle bridges: bootstrap private state/phases and use the
# current one-pixel renderer from native sync/copy/interrupt entry points.
mark_owners=int(re.search(r'fast_mark_owners: EQU 0x([0-9A-Fa-f]+)',(O/'stock_player_engine.sym').read_text())[1],16)
gateway_source=f'MARK_OWNERS EQU ${mark_owners:04X}\nBODY_STATE EQU ${ram.get("l2_body_workspace",ram_layout["free_segments"][0])[0]:04X}\nLEVEL_NUM EQU {level}\nPHASE_SOURCE EQU ${phase_source:04X}\nPHASE_MASK EQU ${3|((1<<(phase_source//8192))if phase_source//8192>1 else 0):02X}\nPHASE_DEST EQU ${ram["player_phases"][0]:04X}\nOWNER_MAP EQU ${ram["published_owner_map"][0]:04X}\nFLAGS EQU ${ram_layout["clock_flags"][0]:04X}\n'+(R/'src/stock_live_player.asm').read_text()
if motion_enabled:gateway_source=gateway_source.replace('; STOCK_MOTION_RESET_HOOK',f' CALL ${motion_address+3:04X}')
if proc_enabled:gateway_source=gateway_source.replace(' CALL $1B26\n RET',f' CALL ${proc_address+3:04X}\n CALL $1B26\n RET',1)
if overlap_enabled:gateway_source=gateway_source.replace(' CALL $1B26\n RET',f' CALL ${overlap_address+3:04X}\n CALL $1B26\n RET',1)
# Reference bits conservatively accumulate newly published rows; reclaim rescans
# only on exhaustion. Copies do not introduce a row outside that tracked set.
p=O/'stock_live_player.asm';p.write_text(gateway_source)
q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
data=p.with_suffix('.bin').read_bytes();assert len(data)<=0xf0
if motion_enabled:assert bytes([0xcd])+(motion_address+3).to_bytes(2,'little')in data,'Missing cold/runtime motion reset call'
assert all(v==255 for v in b[0x1000:0x1000+len(data)])
b[0x1000:0x1000+len(data)]=data
assert b[0x862f:0x8634]==bytes.fromhex('3e03fbd3f4')
b[0x862f:0x8634]=bytes.fromhex('c300100000')
if level==2:
 for opcode in (1,17):
  old=bytes([opcode,0xd0,0xfb]);new=bytes([opcode])+l2_row_palette.to_bytes(2,'little')
  for address in range(8190):
   if b[address:address+3]==old:b[address:address+3]=new
p=O/f'L{level}_shared_cache_internal';p.with_suffix('.rom').write_bytes(b);p.with_suffix('.dck').write_bytes(bytes([0]+[2]*8)+b)
(O/'shared_cache_layout.json').write_text(json.dumps(dict(status='Experimental current actor-art integration; full gameplay parity unverified',frames=len(j['frames']),palette_rows=len(j['palette']),max_frame_cache_bytes=maxraw,kernel_bytes=len(code),l2_body=body_address,completion=completion_address,controls=control_address,title_lifetime=title_address,palette=palette,variants=vaddr,directory=daddr,free_segments=segments,symbols=sym),indent=2));print('Built',len(code),maxraw,segments)
