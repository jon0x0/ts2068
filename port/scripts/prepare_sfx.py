"""Render the original GWAVE algorithm/tables to WAV, then speech2ay harmonic1.
Source-derived reconstruction: 894.886 kHz sound CPU, approximate boundary timing; not a circuit emulator.
"""
from pathlib import Path
import re,sys,json,hashlib,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
from tsaudio.codecs import encode
src=(ROOT/'port/reference/VSNDRM9.ASM').read_text()
def data(a,b):
 out=[]
 for line in src.split(a,1)[1].split(b,1)[0].splitlines():
  line=line.split(';')[0]
  if 'FCB' in line:
   for t in line.split('FCB')[1].strip().split(','):out.append(int(t[1:],16) if t.startswith('$') else int(t))
 return out
waves=data('GWVTAB  EQU','SVTAB   EQU');patterns=data('GFRTAB  EQU','TRANS   PSHA')
waveforms=[]
while waves:
 n=waves[0];waveforms.append(np.array(waves[1:1+n],dtype=int));waves=waves[1+n:]
# Native GWAVE output loop: six cycles per period count plus 24 cycles
# for loads/output/next-sample checks. Pattern/cycle boundaries add overhead.
def render(vector):
 echoes,cycles=vector[0]>>4,vector[0]&15;decay,wid=vector[1]>>4,vector[1]&15
 pre,inc,reps,length,start=vector[2:];rom=waveforms[wid];wav=(rom-(rom>>4)*pre)&255
 pat=patterns[start:start+length];offset=0;events=[];clock=0
 for sweep in range(reps if inc else 1):
  for echo in range(echoes or 256):
   for period in pat:
    p=(period+offset)&255
    for cycle in range(cycles or 256):
     for v in wav:
      clock+=6*(p or 256)+24;events.append((clock,int(v)>>1))
     clock+=36
    clock+=36
   wav=(wav-(rom>>4)*decay)&255;clock+=len(wav)*(56+10*decay)+40
  if not inc:break
  offset=(offset+inc)&255
  valid=[p for p in pat if (p+offset<=255 if inc<128 else p+offset>255 and (p+offset)&255)]
  if not valid:break
  pat=valid
  if decay:wav=(rom-(rom>>4)*pre)&255
 rate=22050;times=np.array([t for t,v in events])/(3579545/4)
 t=np.arange(int(times[-1]*rate)+1)/rate
 vals=np.array([v for _,v in events]);out=vals[np.maximum(0,np.searchsorted(times,t,side='right')-1)].astype(float)
 out-=out.mean();out/=max(abs(out).max(),1)
 return rate,out
report=[]
for name,label in [('shot','PFIREV'),('pickup','PCRYSV'),('assembly','CLANGV'),('bomb-launch','BBSV')]:
 line=next(l for l in src.splitlines() if l.startswith(label+' '))
 vector=[int(x.strip()[1:],16) for x in line.split('FCB')[1].split(';')[0].strip().split(',')]
 rate,pcm=render(vector)
 if name=='assembly':pcm=pcm[:int(rate*.20)] # short piece-added cue; full preset is the game-over sequence
 # Keep full reconstructed effect; encode once, never synthesize during play.
 target=ROOT/'assets'/('sfx-'+name+'.wav')
 with wave.open(str(target),'wb') as w:w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes((pcm*28000).astype('<i2').tobytes())
 raw,count,info=encode(target,'harmonic1');(target.with_suffix('.ay')).write_bytes(raw)
 # Compact audible registers for harmonic1; B/C are muted and envelope unused.
 rows=np.frombuffer(raw,dtype=np.uint8).reshape(-1,14)
 assert np.all(rows[:,[9,10]]==0) and np.all(rows[:,8]<16) and np.all(rows[:,13]==255) and np.all(rows[:,7]&0x36==0x36)
 packed=rows[:,[0,1,6,7,8]].tobytes();target.with_suffix('.packed').write_bytes(packed)
 item=dict(name=name,preset=label,vector=vector,frames=count,bytes=len(packed),seconds=len(pcm)/rate,wav_sha256=hashlib.sha256(target.read_bytes()).hexdigest());report.append(item);print(item)
(ROOT/'assets/sfx-manifest.json').write_text(json.dumps(dict(source='https://github.com/synamaxmusic/sinistar/blob/main/VSNDRM9.ASM',source_sha256=hashlib.sha256(src.encode()).hexdigest(),method='GWAVE table reconstruction, 894.886kHz loop timing, approximate boundary overhead, 0.20s assembly cue; speech2ay harmonic1',effects=report),indent=2)+'\n')
