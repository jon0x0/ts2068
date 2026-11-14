from pathlib import Path
import subprocess,os
node='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
os.environ.pop('RTYPE_BOSS_LEVELS',None)
for tail in ['irq','classifier','compact','exact','drawing','overlay','movement','controls','charged_fire','death','title','snake','restart','failures','progression','boss']:
 r=subprocess.run([node,'--max-old-space-size=128','--max-semi-space-size=4',f'scripts/verify_boss_speed_{tail}.mjs'],capture_output=True,text=True);Path(f'build/fullgame/boss_speed_r53/final_{tail}.log').write_text(r.stdout+r.stderr);print(tail,r.returncode,flush=True)
 if r.returncode:print(r.stdout+r.stderr);raise SystemExit(r.returncode)
