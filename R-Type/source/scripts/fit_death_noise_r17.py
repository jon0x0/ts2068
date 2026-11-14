from pathlib import Path
import sys,json,subprocess,shutil,os,wave
import numpy as np
r=Path(__file__).resolve().parents[1];tool=r/'../../speech2ay';sys.path.insert(0,str(tool))
from tsaudio import search
from tsaudio.codecs import source
from tsaudio.dsp import resample
out=r/'build/audio/death_noise_r17';out.mkdir(exist_ok=True)
gcc=shutil.which('gcc');ayumi=r/'../../audio2ay-master/ayumi';exe=out/'ay-worker.exe'
subprocess.run([gcc,'-O2','-std=c99','-I'+str(ayumi),str(tool/'tsaudio/ay_optimizer_worker.c'),str(ayumi/'ayumi.c'),'-lm','-o',str(exe)],check=True)
env=dict(os.environ);env['PATH']=str(Path(gcc).parent)+os.pathsep+env['PATH'];sim=search.Simulator(exe,env,11702.57,7.8)
old=json.loads((r/'build/audio/arcade_sfx_reference_r16.json').read_text())['frames']['53'];rows=[]
for f in old:
 a=[0]*14
 for reg,v in zip([0,1,6,7,8],f):a[reg]=v
 a[13]=255;rows.append(a)
def render(frames):
 sim.command(2);audio=[]
 for f in frames:audio.extend(sim.evaluate([f],882)[0]);sim.command(1,0)
 return np.asarray(audio)
before=render(rows);rate,x=source(r/'build/audio/speech2ay_candidates/arcade_command53.wav');target=np.asarray(resample(x,rate,44100));target=np.pad(target,(0,max(0,len(before)-len(target))))[:len(before)];target*=np.std(before)/(np.std(target)+1e-12)
sim.command(2);context=np.zeros(1024);chosen=[];costs=[]
def score(waves,expected):
 p=search.score_components(context,waves,expected)
 return p['spectrum']+3*p['periodicity']+.05*p['roughness']
try:
 for i in range(0,len(rows),2):
  lo=i*882;hi=min(i+2,len(rows))*882;n=hi-lo;expected=np.r_[np.pad(target[max(0,lo-1024):lo],(max(0,1024-lo),0)),target[lo:hi]]
  choices=[]
  for noise in range(1,32):
   for volume in range(16):
    f=[0]*14;f[6]=noise;f[7]=0xB9;f[8]=volume;f[13]=255;choices.append(f)
  scores=score(sim.evaluate(choices,n),expected);pure=choices[int(np.argmin(scores))];choices=[pure] if pure[8]==0 else []
  for period in np.unique(np.rint(np.geomspace(48,4095,12)).astype(int)):
   for va in sorted({max(0,pure[8]-2),pure[8],min(15,pure[8]+1)}):
    for vb in [max(0,va-4),max(0,va-2),va]:
     f=pure.copy();f[2]=int(period)&255;f[3]=int(period)>>8;f[7]=0xA1;f[8]=va;f[9]=vb
     if va and vb: choices.append(f)
     if va and vb and period==48:
      pure_pair=f.copy();pure_pair[7]=0xA3;choices.append(pure_pair)
  waves=sim.evaluate(choices,n);scores=score(waves,expected);idx=int(np.argmin(scores));best=choices[idx];audio=waves[idx];sim.command(1,idx);context=np.r_[context,audio][-1024:];chosen.extend([best]*min(2,len(rows)-i));costs.append(float(scores[idx]));print('noise fit',i,'/',len(rows),flush=True)
 after=render(chosen)
finally:sim.close()
frames=[f[:11]for f in chosen]
(out/'frames.json').write_text(json.dumps({'tick_hz':50,'channels':2,'register_frames':frames,'noise_frames':sum(f[8]>0 and not(f[7]&8)for f in chosen),'gated_B_frames':sum(f[9]>0 and not(f[7]&2)for f in chosen),'method':'Stateful Ayumi noise-first spectral/periodicity fit; A noise and B shared-noise with optional tone gate; music C reserved','mean_objective':float(np.mean(costs))},indent=2))
gain=.9/max(np.max(abs(before)),np.max(abs(after)),1e-9)
for name,v in [('r16_before.wav',before),('noise_fit.wav',after)]:
 with wave.open(str(out/name),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(44100);w.writeframes(np.clip(v*gain*32767,-32768,32767).astype('<i2').tobytes())
print('Fitted death noise',len(frames),'frames')
