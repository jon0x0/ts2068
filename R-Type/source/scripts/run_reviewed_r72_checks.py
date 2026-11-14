from pathlib import Path
import subprocess,os,json,hashlib
O=Path('build/fullgame/reviewed_r72');node='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';results=[]
def hashes():return {str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in list(O.glob('*_region.bin'))+list((O/'rtype').glob('*.tap'))+[O/'launcher.bin']}
frozen=hashes();(O/'frozen_primary_hashes.json').write_text(json.dumps(frozen,indent=2))
for name,script,env in [('L3ordinary','verify_l3_play_r72.mjs',{}),('L6ordinary','verify_l6_native_fit_r72.mjs',{}),('jumps4','verify_level_jumps_r72.mjs',{}),('pause2','verify_pause_r72.mjs',{'TEST_LEVEL':'2'}),('keys','verify_key_definition_r72.mjs',{}),('death4','verify_boss_motion_death_r72.mjs',{}),('preload2','verify_preload_title_r72.mjs',{'TEST_LEVEL':'2'}),('force','verify_force_r72.mjs',{}),('rapidfire','verify_rapid_fire_r72.mjs',{})]:
 print('RUN',name,flush=True);p=subprocess.run([node,'--max-old-space-size=128','--max-semi-space-size=4','scripts/'+script],env={**os.environ,**env},capture_output=True,text=True);(O/f'check_{name}.log').write_text(p.stdout+p.stderr);results.append({'case':name,'passed':p.returncode==0});(O/'r72_checks.json').write_text(json.dumps(results,indent=2));print(name,p.returncode,(p.stdout+p.stderr)[-350:],flush=True);assert p.returncode==0;assert hashes()==frozen
