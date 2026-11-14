from pathlib import Path
import subprocess,os,hashlib,json
node='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
os.environ.pop('RTYPE_BOSS_LEVELS',None)
out=Path('build/fullgame/projectile_clock_r55')
initial={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in out.glob('*_region.bin')}
cases=['component','irq','capacity','world_changes','controls','charged_fire','death','title','snake','restart','failures','boss','progression','profile']
for name in cases:
 script='verify_projectile_clock.mjs'if name=='component'else 'profile_projectile_clock.mjs'if name=='profile'else f'verify_projectile_clock_{name}.mjs'
 r=subprocess.run([node,'--max-old-space-size=128','--max-semi-space-size=4','scripts/'+script],capture_output=True,text=True)
 (out/f'final_{name}.log').write_text(r.stdout+r.stderr)
 print(name,r.returncode,flush=True)
 if r.returncode:print(r.stdout+r.stderr);raise SystemExit(r.returncode)
assert initial=={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in out.glob('*_region.bin')}
(out/'final_run.json').write_text(json.dumps(dict(passed=True,region_sha256=initial,cases=cases),indent=2))
