from pathlib import Path
import sys,shutil,json,re,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
BASE=R/'build/fullgame/native_fit_r64';OUT=R/'build/fullgame/hardware_fire_r65'
def main():
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'rtype').mkdir(exist_ok=True)
 for p in BASE.iterdir():
  if p.is_file() and(p.suffix in['.bin','.asm','.sym']or p.name in['global_tags.json','generic_manifest.json','l7_art_manifest.json','r64_contracts.json']):shutil.copy2(p,OUT/p.name)
 for p in (BASE/'RTYPE').iterdir():
  if p.is_file():(OUT/'rtype'/('rt.tap'if p.name=='RTFULL.TAP'else p.name)).write_bytes(p.read_bytes())
 def assemble(name,source):
  p=OUT/(name+'.asm');p.write_text(source);q=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],cwd=R,capture_output=True,text=True);p.with_suffix('.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stdout+q.stderr;return p.with_suffix('.bin').read_bytes()
 old=assemble('native_input_before',(R/'src/native_input.asm').read_text());new=assemble('native_input',(R/'src/native_input_r65.asm').read_text());assert len(old)==len(new);changes=[i for i,(a,b)in enumerate(zip(old,new))if a!=b];assert len(changes)==2 and all(i<0x6e for i in changes)
 for name in ['boot']+[f'level{n:02d}'for n in range(1,9)]:
  b=bytearray((BASE/f'{name}_region.bin').read_bytes())
  for i in changes:assert b[0x1a00+i]==old[i];b[0x1a00+i]=new[i]
  (OUT/f'{name}_region.bin').write_bytes(b)
 for n in range(1,9):
  b=(OUT/f'level{n:02d}_region.bin').read_bytes();(OUT/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)));(OUT/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+s*1024:p*8192+(s+1)*1024],k)for k,(p,s)in enumerate((p,s)for p in[0,1,4,5,6,7]for s in range(8))))
 (OUT/'fire_contract.json').write_text(json.dumps({'physical_fire_bit':7,'native_fire_output_bit':4,'significant_input_mask':'8F','changes':[hex(0x1a00+i)for i in changes],'folder':'rtype','launcher':'rt.tap','internal_data_filenames':'unchanged uppercase; relative paths'},indent=2));print('Patched',[(hex(0x1a00+i),old[i],new[i])for i in changes])
if __name__=='__main__':main()
