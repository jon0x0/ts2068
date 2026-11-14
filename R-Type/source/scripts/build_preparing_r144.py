from pathlib import Path
import shutil,subprocess,sys
R=Path.cwd();B=R/'build/fullgame/score_colour_r143';O=R/'build/fullgame/preparing_r144';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.bin','.asm','.sym','.json'] and not any(k in p.name for k in ['validation','summary','release_manifest']):shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
g={'P':['11110','10001','10001','11110','10000','10000','10000'],'R':['11110','10001','10001','11110','10100','10010','10001'],'E':['11111','10000','10000','11110','10000','10000','11111'],'A':['01110','10001','10001','11111','10001','10001','10001'],'I':['111','010','010','010','010','010','111'],'N':['10001','11001','10101','10011','10001','10001','10001'],'G':['01111','10000','10000','10111','10001','10001','01111'],'L':['10000','10000','10000','10000','10000','10000','11111'],'V':['10001','10001','10001','10001','10001','01010','00100'],' ':['000']*7}
rows=[''.join(g[c][y].ljust(5,'0')+'0'for c in 'PREPARING LEVEL').ljust(96,'0')for y in range(7)];bits=bytes(int(row[x:x+8],2)for row in rows for x in range(0,96,8))
s=''' ORG $DF50
 DI
 XOR A
 OUT ($FE),A
 LD BC,$FFF5
 LD E,8
 LD D,3
mute:
 LD A,E
 OUT (C),A
 INC C
 XOR A
 OUT (C),A
 DEC C
 INC E
 DEC D
 JR NZ,mute
 XOR A
 OUT ($FF),A
 LD ($3FF0),A
 LD HL,$4000
 LD DE,$4001
 LD BC,$17FF
 LD (HL),A
 LDIR
 LD HL,$5800
 LD DE,$5801
 LD BC,767
 LD (HL),$47
 LDIR
 LD HL,pixels
 LD DE,$486A
 LD B,7
row:
 PUSH BC
 LD BC,12
 LDIR
 LD A,E
 SUB 12
 LD E,A
 INC D
 POP BC
 DJNZ row
 JP $DEDB
pixels:
 DB '''+','.join(map(str,bits))+'\n ASSERT $ <= $E000\n'
p=O/'prepare_l7.asm';p.write_text(s);exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';q=subprocess.run([str(exe),f'--raw={O}/prepare_l7.bin',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
v=(O/'prepare_l7.bin').read_bytes();print('wrapper',len(v));b=bytearray((B/'level07_region.bin').read_bytes());assert not any(b[0xdf50:0xe000]);b[0xdf50:0xdf50+len(v)]=v
for start,end in[(0xd4,0xdb),(0xdc0,0xdde)]:
 a=b.find(bytes.fromhex('c3dbde'),start,end);assert a>=0;b[a:a+3]=bytes.fromhex('c350df')
(O/'level07_region.bin').write_bytes(b)
sys.path.insert(0,'scripts');from build_rocket_fix import code
for name in ['LEVEL07.TAP','START07.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[k*8192+t*1024:k*8192+(t+1)*1024]for k in [0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for n in ['launcher.bin','demand_loader.bin']:
 p=O/n;p.write_bytes(p.read_bytes().replace(b'R143',b'R144'))
p=O/'rtype/rt.tap';s=p.read_bytes();a=0;v=bytearray()
while a<len(s):
 n=int.from_bytes(s[a:a+2],'little');q=bytearray(s[a+2:a+2+n]).replace(b'R143',b'R144');q[-1]=0
 for x in q[:-1]:q[-1]^=x
 v+=len(q).to_bytes(2,'little')+q;a+=n+2
p.write_bytes(v)
s=(R/'scripts/boss_motion_fixture_r143.mjs').read_text().replace('score_colour_r143','preparing_r144');(R/'scripts/boss_motion_fixture_r144.mjs').write_text(s)
