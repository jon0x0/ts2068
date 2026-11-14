from pathlib import Path
import subprocess,re,struct,json
from build_rocket_fix import block,code
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/diagnostics/native_pixel_movement'
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
    p=subprocess.run([str(asm),f'--raw={OUT/"player.bin"}',f'--sym={OUT/"player.sym"}',str(ROOT/'src/pixel_movement_demo.asm')],cwd=ROOT,capture_output=True,text=True);(OUT/'assembly.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stdout+p.stderr
    def line(n,b):return struct.pack('>H',n)+struct.pack('<H',len(b)+1)+b+b'\r'
    program=line(10,bytes([253,32,176])+b'"32767"')+line(20,bytes([239])+b'"" '+bytes([175]))+line(30,bytes([249,32,192,32,176])+b'"32768"')
    header=bytes([0])+b'PIXEL TEST'+struct.pack('<HHH',len(program),10,len(program))
    (OUT/'Pixel_movement_TS2068.tap').write_bytes(block(0,header)+block(255,program)+code('PIXEL TEST',(OUT/'player.bin').read_bytes(),32768))
    print(OUT/'Pixel_movement_TS2068.tap')
if __name__=='__main__':main()
