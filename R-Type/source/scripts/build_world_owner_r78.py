from pathlib import Path
import shutil,sys,subprocess
R=Path.cwd();B=R/'build/fullgame/startup_bulk_r77';O=R/'build/fullgame/world_owner_r78';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
def helper(origin):
 text=f'        ORG ${origin:04X}\n'+"""        DI
        PUSH IX
        LD IX,$1E30
        LD HL,$7E00
        LD C,20
row:    LD D,(IX+1)
        LD E,(IX+0)
        LD A,E
        AND $E0
        LD E,A
        LD B,32
cell:   PUSH BC
        PUSH DE
        LD B,8
        LD C,0
bits:   LD A,(DE)
        OR C
        LD C,A
        INC D
        DJNZ bits
        POP DE
        LD A,C
        NEG
        SBC A,A
        LD (HL),A
        INC HL
        INC E
        POP BC
        DJNZ cell
        LD DE,16
        ADD IX,DE
        DEC C
        JR NZ,row
        POP IX
        RET
"""
 p=O/('rebuild_'+hex(origin)[2:]+'.asm');p.write_text(text);q=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',str(p)],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr;return p.with_suffix('.bin').read_bytes()
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());start,end=(0xa000,0xa400)if n==5 else(0x3a00,0x3e00);pat=bytes.fromhex('214086e521');at=b.find(pat,start,end);assert at>=0;b[at+1:at+3]=bytes.fromhex('f00c');special=n==5;mapping=0x2b if special else 0x0b;entry=0xa401 if special else 0x3e01;blob=helper(entry);assert len(blob)<=63;assert b[entry-1]==0xc9;b[entry:entry+len(blob)]=blob;assert b[0xd75:0xd7d]==bytes([5])*8;b[0xd75:0xd7d]=bytes.fromhex('3e09d3f4fbc34686');b[0xcf0:0xd00]=bytes.fromhex('cd8514cd2187')+bytes([0x3e,mapping,0xd3,0xf4,0xcd])+entry.to_bytes(2,'little')+bytes.fromhex('c3960d');assert b[0xd96:0xda0]==bytes([5])*10;b[0xd96:0xd9f]=bytes.fromhex('21000022827ac3750d');assert b[0xdc0:0xdc3]==bytes.fromhex('cdf00c');b[0xdc0:0xdc3]=bytes.fromhex('cdc386');p.write_bytes(b)
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))
s=(R/'scripts/boss_motion_fixture_r77.mjs').read_text(encoding='utf-8-sig').replace('startup_bulk_r77','world_owner_r78');(R/'scripts/boss_motion_fixture_r78.mjs').write_text(s,encoding='utf-8')
for stem,ver in [('verify_colour_jumps',76),('verify_boss_game',77),('verify_preload_title',77)]:
 s=(R/f'scripts/{stem}_r{ver}.mjs').read_text(encoding='utf-8-sig').replace(f'boss_motion_fixture_r{ver}','boss_motion_fixture_r78');(R/f'scripts/{stem}_r78.mjs').write_text(s,encoding='utf-8')


player=(O/'overlay_protection.bin').read_bytes();oldplayer=(B/'overlay.bin').read_bytes();assert len(player)<=2432 and all(player[i]==0xc3 for i in[0,3,6,9,12])
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());assert b[0xe400:0xe400+len(oldplayer)]==oldplayer;b[0xe400:0xed80]=player.ljust(2432,b'\xff');p.write_bytes(b)
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))
