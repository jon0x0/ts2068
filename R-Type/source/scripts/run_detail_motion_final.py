from pathlib import Path
import subprocess
node='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for tail in ['controls','charged_fire','death','title','snake','restart','failures','progression','boss']:
 r=subprocess.run([node,'--max-old-space-size=128','--max-semi-space-size=4','scripts/verify_detail_motion_'+tail+'.mjs'],capture_output=True,text=True);Path('build/fullgame/detail_motion_r52/final_'+tail+'.log').write_text(r.stdout+r.stderr);print(tail,r.returncode,flush=True)
 if r.returncode:print(r.stdout+r.stderr);raise SystemExit(r.returncode)
