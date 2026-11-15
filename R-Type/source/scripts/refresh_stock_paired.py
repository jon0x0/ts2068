"""Refresh paired TAP/cartridge traces; never changes cartridge binaries."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,sys,json,time,os
R=Path(__file__).resolve().parents[1]
NODE='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
levels=list(map(int,sys.argv[1:]))or list(range(1,9))
def run(n):
 for boss in (False,True):
  args=[NODE,'scripts/compare_tap_cartridge.mjs',str(n),'--internal','--seeded','--controls']+(['--boss','--safe']if boss else[])+(['--shield-native']if n==7 else[])
  name=f'level{n:02d}'+('_boss'if boss else'')+'_seeded_candidate'+('_safe'if boss else'')+('_native_shield'if n==7 else'')
  out=R/'build/cartridges/tap_comparison'/name;out.mkdir(parents=True,exist_ok=True)
  with(out/'refresh.log').open('w')as log:
   p=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
  assert p.returncode==0,(n,boss,'process failed')
  result=json.loads((out/'comparison.json').read_text());assert result['passed'],(n,boss,'paired trace failed')
  print('PASS paired',n,'boss'if boss else'early',flush=True)
 return n
with ThreadPoolExecutor(max_workers=max(1,min(4,int(os.environ.get('RTYPE_PAIRED_WORKERS','2')))))as pool:list(pool.map(run,levels))
