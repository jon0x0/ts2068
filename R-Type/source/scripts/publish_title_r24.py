"""Publish the two level-one candidates after focused title/ROM regression gates."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 motion=json.loads((ROOT/'build/diagnostics/title_delta_r24/validation.json').read_text());assert motion['passed']
 for target,folder,file in [('sram','ecm_native','RType_level1_ECM_TSPico_RAM_r24'),('rom','readonly_ecm','RType_ECM_ROM_candidate')]:
  out=ROOT/'build'/folder;digest=sha(out/(file+'.bin'));assert any(v['target']==target and v['sha256']==digest and v['states']==116 and v['starChecks']>=900000 and v['passed']for v in motion['results'])
  fuse=json.loads((out/'probe_600_r24_text.json').read_text());assert fuse['cartridge_sha256']==digest and fuse['video_mode']==2
  for report in ['music_validation_r24.json','music_toggle_validation_r24.json']:
   values=json.loads((ROOT/'build/audio'/report).read_text());assert any(v['target']==target and v['bin_sha256']==digest and v['passed']for v in values)
  sprite=json.loads((out/('sprite_validation.json'if target=='rom'else'all_sram_validation.json')).read_text());assert sprite['bin_sha256']==digest and sprite['passed']
  if target=='rom':
   runtime=json.loads((out/'runtime_validation.json').read_text());assert runtime['bin_sha256']==digest and runtime['romWrites']==0 and runtime['immutableBanks']and runtime['frames']>=8000 and runtime['updates']>100
   raw=(out/(file+'.bin')).read_bytes();assert len(raw)==65536;assert (out/(file+'.dck')).read_bytes()==bytes([0]+[2]*8)+raw
   name='RType_level1_ECM_64K_PicoROM_r24'
   for ext in ['rom','bin']:(out/(name+'.'+ext)).write_bytes(raw)
   (out/(name+'.dck')).write_bytes((out/(file+'.dck')).read_bytes())
  print(target,digest)
if __name__=='__main__':main()
