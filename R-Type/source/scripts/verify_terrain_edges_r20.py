"""Verify live terrain colours through all eight actual scrolling phases."""
from pathlib import Path
import subprocess,sys,json,argparse
from PIL import Image
from build_graphics import screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--readonly',action='store_true');ap.add_argument('--frame',type=int,default=1200);ap.add_argument('--revision',choices=('r20',));args=ap.parse_args()
 out=ROOT/'build/diagnostics/terrain_motion';out.mkdir(parents=True,exist_ok=True);all_results={}
 for revision in (('rom_r20',) if args.readonly else (args.revision,) if args.revision else ('r20',)):
  results=[];frames=[]
  for phase in range(8):
   label=f'{revision}_terrain';dock=ROOT/('build/readonly_ecm/RType_ECM_ROM_candidate.dck' if args.readonly else f'build/ecm_native/RType_level1_ECM_TSPico_RAM_{revision}.dck')
   p=subprocess.run([sys.executable,str(ROOT/'scripts/probe_ecm.py'),'--frame',str(args.frame),'--joystick-start','--coherent','--scroll-phase',str(phase),'--dck',str(dock),'--label',label]+(['--readonly'] if args.readonly else []),cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr
   stem=f'probe_{args.frame}_joy_phase{phase}_{label}';folder=ROOT/('build/readonly_ecm' if args.readonly else 'build/ecm_native');b=(folder/f'{stem}.bin').read_bytes();back=(folder/f'{stem}.back_attrs.bin').read_bytes();bad=[];cells=0
   for row in range(16,20):
    for col in range(1,31):
     ident=b[0x7e00+row*32+col-0x4000]
     if ident<0xdc and (phase==0 or col==30 or b[0x7e00+row*32+col+1-0x4000]<0xdc):continue
     a=b[0x1800+row*32+col];n=back[row*32+col+1] if col==30 else b[0x1800+row*32+col+1];decode=lambda a,y: (ROOT/'build/art_assets/terrain_palette.bin').read_bytes()[(a&127)*8+y] if a&128 else a;mask=(255<<(phase or 8))&255;actual=[b[8192+screen_offset(row*8+y)+col] for y in range(8)];expected=([decode(back[row*32+col],y) for y in range(8)] if phase==0 else [decode(n,y) for y in range(8)] if ident<0xdc else [decode(a if b[screen_offset(row*8+y)+col]&mask else n,y) for y in range(8)]);cells+=1
     if any(actual[y]!=expected[y] and b[screen_offset(row*8+y)+col] for y in range(8)):bad.append(dict(row=row,col=col,id=ident,expected=expected,actual=actual))
   assert cells>0,(revision,phase)
   results.append(dict(phase=phase,terrain_cells=cells,mismatches=bad,probe=stem));frames.append(Image.open(folder/f'{stem}.png').crop((0,128,256,160)).resize((768,96),Image.Resampling.NEAREST))
  frames[0].save(out/f'{revision}_{args.frame}_terrain_phases.gif',save_all=True,append_images=frames[1:],duration=200,loop=0)
  all_results[revision]=results;print(revision,'mismatched cells across phases:',[len(v['mismatches']) for v in results],flush=True)
 if 'r8' in all_results:assert any(v['mismatches'] for v in all_results['r8']),all_results['r8']
 if 'rom_r20' in all_results:assert not any(v['mismatches'] for v in all_results['rom_r20']),all_results['rom_r20']
 if 'r20' in all_results:assert not any(v['mismatches'] for v in all_results['r20']),all_results['r20']
 (out/f'validation_{args.frame}_{"rom_r20" if args.readonly else args.revision or "r20"}.json').write_text(json.dumps(all_results,indent=2));print('Terrain phase validation passed:', list(all_results))
if __name__=='__main__':main()
