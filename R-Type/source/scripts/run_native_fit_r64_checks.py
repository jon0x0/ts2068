from pathlib import Path
import subprocess,json,hashlib,os
R=Path.cwd();O=R/'build/fullgame/native_fit_r64';NODE='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
def hashes():
 files=list(O.glob('*_region.bin'))+list((O/'RTYPE').glob('*.TAP'))+[O/'launcher.bin'];return{str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
frozen=hashes();(O/'frozen_r64.json').write_text(json.dumps(frozen,indent=2));results=[]
for name,script,extra in [('title1','verify_title_preload_r64.mjs',{'TEST_LEVEL':'1'}),('title5','verify_title_preload_r64.mjs',{'TEST_LEVEL':'5'}),('bolts','verify_bolt_redraw_r64.mjs',{}),('projectiles','verify_projectiles_r64.mjs',{}),('L6art','verify_l6_native_fit_r64.mjs',{}),('L7art','verify_l7_art_r64.mjs',{}),('L3play','verify_l3_play_r64.mjs',{}),('controls','verify_controls_r64.mjs',{}),('jumps','verify_level_jumps_r64.mjs',{}),('preload6','verify_preload_all_r64.mjs',{'RTYPE_PRELOAD_LEVEL':'6'}),('preload5','verify_preload_all_r64.mjs',{'RTYPE_PRELOAD_LEVEL':'5'}),('death6','verify_l6_death_r64.mjs',{}),('force','verify_force_r64.mjs',{}),('rapidfire','verify_rapid_fire_r64.mjs',{})]:
 print('RUN',name,flush=True);p=subprocess.run([NODE,'--max-old-space-size=128','--max-semi-space-size=4','scripts/'+script],cwd=R,env={**os.environ,**extra},capture_output=True,text=True);(O/f'check_{name}.log').write_text(p.stdout+p.stderr);results.append({'case':name,'passed':p.returncode==0});(O/'current_checks.json').write_text(json.dumps(results,indent=2));print(name,p.returncode,(p.stdout+p.stderr)[-400:],flush=True);assert p.returncode==0;assert hashes()==frozen
print('ALL R64 CHECKS PASSED',flush=True)
