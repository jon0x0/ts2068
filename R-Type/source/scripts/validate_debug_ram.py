"""Reproduce and validate the eight-level resident disk cache."""
from pathlib import Path
import json,sys,subprocess,zipfile,functools,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/fullgame/debug_ram_r38'
 if '--finalize-only'not in sys.argv:
  subprocess.run([sys.executable,str(ROOT/'scripts/build_debug_ram.py')],cwd=ROOT,check=True)
  node=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
  for name in ['verify_ram_key.mjs','verify_ram_live.mjs','verify_ram_progression.mjs','verify_ram_restart.mjs','verify_ram_failures.mjs']:
   subprocess.run([str(node),str(ROOT/'scripts'/name)],cwd=ROOT,check=True)
 manifest=json.loads((out/'manifest.json').read_text());progress=json.loads((out/'cache_progression_validation.json').read_text());restart=json.loads((out/'cache_restart_validation.json').read_text());failures=json.loads((out/'failure_validation.json').read_text())
 assert progress['passed']and progress['all8_revisited_without_disk']and progress['cachedVisits']==list(range(1,9))
 assert len(progress['mounts'])==8 and 'LEVEL01.TAP'not in progress['mounts']
 assert len(restart)==2 and all(v['passed']and v['core_and_workspace_checks']==3 and v['max_selector_prime_reads']>8 for v in restart)
 assert len(failures)==4 and all(v['passed']for v in failures)
 pages=0;zipname=out/'RType_TS2068_debug_ram_r38.zip'
 with zipfile.ZipFile(zipname)as z:
  for row in manifest['levels']:
   data=z.read('RTYPE/'+row['file']);at=0;index=0;chunks=[]
   while at<len(data):
    n=int.from_bytes(data[at:at+2],'little');b=data[at+2:at+2+n];assert functools.reduce(int.__xor__,b)==0
    if index%2:assert b[0]==255 and len(b[1:-1])==8192;chunks.append(b[1:-1])
    else:assert b[0]==0 and b[1]==3 and int.from_bytes(b[14:16],'little')==index//2
    at+=n+2;index+=1
   assert index==16;region=b''.join(chunks);assert hashlib.sha256(region).hexdigest()==row['sha256'];pages+=8
   number=1 if row['file']=='RTBOOT.TAP'else int(row['file'][5:7]);assert region[0xd70]==48+number
 assert pages==72
 manifest.update(status='Eight resident-level cache: all8 revisits without disk, restarts, delayed selector readiness and error controls pass; physical confirmation pending',validated_asset_pages=pages,package_sha256=hashlib.sha256(zipname.read_bytes()).hexdigest(),loader_sha256=hashlib.sha256((out/'demand_loader.bin').read_bytes()).hexdigest(),gateway_sha256=hashlib.sha256((out/'demand_gateway.bin').read_bytes()).hexdigest(),all8_revisited_without_disk=True,physical_validation=False,level2_emergence_issue='Mirrored sprite lookup table restored on gameplay initialization; hardware confirmation pending')
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('Resident cache verified:',manifest['package_sha256'])
if __name__=='__main__':main()
