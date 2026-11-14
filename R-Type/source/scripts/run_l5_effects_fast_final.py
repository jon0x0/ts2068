from pathlib import Path
import subprocess,json,os,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/l5_effects_fast_r59';NODE=Path('C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
def main():
 freeze={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in OUT.glob('*_region.bin')};(OUT/'frozen_regions.json').write_text(json.dumps(freeze,indent=2));rows=[]
 cases=['fx','components','clipping','irq','game','profile','controls','charged_fire','death','title','snake','failures','rapid_fire','l5_order','restart','progression']
 for name in cases:
  script='scripts/profile_l5_effects_fast.mjs'if name=='profile'else'scripts/verify_l5_effects_fast_'+name+'.mjs';env=os.environ.copy();env['RTYPE_BOSS_LEVELS']='5';print('RUN',name,flush=True)
  r=subprocess.run([str(NODE),'--max-old-space-size=128','--max-semi-space-size=4',script],cwd=ROOT,capture_output=True,text=True,env=env);(OUT/('final_'+name+'.log')).write_text(r.stdout+r.stderr);print(r.stdout[-550:],flush=True);rows.append(dict(case=name,passed=r.returncode==0));(OUT/'final_checks.json').write_text(json.dumps(rows,indent=2))
  assert r.returncode==0,r.stderr[-2500:]
  assert freeze=={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in OUT.glob('*_region.bin')},'Region changed during checks'
 print('ALL PASSED',flush=True)
if __name__=='__main__':main()
