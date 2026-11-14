"""Expanded-RAM full-game pixel integration candidate, not finalized package."""
from pathlib import Path
import subprocess,json,re,shutil,hashlib
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/pixel_game_r47'
def main():
 source=ROOT/'build/fullgame/bellmite_sparse_r46';OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(source/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
 def assemble(name,file):
  r=subprocess.run([str(asm),f'--raw={OUT/(name+".bin")}',f'--sym={OUT/(name+".sym")}',str(ROOT/file)],cwd=ROOT,capture_output=True,text=True);(OUT/(name+'.log')).write_text(r.stdout+r.stderr);assert not r.returncode,r.stdout+r.stderr;return(OUT/(name+'.bin')).read_bytes()
 irq=assemble('irq','src/game_pixel_irq.asm');engine=assemble('overlay','src/game_pixel_overlay.asm');gateway=assemble('gateway','src/game_pixel_gateway.asm');syms={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',(OUT/'gateway.sym').read_text(),re.I)}
 phases=(ROOT/'build/diagnostics/pixel_movement_trial/ship_phases.bin').read_bytes();records=[]
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  b=bytearray((source/f'{name}_region.bin').read_bytes());gate=bytes(b[0xfbaa:0xfbaa+25]);assert gate[:1]==b'\xf5';assert len(gateway)<=0xa7
  mirror=bytearray([255])*192;mirror[:len(gateway)]=gateway;mirror[0xa7:0xa7+len(gate)]=gate
  assert len(mirror)==192
  b[0xe400:0xe400+len(engine)]=engine;b[0xed80:0xf080]=phases[768:1536];b[0xf080:0xf680]=bytes(1536);b[0xf680:0xfb00]=bytes(0x480);b[0xfb00:0xfbc0]=mirror;b[0xfbc0:0xfbe0]=bytes(32);b[0xfd20:0xfd48]=irq
  if name=='boot':
   def patch(addr,old,new):
    at=addr-(0x2000 if addr>=0xc000 else 0x4000);assert b[at:at+len(old)]==old,(hex(addr),b[at:at+len(old)].hex(),old.hex());b[at:at+len(new)]=new
   def call(addr):return b'\xcd'+addr.to_bytes(2,'little')
   def jump(addr):return b'\xc3'+addr.to_bytes(2,'little')
   b[0xdb00:0xdbc0]=mirror;b[0xdd20:0xdd48]=irq
   patch(0x8ed6,bytes.fromhex('c3 aa 5b 00'),jump(0xfba7)+b'\0')
   patch(0x8d27,call(0xfb00),call(0x8ea2))
   patch(0xbe2d,bytes.fromhex('cd 30 f9'),call(syms['irq_pixel']))
   patch(0x94f6,bytes.fromhex('2a a1 7a'),jump(syms['sync_pixel']))
   patch(0x9560,call(0x99fe),call(0xc07a))
   patch(0x9563,bytes.fromhex('ed 4b a1 7a'),jump(syms['collision_pixel'])+b'\0')
   calls=[]
   for addr in [0x8979,0x8a94,0x8afe,0xc290]:
    at=addr-(0x2000 if addr>=0xc000 else 0x4000)
    if b[at:at+3]==call(0x8842):patch(addr,call(0x8842),call(syms['copy_pixel']));calls.append(addr)
  assert len(b)==65536
  (OUT/f'{name}_region.bin').write_bytes(b);tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)));records.append(dict(file=tap,level=n,sha256=hashlib.sha256(b).hexdigest()))
 for f in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym','native_level5.bin','enemy_palette.bin']:shutil.copy2(source/f,OUT/f)
 (OUT/'manifest.json').write_text(json.dumps(dict(status='Unreleased full-game pixel candidate, validation pending',regions=records,overlay_bytes=len(engine),gateway_bytes=len(gateway),selected_game_keys_preserved=True,fixed_QAOP_only_in_standalone_trial=True),indent=2));print('Candidate built',len(engine),len(gateway))
if __name__=='__main__':main()

