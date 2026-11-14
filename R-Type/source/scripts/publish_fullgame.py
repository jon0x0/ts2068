"""Publish only hash-matched, fully validated controller-model candidates."""
from pathlib import Path
import json,hashlib,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'build/fullgame';image=(out/'RType_fullgame_candidate.ram512').read_bytes();digest=sha(image);assert len(image)==524288
 levels=json.loads((out/'ecm_candidates.json').read_text());assert [v['level']for v in levels]==list(range(1,9))
 for v in levels:assert sha((out/f'level{v["level"]:02d}/game.bin').read_bytes())==v['sha256']
 report_names=['boss_validation.json','controls_validation.json','gateway_validation.json','progression_validation.json','ending_validation.json','preloader_validation.json']
 for name in report_names:
  report=json.loads((out/name).read_text());assert report['passed'],name
  if 'sha256'in report:assert report['sha256']==digest,name
  if name=='preloader_validation.json':assert report['loader_sha256']==sha((out/'preloader.bin').read_bytes())
  for v in report.get('results',[]):
   if 'level'in v and ('bin_sha256'in v or 'sha256'in v):assert v.get('bin_sha256',v.get('sha256'))==levels[v['level']-1]['sha256'],name
 music=json.loads((out/'audio/native_validation.json').read_text());assert len(music)==8
 for v in music:assert v['passed']and v['sha256']==levels[v['level']-1]['sha256']
 runtime=json.loads((out/'foundation/ecm_validation.json').read_text());assert len(runtime)==8 and all(v['passed']and v['late_updates']>20 for v in runtime)
 for level in range(1,9):assert not json.loads((out/f'converted/level{level:02d}/manifest.json').read_text())['background_boss_pending']
 delta=__import__('os').environ.get('RTYPE_TITLE_DELTA')=='1';selection=__import__('os').environ.get('RTYPE_LEVEL_SELECT')=='1';retained=all(v.get('retained_palette_version')==1 for v in levels);revision='r27'if retained else'r25'if selection else'r24'if delta else'r23'
 
 if retained:
  check=json.loads((out/'retained_palette_validation.json').read_text());assert check['passed']
  for row in check['results']:assert row['bin_sha256']==levels[row['level']-1]['sha256']
 if selection:
  for report in ['level_select_validation.json','level_select_keyboard_validation.json','boss_selector_validation.json','level_select_page_validation.json']:
   check=json.loads((out/report).read_text());assert check['passed']and check['sha256']==digest
 if delta:
  title=json.loads((ROOT/'build/diagnostics/title_delta_r24/validation_full.json').read_text());assert title['passed']and any(v['target']=='full'and v['sha256']==sha((out/'level01/game_progression.bin').read_bytes())and v['passed']for v in title['results'])
 name='RType_TS2068_ECM_fullgame_TSPico512_'+revision;shutil.copy2(out/'RType_fullgame_candidate.ram512',out/(name+'.ram512'))
 archive=out/(name+'.zip')
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  for p in sorted((out/'package/RTYPE').iterdir()):z.write(p,'RTYPE/'+p.name)
  for name in report_names:z.write(out/name,'validation/'+name)
  
  if selection:
   for level in range(1,9):z.write(out/f'level{level:02d}/game.dck',f'Fuse-level-previews/Level_{level}.dck')
   z.writestr('Fuse-level-previews/README.txt','Open a Level_N.dck and press Fire to test that stage directly, without the512KB SD loader. These are single-level writable-DOCK previews; they do not load the following level after victory. Number-key selection belongs to the full TSPico512 game.\n')
   for report in ['level_select_validation.json','level_select_keyboard_validation.json','boss_selector_validation.json','level_select_page_validation.json']:z.write(out/report,'validation/'+report)
  if delta:z.write(ROOT/'build/diagnostics/title_delta_r24/validation_full.json','validation/title.json')
  if retained:z.write(out/'retained_palette_validation.json','validation/retained_palette.json')
  z.write(out/'audio/native_validation.json','validation/music.json');z.write(out/'foundation/ecm_validation.json','validation/sustained_gameplay.json')
  z.write(ROOT/('docs/fullgame_'+revision+'.md'),'README_fullgame.md')
 record=dict(status='Published emulator/controller-model candidate; hardware untested',image_sha256=digest,package=archive.name,package_sha256=sha(archive.read_bytes()),levels=8,level_music_tracks=8,extra_music_entries_prepared=8,hardware_verified=False,standalone64k_fullgame=False)
 (out/('release_'+revision+'.json')).write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
if __name__=='__main__':main()
