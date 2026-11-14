from pathlib import Path
import subprocess,os,json
node='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';o=Path('build/fullgame/l2_rpc_r67');r=[]
cases=[('boss','probe_l2_boss_r67.mjs',{}),('ordinary','probe_l2_fine_scroll_r67.mjs',{}),('jumps','verify_level_jumps_r67.mjs',{}),('pause','verify_pause_r67.mjs',{'TEST_LEVEL':'2'}),('keys','verify_key_definition_r67.mjs',{}),('death','verify_boss_motion_death_r67.mjs',{}),('preload','verify_preload_title_r67.mjs',{'TEST_LEVEL':'2'})]
for name,script,env in cases:
 p=subprocess.run([node,'--max-old-space-size=128','--max-semi-space-size=4','scripts/'+script],env={**os.environ,'TEST_LEVEL':'1',**env},capture_output=True,text=True);(o/f'check_{name}.log').write_text(p.stdout+p.stderr);r.append({'case':name,'passed':p.returncode==0});(o/'r67_checks.json').write_text(json.dumps(r,indent=2));print(name,p.returncode,(p.stdout+p.stderr)[-450:],flush=True);assert p.returncode==0
