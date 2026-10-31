"""Assemble either release player, or a generated player, and wrap it in TAP."""
from pathlib import Path
import argparse,os,shutil,struct,subprocess
def tap_block(flag,payload):
 check=flag
 for value in payload:check^=value
 return struct.pack('<H',len(payload)+2)+bytes([flag])+payload+bytes([check])
ROOT=Path(__file__).resolve().parents[1]
# Timex BASIC token values used by the hardware-tested wrapper.
TOKENS={'CLEAR':253,'LOAD':239,'CODE':175,'PAUSE':242,'RANDOMIZE':249,'USR':192,'VAL':176,'STOP':226}
def build(source,name,out,assembler=None,tap_name=None):
 out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 exe=assembler or os.environ.get('SJASMPLUS') or shutil.which('sjasmplus')
 if not exe:raise RuntimeError('Install sjasmplus or pass --assembler /path/to/sjasmplus')
 source=Path(source).resolve()
 subprocess.run([str(exe),'--nologo','--msg=war',f'--raw={out/name}.bin',f'--sym={out/name}.sym',f'--lst={out/name}.lst',str(source)],cwd=ROOT/'src',check=True)
 code=(out/(name+'.bin')).read_bytes();assert len(code)<0x3800
 kw=lambda k:bytes([TOKENS[k]])+b' '
 val=lambda n:kw('VAL')+f'"{n}"'.encode()
 def line(n,body):return struct.pack('>H',n)+struct.pack('<H',len(body)+1)+body+b'\r'
 program=b''.join(line(n,b) for n,b in [(10,kw('CLEAR')+val(49151)),(20,kw('LOAD')+b'"" '+kw('CODE')),(30,kw('PAUSE')+val(60)),(40,kw('RANDOMIZE')+kw('USR')+val(57600)),(50,kw('STOP'))])
 header=bytes([0])+b'RAM VIDEO '.ljust(10,b' ')+struct.pack('<HHH',len(program),10,len(program))
 ch=bytes([3])+b'RAM PLAYER'.ljust(10,b' ')+struct.pack('<HHH',len(code),49152,0x8000)
 tape=tap_block(0,header)+tap_block(255,program)+tap_block(0,ch)+tap_block(255,code)
 target=out/(tap_name or name.upper()+'.TAP');target.write_bytes(tape);return target
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--variant',choices=['detail2','original'],default='detail2');p.add_argument('--assembler');p.add_argument('--output',type=Path,default=ROOT/'build')
 a=p.parse_args();name='sc512' if a.variant=='detail2' else 'sw512'
 print(build(ROOT/'src'/f'{name}_player.asm',name,a.output,a.assembler))
