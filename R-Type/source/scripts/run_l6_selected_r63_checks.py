from pathlib import Path
import subprocess,json,hashlib,os
R=Path.cwd();O=R/'build/fullgame/l6_selected_r63';NODE='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
def hashes():
 files=list(O.glob('*_region.bin'))+list((O/'RTYPE').glob('*.TAP'))+[O/'launcher.bin'];return {str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
frozen=hashes();(O/'frozen_r63.json').write_text(json.dumps(frozen,indent=2));results=[]
for name,script,extra in [('L6art','verify_l6_selected_r63.mjs',{}),('controls','verify_boss_motion_controls_r63.mjs',{}),('jumps','verify_level_jumps_r63.mjs',{}),('preload6','verify_preload_all_r63.mjs',{'RTYPE_PRELOAD_LEVEL':'6'}),('death6','verify_l6_death_r63.mjs',{}),('force','verify_force_r63.mjs',{})]:
 print('RUN',name,flush=True);p=subprocess.run([NODE,'--max-old-space-size=128','--max-semi-space-size=4','scripts/'+script],cwd=R,env={**os.environ,**extra},capture_output=True,text=True);(O/f'check_{name}.log').write_text(p.stdout+p.stderr);results.append({'case':name,'passed':p.returncode==0});(O/'current_checks.json').write_text(json.dumps(results,indent=2));print(name,p.returncode,(p.stdout+p.stderr)[-200:],flush=True);assert p.returncode==0;assert hashes()==frozen
print('ALL R63 CHECKS PASSED',flush=True)
