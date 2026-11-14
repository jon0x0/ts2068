from pathlib import Path
import subprocess,json,os
PATCHES={0x9201:11,0x925b:21,0x95e6:3,0x9821:3,0x98c0:15,0x9a4e:5,0x9ad1:2,0x9b93:12,0x9ba5:4,0x9c95:14,0x9cee:19,0x9d67:18,0xa152:10,0xa5c8:13,0xa5ce:4,0xa5d4:11,0xbf9b:17,0xc00c:20,0xc140:6,0xc1f3:13,0xfde2:8}
def patch(root,ram,readonly=False):
 offset=0 if len(ram)==65536 else 0x4000;ram=bytearray(ram);out=root/'build/audio';out.mkdir(exist_ok=True)
 original=bytes(0x4000)+(root/'build/native/snapshot.bin').read_bytes()
 for a,v in PATCHES.items():
  assert original[a-2]==0x21 or original[a-1] in (0x26,0xc6),(hex(a),original[a-2:a+4].hex())
  assert ram[a-offset]==original[a],hex(a)
  ram[a-offset]=v
 delta=os.environ.get('RTYPE_TITLE_DELTA')=='1'
 text=('        DEFINE TITLE_DELTA 1\n'if delta else '')+('        DEFINE ROM_ONLY 1\n' if readonly else '')+(root/'src/ay_sfx.asm').read_text();source=out/('ay_rom.asm' if readonly else 'ay_sram.asm');source.write_text(text)
 assembler=root.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';raw=source.with_suffix('.bin');sym=source.with_suffix('.sym')
 p=subprocess.run([str(assembler),f'--raw={raw}',f'--sym={sym}',str(source)],cwd=root,capture_output=True,text=True);source.with_suffix('.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
 code=raw.read_bytes();ram[0xf87c-offset:0xf87c-offset+len(code)]=code
 assert ram[0xbe2d-offset:0xbe30-offset]==bytes.fromhex('21 8a 7a')
 ram[0xbe2d-offset:0xbe30-offset]=bytes.fromhex('cd 30 f9')
 assert ram[0x8859-offset:0x885c-offset]==bytes.fromhex('7a c6 26')
 ram[0x8859-offset:0x885c-offset]=bytes.fromhex('c3 50 fa')
 assert ram[0x8d27-offset:0x8d2a-offset]==bytes.fromhex('cd a2 8e')
 ram[0x8d27-offset:0x8d2a-offset]=bytes.fromhex('cd 00 fb')
 assert ram[0xbe23-offset:0xbe26-offset]==bytes.fromhex('f5 c5 d5')
 ram[0xbe23-offset:0xbe26-offset]=bytes.fromhex('c3 20 fd')
 assert ram[0xbe5b-offset:0xbe5e-offset]==bytes.fromhex('f1 fb c9')
 ram[0xbe5b-offset:0xbe5e-offset]=bytes.fromhex('c3 40 fd')
 ram[0xfbd0-offset:0xfc50-offset]=(root/'build/art_assets/terrain_palette.bin').read_bytes()[:128]
 if delta:
  assert ram[0xbe97-offset:0xbe9b-offset]==bytes.fromhex('1a 1c 06 01')
  ram[0xbe97-offset:0xbe9a-offset]=bytes.fromhex('c3 a0 01')
 # Replace the original six-glyph animation, preserving its later input entry.
 motion=out/('title_motion_rom.asm' if readonly else 'title_motion_sram.asm')
 motion.write_text(('        DEFINE ROM_ONLY 1\nRUNTIME_MAP EQU 3\nMODE_SHADOW EQU $BE00\n' if readonly else 'RUNTIME_MAP EQU 9\nMODE_SHADOW EQU $3FF0\n')+(root/('src/title_motion_delta_main.asm'if delta else 'src/title_motion_main.asm')).read_text())
 p=subprocess.run([str(assembler),f'--raw={motion.with_suffix(".bin")}',f'--sym={motion.with_suffix(".sym")}',str(motion)],cwd=root,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr
 data=motion.with_suffix('.bin').read_bytes();ram[0x8a4d-offset:0x8a4d-offset+len(data)]=data
 return ram
