from pathlib import Path
import subprocess,json,os,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/boss_motion_r60';NODE=Path('C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
def main():
 frozen={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in OUT.glob('*_region.bin')};(OUT/'frozen_regions.json').write_text(json.dumps(frozen,indent=2));rows=[]
 for name in ['game','components','irq','clipping','fx','profile','controls','charged_fire','death','title','snake','failures','rapid_fire','l5_order','walkers','restart','progression']:
  if os.environ.get('RTYPE_CHECKS') and name not in os.environ['RTYPE_CHECKS'].split(','):continue
  script=f'scripts/verify_boss_motion_{name}_r60.mjs'if name!='profile'else'scripts/profile_boss_motion_r60.mjs';env=os.environ.copy();env['RTYPE_BOSS_LEVELS']='5'if name=='profile'else'1,2,3,4,5,6,7,8';print('RUN',name,flush=True)
  r=subprocess.run([str(NODE),'--max-old-space-size=128','--max-semi-space-size=4',script],cwd=ROOT,capture_output=True,text=True,env=env);(OUT/f'final_{name}.log').write_text(r.stdout+r.stderr);print(r.stdout[-1600:],flush=True);rows.append(dict(case=name,passed=r.returncode==0));(OUT/'final_checks.json').write_text(json.dumps(rows,indent=2));assert r.returncode==0,r.stderr[-2500:];assert frozen=={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in OUT.glob('*_region.bin')}
 print('ALL PASSED',flush=True)
if __name__=='__main__':main()
