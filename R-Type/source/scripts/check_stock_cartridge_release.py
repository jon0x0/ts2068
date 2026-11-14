"""Fail closed: partial stock-cartridge work must not be packaged as a release."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[1]
def check(path):
 j=json.loads(path.read_text());errors=[]
 if [x.get('level')for x in j.get('levels',[])]!=list(range(1,9)):errors.append('All eight levels are required in order')
 source=R/'build/fullgame/visible_hits_r145'
 for name,want in j.get('source_hashes',{}).items():
  p=source/('RType_TS2068_r145.zip'if name=='expanded_release'else name)
  if not p.exists()or hashlib.sha256(p.read_bytes()).hexdigest()!=want:errors.append('Source baseline changed: '+name)
 required={'current_actor_art','terrain_art_and_scroll_palettes','composite_boss_art_and_animation','current_stock_renderer','one_pixel_player','projectiles_and_visible_collision','native_input_pause_controls','current_audio_and_title','boss_targets_and_recovery','cartridge_loading_instructions','rom_ram_and_interrupt_contracts','cold_gameplay_death_restart'}
 for v in j.get('levels',[]):
  prefix=f'L{v.get("level")}: '
  if set(v.get('requirements',{}))!=required:errors.append(prefix+'Incomplete requirement matrix')
  for key in sorted(required):
   q=v.get('requirements',{}).get(key,{})
   if q.get('passed')is not True:errors.append(prefix+key+' pending');continue
   evidence=q.get('evidence')
   if not isinstance(evidence,dict):errors.append(prefix+key+' missing evidence');continue
   p=R/evidence.get('path','')
   if not p.is_file()or hashlib.sha256(p.read_bytes()).hexdigest()!=evidence.get('sha256'):errors.append(prefix+key+' evidence missing/stale')
  outputs=[]
  for key in ('rom','bin','dck'):
   f=v.get(key)
   if not isinstance(f,dict):errors.append(prefix+key+' missing');continue
   p=R/f.get('path','')
   if not p.is_file():errors.append(prefix+key+' missing file');continue
   b=p.read_bytes()
   if hashlib.sha256(b).hexdigest()!=f.get('sha256'):errors.append(prefix+key+' hash differs')
   outputs.append((key,b))
  out=dict(outputs)
  if 'rom'in out and len(out['rom'])!=65536:errors.append(prefix+'ROM must be exactly 64KB')
  if 'rom'in out and 'bin'in out and out['rom']!=out['bin']:errors.append(prefix+'ROM/BIN differ')
  if 'dck'in out and('rom'not in out or out['dck']!=bytes([0]+[2]*8)+out['rom']):errors.append(prefix+'DCK must contain exactly the ROM with all banks read-only')
 return errors
if __name__=='__main__':
 p=Path(sys.argv[1])if len(sys.argv)>1 else R/'build/cartridges/integration_work/integration_status.json';errors=check(p)
 print(json.dumps(dict(publish_ready=not errors,unmet_count=len(errors),unmet=errors),indent=2));sys.exit(bool(errors))
