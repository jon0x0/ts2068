from pathlib import Path
import json,hashlib,subprocess
R=Path.cwd();B=R/'build/fullgame/visible_hits_r145';O=R/'build/cartridges/r147_work';O.mkdir(parents=True,exist_ok=True)
p=R/'build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r24.rom';old=p.read_bytes();b=bytearray(old);w=next(q for q in json.loads((B/'walker_runtime.json').read_text())if q['level']==1);raw=(B/'L1_runtime_art.bin').read_bytes();base=w['assets'][0]['pointer'];palette=[];entries=[];frames=[];ram_cursor=0xcee1
for i,n in enumerate(range(176,180)):
 a=next(q for q in w['assets']if q['id']==n);v=raw[a['pointer']-base:a['pointer']-base+a['bytes']];native=bytearray();start=[0,0x80,ram_cursor,ram_cursor][i]if i<2 else ram_cursor
 for cy in range(4):
  for cx in range(4):
   bits=bytes(v[2*(cx*32+cy*8+y)]for y in range(8));attrs=bytes(v[2*(cx*32+cy*8+y)+1]for y in range(8));visible=any(((at&7)and bb)or((at&56)and bb!=255)for bb,at in zip(bits,attrs))
   if not visible:native.append(54);continue
   if attrs not in palette:palette.append(attrs)
   entries.append((start+len(native),palette.index(attrs)));native+=bytes([7])+bits
 if i<2:assert len(native)<=128;assert old[start:start+len(native)]==bytes([255])*len(native);b[start:start+len(native)]=native
 else:
  assert start+len(native)<=0xd00d;b[start-0x2000:start-0x2000+len(native)]=native;ram_cursor+=len(native)
 at=0xd7f9+(30+i-1)*4-0x2000;b[at:at+4]=bytes([4,4])+start.to_bytes(2,'little');frames.append(dict(native_id=30+i,selected_id=n,address=start,bytes=len(native),source_sha256=hashlib.sha256(v).hexdigest()))
assert len(palette)*8<=208 and old[0xd30:0xd30+len(palette)*8]==bytes([255])*(len(palette)*8);b[0xd30:0xd30+len(palette)*8]=b''.join(palette)
# Existing score/title/background logic falls back to its original colour resolver.
fallback=0x18f7
source=f''' ORG $1E20
stock_colour:
 PUSH BC
 PUSH DE
 PUSH IX
 LD D,H
 LD E,L
 LD IX,lookup
 LD B,{len(entries)}
find:
 LD A,(IX+0)
 CP E
 JR NZ,next
 LD A,(IX+1)
 CP D
 JR NZ,next
 LD L,(IX+2)
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,$0D30
 ADD HL,DE
 LD A,(IX+2)
 OR $80
 POP IX
 POP DE
 POP BC
 SCF
 RET
next:
 INC IX
 INC IX
 INC IX
 DJNZ find
 POP IX
 POP DE
 POP BC
 JP ${fallback:04X}
lookup:
'''+''.join(' DW '+str(a)+'\n DB '+str(i)+'\n'for a,i in entries)+' ASSERT $ <= $1F70\n'
p=O/'stock_colour.asm';p.write_text(source);exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';q=subprocess.run([str(exe),f'--raw={O}/stock_colour.bin',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
v=(O/'stock_colour.bin').read_bytes();assert old[0x1e20:0x1e20+len(v)]==bytes([255])*len(v);b[0x1e20:0x1e20+len(v)]=v
pat=bytes([0xcd,fallback&255,fallback>>8]);hits=[]
for a in range(0x1400,0x1a00):
 if old[a:a+3]==pat:b[a:a+3]=bytes.fromhex('cd201e');hits.append(a)
assert hits
# Native joystick input: physical button is raw bit7, not unused bit4.
a=b.find(bytes.fromhex('e61f5f1600'),0x1a00,0x1a6e);assert a>=0;b[a+1]=0x8f
a=b.find(bytes.fromhex('cb632802cbe2'),0x1a00,0x1a6e);assert a>=0;b[a+1]=0x7b
b[0xfd00:0xfe00]=bytes(int(f'{i:08b}'[::-1],2)for i in range(256))
# New rows use a separate retained-token marker; old art keeps its native tokens.
source2=""" ORG $106C
stock_background:
 CALL $1E20
 JP NC,$15B3
 JP P,$15A6
 AND $7F
 LD (DE),A
 CALL $15EC
 OR $20
 LD C,A
 JP $15B9
stock_restore:
 PUSH AF
 PUSH DE
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
 JR Z,legacy
 LD C,A
 LD A,D
 SUB 9
 LD D,A
 LD A,(DE)
 LD E,A
 LD D,0
 SLA E
 RL D
 SLA E
 RL D
 SLA E
 RL D
 PUSH HL
 LD HL,$0D30
 ADD HL,DE
 EX DE,HL
 POP HL
 SET 5,H
 BIT 7,C
 JR Z,forward
 LD A,H
 ADD A,7
 LD H,A
 LD B,8
backward:
 LD A,(DE)
 LD (HL),A
 INC DE
 DEC H
 DJNZ backward
 JR done
forward:
 LD B,8
loop:
 LD A,(DE)
 LD (HL),A
 INC DE
 INC H
 DJNZ loop
done:
 POP DE
 POP AF
 RET
legacy:
 POP DE
 POP AF
 JP $162F
 ASSERT $ <= $10F0
"""
p2=O/'stock_retained.asm';p2.write_text(source2)
q=subprocess.run([str(exe),f'--raw={O}/stock_retained.bin',f'--sym={O}/stock_retained.sym',str(p2)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
import re
symbols={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9A-Fa-f]+)',(O/'stock_retained.sym').read_text())}
v2=(O/'stock_retained.bin').read_bytes();assert old[0x106c:0x106c+len(v2)]==bytes([255])*len(v2);b[0x106c:0x106c+len(v2)]=v2
b[0x15a3:0x15a6]=bytes([0xc3,0x6c,0x10])
for a in (0x160d,0x1615):
 assert b[a]==0xcd and int.from_bytes(b[a+1:a+3],'little')==0x162f
 b[a+1:a+3]=symbols['stock_restore'].to_bytes(2,'little')
# The restore hook must preserve all native registers, including its loop scratch.
# The small outer trampoline saves BC/HL around the new routine.
wrap=O/'stock_restore_wrap.asm';wrap.write_text(f" ORG $01BE\n PUSH BC\n PUSH HL\n CALL ${symbols['stock_restore']:04X}\n POP HL\n POP BC\n RET\n ASSERT $ <= $0200\n")
q=subprocess.run([str(exe),f'--raw={O}/stock_restore_wrap.bin',str(wrap)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
v3=(O/'stock_restore_wrap.bin').read_bytes();assert old[0x1be:0x1be+len(v3)]==bytes([255])*len(v3);b[0x1be:0x1be+len(v3)]=v3
for a in (0x160d,0x1615):b[a+1:a+3]=(0x1be).to_bytes(2,'little')
# Preserve the marker with dirty updates, clear it when replacing with old art.
a=b.find(bytes.fromhex('e63f'),0x15b9,0x15c2);assert a>=0;b[a+1]=0x1f
for a in range(0x1614,0x162f):
 if b[a:a+2]==bytes.fromhex('e6c0'):b[a+1]=0xe0
for a in range(0x16e5,0x16ee):
 if b[a:a+2]==bytes.fromhex('e6c0'):b[a+1]=0xe0
for a in range(0x1745,0x1790):
 if b[a:a+2]==bytes.fromhex('e6c0'):b[a+1]=0xe0
 elif b[a:a+2]==bytes.fromhex('e63f'):b[a+1]=0x1f
p=O/'L1_shell32_stock_prototype';p.with_suffix('.rom').write_bytes(b);p.with_suffix('.dck').write_bytes(bytes([0]+[2]*8)+b)
(O/'prototype_manifest.json').write_text(json.dumps(dict(status='Stock ECM renderer integration prototype; selected L1 shell family only, not full r145 parity',baseline_sha256=hashlib.sha256(old).hexdigest(),rom_sha256=hashlib.sha256(b).hexdigest(),frames=frames,palette_rows=len(palette),lookup_entries=len(entries),colour_code_bytes=len(v),patched_calls=hits,rom_banks=8,writable_dock_banks=0),indent=2));print(frames,len(palette),len(v),hits)
