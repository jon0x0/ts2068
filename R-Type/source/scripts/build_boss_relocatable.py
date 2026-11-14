"""Build a native relocatable Bellmite delta trial from captured native compositions."""
from pathlib import Path
import json,struct,subprocess,hashlib
from PIL import Image,ImageDraw
from build_rocket_fix import block,code
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/diagnostics/boss_relocatable'
def off(y):return((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
def encode(a,b):
 s=bytearray();writes=0
 for y in range(160):
  x=8
  while x<29:
   i=off(y)+x
   if a[i]==b[i]and a[i+6144]==b[i+6144]:x+=1;continue
   first=x;v=bytearray()
   while x<29:
    i=off(y)+x
    if a[i]==b[i]and a[i+6144]==b[i+6144]:break
    bx=a[i]^b[i];ax=a[i+6144]^b[i+6144];v+=bytes([bx,ax]);writes+=bool(bx)+bool(ax);x+=1
   s+=bytes([y,first-8,x-first])+v
 return s+b'\xff',writes

def main():
 frames=[(OUT/f'frame_{i}.bin').read_bytes()for i in range(200,208)]
 streams=bytearray();ptrs=bytearray();records=[]
 for i,(a,b)in enumerate(zip([bytes(12288)]+frames,frames)):
  encoded,writes=encode(a,b);ptrs+=struct.pack('<H',0x8800+len(streams));records.append(dict(pose=i,pointer=0x8800+len(streams),bytes=len(encoded),visible_writes=writes));streams+=encoded
 assert 0x8800+len(streams)<0xf200
 (OUT/'streams.bin').write_bytes(streams);(OUT/'pointers.bin').write_bytes(ptrs)
 asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
 r=subprocess.run([str(asm),f'--raw={OUT/"trial.bin"}',f'--sym={OUT/"trial.sym"}',str(ROOT/'src/boss_relocatable_trial.asm')],cwd=ROOT,capture_output=True,text=True);(OUT/'assembly.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stdout+r.stderr
 def line(n,b):return struct.pack('>H',n)+struct.pack('<H',len(b)+1)+b+b'\r'
 program=line(10,bytes([253,32,176])+b'"32767"')+line(20,bytes([239])+b'"" '+bytes([175]))+line(30,bytes([249,32,192,32,176])+b'"32768"')
 header=bytes([0])+b'BOSS DELTA'+struct.pack('<HHH',len(program),10,len(program));tap=OUT/'Bellmite_relocatable_deltas_TS2068.tap';tap.write_bytes(block(0,header)+block(255,program)+code('BOSS DELTA',(OUT/'trial.bin').read_bytes(),32768))
 manifest=dict(scope='Standalone native cached eight-pose Bellmite cluster trial; not interactive boss gameplay',source='25 captured actor draws per pose, native r49 composition of original poses200..207',width_bytes=21,height=160,original_left=8,streams=records,stream_bytes=len(streams),bidirectional=True,physical_validation=False,tap_sha256=hashlib.sha256(tap.read_bytes()).hexdigest())
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
 (OUT/'README.txt').write_text('Bellmite relocatable boss deltas - native TS2068 trial\n\nLoad Bellmite_relocatable_deltas_TS2068.tap. Keys1/2/3 relocate the entire composed boss cluster to three origins (0,0), (40,16), (88,32). Space pauses/resumes. Reset to exit. The eight consecutive native boss poses play forwards/backwards, reusing the same XOR streams in either direction. This is the boss, not the player. No chosen gameplay keys are changed.\n\nThe25 overlapping parts are composed before encoding using the r49 renderer. Runtime Z80 code updates only changed bitmap/ECM bytes at the selected origin. The trial omits game logic, music, projectiles, collisions and changing backgrounds. Arbitrary boss-part states need composition/fallback. Moving to a new preset clears/reinitializes once; continuous animation uses only deltas. This proves relocation of cached composed boss animation, not arbitrary pixel translation over moving scenery or game integration.\n\nMeasured cycles and tests are in validation.json. Encoding and native composition are excluded from cached publication timings. Memory cost is26587bytes of streams plus16pointers, code and state. This trial fits stock HOME RAM. The full game r49 already contains regular one-pixel player movement.\n',encoding='utf-8')
 print(tap);print('Stream bytes',len(streams))
if __name__=='__main__':main()
