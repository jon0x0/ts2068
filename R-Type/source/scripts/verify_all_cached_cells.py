"""Execute every nonempty sprite cell, all mirrors/IFF states, both destinations."""
from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 reports=[]
 for base in ('0x40','0x60'):
  for start in range(0,617,16):
   p=subprocess.run([sys.executable,str(ROOT/'scripts/verify_ecm_renderer.py'),'--bitmap-base',base,'--all-cells','--cell-start',str(start)],cwd=ROOT,capture_output=True,text=True)
   if p.returncode:raise RuntimeError(p.stdout+p.stderr)
   report=json.loads((ROOT/f'build/ecm_native/tile_cpu_{int(base,0):02x}_all_{start:03d}.json').read_text());reports.append(report)
  print('Verified all617 cells for bitmap base',base,flush=True)
 total=sum(x['cases'] for x in reports);assert total==617*4*2*2,total
 (ROOT/'build/optimized/all_cached_cells.json').write_text(json.dumps(dict(cases=total,passed=True,reports=len(reports)),indent=2));print('All',total,'cached-cell CPU cases pass')
if __name__=='__main__':main()
