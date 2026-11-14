from pathlib import Path
import subprocess,shutil,json,hashlib
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'build/fullgame/detail_motion_r52';OUT=ROOT/'build/fullgame/boss_speed_r53'
def main():
 OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(SRC/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 def asm(name,source):
  r=subprocess.run([str(ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={OUT/(name+".bin")}',f'--sym={OUT/(name+".sym")}',str(ROOT/source)],capture_output=True,text=True,cwd=ROOT);assert r.returncode==0,r.stdout+r.stderr;return(OUT/(name+'.bin')).read_bytes()
 engine=asm('overlay','src/game_pixel_overlay_fullrate.asm');assert len(engine)<=0x980
 irq=asm('irq','src/game_pixel_irq_stack.asm');gateway=asm('gateway','src/game_pixel_gateway_fullrate.asm');shader=asm('compositor','src/bellmite_interruptible.asm');helper=asm('irq_helpers','src/boss_irq_helpers.asm');exit=asm('irq_exit','src/boss_irq_exit.asm');busy=asm('busy_input','src/game_pixel_busy_input.asm');assert len(gateway)<=0xa7
 import re
 shader_syms={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',(OUT/'compositor.sym').read_text(),re.I)}
 copies=[]
 for label,addr,file in [('forward',0x1a6e,'boss_copy_fast'),('reverse',0xf57,'boss_copy_reverse'),('flash',0xfc3,'boss_copy_flash')]:
  generated=OUT/(file+'.asm');generated.write_text(f'FLASH EQU ${shader_syms["flash"]:04X}\nREVERSE_Y EQU ${shader_syms["reverse_y"]:04X}\n'+(ROOT/f'src/{file}.asm').read_text());copies.append((addr,asm(file,generated)))
 records=[]
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  b=bytearray((SRC/f'{name}_region.bin').read_bytes());
  original=bytes(b[0x18d9:0x1937]);ends=[int.from_bytes(original[i+1:i+3],'little')for i in range(len(original)-2)if original[i]==0x11];assert ends[0]==0xc4ce;end=ends[1];pool=ends[2:];assert len(pool) in (0,2)
  retained=0x1906 if pool else 0x18f6
  defines=f'SOURCE_ENEMY_END EQU ${end:04X}\nENEMY_POOL_START EQU ${pool[0]if pool else 0:04X}\nENEMY_POOL_END EQU ${pool[1]if pool else 0:04X}\nRETAINED_ENTRY EQU ${retained:04X}\n'
  generated=OUT/f'{name}_palette.asm';generated.write_text(defines+(ROOT/'src/boss_palette_fast.inc').read_text());palette=asm(name+'_palette',generated);assert len(palette)==144;b[0x18a7:0x1937]=palette;b[0xe400:0xed80]=bytes([255])*0x980;b[0xe400:0xe400+len(engine)]=engine
  b[0xfb00:0xfba7]=bytes([255])*0xa7;b[0xfb00:0xfb00+len(gateway)]=gateway;b[0xfd20:0xfd48]=irq
  assert all(v==255 for v in b[0xe25:0xe40]);b[0xe25:0xe25+len(busy)]=busy
  assert all(v==255 for v in b[0x971:0x990]);b[0x971:0x971+len(exit)]=exit
  if n==5:
   assert all(v==255 for v in b[0x1c8:0x200]);b[0x1c8:0x1c8+len(helper)]=helper;b[0x88eb:0x8c00]=bytes([255])*(0x8c00-0x88eb);b[0x88eb:0x88eb+len(shader)]=shader;b[0x8f00:0x9000]=bytes([0x5b])*256;assert b[0x9000]==0
   for addr,payload in copies:
    assert all(v==255 for v in b[addr:addr+len(payload)]);b[addr:addr+len(payload)]=payload
  if name=='boot':
   assert b[0xdd0c:0xdd0f]==bytes.fromhex('cdee88');b[0xdd0c:0xdd0f]=bytes.fromhex('cdeb88')
   b[0xdb00:0xdbc0]=b[0xfb00:0xfbc0];b[0xdd20:0xdd48]=irq;assert b[0x7e5b:0x7e5e]==bytes.fromhex('c340fd');b[0x7e5b:0x7e5e]=bytes.fromhex('c37109')
   import re
   syms={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',(OUT/'gateway.sym').read_text(),re.I)}
   old={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',(SRC/'gateway.sym').read_text(),re.I)}
   for addr in [0x94f6,0x9563,0x8979,0x8a94,0x8afe,0xc290]:
    at=addr-(0x2000 if addr>=0xc000 else 0x4000);target=int.from_bytes(b[at+1:at+3],'little')
    for key in ['sync_pixel','collision_pixel','copy_pixel']:
     if target==old[key]:b[at+1:at+3]=syms[key].to_bytes(2,'little')
  (OUT/f'{name}_region.bin').write_bytes(b);tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)));records.append(dict(file=tap,level=n,sha256=hashlib.sha256(b).hexdigest()))
 for f in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym']:shutil.copy2(SRC/f,OUT/f)
 (OUT/'manifest.json').write_text(json.dumps(dict(regions=records,status='r53 candidate'),indent=2));print('Built r53 shader',len(shader),'gateway',len(gateway))
if __name__=='__main__':main()
