"""Convert a local movie interval into two complete RAM512 sample sets.

No automatic frame/cell dropping. If 512 KiB is exceeded, choose a smaller
window, lower fps, or shorter interval. The source movie is never modified.
"""
from pathlib import Path
import argparse,hashlib,json,math,re,struct,subprocess
import numpy as np
from ram_format import physical,words,pack,code_pair
from build_player import ROOT,build as build_player
def sha(b):return hashlib.sha256(b).hexdigest()
def mode(s):
 m=re.fullmatch(r'(\d+)x(\d+)@(\d+)',s)
 if not m:raise argparse.ArgumentTypeError('Use WIDTHxHEIGHT@FPS, such as 256x108@12')
 w,h,fps=map(int,m.groups())
 if not (16<=w<=256 and w%8==0 and 1<=h<=192 and 1<=fps<=60 and 60%fps==0):raise argparse.ArgumentTypeError('Width must be 16..256 in 8-pixel steps, height 1..192, and fps must divide 60')
 return w,h,fps
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('input',type=Path);p.add_argument('--start',type=float,default=0);p.add_argument('--duration',type=float,required=True)
 p.add_argument('--mode',type=mode,action='append',help='Repeat twice; defaults to 256x108@12 and 232x98@15')
 p.add_argument('--colour',choices=['detail2','original'],default='detail2');p.add_argument('--prefix',default='CV',help='Two uppercase letters, distinct from existing demos')
 p.add_argument('--output',type=Path,required=True);p.add_argument('--assembler');p.add_argument('--data-only',action='store_true',help='Skip player assembly; include generated source for later assembly')
 a=p.parse_args();modes=a.mode or [(256,108,12),(232,98,15)]
 if len(modes)!=2:p.error('Supply exactly two --mode values')
 if not re.fullmatch('[A-Z]{2}',a.prefix):p.error('--prefix must be two uppercase letters')
 if not a.input.is_file() or a.start<0 or not math.isfinite(a.start) or not math.isfinite(a.duration) or a.duration<=0:p.error('Input must exist, start must be nonnegative, duration must be positive')
 if a.output.exists() and any(a.output.iterdir()):p.error('Choose an empty output directory to avoid replacing samples')
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 if a.colour=='detail2':from trench_colour2 import quantize
 else:from trench_quantizer import quantize
 profiles={}
 for tag,(w,h,fps) in zip(('F','W'),modes):
  data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(a.start),'-i',str(a.input.resolve()),'-t',str(a.duration),'-an','-vf',f'fps={fps},scale={w}:{h}:flags=lanczos','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
  size=w*h*3;n=len(data)//size
  if len(data)%size or not 2<=n<=384:raise ValueError('Need 2..384 complete frames per mode')
  if n<math.floor(a.duration*fps):raise ValueError('Source ended before the requested interval was complete')
  fs=[];old=None
  for i in range(n):
   old=quantize(np.frombuffer(data[i*size:(i+1)*size],dtype=np.uint8).reshape(h,w,3),old);fs.append(physical(old,w,h))
   if i%24==0:print(tag,w,h,fps,'frame',i,flush=True)
  packets=[words(x,y) for x,y in zip(fs,fs[1:])]+[words(fs[-1],fs[0])]
  try:pages,index,last,meaningful=pack(fs,packets)
  except OverflowError as e:raise SystemExit(f'{tag}: {e}. Choose a smaller window, lower fps or shorter duration; no frames were silently discarded.')
  # Independent reconstruction verifies every paired patch and the loop.
  state=[bytearray(fs[0].bitmap),bytearray(fs[0].attributes)]
  for i,packet in enumerate(packets):
   for address,value in struct.iter_unpack('<HH',packet):
    if address==0x5800:continue
    if address%2 or not (0x4000<=address<=0x57fe or 0x6000<=address<=0x77fe):raise ValueError('Invalid patch destination')
    plane=int(address>=0x6000);base=0x6000 if plane else 0x4000
    state[plane][address-base:address-base+2]=value.to_bytes(2,'little')
   assert state[0]==fs[(i+1)%n].bitmap and state[1]==fs[(i+1)%n].attributes
  image=b''.join(pages);sums=b''.join(struct.pack('<H',sum(page)&65535) for page in pages)
  meta=bytearray(64);meta[:4]=b'R512';meta[4:8]=bytes([1,60//fps,64,last]);struct.pack_into('<HHHHHI',meta,8,n,n,len(index),w,h,meaningful)
  vols=[];d=out/tag;d.mkdir()
  for filename,payload in [('sram.bin',image),('frames.ecm',b''.join(f.bitmap+f.attributes for f in fs)),('meta.bin',meta),('index.bin',index),('sums.bin',sums)]: (d/filename).write_bytes(payload)
  for vi in range(16):
   payload=(code_pair('RAM META',meta)+code_pair('RAM INDEX',index)+code_pair('RAM SUMS',sums)) if vi==0 else b''
   payload+=b''.join(code_pair(f'RAM {q:02}',pages[q]) for q in range(vi*4,vi*4+4))
   name=f'{a.prefix}{tag}{vi:03}.TAP';(out/name).write_bytes(payload);vols.append(dict(name=name,sha256=sha(payload)))
  profiles[tag]=dict(width=w,height=h,fps_target=fps,source_frames=n,nominal_loop_seconds=n/fps,meaningful_bytes=meaningful,sram_sha256=sha(image),all_frames_exact=True,volumes=vols)
 source=(ROOT/'src/sc512_player.asm').read_text().replace('SCF000.TAP',a.prefix+'F000.TAP').replace('STAR WARS COLOUR DETAIL 2','CUSTOM 512K VIDEO')
 begin=source.index('help: db ');end=source.index('volume_text:',begin)
 lines=[f"help: db 'SOURCE {a.start:.2f} TO {a.start+a.duration:.2f} SEC',13"]
 for i,pr in enumerate(profiles.values(),1):lines+=[f"      db '{i} {pr['width']}X{pr['height']} ECM / {pr['fps_target']} FPS TARGET',13",f"      db '  {pr['source_frames']} FRAMES / {pr['nominal_loop_seconds']:.2f} SEC',13"]
 lines+=["      db 13,'REPLACES ALL 512K SRAM',13,'X STOP  SPACE PAUSE / RESUME',13,0"]
 source=source[:begin]+'\n'.join(lines)+'\n'+source[end:]
 name=a.prefix.lower()+'512';generated=ROOT/'src'/f'{name}_generated.asm'
 if generated.exists():raise FileExistsError(f'Refusing to replace {generated}; choose another prefix')
 generated.write_text(source);(out/'player.asm').write_text(source)
 (out/'manifest.json').write_text(json.dumps(dict(source=a.input.name,start=a.start,duration=a.duration,colour=a.colour,profiles=profiles),indent=2)+'\n')
 if not a.data_only:print(build_player(generated,name,out,a.assembler,a.prefix+'512.TAP'))
 print('Put the player and all 32 samples directly in /TAP/ on the SD card. They will not run elsewhere.')
if __name__=='__main__':main()
