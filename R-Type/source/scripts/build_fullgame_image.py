from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/fullgame';asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
 def assemble(name,defines):
  source=out/(name+'.asm');source.write_text(defines+(ROOT/'src'/(name+'.asm')).read_text());result=subprocess.run([str(asm),f'--raw={out/(name+".bin")}',f'--sym={out/(name+".sym")}',str(source)],cwd=ROOT,capture_output=True,text=True);assert not result.returncode,result.stdout+result.stderr;return(out/(name+'.bin')).read_bytes()
 provisional=assemble('fullgame_transition_tail','DRIVER_LENGTH EQU 0\n')
 gateway=assemble('fullgame_gateway',f'TRAMP_LENGTH EQU {len(provisional)}\n');assert len(gateway)<=400
 tail=assemble('fullgame_transition_tail',f'DRIVER_LENGTH EQU {len(gateway)}\n');assert len(tail)==len(provisional) and len(tail)<=180
 entry=assemble('fullgame_transition_entry',f'DRIVER_LENGTH EQU {len(gateway)}\n');assert len(entry)<=40

 import os,re
 selection=os.environ.get('RTYPE_LEVEL_SELECT')=='1'
 if selection:
  selector=assemble('fullgame_level_select','');assert len(selector)<=256
  selector_symbols={n:int(v,16)for n,v in re.findall(r'(\w+): EQU 0x([0-9a-fA-F]+)',(out/'fullgame_level_select.sym').read_text())}
 image=bytearray();records=[]
 for level in range(1,9):
  folder=out/f'level{level:02d}';game=bytearray((folder/'game.bin').read_bytes());assert game[0xa2a3:0xa2a6]==bytes.fromhex('cd 03 fe');game[0xa2a3:0xa2a6]=bytes.fromhex('cd 08 0a');game[0xa08:0xa08+len(entry)]=entry;game[0xa30:0xa30+len(gateway)]=gateway
  for restart_offset in (0x4631,0x52b8):
   assert game[restart_offset:restart_offset+3]==bytes.fromhex('cd 03 fe')
   game[restart_offset:restart_offset+3]=bytes.fromhex('cd 08 0a')
  assert json.loads((folder/'compiled_ship.json').read_text())['bytes']<=224
  game[0xfbe0:0xfbe0+len(tail)]=tail
  if selection:
   assert not (folder/'boss_colours.bin').read_bytes(),'Full-game dictionaries must use DOCK1, leaving the legacy palette slot unused'
   game[0xc00:0xc00+len(selector)]=selector
   renderer_symbols={n:int(v,16)for n,v in re.findall(r'(\w+): EQU 0x([0-9a-fA-F]+)',(folder/'renderer.sym').read_text())}
   for address,old,label in [(0x463d,bytes.fromhex('cd d8 73'),'select_start'),(0x4a4d,bytes.fromhex('cd 20 0f'),'select_title_init')]:
    assert game[address:address+3]==old,(level,hex(address),game[address:address+3].hex())
    game[address:address+3]=bytes([205])+selector_symbols[label].to_bytes(2,'little')
   assert game[0xa011:0xa014]==bytes([205])+renderer_symbols['ecm_title_input'].to_bytes(2,'little')
   game[0xa011:0xa014]=bytes([195])+selector_symbols['select_dispatch'].to_bytes(2,'little')
   # Numeric5 is now a selector, so skip the legacy menu-only Sinclair1 Fire fallback.
   assert game[0xa01c:0xa01f]==bytes.fromhex('cd 0a 8b')
   game[0xa01c:0xa01f]=bytes.fromhex('c3 27 c0')
   assert game[0xa042:0xa045]==bytes.fromhex('32 fb 74')
   game[0xa042:0xa045]=bytes([205])+selector_symbols['select_arm'].to_bytes(2,'little')
   game[0xdd95:0xdd97]=bytes([1,0])

  (folder/'game_progression.bin').write_bytes(game);(folder/'game_progression.dck').write_bytes(bytes([0,2,3,3,3,2,2,2,2])+game)
  region=bytearray((folder/'runtime_region.bin').read_bytes()) if level>1 else game
  # Runtime chunks1/2/3 are initialized views; all other chunks retain the source image.
  if level>1:
   for bank in [0,4,5,6,7]:region[bank*8192:(bank+1)*8192]=game[bank*8192:(bank+1)*8192]
  (out/f'RType_region{level-1:02d}_slot{(level-1)*2:02d}.bin').write_bytes(region);image+=region;records.append(dict(level=level,region=level-1,slot=(level-1)*2,bytes=len(region),sha256=hashlib.sha256(region).hexdigest()))
 (out/'RType_fullgame_candidate.ram512').write_bytes(image);assert len(image)==524288
 (out/'fullgame_manifest.json').write_text(json.dumps(dict(status='Eight-level arcade-boss ECM candidate; deterministic validation required; physical hardware untested',bytes=len(image),sha256=hashlib.sha256(image).hexdigest(),regions=records,source='Eight ECM level candidates with per-level AY tracks and separate initialized runtime regions',gateway='Temporary HOMEA000 driver, restored viaHOME5E00 tail; stock legacy MEMDOCK even slots and eight selector-priming reads'),indent=2));print('Built eight-region full-game candidate',hashlib.sha256(image).hexdigest())
if __name__=='__main__':main()

