"""Build separate native ECM level candidates with their own music and metadata."""
from pathlib import Path
import os,sys,json,subprocess,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
 records=[]
 selected=[int(v)for v in os.environ.get('RTYPE_BUILD_LEVELS','1,2,3,4,5,6,7,8').split(',')]
 previous=json.loads((ROOT/'build/fullgame/ecm_candidates.json').read_text())if (ROOT/'build/fullgame/ecm_candidates.json').exists()else []
 for level in selected:
  env=os.environ.copy();env.update(RTYPE_FULLGAME='1',RTYPE_LEVEL=str(level));out=ROOT/f'build/fullgame/level{level:02d}';out.mkdir(exist_ok=True)
  p=subprocess.run([sys.executable,str(ROOT/'scripts/build_ecm_native.py')],cwd=ROOT,env=env,capture_output=True,text=True);(out/'build.log').write_text(p.stdout+p.stderr)
  if p.returncode:raise RuntimeError(f'Level{level}: '+p.stdout+p.stderr)
  for folder,names in {
   'ecm_native':['RType_level1_ECM_TSPico_RAM.bin','RType_level1_ECM_TSPico_RAM.dck','renderer.bin','renderer.sym','cache_ids.bin','cached_colours.bin','compiled_ship.json','boss_colours.bin','boss_manifest.json'],
   'audio':['music_sram.bin','music_sram.sym','music_layout_sram.json','ay_sram.bin','ay_sram.sym','terrain_groups.bin','music_channel_ownership.bin'],
   'art_assets':['terrain_patches.bin','terrain_palette.bin','terrain_group_full.bin','terrain_groups.json','terrain_group_styles.npy'],
   'native':['snapshot.bin','input.bin']}.items():
   for name in names:
    src=ROOT/'build'/folder/name;dest=out/('game.bin'if name=='RType_level1_ECM_TSPico_RAM.bin'else'game.dck'if name=='RType_level1_ECM_TSPico_RAM.dck'else name);shutil.copy2(src,dest)
  raw=(out/'game.bin').read_bytes();records.append(dict(level=level,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),music_entry=level-1,retained_palette_version=1,status='Native ECM level with its level song and arcade-derived boss assets; controller model validation required'))
  print('Built level',level,records[-1]['sha256'],flush=True)
 (ROOT/'build/fullgame/ecm_candidates.json').write_text(json.dumps(sorted(records+[v for v in previous if v['level']not in selected],key=lambda v:v['level']),indent=2))
if __name__=='__main__':main()
