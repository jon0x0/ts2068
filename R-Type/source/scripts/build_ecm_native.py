"""Native live ECM shading prototype: writable TSPico DOCK required, not PicoROM."""
from pathlib import Path
import subprocess,json,hashlib,os
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 subprocess.run([__import__('sys').executable,str(ROOT/'scripts/build_native.py'),'--native-input'],cwd=ROOT,check=True)
 out=ROOT/'build/ecm_native';out.mkdir(parents=True,exist_ok=True)
 # Reproduce compatibility fixes without modifying the accepted native output.
 from render_optimizations import kernels,patch_kernels,colour_cache
 kernel_code,kernel_sym=kernels(ROOT)
 from native_compat import patch_input
 from fullgame_context import raw_snapshot,FULL,LEVEL
 ram=raw_snapshot()
 ram,patches=patch_input(ROOT,ram)
 assert ram[0xbf81:0xbf83]==bytes.fromhex('cb bf')
 ram=bytearray(ram);ram[0xbf81:0xbf83]=b'\x00\x00'
 # Separate tile colour publication from input compatibility.
 ram=patch_kernels(ram,kernel_sym)
 from build_live_art import build as build_art,patch_pixels
 art_frames,art_colours,title_blob,title_plan=build_art(ROOT)
 ram=patch_pixels(ROOT,ram,art_frames)
 from ay_integration import patch as patch_ay
 ram=patch_ay(ROOT,ram)
 assert ram[0x4689:0x468c]==bytes.fromhex('cd d6 c2')
 ram[0x4689:0x468c]=bytes.fromhex('cd 00 14')
 # Reuse DOCK1 only after its original payload has been copied into game RAM.
 # Palette bytes are generated before the boot-time cache ID stream.
 rom=bytearray(b'\xff'*65536)
 # Authored shading, not a claim of newly decoded arcade sprite geometry.
 ramps=[
  [5,13,15,15,7,13,5,1,1,1,1,1,1,1,1,1]*2,
  [2,10,6,14,15,15,14,6,14,15,15,14,6,10,2,10,6,14,6,10,2,10,2,2,2,2,2,2,2,2,2,2],
  [4,12,6,14,12,4,12,4]*4,
  [2,10,6,14,10,2,10,2]*4,
  [1,9,3,11,15,11,3,1]*4,
  [1,5,13,15,13,5,1,9]*4,
  [1,9,5,13,9,1,9,1]*4,
  [2,6,14,15,14,6,2,10]*4]
 for family,base in enumerate((12,10,11,13,9,14),2):ramps[family]=[base]*32
 for family,ramp in enumerate(ramps):
  for variant in range(2):
   colors=list(ramp)
   if variant:colors=[(c&7 if family>=2 or i%4==3 else c) for i,c in enumerate(colors)]
   attrs=bytes(((c&7)|((c>=8)<<6)) for c in colors)
   page=2+family*2+variant;rom[page*256:(page+1)*256]=attrs*8
 for ident in range(256):
  family=0 if ident in (2,3,4) else 1 if 0x4b<=ident<=0x57 or ident in (0x5e,0x5f,0x61) else 2+(ident%6)
  rom[ident]=2+family*2
 for ink,family in enumerate((6,6,3,4,2,5,7,0)):rom[0x100+ink]=2+family*2
 for attr in list(range(8))+list(range(0x40,0x48)):
  ink=attr&7;bright=attr&0x40
  cold=(0,5,3,1,6,1,4,5)[ink];hot=(0,2,6,2,6,6,2,6)[ink]
  rom[0x180+attr]=bright|(cold<<3)|ink
  rom[0x108+attr]=bright|(hot<<3)|ink
 (out/'authoring_palette.bin').write_bytes(bytes(rom[:0x1200]))
 colors,cache_ids=colour_cache(ram,rom)
 from compiled_ship import build as compile_ship,HOT
 ship_code,ship_table=compile_ship(ROOT,ram,colors,cache_ids)
 ram[0xb8b0:0xb8b0+len(ship_table)]=ship_table

 (out/'cache_ids.bin').write_bytes(cache_ids)
 (out/'cached_colours.bin').write_bytes(colors)
 boot=(ROOT/'src/native_boot.asm').read_text()
 marker='        LD HL,$'+f'{json.loads((ROOT/"build/spectrum_baseline/postload_checkpoint.json").read_text())["cpu"]["af"+chr(39)]:04X}'
 assert marker in boot
 setup="""        LD A,$94
        OUT ($F4),A
        LD HL,$FB00
        LD DE,$5B00
        LD BC,512
        LDIR
        LD A,$1A
        OUT ($F4),A
        LD HL,$2000
        LD DE,$6000
        LD BC,$2000
        LDIR
        LD A,$12
        OUT ($F4),A
        LD HL,$2000
        LD DE,$2001
        LD BC,$1FFF
        LD (HL),$FF
        LDIR
        LD IY,cache_ids
        LD SP,$3FF0
        LD IX,$BC67
        LD B,111
phase_descriptor:
        PUSH BC
        LD E,(IX+0)
        LD D,(IX+1)
        LD L,(IX+2)
        LD H,(IX+3)
        LD A,E
        AND A
        JR Z,phase_next
        LD A,D
        AND A
        JR Z,phase_next
        LD C,0
phase_row:
        LD B,(IX+0)
        LD E,0
phase_cell:
        PUSH HL
        LD A,H
        AND $1F
        OR $20
        LD H,A
        LD A,E
        AND 1
        RRCA
        OR C
        LD A,(IY+0)
        INC IY
        LD (HL),A
        POP HL
        LD A,(HL)
        INC HL
        CP $36
        JR Z,phase_advance
        AND $38
        JR NZ,phase_skip_pixels
        PUSH BC
        PUSH DE
        LD B,8
phase_pixel:
        LD A,(HL)
        CP $FF
        JR NZ,phase_pixel_next
        PUSH HL
        LD A,H
        AND $1F
        OR $20
        LD H,A
        LD (HL),1          ; originally fully opaque eight-pixel strip
        POP HL
        LD A,B
        AND 1
        LD A,$55
        JR Z,phase_pattern
        LD A,$AA
phase_pattern:
        LD (HL),A          ; fixed texture; paired paper remains foreground
phase_pixel_next:
        INC HL
        DJNZ phase_pixel
        POP DE
        POP BC
        JR phase_advance
phase_skip_pixels:
        LD A,L
        ADD A,8
        LD L,A
        JR NC,phase_advance
        INC H
phase_advance:
        INC E
        DJNZ phase_cell
        LD A,C
        ADD A,8
        LD C,A
        DEC D
        JR NZ,phase_row
phase_next:
        LD DE,4
        ADD IX,DE
        POP BC
        DJNZ phase_descriptor
        XOR A
        LD ($3FF0),A
        LD A,$10
        OUT ($F4),A
"""
 if FULL:
  setup=setup.replace('        XOR A\n        LD ($3FF0),A',"""        LD A,$92
        OUT ($F4),A
        LD HL,$E000
        LD DE,$2000
        LD BC,1024
        LDIR
        LD A,$12
        OUT ($F4),A
        XOR A
        LD ($3FF0),A""")
 boot=boot.replace(marker,setup+marker,1).replace('handoff: LD A,1','handoff: LD A,9')
 boot=boot.replace('        DS $862F-$,$FF','cache_ids: INCBIN "build/ecm_native/cache_ids.bin"\n        DS $862F-$,$FF')
 boot=boot.replace('        DS $862F-$,$FF','        ASSERT $ < $862F\n        DS $862F-$,$FF')
 (out/'ecm_boot.asm').write_text(boot)
 assembler=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
 def assemble(source,name):
  from fullgame_context import FULL,transform
  if FULL:
   generated=out/(name+'_full.asm');generated.write_text(transform(source,source.read_text()));source=generated
  if os.environ.get('RTYPE_TITLE_DELTA')=='1' and name=='renderer':
   generated=out/(name+'_delta.asm');generated.write_text('        DEFINE TITLE_DELTA 1\n'+source.read_text());source=generated
  r=subprocess.run([str(assembler),f'--raw={out/(name+".bin")}',f'--sym={out/(name+".sym")}',str(source)],cwd=ROOT,capture_output=True,text=True)
  (out/(name+'.log')).write_text(r.stdout+r.stderr)
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
  return (out/(name+'.bin')).read_bytes()
 scan_code=assemble(ROOT/'src/scan_clean_cell.asm','scan_clean_cell')
 fast_palette_code=assemble(ROOT/'src/terrain_fast.asm','terrain_fast')
 restore_terrain_code=assemble(ROOT/'src/restore_terrain_palette.asm','restore_terrain')
 palette_code=assemble(ROOT/'src/terrain_palette.asm','terrain_palette')
 orb_code=assemble(ROOT/'src/animate_orb.asm','animate_orb')
 bootcode=assemble(out/'ecm_boot.asm','boot');renderer=assemble(ROOT/'src/ecm_tspico.asm','renderer')
 for src,dst in ((7,2),(1,3),(2,4),(3,5),(5,6),(6,7)):rom[src*8192:(src+1)*8192]=ram[(dst-2)*8192:(dst-1)*8192]
 rom[0x8000:0x8000+len(bootcode)]=bootcode
 native=(ROOT/'build/native/input.bin').read_bytes();rom[0x1a00:0x1a00+len(native)]=native
 rom[0x1f70:0x1f70+len(scan_code)]=scan_code
 rom[0x1200:0x1200+len(kernel_code)]=kernel_code
 rom[0x1400:0x1400+len(renderer)]=renderer
 assert 0x1b20+len(colors)<=0x1e30
 rom[0x1b20:0x1b20+len(colors)]=colors
 from build_graphics import screen_offset
 row_plan=b''.join((0x4002+screen_offset(y)).to_bytes(2,'little') for y in range(160))
 rom[0x1e30:0x1e30+len(row_plan)]=row_plan
 symbols={n:int(v,16) for n,v in __import__('re').findall(r'(\w+): EQU 0x([0-9A-Fa-f]+)',(out/'renderer.sym').read_text())}
 # Menu native input is also an enabled-IRQ mainline call, so guard it explicitly.
 addr=symbols['ecm_menu_input']
 title_addr=symbols['ecm_title_input']
 ram[0x8011:0x8014]=bytes([0xcd,title_addr&255,title_addr>>8])
 ram[0x4b06:0x4b0a]=bytes([0xc3,addr&255,addr>>8,0])
 menu=symbols['ecm_menu_restore']
 assert ram[0x3796:0x3799]==bytes.fromhex('cd c2 73')
 ram[0x3796:0x3799]=bytes([0xcd,menu&255,menu>>8])
 paint=symbols['paint_tile']
 ram[0x4ea2:0x4ea5]=bytes([0xc3,paint&255,paint>>8])
 init=symbols['ecm_game_init']
 assert ram[0x4640:0x4643]==bytes.fromhex('cd c3 86')
 ram[0x4640:0x4643]=bytes([0xcd,init&255,init>>8])
 for address,old,label in ((0x8cdd,'11 01 78','scroll_background_colour'),(0x89fb,'7e e6 7f','new_column_colour')):
  offset=address-0x4000;assert ram[offset:offset+3]==bytes.fromhex(old)
  target=symbols[label];ram[offset:offset+3]=bytes([0xcd,target&255,target>>8])
 assert ram[0x49c3:0x49c6]==bytes.fromhex('21 00 5e')
 ram[0x49c3:0x49c6]=bytes.fromhex('cd 90 09')
 assert ram[0x4974:0x4979]==bytes.fromhex('60 6b c3 69 88')
 target=symbols['terrain_after_pixel_scroll']
 ram[0x4974:0x4977]=bytes([0xc3,target&255,target>>8])
 assert ram[0x4872:0x4875]==bytes.fromhex('da 81 88')
 ram[0x4872:0x4875]=bytes.fromhex('da 70 1f')
 # Hook actual bitmap repairs, never the clean-cell scan.
 assert ram[0x4883:0x4886]==bytes.fromhex('ca b3 88')
 for address,old,label in ((0x8886,'7c c6 20','restore_nonempty_colour'),(0x88bc,'af 77 24','restore_empty_colour')):
  offset=address-0x4000
  assert ram[offset:offset+3]==bytes.fromhex(old)
  target=symbols[label]
  ram[offset:offset+3]=bytes([0xcd,target&255,target>>8])
 rom[0x2000:0x4000]=ram[0x2000:0x4000]
 rom[0x4000:0x6000]=ram[0x4000:0x6000]
 rom[0x6000:0x8000]=ram[0x6000:0x8000]
 rom[0xa000:0xc000]=ram[0x8000:0xa000]
 assert len(native)<=0x118
 assert rom[0x1b18:0x1b20]==b'\xff'*8
 for address in (0x87e3,0x881b):
  offset=address-0x4000;assert ram[offset:offset+3]==bytes.fromhex('7e 12 1c');ram[offset:offset+3]=bytes.fromhex('cd f0 0e')
 rom[0x4000:0x6000]=ram[0x4000:0x6000]
 for address,old,label in ((0x77d0,'cd f0 fd','title_publish'),(0x77ed,'cd 90 76','title_scores_restore')):
  offset=address-0x4000;assert ram[offset:offset+3]==bytes.fromhex(old)
  target=symbols[label];ram[offset:offset+3]=bytes([0xcd,target&255,target>>8])
 rom[0x2000:0x4000]=ram[0x2000:0x4000]
 rom[0x0100:0x0100+len(fast_palette_code)]=fast_palette_code
 rom[0x0f00:0x0f00+len(restore_terrain_code)]=restore_terrain_code
 rom[0x0e00:0x0e00+len(palette_code)]=palette_code
 rom[0x9c00:0xa000]=(ROOT/'build/art_assets/terrain_palette.bin').read_bytes()
 rom[0x0d00:0x0d00+len(orb_code)]=orb_code
 rom[0x1000:0x1000+len(art_frames)]=art_frames
 rom[0x10f0:0x10f4]=bytes([0,1,2,1])
 rom[0x1100:0x1160]=title_plan
 rom[0x9000:0x9c00]=title_blob
 from boss_colours import build as build_boss_colours
 boss_lookup,boss_palette=build_boss_colours(ROOT)
 rom[0x0200:0x0200+len(boss_lookup)]=boss_lookup
 rom[0x0c00:0x0c00+len(boss_palette)]=boss_palette
 if FULL:rom[0xe000:0xe400]=(ROOT/f'build/fullgame/converted/level{LEVEL:02d}/enemy_palette.bin').read_bytes()
 rom[0xfb00:0xfd00]=ship_code
 from build_ay_sfx import build as pack_ay
 for address,data in pack_ay(ROOT):rom[address:address+len(data)]=data
 desc=[2,3,3,3,2,2,2,2]
 from build_music import build as pack_music
 rom=pack_music(ROOT,rom,False)
 raw=bytes(rom);dck=bytes([0]+desc)+raw
 (out/'RType_level1_ECM_TSPico_RAM.dck').write_bytes(dck)
 (out/'RType_level1_ECM_TSPico_RAM.bin').write_bytes(raw)
 for ext,data in (('bin',raw),('dck',dck)):
  from fullgame_context import FULL,LEVEL
  filename=(f'RType_ECM_full_level{LEVEL:02d}.' if FULL else 'RType_level1_ECM_TSPico_RAM_r24.' if os.environ.get('RTYPE_TITLE_DELTA')=='1' else 'RType_level1_ECM_TSPico_RAM_r22.')+ext
  (out/filename).write_bytes(data)
 (out/'manifest.json').write_text(json.dumps(dict(revision='r24-title-delta'if os.environ.get('RTYPE_TITLE_DELTA')=='1'else'r22-music-toggle',coverage=dict(playable_levels=[1],native_music_tracks=1,all_arcade_boss_graphics_converted=False),music_control=dict(key='M',default='on',sound_effects_independent=True,resume='current song position'),bin_sha256=sha(raw),dck_sha256=sha(dck),descriptors=desc,
  runtime_hsr=9,ecm_hsr=3,tile_metadata_hsr=11,renderer_bytes=len(renderer),
  colour_cache=dict(rows=len(colors)//8,bytes=len(colors),indices=len(cache_ids)),
  memory_ownership=dict(hud_staging='HOME7800-787F',hud_history='DOCK2:5800-587F',scroll_stack_save='DOCK1:3FE0-3FE1',scroll_row_plan='ROM0:1E30-1F6F',cached_colours='ROM0:1B20-1E1F',mirror_kernels='ROM0:1200-1253'),
  title=dict(method='Selected arcade-derived 239x39 logo at x4,y101, animated as six coloured glyphs sweeping left and spreading into position; paired offscreen composition replaces the original monochrome animation; protected from star writes until high-score transition.'),
  limitation='Level one only. Arcade-derived terrain interior textures retain native terrain envelope and solid-cell flags; three original arcade orb cels replace one 16x16 enemy. Other enemy geometry remains Spectrum-derived. Physical hardware untested; 512KB assets remain staging-only.'),indent=2))
 print('Built ECM RAM prototype',len(renderer),'renderer bytes',sha(raw))
if __name__=='__main__':main()
