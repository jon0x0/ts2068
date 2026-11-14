"""L1 current actor-art cache on a true-ROM stock HOME layout. Experimental."""
from pathlib import Path
import json,subprocess,re,hashlib
from pack_optimal_r87 import pack_optimal
from boss_motion_assets_r60 import unpack
R=Path.cwd();O=R/'build/cartridges/r147_work';base=(O/'compressed_kernel_base.rom').read_bytes();b=bytearray(base);layout=json.loads((O/'compressed_kernel_layout.json').read_text());j=json.loads((O/'L1_stock_frames.json').read_text());exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
# Rebuild the HOME8000 image after installing its native selector hook.
p=next(p for p in layout['packets']if p['bank']==2);home=bytearray(unpack(base[0x4000:0x4000+p['bytes']]));assert len(home)==8192
home[0xe85:0xe8c]=bytes.fromhex('c3883a00000000')
pkt=pack_optimal(home);assert len(pkt)<8192;b[0x4000:0x6000]=bytes([255])*8192;b[0x4000:0x4000+len(pkt)]=pkt
segments=[s.copy()for s in layout['free_segments']if s[0]//8192 in (2,3,5,6,7)];segments=[([0x4000+len(pkt),0x6000]if s[0]//8192==2 else s)for s in segments]
segments += [[0x80D0,0x862F],[0x8634,0x8800]]
def put(data,banks=None):
 seg=next((s for s in segments if s[1]-s[0]>=len(data)and(banks is None or s[0]//8192 in banks)),None);assert seg is not None,(len(data),segments)
 a=seg[0];seg[0]+=len(data);b[a:a+len(data)]=data;return a
# Palette in one ROM5 window: temporary bank reads never hide HOME6000 or stack.
palette=put(bytes(v for row in j['palette']for v in row),[5]);assert len(j['palette'])<=512
variants=bytes(255 if v['frame']<0 else v['frame']for v in j['variants']);vaddr=put(variants,[6]);daddr=put(bytes(len(j['frames'])*3),[6]);pointers=[None]*len(j['frames']);maxraw=0
for fi,f in sorted(enumerate(j['frames']),key=lambda q:len(q[1]['bits']),reverse=True):
 local=sorted(set(f['rows'])-{-1});assert len(local)<254
 mapping={pi:i+(i>=54) for i,pi in enumerate(local)};local=local[:54]+([0]+local[54:] if len(local)>54 else []);native=bytearray(f['bits']);offset=0
 for pi in f['rows']:
  if pi<0:assert native[offset]==54;offset+=1
  else:native[offset]=mapping[pi];offset+=9
 raw=bytes([f['w'],f['h'],len(local)])+b''.join(pi.to_bytes(2,'little')for pi in local)+native;maxraw=max(maxraw,len(raw));a=put(pack_optimal(raw),[2,3,4,5,7]);pointers[fi]=bytes([3|(1<<(a//8192))])+a.to_bytes(2,'little')
assert 0xc63e+maxraw<0xd7f9
b[daddr:daddr+len(pointers)*3]=b''.join(pointers)
# Small directory is copied to cache RAM on boot? Access it via a ROM window,
# keeping source and private stack visible. Direct ROM reads helper stores byte.
source=f''' ORG $3A88
CTX EQU $C5CE
OLDSP EQU CTX
LASTPI EQU CTX+2
PALPTR EQU CTX+4
BITS EQU CTX+6
TEMP EQU CTX+8
PHASES EQU $C4CE
CACHE EQU $C63E
stock_select:
 PUSH AF
 LD A,I
 PUSH AF
 POP DE
 LD A,E
 AND 4
 LD (CTX+16),A
 POP AF
 DI
 CALL select_inner
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
 LD E,A
 LD D,0
 DEC E
 LD L,E
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD A,IYL
 LD C,A
 LD B,0
 PUSH HL
 LD HL,PHASES
 ADD HL,BC
 LD A,(HL)
 INC (HL)
 AND 3
 ADD A,A
 ADD A,A
 LD C,A
 LD A,(IX+9)
 AND 3
 ADD A,C
 LD C,A
 POP HL
 ADD HL,BC
 LD BC,${vaddr:04X}
 ADD HL,BC
 LD A,${3|(1<<(vaddr//8192)):02X}
 CALL read_byte
 CP 255
 JR Z,empty
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
 LD L,A
 LD H,0
 LD D,H
 LD E,L
 ADD HL,HL
 ADD HL,DE
 LD DE,${daddr:04X}
 ADD HL,DE
 LD A,${3|(1<<(daddr//8192)):02X}
 CALL read_byte
 LD C,A
 INC HL
 LD A,${3|(1<<(daddr//8192)):02X}
 CALL read_byte
 LD E,A
 INC HL
 LD A,${3|(1<<(daddr//8192)):02X}
 CALL read_byte
 LD H,A
 LD L,E
 LD A,C
 LD DE,CACHE
 LD (OLDSP),SP
 LD SP,$C63C
 CALL $000A
 LD SP,(OLDSP)
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
 LD DE,0
 LD HL,CACHE
 POP IX
 POP BC
 RET
read_byte:
 OUT ($F4),A
 LD A,(HL)
 PUSH AF
 LD A,3
 OUT ($F4),A
 POP AF
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
 LD BC,$D7F9
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
 CP $C5
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
 ASSERT $ <= $4000
'''
p=O/'stock_actor_kernel.asm';p.write_text(source);q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
sym={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9A-Fa-f]+)',p.with_suffix('.sym').read_text())};code=p.with_suffix('.bin').read_bytes();b[0x3a88:0x3a88+len(code)]=code
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
a=b.find(bytes.fromhex('e61f5f1600'),0x1a00,0x1a6e);assert a>=0;b[a+1]=0x8f
a=b.find(bytes.fromhex('cb632802cbe2'),0x1a00,0x1a6e);assert a>=0;b[a+1]=0x7b
p=O/'L1_actor_cache_experimental';p.with_suffix('.rom').write_bytes(b);p.with_suffix('.dck').write_bytes(bytes([0]+[2]*8)+b)
(O/'actor_cache_layout.json').write_text(json.dumps(dict(status='Experimental current actor-art integration; full gameplay parity unverified',frames=len(j['frames']),palette_rows=len(j['palette']),max_frame_cache_bytes=maxraw,kernel_bytes=len(code),palette=palette,variants=vaddr,directory=daddr,free_segments=segments,symbols=sym),indent=2));print('Built',len(code),maxraw,segments)
