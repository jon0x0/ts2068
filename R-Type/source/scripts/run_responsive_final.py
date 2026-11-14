from pathlib import Path
import subprocess,json,hashlib
node=Path('C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
for tail in ['charged_fire','death','title','snake','restart','failures','progression','boss']:
 r=subprocess.run([str(node),'--max-old-space-size=128','--max-semi-space-size=4',f'scripts/verify_responsive_game_{tail}.mjs'],capture_output=True,text=True)
 Path(f'build/fullgame/responsive_game_r50/final_{tail}.log').write_text(r.stdout+r.stderr)
 print(tail,r.returncode,flush=True)
 if r.returncode:print(r.stdout+r.stderr);raise SystemExit(r.returncode)
