"""Verify live terrain colours through all eight actual scrolling phases."""
from pathlib import Path
import subprocess,sys,json,argparse
from PIL import Image
from build_graphics import screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--readonly',action='store_true');ap.add_argument('--frame',type=int,default=1200);ap.add_argument('--revision',choices=('r8','r9'));args=ap.parse_args()
 out=ROOT/'build/diagnostics/terrain_motion';out.mkdir(parents=True,exist_ok=True);all_results={}
 for revision in (('rom',) if args.readonly else (args.revision,) if args.revision else ('r8','r9')):
  results=[];frames=[]
  for phase in range(8):
   label=f'{revision}_terrain';dock=ROOT/('build/readonly_ecm/RType_ECM_ROM_candidate.dck' if args.readonly else f'build/ecm_native/RType_level1_ECM_TSPico_RAM_{revision}.dck')
   p=subprocess.run([sys.executable,str(ROOT/'scripts/probe_ecm.py'),'--frame',str(args.frame),'--joystick-start','--coherent','--scroll-phase',str(phase),'--dck',str(dock),'--label',label]+(['--readonly'] if args.readonly else []),cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr
   stem=f'probe_{args.frame}_joy_phase{phase}_{label}';folder=ROOT/('build/readonly_ecm' if args.readonly else 'build/ecm_native');b=(folder/f'{stem}.bin').read_bytes();bad=[];cells=0
   for row in range(16,20):
    for col in range(1,31):
     ident=b[0x7e00+row*32+col-0x4000]
     if ident<0xdc:continue
     expected=b[0x1800+row*32+col]&127;actual=[b[8192+screen_offset(row*8+y)+col] for y in range(8)];cells+=1
     if actual!=[expected]*8:bad.append(dict(row=row,col=col,id=ident,expected=expected,actual=actual))
   assert cells>0,(revision,phase)
   results.append(dict(phase=phase,terrain_cells=cells,mismatches=bad,probe=stem));frames.append(Image.open(folder/f'{stem}.png').crop((0,128,256,160)).resize((768,96),Image.Resampling.NEAREST))
  frames[0].save(out/f'{revision}_{args.frame}_terrain_phases.gif',save_all=True,append_images=frames[1:],duration=200,loop=0)
  all_results[revision]=results;print(revision,'mismatched cells across phases:',[len(v['mismatches']) for v in results],flush=True)
 if 'r8' in all_results:assert any(v['mismatches'] for v in all_results['r8']),all_results['r8']
 if 'rom' in all_results:assert not any(v['mismatches'] for v in all_results['rom']),all_results['rom']
 if 'r9' in all_results:assert not any(v['mismatches'] for v in all_results['r9']),all_results['r9']
 (out/f'validation_{args.frame}_{"rom" if args.readonly else args.revision or "both"}.json').write_text(json.dumps(all_results,indent=2));print('Terrain phase validation passed:', list(all_results))
if __name__=='__main__':main()
