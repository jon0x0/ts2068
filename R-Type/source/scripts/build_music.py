from pathlib import Path
import json,subprocess,re,os
def build(root,rom,readonly):
 out=root/'build/audio'
 delta=os.environ.get('RTYPE_TITLE_DELTA')=='1'
 from fullgame_context import FULL,LEVEL
 grammar=root/f'build/fullgame/audio/music_grammar_{LEVEL-1}.json' if FULL else out/'music_grammar.json'
 g=json.loads(grammar.read_text());rom=bytearray(rom);original_rom=bytes(rom)
 from build_ay_sfx import build as effects
 protected_sfx=effects(root)
 free=json.loads((out/'arcade_sfx_packed_r17.json').read_text())['free_segments']
 segments=[free[1].copy(),free[0].copy()]+([[0x80D0,0x862F],[0x8634,0x8800],[0x3A88,0x4000]] if readonly else [[0x84B4,0x862F],[0x8634,0x9000]])+[[0x9EA0,0x9FF0],[0xFE00,0x10000]]
 def put(data):
  seg=next((s for s in segments if s[1]-s[0]>=len(data)),None)
  assert seg is not None,(len(data),segments)
  a=seg[0];seg[0]+=len(data);rom[a:a+len(data)]=data;return a
 pairs=put(b''.join(int(a).to_bytes(2,'little')for p in g['pairs']for a in p))
 sequence=put(b''.join(int(a).to_bytes(2,'little')for a in g['sequence']))
 frames=[put(bytes(f))for f in g['frames']]
 directory=put(b''.join(a.to_bytes(2,'little')for a in frames))

 defines=f'MUSIC_LEAVES EQU {g["leaves"]}\nMUSIC_DIRECTORY EQU ${directory:04X}\nMUSIC_PAIRS EQU ${pairs:04X}\nMUSIC_SEQUENCE EQU ${sequence:04X}\n'
 source=out/('music_rom.asm' if readonly else 'music_sram.asm');source.write_text(defines+(root/'src/music_player.asm').read_text())
 asm=root.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
 p=subprocess.run([str(asm),f'--raw={source.with_suffix(".bin")}',f'--sym={source.with_suffix(".sym")}',str(source)],cwd=root,capture_output=True,text=True);source.with_suffix('.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
 code=source.with_suffix('.bin').read_bytes();assert len(code)<=384;player_length=len(code);rom[0x9c00:0x9c00+len(code)]=code
 init_source=out/('title_screen_init_rom.asm' if readonly else 'title_screen_init_sram.asm')
 init_source.write_text(f'RUNTIME_MAP EQU {3 if readonly else 9}\nMODE_SHADOW EQU ${0xbe00 if readonly else 0x3ff0:04X}\n'+(root/'src/title_screen_init.asm').read_text())
 p=subprocess.run([str(asm),f'--raw={init_source.with_suffix(".bin")}',str(init_source)],cwd=root,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr
 init=init_source.with_suffix('.bin').read_bytes();assert len(init)<=96
 assert all(v==255 for v in rom[0xf20:0xf20+len(init)]),'display initializer reservation'
 rom[0xf20:0xf20+len(init)]=init
 if delta:
  symbols={n:int(v,16)for n,v in re.findall(r'(\w+): EQU 0x([0-9a-fA-F]+)',(out/('ay_rom.sym'if readonly else 'ay_sram.sym')).read_text())}
  text=(root/'src/title_delta.asm').read_text()
  operands=[('DELTA_BASE_OPERAND','delta_base'),('DELTA_COLOUR_OFFSET_OPERAND','delta_colour_offset'),('DELTA_PREFIX_OPERAND','delta_prefix'),('DELTA_COLOUR_BASE_OPERAND','delta_colour_base')]
  text=''.join(f'{name} EQU ${symbols[label]+1:04X}\n'for name,label in operands)+text
  generated=out/('title_delta_rom.asm'if readonly else 'title_delta_sram.asm');generated.write_text(f'RUNTIME_MAP EQU {3 if readonly else 9}\n'+text)
  p=subprocess.run([str(asm),f'--raw={generated.with_suffix(".bin")}',f'--sym={generated.with_suffix(".sym")}',str(generated)],cwd=root,capture_output=True,text=True);assert not p.returncode,p.stdout+p.stderr
  data=generated.with_suffix('.bin').read_bytes();assert len(data)<=400;rom[0x9d10:0x9d10+len(data)]=data
  from build_title_delta import build as delta_atlas
  atlas=delta_atlas(root);rom[0xe400:0xe400+len(atlas)]=atlas
  for filename,address,limit in [('title_star_guard',0x1a0,40),('music_channel_ownership',0xea0,80),('music_toggle',0x11d0,48)]:
   generated=out/(filename+'.bin');p=subprocess.run([str(asm),f'--raw={generated}',str(root/('src/'+filename+'.asm'))],cwd=root,capture_output=True,text=True);assert not p.returncode,p.stdout+p.stderr;data=generated.read_bytes();assert len(data)<=limit;rom[address:address+len(data)]=data
 else:
  for filename,address,limit in [('title_colour_settle',0x1a0,32),('music_channel_ownership',0xea0,80),('music_toggle',0x11d0,48),('title_motion_colour',0x1c8,56),('title_sweep',0x9d10,112)]:
   generated=out/(filename+'.bin')
   p=subprocess.run([str(asm),f'--raw={generated}',str(root/('src/'+filename+'.asm'))],cwd=root,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr
   data=generated.read_bytes();assert len(data)<=limit;rom[address:address+len(data)]=data
  assert len(source.with_suffix('.bin').read_bytes())<=272,'music must end before sweep code'
  assert 'SUB 8' in (root/'src/title_motion_main.asm').read_text(), 'Fine4 atlas is reclaimed; title sweep must stay aligned to8 pixels'
  from build_title_sweep import build as build_sweep
  rom[0x9d80:0x9ea0]=build_sweep(root)[:288] # step8 title uses only aligned phase;336 bytes reclaimed for music
 pub=out/'title_motion_publish.bin' 
 p=subprocess.run([str(asm),f'--raw={pub}',str(root/'src/title_motion_publish.asm')],cwd=root,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr
 code=pub.read_bytes();rom[0x1ac0:0x1ac0+len(code)]=code
 # Data above E000 is read without touching the temporarily hidden stack.
 baseline=3 if readonly else 9
 helper=bytes([0x3e,baseline|0x90,0xd3,0xf4,0x5e,0x3e,baseline|0x10,0xd3,0xf4,0xc9])
 rom[0x1aa0:0x1aa0+len(helper)]=helper
 rom[0x1ab0:0x1abd]=bytes([0x3e,0x13,0xd3,0xf4,0xcd,0x10 if delta else 0x80,0x9d if delta else 0xfc,0x3e,baseline,0xd3,0xf4,0xc9,0x00])
 (out/('music_layout_rom.json' if readonly else 'music_layout_sram.json')).write_text(json.dumps(dict(directory=directory,pairs=pairs,sequence=sequence,player_bytes=player_length,free_segments=segments),indent=2))
 assert rom[0xfb00:0xfe00]==original_rom[0xfb00:0xfe00], 'compiled sprite / bit reversal reservation'
 for address,data in protected_sfx: assert rom[address:address+len(data)]==data, 'effect allocation collision'
 return rom
