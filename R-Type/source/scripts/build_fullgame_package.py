from pathlib import Path
import struct,json,hashlib,subprocess,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
def block(flag,payload):
 checksum=flag
 for byte in payload:checksum^=byte
 return struct.pack('<H',len(payload)+2)+bytes([flag])+payload+bytes([checksum])
def code(name,data,address):
 header=bytes([3])+name.encode().ljust(10,b' ')+struct.pack('<HHH',len(data),address,0x8000)
 return block(0,header)+block(255,data)
def main():
 out=ROOT/'build/fullgame';package=out/'package/RTYPE';package.mkdir(parents=True,exist_ok=True)
 image=(out/'RType_fullgame_candidate.ram512').read_bytes();assert len(image)==524288
 records=[]
 for volume in range(16):
  data=b''
  for page in range(volume*4,volume*4+4):data+=code(f'RTPAGE{page:02X}',image[page*8192:(page+1)*8192],page)
  name=f'RTFG{volume:02X}.TAP';(package/name).write_bytes(data);records.append(dict(file=name,pages=list(range(volume*4,volume*4+4)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';p=subprocess.run([str(asm),f'--raw={out/"preloader.bin"}',f'--sym={out/"preloader.sym"}',str(ROOT/'src/fullgame_preloader.asm')],cwd=ROOT,capture_output=True,text=True);assert not p.returncode,p.stdout+p.stderr
 player=(out/'preloader.bin').read_bytes();assert len(player)<8192
 tokens={'CLEAR':253,'LOAD':239,'CODE':175,'PAUSE':242,'RANDOMIZE':249,'USR':192,'VAL':176,'STOP':226};kw=lambda name:bytes([tokens[name]])+b' ';val=lambda n:kw('VAL')+f'"{n}"'.encode()
 def line(n,body):return struct.pack('>H',n)+struct.pack('<H',len(body)+1)+body+b'\r'
 program=b''.join(line(n,b)for n,b in [(10,kw('CLEAR')+val(32767)),(20,kw('LOAD')+b'"" '+kw('CODE')),(30,kw('PAUSE')+val(60)),(40,kw('RANDOMIZE')+kw('USR')+val(32768)),(50,kw('STOP'))]);header=bytes([0])+b'RTYPE FULL'.ljust(10,b' ')+struct.pack('<HHH',len(program),10,len(program));tape=block(0,header)+block(255,program)+code('RTYPE LOAD',player,32768);(package/'RTFULL.TAP').write_bytes(tape)
 (package/'README.txt').write_text('R-Type TS2068 full-game integration candidate\n\nCopy the RTYPE folder into the SD card TAP folder. On stock legacy TSPico, load RTFULL.TAP\nwith the normal Timex tape-loading command. The native loader changes to /RTYPE,\nloads all64 SRAM pages and verifies all pages again before starting the game.\nRequires the full512KB SRAM and stock MEMDOCK legacy protocol. M toggles music.\nThis candidate is under emulator validation; physical hardware testing pending.\nEight native levels, eight level songs, arcade-derived boss conversions and the native ending are integrated.\nOriginal enemy movement/AI remains Spectrum-derived. Arcade art is fitted to native geometry; visual refinement remains possible.\nController validation uses diagnostic boss victories and death bypass; it does not prove normal boss difficulty or physical compatibility.\nThe full game requires512KB TSPico SRAM. This is not a64KB PicoROM image.\n')
 import os
 if os.environ.get('RTYPE_LEVEL_SELECT')=='1':
  p=package/'README.txt';p.write_text(p.read_text()+'\nTitle: press1-8 to choose the starting level, then release and press Fire (joystick or keyboard0). The selected level is shown onscreen. Default1.\n')
 (out/'package_manifest.json').write_text(json.dumps(dict(status='Candidate, under integration; no hardware pass claim',image_sha256=hashlib.sha256(image).hexdigest(),preloader_bytes=len(player),pages=64,regions=8,protocol='Stock legacy MEMDOCK, even SRAM slots0..14, eight read-only priming accesses',verification='CODE block XOR plus two8-bit running sums and a complete post-load alias sweep',volumes=records),indent=2));print('Packaged',len(player),'byte native preloader and16 TAP volumes')
if __name__=='__main__':main()
