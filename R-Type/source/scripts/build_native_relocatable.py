from pathlib import Path
import json,struct,subprocess,hashlib
from build_rocket_fix import block,code
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/diagnostics/native_relocatable'
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 rows=json.loads((ROOT/'build/diagnostics/delta_benchmark/object_templates.json').read_text());rows=[r for r in rows if r['pose']==3];assert len(rows)==64
 dirs=[(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
 stream=bytearray();ptrs=bytearray()
 for phase in range(8):
  for dx,dy in dirs:
   r=next(r for r in rows if r['phase']==phase and r['dx']==dx and r['dy']==dy);ptrs+=struct.pack('<H',0xa080+len(stream));stream+=bytes(r['stream'])
 assert len(ptrs)==128;assert len(stream)==6618
 (OUT/'pointers.bin').write_bytes(ptrs);(OUT/'streams.bin').write_bytes(stream)
 source=(ROOT/'src/relocatable_delta.asm').read_text().replace('        ORG $8200','').replace('$9000','$8F00').replace('$9100','$8F20');(OUT/'decoder.inc').write_text(source)
 asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
 run=subprocess.run([str(asm),f'--raw={OUT/"player.bin"}',f'--sym={OUT/"player.sym"}',str(ROOT/'src/pixel_movement_relocatable.asm')],cwd=ROOT,capture_output=True,text=True);(OUT/'assembly.log').write_text(run.stdout+run.stderr);assert not run.returncode,run.stdout+run.stderr
 def line(n,b):return struct.pack('>H',n)+struct.pack('<H',len(b)+1)+b+b'\r'
 program=line(10,bytes([253,32,176])+b'"32767"')+line(20,bytes([239])+b'"" '+bytes([175]))+line(30,bytes([249,32,192,32,176])+b'"32768"')
 header=bytes([0])+b'DELTA TEST'+struct.pack('<HHH',len(program),10,len(program));tap=OUT/'Relocatable_delta_QAOP_TS2068.tap';tap.write_bytes(block(0,header)+block(255,program)+code('DELTA TEST',(OUT/'player.bin').read_bytes(),32768))
 (OUT/'manifest.json').write_text(json.dumps(dict(scope='Standalone native relocatable-delta QAOP movement trial; no game enemies, weapons or collision',templates=64,template_bytes=len(stream),pointer_bytes=len(ptrs),tap_sha256=hashlib.sha256(tap.read_bytes()).hexdigest(),physical_validation=False),indent=2))
 (OUT/'README.txt').write_text('Relocatable object-delta trial\n\nLoad Relocatable_delta_QAOP_TS2068.tap. Q up, A down, O left, P right; both native joystick sockets work together with keyboard. One pixel per video refresh, including diagonal movement.\nThis is a standalone native renderer comparison, NOT the full game. No enemies, weapons, collisions or level loading. Black background only; arbitrary scene overlap still needs composition. The sprite is initially drawn once; subsequent movement uses cached relocatable bitmap/ECM XOR transitions. Unchanged pixels are never erased. Release keys to stop. Reset to exit.\n')
 print(tap)
if __name__=='__main__':main()
