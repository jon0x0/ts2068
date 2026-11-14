from pathlib import Path
import subprocess,os,json
node='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';o=Path('build/fullgame/hardware_fire_r65');r=[]
for name,script,env in [('keys1','verify_key_definition_r65.mjs',{}),('keys5','verify_key_definition_r65.mjs',{'TEST_LEVEL':'5'}),('resident5','verify_resident_title_r65.mjs',{'TEST_LEVEL':'5'}),('rapidfire','verify_joystick_fire_r65.mjs',{}),('boundP','verify_pause_bound_r65.mjs',{}),('plainP','verify_pause_plain_r65.mjs',{})]:
 p=subprocess.run([node,'--max-old-space-size=128','--max-semi-space-size=4','scripts/'+script],env={**os.environ,'TEST_LEVEL':'1',**env},capture_output=True,text=True);(o/f'check_{name}.log').write_text(p.stdout+p.stderr);r.append({'case':name,'passed':p.returncode==0});(o/'r65_extra_checks.json').write_text(json.dumps(r,indent=2));print(name,p.returncode,(p.stdout+p.stderr)[-350:],flush=True);assert p.returncode==0
