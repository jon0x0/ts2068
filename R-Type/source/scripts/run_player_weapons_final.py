from pathlib import Path
import subprocess,os,hashlib,json
node='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';os.environ.pop('RTYPE_BOSS_LEVELS',None)
out=Path('build/fullgame/player_weapons_r54');initial={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in out.glob('*_region.bin')}
for tail in ['irq','capacity','overlay','world_changes','sweep','native_shots','controls','charged_fire','death','title','snake','restart','failures','progression','boss']:
 r=subprocess.run([node,'--max-old-space-size=128','--max-semi-space-size=4',f'scripts/verify_player_weapons_{tail}.mjs'],capture_output=True,text=True);Path(f'build/fullgame/player_weapons_r54/final_{tail}.log').write_text(r.stdout+r.stderr);print(tail,r.returncode,flush=True)
 if r.returncode:print(r.stdout+r.stderr);raise SystemExit(r.returncode)

assert initial=={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in out.glob("*_region.bin")}
(out/"final_run.json").write_text(json.dumps(dict(passed=True,region_sha256=initial),indent=2))
