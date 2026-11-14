import subprocess,os,json
from pathlib import Path
node='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';out=Path('build/fullgame/hardware_fire_r65');results=[]
for name,script,env in [('pause1','verify_pause_r65.mjs',{}),('pause5','verify_pause_r65.mjs',{'TEST_LEVEL':'5','JOY_SOCKET':'1'}),('load5','verify_preload_title_r65.mjs',{'TEST_LEVEL':'5'}),('controls','verify_controls_r65.mjs',{}),('jumps','verify_level_jumps_r65.mjs',{}),('L3','verify_l3_play_r65.mjs',{})]:
 p=subprocess.run([node,'--max-old-space-size=128','--max-semi-space-size=4','scripts/'+script],env={**os.environ,'TEST_LEVEL':'1',**env},capture_output=True,text=True);(out/f'check_{name}.log').write_text(p.stdout+p.stderr);results.append({'case':name,'passed':p.returncode==0});(out/'r65_checks.json').write_text(json.dumps(results,indent=2));print(name,p.returncode,(p.stdout+p.stderr)[-600:],flush=True);assert p.returncode==0
