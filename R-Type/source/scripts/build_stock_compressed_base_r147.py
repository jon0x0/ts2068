"""Repack true-ROM initial HOME images; preserve the old native finalizer."""
from pathlib import Path
import json,subprocess,re,hashlib
from pack_optimal_r87 import pack_optimal
R=Path.cwd();O=R/'build/cartridges/r147_work';old=(R/'build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r24.rom').read_bytes();b=bytearray(old)
exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
def asm(name,source):
 p=O/(name+'.asm');p.write_text(source);q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
 return p.with_suffix('.bin').read_bytes()
# Reclaim raw initial graphics storage: native selectors will use the new cache.
free=[];packets=[]
for bank,dest in ((7,0x4000),(3,0xa000),(5,0xc000),(6,0xe000),(2,0x8000)):
 raw=bytearray(old[bank*8192:(bank+1)*8192])
 if dest==0xc000:raw[0x4ce:0x17f9]=bytes(0x17f9-0x4ce)
 if dest==0x4000:raw[0x1d00:0x1e00]=bytes(int(f'{i:08b}'[::-1],2)for i in range(256))
 packet=pack_optimal(raw);assert len(packet)<8192
 b[bank*8192:(bank+1)*8192]=bytes([255])*8192;b[bank*8192:bank*8192+len(packet)]=packet
 packets.append(dict(bank=bank,destination=dest,bytes=len(packet),raw_sha256=hashlib.sha256(raw).hexdigest()));free.append([bank*8192+len(packet),(bank+1)*8192])
# Boot-only decoder executes from permanent ROM0; no source mapping hides it.
decoder=asm('stock_unpack', ''' ORG $0000
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
''');b[:0x100]=bytes([255])*256;b[:len(decoder)]=decoder
# Stack remains visible across each source mapping and outside each destination.
lines=[' ORG $8008',' DI',' XOR A',' OUT ($FF),A',' LD SP,$BE20']
for bank,dest in ((7,0x4000),(3,0xa000),(5,0xc000),(6,0xe000),(2,0x8000)):
 if bank==3:lines+=[' LD SP,$5A80']
 if bank==2:lines+=[' LD SP,$BE20']
 lines += [f' LD A,${(0x13|(1<<bank)):02X}',f' LD HL,${bank*8192:04X}',f' LD DE,${dest:04X}',' OUT ($F4),A']+([' LD A,7'] if bank==2 else [])+[' CALL $0000']
lines+=[' LD HL,$8800',' LD DE,$7800',' LD BC,$800',' LDIR',' LD HL,$9EA0',' LD DE,$5A00',' LD BC,128',' LDIR',' JP $807B',' ASSERT $ <= $807B']
boot=asm('stock_compressed_boot','\n'.join(lines));b[0x8008:0x807b]=bytes([255])*(0x807b-0x8008);b[0x8008:0x8008+len(boot)]=boot
# Original HOME 5A00 staging bytes must be restored after private boot-stack use.
b[0x9ea0:0x9f20]=old[0xfa00:0xfa80]
# Relocate the complete music grammar to ROM3, freeing permanent ROM1 for kernel.
g=json.loads((R/'build/audio/music_grammar.json').read_text());seg=next(s for s in free if s[0]//8192==3)
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
