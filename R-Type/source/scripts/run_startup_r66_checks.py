from pathlib import Path
import subprocess,os,json
node='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';o=Path('build/fullgame/startup_r66');r=[]
for name,script,env in [('queue3','verify_startup_queue_r66.mjs',{'TEST_LEVEL':'3'}),('queue5','verify_startup_queue_r66.mjs',{'TEST_LEVEL':'5'}),('pause1','verify_pause_r66.mjs',{}),('pause5','verify_pause_r66.mjs',{'TEST_LEVEL':'5'}),('keys','verify_key_definition_r66.mjs',{}),('jumps','verify_level_jumps_r66.mjs',{}),('game_load5','verify_preload_title_r66.mjs',{'TEST_LEVEL':'5'})]:
 p=subprocess.run([node,'--max-old-space-size=128','--max-semi-space-size=4','scripts/'+script],env={**os.environ,'TEST_LEVEL':'1',**env},capture_output=True,text=True);(o/f'check_{name}.log').write_text(p.stdout+p.stderr);r.append({'case':name,'passed':p.returncode==0});(o/'r66_checks.json').write_text(json.dumps(r,indent=2));print(name,p.returncode,(p.stdout+p.stderr)[-350:],flush=True);assert p.returncode==0
