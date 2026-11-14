"""Build a true read-only64KB ECM candidate. Validation gates publication."""
from pathlib import Path
import sys,json,re,subprocess,hashlib,os
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'elite/tmp/pydeps'))
from z80dis.z80 import decode,disasm
from render_optimizations import kernels,patch_kernels

def main():
 out=ROOT/'build/readonly_ecm';out.mkdir(parents=True,exist_ok=True)
 from compiled_ship import HOT
 original=(ROOT/'build/native/snapshot.bin').read_bytes();mem=bytes(0x4000)+original;meta=json.loads((ROOT/'build/spectrum_baseline/postload_checkpoint.json').read_text());cpu=meta['cpu']
 ids=iter((ROOT/'build/ecm_native/cache_ids.bin').read_bytes());gfx=bytearray();address_map={};descriptors=[];cells=[]
 for ident in range(1,112):
  d=0xbc67+(ident-1)*4;w,h=mem[d:d+2];p=int.from_bytes(mem[d+2:d+4],'little');newp=0x2000+len(gfx)
  descriptors.append(bytes([w,h])+newp.to_bytes(2,'little'))
  for y in range(h):
   for x in range(w):
    attr=mem[p];index=next(ids);address_map[p]=0x2000+len(gfx);gfx.append(attr);start=p
    if attr!=0x36:
     gfx.append(index)
     for line in range(8):
      old=p+1+line;address_map[old]=0x2000+len(gfx);value=mem[old]
      if not attr&0x38 and value==255:value=0x55 if line%2==0 else 0xaa
      gfx.append(value)
     p+=9
    else:p+=1
    cells.append(dict(id=ident,old=start,new=address_map[start],attribute=attr,cache_index=index))
 for a in range(0xbc5e,0xbc67):address_map[a]=0x2000+len(gfx);gfx.append(mem[a])
 descriptor_start=0x2000+len(gfx)
 for i,data in enumerate(descriptors):
  for j in range(4):address_map[0xbc67+i*4+j]=descriptor_start+i*4+j
  gfx+=data
 assert len(gfx)<=8192 and len(cells)==786
 def mapped(a):
  if 0x6000<=a<0x7800:return a+0x4600
  return address_map.get(a,a)
 from build_live_art import build as build_art,patch_pixels
 art_frames,art_colours,title_blob,title_plan=build_art(ROOT)
 ram=bytearray(bytes(0x4000)+patch_pixels(ROOT,mem[0x4000:],art_frames));patches=[];pcs=set(int(s.split(':')[0],16) for s in (ROOT/'build/native/reachable_disassembly.txt').read_text().splitlines())
 trace=json.loads((out/'runtime_layout_trace.json').read_text());pcs.update(a for a in trace['pcs'] if 0x73bc<=a<0x7800 or a>=0x85fd or a==0x8383)
 covered=set();high_candidates=[]
 for pc in sorted(pcs):
  if pc<0x4000 or pc in covered or 0xa604<=pc<0xbe23 or 0xc4ae<=pc<0xf800:continue
  ins=decode(mem[pc:],pc)
  if ins.len<1:continue
  covered.update(range(pc+1,pc+ins.len));text=disasm(mem[pc:pc+max(4,ins.len)],pc)
  if ins.len>=3:
   old=int.from_bytes(mem[pc+ins.len-2:pc+ins.len],'little');new=mapped(old)
   if new!=old:
    ram[pc+ins.len-2:pc+ins.len]=new.to_bytes(2,'little');patches.append(dict(pc=pc,instruction=text,old=old,new=new))
  if re.match(r'LD [HD],0x[67][0-9a-f]$',text):high_candidates.append(dict(pc=pc,instruction=text))
 # Typed pointer tables: the startup clear list and IRQ callbacks.
 p=0x75b7
 while mem[p+1]:
  old=int.from_bytes(mem[p:p+2],'little');ram[p:p+2]=mapped(old).to_bytes(2,'little');p+=4
 for i in range(5):
  p=0xbe60+i*5;ram[p:p+2]=mapped(int.from_bytes(mem[p:p+2],'little')).to_bytes(2,'little')
 # F9D8 indexes 35 sound program pointers; entry34 lives in relocated RAM.
 for p in range(0xfc0b,0xfc51,2):
  old=int.from_bytes(mem[p:p+2],'little');ram[p:p+2]=mapped(old).to_bytes(2,'little')
 ram[0xc3ef]=0xa6;ram[0x8ebf]=0xa6
 assert ram[0xff81:0xff83]==bytes.fromhex('cb bf')
 ram[0xff81:0xff83]=b'\x00\x00'
 from ay_integration import patch as patch_ay
 ram=patch_ay(ROOT,ram,True)
 ram[0x8d27:0x8d2a]=bytes.fromhex('cd a2 8e') # compact ROM background uses tokens; cache path remains SRAM-only
 from compiled_ship import build as compile_ship,HOT
 ship_code,ship_table=compile_ship(ROOT,ram[0x4000:],(ROOT/'build/ecm_native/cached_colours.bin').read_bytes(),(ROOT/'build/ecm_native/cache_ids.bin').read_bytes(),address_map)
 ram[0xf8b0:0xf8b0+len(ship_table)]=ship_table

 # Move the existing workspace into RAM released by immutable graphics.
 home=bytearray(ram);home[0xa600:0xbe00]=ram[0x6000:0x7800];home[0x6000:0x7800]=bytes(6144);home[0xbe00:0xbe23]=bytes(35)
 (out/'logical_patched.bin').write_bytes(ram[0x4000:]);(out/'initial_home.bin').write_bytes(home[0x4000:])
 # Assemble input against its relocated original key state.
 input_source=(ROOT/'src/native_input.asm').read_text().replace('$74FC','$BAFC').replace('$74FA','$BAFA')
 (out/'input.asm').write_text(input_source)
 asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
 def assemble(source,name):
  if os.environ.get('RTYPE_TITLE_DELTA')=='1' and source.name=='ecm_rom.asm':
   generated=out/(name+'_delta.asm');generated.write_text('        DEFINE TITLE_DELTA 1\n'+source.read_text());source=generated
  r=subprocess.run([str(asm),f'--raw={out/(name+".bin")}',f'--sym={out/(name+".sym")}',str(source)],cwd=ROOT,capture_output=True,text=True);(out/(name+'.log')).write_text(r.stdout+r.stderr)
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
  symbols={n:int(v,16) for n,v in re.findall(r'(\w+): EQU 0x([0-9A-Fa-f]+)',(out/(name+'.sym')).read_text())};return (out/(name+'.bin')).read_bytes(),symbols
 (out/'animate_orb.asm').write_text('        DEFINE ROM_ONLY 1\n'+(ROOT/'src/animate_orb.asm').read_text())
 initial_terrain_code,_=assemble(ROOT/'src/initial_terrain.asm','initial_terrain')
 (out/'scan_clean_cell.asm').write_text('        DEFINE ROM_ONLY 1\n'+(ROOT/'src/scan_clean_cell.asm').read_text())
 scan_code,_=assemble(out/'scan_clean_cell.asm','scan_clean_cell')
 fast_palette_code,_=assemble(ROOT/'src/terrain_fast.asm','terrain_fast')
 restore_terrain_code,_=assemble(ROOT/'src/restore_terrain_palette.asm','restore_terrain')
 palette_code,_=assemble(ROOT/'src/terrain_palette.asm','terrain_palette')
 orb_code,_=assemble(out/'animate_orb.asm','animate_orb')
 renderer,sym=assemble(ROOT/'src/ecm_rom.asm','renderer');input_code,_=assemble(out/'input.asm','input');kernel_code,kernel_sym=kernels(ROOT)
 assert home[0x8872:0x8875]==bytes.fromhex('da 81 88')
 home[0x8872:0x8875]=bytes.fromhex('da 70 1f')
 home[0x8e02:0x8e05]=bytes([0xc3,kernel_sym['copy_vertical']&255,kernel_sym['copy_vertical']>>8]);home[0x8e5c:0x8e5f]=bytes([0xc3,kernel_sym['copy_vertical_reverse_bits']&255,kernel_sym['copy_vertical_reverse_bits']>>8])
 def hook(pc,old,label,opcode=0xcd):
  assert home[pc:pc+len(bytes.fromhex(old))]==bytes.fromhex(old),(hex(pc),home[pc:pc+4].hex(),old)
  target=sym[label];home[pc:pc+3]=bytes([opcode,target&255,target>>8])
 assert home[0x89c3:0x89c6]==bytes.fromhex('21 00 5e')
 home[0x89c3:0x89c6]=bytes.fromhex('cd 90 09')
 for address in (0x87e3,0x881b):
  assert home[address:address+3]==bytes.fromhex('7e 12 1c');home[address:address+3]=bytes.fromhex('cd f0 0e')
 hook(0xbdd0,'cd f0 fd','title_publish');hook(0xbded,'cd 90 bc','title_scores_restore')
 hook(0x8689,'cd d6 c2','ecm_input');hook(0xc011,'cd 00 1a','ecm_title_input')
 hook(0x8b06,'c3 00 1a','ecm_menu_input',0xc3);hook(0xbd96,'cd c2 b9','ecm_menu_restore')
 hook(0x8ea2,'3a 9c 7a','paint_tile',0xc3);hook(0x8640,'cd c3 86','ecm_game_init')
 hook(0x8cdd,'11 01 78','scroll_background_colour');hook(0x89fb,'7e e6 7f','new_column_colour')
 hook(0x8974,'60 6b c3 69 88','terrain_after_pixel_scroll',0xc3)
 hook(0x8886,'7c c6 20','restore_nonempty_colour');hook(0x88bc,'af 77 24','restore_empty_pixels',0xc3)
 hook(0x88ad,'3e 01 12','mark_dirty');hook(0x88b7,'1a a7 ca','test_dirty',0xc3)
 hook(0xbf11,'0a a7 c0','star_dirty_guard');hook(0xbeea,'0a 0d a7','star_neighbor_dirty')
 hook(0x8854,'01 1e 00','copy_front_colour_row',0xc3)
 for pc,label in ((0x8d5b,'skip_cell_one'),(0x8dc9,'skip_cell_two'),(0x8e1f,'skip_cell_three'),(0x8e7b,'skip_cell_four')):hook(pc,'23 23 23',label,0xc3)
 (out/'initial_home.bin').write_bytes(home[0x4000:])
 # AROS bootstrap: all DOCK banks are ROM. The temporary HOME helper never
 # executes in a mapped source chunk, and disappears before game entry.
 lines=['ORG $8000','DB 2,2','DW entry','DB $EF,1','DW 0','entry: DI','XOR A','OUT ($FF),A']
 for chunk,destination in ((7,0x4000),(3,0xa000),(5,0xc000),(6,0xe000)):
  lines += [f'LD A,${0x10|(1<<chunk):02X}','OUT ($F4),A',f'LD HL,${chunk*8192:04X}',f'LD DE,${destination:04X}','LD BC,$2000','LDIR']
 lines+=['LD A,$10','OUT ($F4),A','LD HL,$8800','LD DE,$7800','LD BC,$800','LDIR','LD HL,helper_image','LD DE,$BE00','LD BC,helper_end-helper','LDIR','JP $BE00','helper_image:','DISP $BE00','helper:','LD A,4','OUT ($F4),A','LD HL,$4000','LD DE,$8000','LD BC,$2000','LDIR','LD A,$13','OUT ($F4),A','JP finalize','helper_end:','ENT','finalize:','LD HL,$BE00','LD DE,$BE01','LD BC,34','LD (HL),0','LDIR']
 for address,key in ((0x58fd,"af'"),(0x58ff,'af')):lines += [f'LD HL,${cpu[key]:04X}',f'LD (${address:04X}),HL']
 lines+=['LD SP,$58FD','POP AF',"EX AF,AF'",'POP AF']
 for address in (0x58fd,0x58ff):lines += [f'LD HL,${int.from_bytes(home[address:address+2],"little"):04X}',f'LD (${address:04X}),HL']
 for reg in ('bc','de','hl'):lines += [f'LD {reg.upper()},${cpu[reg+chr(39)]:04X}']
 lines+=['EXX']
 for reg in ('bc','de','hl','ix','iy','sp'):lines += [f'LD {reg.upper()},${cpu[reg]:04X}']
 lines += [f'LD A,${cpu["i"]:02X}','LD I,A','IM 2','JP handoff','ASSERT $ < $862F','DS $862F-$,$FF','handoff: LD A,3','EI','OUT ($F4),A','ASSERT $ == $8634']
 (out/'boot.asm').write_text('\n'.join(x if ':' in x else '        '+x for x in lines)+'\n');boot,_=assemble(out/'boot.asm','boot')
 rom=bytearray([255]*65536);rom[0x2000:0x2000+len(gfx)]=gfx
 for chunk,source in ((2,0x8000),(3,0xa000),(5,0xc000),(6,0xe000),(7,0x4000)):rom[chunk*8192:(chunk+1)*8192]=home[source:source+8192]
 rom[0x8000:0x8000+len(boot)]=boot;rom[0x8800:0x9000]=home[0x7800:0x8000]
 rom[0x1f70:0x1f70+len(scan_code)]=scan_code
 rom[0x1200:0x1200+len(kernel_code)]=kernel_code;rom[0x1400:0x1400+len(renderer)]=renderer;rom[0x1a00:0x1a00+len(input_code)]=input_code
 colors=(ROOT/'build/ecm_native/cached_colours.bin').read_bytes();rom[0x1b20:0x1b20+len(colors)]=colors
 rom[0x0100:0x0100+len(fast_palette_code)]=fast_palette_code
 rom[0x0f00:0x0f00+len(restore_terrain_code)]=restore_terrain_code
 rom[0x0e00:0x0e00+len(palette_code)]=palette_code
 rom[0x9c00:0xa000]=(ROOT/'build/art_assets/terrain_palette.bin').read_bytes()
 rom[0x0d00:0x0d00+len(orb_code)]=orb_code
 rom[0x1000:0x1000+len(art_frames)]=art_frames
 rom[0x10f0:0x10f4]=bytes([0,1,2,1])
 rom[0x1100:0x1160]=title_plan
 rom[0x1160:0x1160+len(initial_terrain_code)]=initial_terrain_code
 rom[0x9000:0x9c00]=title_blob
 from boss_colours import build as build_boss_colours
 boss_lookup,boss_palette=build_boss_colours(ROOT)
 rom[0x0200:0x0200+len(boss_lookup)]=boss_lookup
 rom[0x0c00:0x0c00+len(boss_palette)]=boss_palette
 rom[0xfb00:0xfd00]=ship_code
 from build_ay_sfx import build as pack_ay
 for address,data in pack_ay(ROOT):rom[address:address+len(data)]=data
 from build_music import build as pack_music
 rom=pack_music(ROOT,rom,True)
 raw=bytes(rom);dck=bytes([0]+[2]*8)+raw
 (out/'RType_ECM_ROM_candidate.bin').write_bytes(raw);(out/'RType_ECM_ROM_candidate.dck').write_bytes(dck)
 report=dict(source_ecm_sha256=hashlib.sha256((ROOT/'build/ecm_native/RType_level1_ECM_TSPico_RAM_r22.bin').read_bytes()).hexdigest(),status='EXPERIMENTAL CANDIDATE; not published as verified PicoROM until true-ROM execution passes',bin_sha256=hashlib.sha256(raw).hexdigest(),descriptors=[2]*8,workspace_old='6000-77FF',workspace_new='A600-BDFF',graphics_rom_bytes=len(gfx),descriptor_start=descriptor_start,renderer_bytes=len(renderer),address_map={str(k):v for k,v in address_map.items()},cells=cells,patches=patches,high_byte_candidates=high_candidates)
 report.update(revision='r22-music-toggle',coverage=dict(playable_levels=[1],native_music_tracks=1,all_arcade_boss_graphics_converted=False),music_control=dict(key='M',default='on',sound_effects_independent=True,resume='current song position'),title=json.loads((ROOT/'build/ecm_native/manifest.json').read_text())['title'],art_manifest='build/art_assets/manifest.json',terrain_profile='arcade warm-metal by default; RTYPE_ART_PROFILE=chroma/preserve retains previous comparisons',limitation='Level one only; arcade-derived terrain textures and three orb cels integrated. Other enemy geometry remains Spectrum-derived; physical hardware untested; 512KB consumers remain staging-only.')
 (out/'manifest.json').write_text(json.dumps(report,indent=2));print('Built read-only candidate',len(renderer),'renderer bytes;',len(patches),'relocations;',len(gfx),'ROM graphics bytes; high-byte candidates',high_candidates)
if __name__=='__main__':main()
