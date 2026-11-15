"""Repack true-ROM initial HOME images; preserve the old native finalizer."""
from pathlib import Path
import json,subprocess,re,hashlib,sys
from pack_optimal_r87 import pack_optimal
from normal_black_policy import patch_stock_title, patch_score, patch_stock_home
from stock_tap_motion_config import procedural_enabled
R=Path.cwd();level=int(sys.argv[1]);assert 1<=level<=8;O=R/f'build/cartridges/integration_work/level{level:02d}';O.mkdir(parents=True,exist_ok=True);old=(R/'build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r24.rom').read_bytes();b=bytearray(old)
patch_stock_title(b)
exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
current_region=(R/f'build/fullgame/visible_hits_r145/level{level:02d}_region.bin').read_bytes()
b[0x480:0x8c0]=current_region[0x480:0x8c0]
def asm(name,source):
 p=O/(name+'.asm');p.write_text(source);q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 return p.with_suffix('.bin').read_bytes()
# Reclaim raw initial graphics storage: native selectors will use the new cache.
foundation=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'][level-1];payload=(R/f'build/fullgame/foundation/level{level:02d}.payload').read_bytes();home=bytearray(65536)
for bank,dest in ((7,0x4000),(3,0xa000),(5,0xc000),(6,0xe000),(2,0x8000)):home[dest:dest+8192]=old[bank*8192:(bank+1)*8192]
patch_stock_home(home)
patch_score(home,0xbccb,'f0fd')
home[0xc4ae:0xc4ae+len(payload)]=payload;home[0xb79c]=48+level
native=(R/f'build/fullgame/foundation/level{level:02d}.raw').read_bytes()
# Import current event records for every level. Matching event pointers alone
# does not establish matching spawn coordinates or actor arrangements.
event_lo=int.from_bytes(home[0xc4b4:0xc4b6],'little')
event_hi=int.from_bytes(home[0xc4b8:0xc4ba],'little')+1
assert 0xc000<=event_lo<event_hi<=0xf800
old_events=bytes(home[event_lo:event_hi]);events=current_region[event_lo-0x2000:event_hi-0x2000]
def sphere_count(data):
 rows=[]
 for at in range(0,len(data),5):
  if data[at]==255:break
  if data[at]==73 and data[at+2]==35:rows.append(list(data[at:at+5]))
 return rows
if level==5:assert len(sphere_count(old_events))==24 and len(sphere_count(events))==12
home[event_lo:event_hi]=events
(O/'native_event_contract.json').write_text(json.dumps(dict(level=level,start=event_lo,end=event_hi,changed_bytes=sum(a!=b for a,b in zip(old_events,events)),current_spheres=len(sphere_count(events))if level==5 else None,source=f'build/fullgame/visible_hits_r145/level{level:02d}_region.bin',event_sha256=hashlib.sha256(events).hexdigest()),indent=2))

# Exact current native tile bytes remain in their original descending slots.
terrain=(O/'terrain/native_tiles.bin').read_bytes()
assert len(terrain)==foundation['terrain_tiles']*144
for tile in range(foundation['terrain_tiles']):
 at=foundation['map_start']-(tile+1)*144
 home[at:at+144]=terrain[tile*144:(tile+1)*144]
home[0xfbd0:0xfc50]=(O/'terrain/palette.bin').read_bytes()

for pc in (0x9152,0xc1e5):
 assert native[pc-0x4000:pc-0x4000+2]==bytes.fromhex('fdcb')
 home[pc:pc+4]=native[pc-0x4000:pc-0x4000+4]
# Install the stock native lifecycle hooks before compressing HOME images.
# Gateways execute in permanent ROM0, keeping both input and the stack visible.
def hook(address,expected,replacement):
 expected=bytes.fromhex(expected)
 assert home[address:address+len(expected)]==expected,(hex(address),home[address:address+len(expected)].hex())
 home[address:address+len(replacement)]=replacement
if level==2:
 hook(0x882d,'3c8787',bytes.fromhex('c3060c'))
 hook(0xbeea,'cdfe16',bytes.fromhex('cd0c0c'))
 hook(0xbf11,'cdf716',bytes.fromhex('cd0f0c'))
 boss=json.loads((O.parent/'L2_boss_terrain.json').read_text())
 for i,coord in enumerate(boss['bossCoordinates']):
  at=foundation['map_start']+(55+(coord&7))*5+(coord>>3)
  assert foundation['map_start']<=at<foundation['map_end']
  home[at]=34+i
hook(0x92ef,'cd90bc',bytes([0xcd])+(0xc15 if level==2 else 0xc06).to_bytes(2,'little'))
if procedural_enabled(level):
 hook(0xc0b4,'7e1214',bytes.fromhex('cde023'))
 hook(0xc0db,'7e1214',bytes.fromhex('cde023'))
 hook(0x8c6c,'7e21fb7a',bytes.fromhex('cde82300'))
 hook(0x90c4,'210078110058018002edb0',bytes.fromhex('cd180c')+bytes(8))
hook(0x865f,'cd068b',bytes.fromhex('cdf81f'))
hook(0xc2a3,'cd03fe',bytes.fromhex('c3030c'))
hook(0x8a4d,'cd200f',bytes.fromhex('cd000c'))
hook(0x94f6,'2aa17a',bytes.fromhex('c30910'))
hook(0x9560,'cdfe99',bytes.fromhex('cd7ac0'))
hook(0x9563,'ed4ba17a',bytes.fromhex('c30c1000'))
hook(0xbe2d,'cd30f9',bytes.fromhex('cd0310'))
for address in (0x8979,0x8afe,0xc290):
 hook(address,'cd4288',bytes.fromhex('cd0610'))
# Replace the retired native normal-shot loop with queued-hit consumption.
# Native actor damage runs only on the main stack, never inside an IRQ.
hits=(R/'src/projectile_hits.asm').read_text().replace('CALL GATEWAY','LD B,E\n        CALL $0D90').replace('$71E1','$B7E1').replace('$71E2','$B7E2')
hit_code=asm('stock_projectile_hits',hits)
assert home[0x9da5:0x9da9]==bytes.fromhex('21b45e06')
home[0x9da5:0x9da5+len(hit_code)]=hit_code
if level==4:
 for address in (0xef5a,0xef61,0xef68):
  assert home[address]==32
  home[address]=16
# Current Force follow/recall rate, independent of native compatibility patches.
for patch in json.loads((R/'build/fullgame/visible_hits_r145/follower_contract.json').read_text())['patches']:
 address=patch['address'];old_bytes=bytes.fromhex(patch['old']);new_bytes=bytes.fromhex(patch['new'])
 assert home[address:address+len(old_bytes)]==old_bytes
 home[address:address+len(new_bytes)]=new_bytes
# The title initializer clears the inherited Spectrum loading screen.
# Keep resident kernels/reversal, but do not store obsolete visible pixels.
home[0x4000:0x5b00]=bytes(0x1b00)
home[0x5b00:0x5d00]=bytes(0x200) # retired compiled-cell code; new cache never calls it
home[0x5e00:0x6000]=bytes(0x200) # native pools start cleared; remain reserved
if procedural_enabled(level):
 # The current selectors no longer read retired graphics from the working
 # playfield. Preserve its interleaved bottom32-row native code/variables/font.
 before=bytes(home)
 home[0x8100:0x8380]=bytes(0x280) # initial flag grid only; preserve the8080 scanline-pointer table
 for y in range(160):
  off=((y&192)<<5)|((y&7)<<8)|((y&56)<<2);home[0xa600+off:0xa600+off+32]=bytes(32)
 assert all(home[0xb680+r*256:0xb700+r*256]==before[0xb680+r*256:0xb700+r*256]for r in range(8))
 (O/'retired_working_image_contract.json').write_text(json.dumps(dict(cleared_pixels=5120,preserved_native_gap_ranges=[[0xa600+0x1000+r*256+128,0xa600+0x1100+r*256]for r in range(8)],scope='Only initial top160-row working pixels; native interleaved lower32-row code/variables/font preserved; runtime regression required')))
free=[];packets=[]
for bank,dest in ((7,0x4000),(3,0xa000),(5,0xc000),(6,0xe000),(2,0x8000)):
 raw=bytearray(home[dest:dest+8192])
 if dest==0xc000:raw[0x4ce:foundation['enemy_descriptors_start']-0xc000]=bytes(foundation['enemy_descriptors_start']-0xc4ce)
 if dest==0x4000:raw[0x1d00:0x1e00]=bytes(256)if procedural_enabled(level)else bytes(int(f'{i:08b}'[::-1],2)for i in range(256))
 packet=pack_optimal(raw);assert len(packet)<8192
 b[bank*8192:(bank+1)*8192]=bytes([255])*8192;b[bank*8192:bank*8192+len(packet)]=packet
 packets.append(dict(bank=bank,destination=dest,bytes=len(packet),raw_sha256=hashlib.sha256(raw).hexdigest()));free.append([bank*8192+len(packet),(bank+1)*8192])
# Boot-only decoder executes from permanent ROM0; no source mapping hides it.
decoder_source=''' ORG $0000
boot_unpack:
 OUT ($F4),A
 CALL unpack
 LD A,$13
 OUT ($F4),A
 RET
runtime_unpack:
 OUT ($F4),A
 CALL unpack
 LD A,3
 OUT ($F4),A
 RET
unpack:
 LD A,(HL)
 INC HL
 OR A
 RET Z
 JP M,backref
 LD C,A
 LD B,0
 LDIR
 JR unpack
backref:
 AND $7F
 ADD A,3
 LD C,(HL)
 INC HL
 LD B,(HL)
 INC HL
 PUSH HL
 LD H,D
 LD L,E
 OR A
 SBC HL,BC
 LD C,A
 LD B,0
 LDIR
 POP HL
 JR unpack
 ASSERT $ <= $0100
'''
if procedural_enabled(level):decoder_source=decoder_source.replace(' ASSERT $ <= $0100',''' ASSERT $ <= $0060
 DS $0060-$,$FF
reverse_init:
 LD HL,$5D00
 LD B,0
reverse_next:
 LD A,L
 LD D,0
 LD C,8
reverse_bit:
 RRA
 RL D
 DEC C
 JR NZ,reverse_bit
 LD (HL),D
 INC L
 DJNZ reverse_next
 RET
 ASSERT $ <= $0100''')
decoder=asm('stock_unpack',decoder_source);b[:0x100]=bytes([255])*256;b[:len(decoder)]=decoder
# Stack remains visible across each source mapping and outside each destination.
lines=[' ORG $8008',' DI',' XOR A',' OUT ($FF),A',' LD SP,$BE20']
for bank,dest in ((7,0x4000),(3,0xa000),(5,0xc000),(6,0xe000),(2,0x8000)):
 if bank==3:lines+=[' LD SP,$5A80']
 if bank==2:lines+=[' LD SP,$BE20']
 lines += [f' LD A,${(0x13|(1<<bank)):02X}',f' LD HL,${bank*8192:04X}',f' LD DE,${dest:04X}',' OUT ($F4),A']+([' LD A,7'] if bank==2 else [])+[' CALL $0000']
lines+=[' LD HL,$8800',' LD DE,$7800',' LD BC,$800',' LDIR',' LD HL,$9EA0',' LD DE,$5A00',' LD BC,128',' LDIR',' JP $807B',' ASSERT $ <= $807B']
boot=asm('stock_compressed_boot','\n'.join(lines));b[0x8008:0x807b]=bytes([255])*(0x807b-0x8008);b[0x8008:0x8008+len(boot)]=boot
# Reassemble the original fixed-size finalizer with the actual restored RAM bytes.
final=(R/'build/readonly_ecm/boot.asm').read_text().split('finalize:',1)[1].split('        ASSERT $ < $862F',1)[0]
final=final.replace('LD HL,$4747',f'LD HL,${int.from_bytes(home[0x58fd:0x58ff],"little"):04X}').replace('LD HL,$4743',f'LD HL,${int.from_bytes(home[0x58ff:0x5901],"little"):04X}')
if procedural_enabled(level):final=' CALL $0060\n'+final
final_code=asm('stock_finalizer','handoff EQU $862F\n ORG $807B\n'+final+'\n ASSERT $ <= $80D0\n')
b[0x807b:0x807b+len(final_code)]=final_code
# Original HOME 5A00 staging bytes must be restored after private boot-stack use.
b[0x9ea0:0x9f20]=home[0x5a00:0x5a80]
# Relocate the complete music grammar to ROM3, freeing permanent ROM1 for kernel.
g=json.loads((R/f'build/fullgame/audio/music_grammar_{level-1}.json').read_text());seg=next(s for s in free if s[0]//8192==3)
def put(data):
 a=seg[0];assert a+len(data)<=seg[1],(len(data),seg);b[a:a+len(data)]=data;seg[0]+=len(data);return a
pairs=put(b''.join(int(a).to_bytes(2,'little')for p in g['pairs']for a in p));sequence=put(b''.join(int(a).to_bytes(2,'little')for a in g['sequence']));frames=[put(bytes(f))for f in g['frames']];directory=put(b''.join(a.to_bytes(2,'little')for a in frames))
s=(R/'src/music_player.asm').read_text();i=s.index('music_byte:');s=s[:i]+'''music_byte:
 CALL $1AA0
 INC HL
 RET
 ASSERT $ <= $9D10
''';defs=f'MUSIC_LEAVES EQU {g["leaves"]}\nMUSIC_DIRECTORY EQU ${directory:04X}\nMUSIC_PAIRS EQU ${pairs:04X}\nMUSIC_SEQUENCE EQU ${sequence:04X}\n';player=asm('stock_music',defs+s);b[0x9c00:0x9d10]=bytes([255])*0x110;b[0x9c00:0x9c00+len(player)]=player
b[0x1aa0:0x1aaa]=bytes.fromhex('3e1bd3f45e3e13d3f4c9');b[0x3a88:0x4000]=bytes([255])*(0x4000-0x3a88)
b[0xfd00:0xfe00]=bytes(int(f'{i:08b}'[::-1],2)for i in range(256))
# This bootstrap-only intermediate has no enemy cache hook yet: never publish it.
p=O/'compressed_kernel_base';p.with_suffix('.rom').write_bytes(b);p.with_suffix('.dck').write_bytes(bytes([0]+[2]*8)+b)
(O/'compressed_kernel_layout.json').write_text(json.dumps(dict(status='Intermediate for native cache integration; original enemy bitmap area reclaimed',packets=packets,free_segments=free,kernel=[0x3a88,0x4000],music=dict(directory=directory,pairs=pairs,sequence=sequence),stock_boot_stack_regions=['BE00-BE1F','5A00-5A7F']),indent=2));print(packets,free)
