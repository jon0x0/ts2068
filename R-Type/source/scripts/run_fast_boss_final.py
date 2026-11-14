from pathlib import Path
import subprocess
node='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for name in ['verify_fast_boss_compositor','verify_fast_boss_game','verify_compact_boss_game','verify_compact_boss_progression']:
 r=subprocess.run([node,'--max-old-space-size=128','--max-semi-space-size=4','scripts/'+name+'.mjs'],capture_output=True,text=True);Path('build/fullgame/fast_boss_r51/'+name+'.log').write_text(r.stdout+r.stderr);print(name,r.returncode,flush=True)
 if r.returncode:print(r.stdout+r.stderr);raise SystemExit(r.returncode)
