"""Rebuild/test/publish the demand-loader candidate without firmware changes."""
from pathlib import Path
import sys,subprocess,json,zipfile,hashlib,functools
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/fullgame/per_level_r33'
 if '--finalize-only'not in sys.argv:
  subprocess.run([sys.executable,str(ROOT/'scripts/build_demand_disk.py')],cwd=ROOT,check=True)
  node=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
  for script in ['verify_demand_disk.mjs','verify_demand_selection.mjs','verify_demand_failures.mjs']:
   subprocess.run([str(node),str(ROOT/'scripts'/script)],cwd=ROOT,check=True)
 manifest=json.loads((out/'manifest.json').read_text());progress=json.loads((out/'progression_validation.json').read_text());selection=json.loads((out/'selection_restart_validation.json').read_text());failures=json.loads((out/'failure_validation.json').read_text())
 assert progress['passed']and progress['all_levels']and progress['ending_restart']
 assert progress['initial']['mounts']==['RTBOOT.TAP']and progress['initial']['blocks']==16
 assert len(selection)==3 and all(v['passed']and v['gameover_restart']for v in selection)
 assert len(failures)==4 and all(v['passed']for v in failures)
 parsed=0
 with zipfile.ZipFile(out/'RType_TS2068_per_level_r33.zip')as archive:
  for record in manifest['levels']:
   data=archive.read('RTYPE/'+record['file']);at=0;chunks=[];index=0
   while at<len(data):
    n=int.from_bytes(data[at:at+2],'little');b=data[at+2:at+n+2];assert functools.reduce(int.__xor__,b)==0
    if index%2:assert b[0]==255 and len(b[1:-1])==8192;chunks.append(b[1:-1])
    else:assert b[0]==0 and b[1]==3 and int.from_bytes(b[14:16],'little')==index//2
    at+=n+2;index+=1
   assert index==16 and hashlib.sha256(b''.join(chunks)).hexdigest()==record['sha256'];parsed+=8
 assert parsed==72
 manifest.update(status='Per-level candidate: startup,8-level disk progression, ending, selected restarts and error controls pass; physical confirmation pending',validated_asset_pages=72,loader_sha256=hashlib.sha256((out/'demand_loader.bin').read_bytes()).hexdigest(),gateway_sha256=hashlib.sha256((out/'demand_gateway.bin').read_bytes()).hexdigest(),package_sha256=hashlib.sha256((out/'RType_TS2068_per_level_r33.zip').read_bytes()).hexdigest(),validation=dict(startup_level_only=True,nested_current_directory=progress['current_directory'],all_level_progression=True,ending_restart=True,selected_gameover_restart=[v['level']for v in selection],negative_controls=[v['kind']for v in failures],idle_title_prefetch=False))
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('Validated demand disk:',manifest['package_sha256'])
if __name__=='__main__':main()
