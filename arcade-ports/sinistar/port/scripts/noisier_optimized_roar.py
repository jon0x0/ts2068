"""Keep optimized pitch voices A/B; fit stronger noise on C in the rise."""
from pathlib import Path
import os,sys,shutil,json,wave,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
from tsaudio import search
from tsaudio.dsp import read_wav,resample
out=ROOT/'port/build/roar-optimized-noise';out.mkdir(parents=True,exist_ok=True)
base=ROOT/'port/build/roar-full-optimizer'
raw=(base/'optimized.ay').read_bytes()
rows=np.frombuffer(raw,dtype=np.uint8).reshape(-1,14).tolist()
env=dict(os.environ);env['PATH']=str(Path(shutil.which('gcc')).parent)+os.pathsep+env['PATH']
sim=search.Simulator(base/'ay-worker.exe',env,11702.57,7.8)
before=search.render(sim,rows)
fs,x=read_wav(ROOT/'assets/sinistar-roar-arcade.wav')
target=np.asarray(resample(x,fs,44100));target=np.pad(target,(0,max(0,len(before)-len(target))))[:len(before)]
target*=np.std(before)/(np.std(target)+1e-12)
sim.command(2);context=np.zeros(1024);chosen=[]
try:
 for i,seed in enumerate(rows):
  lo=round(i*44100/search.HZ);hi=round((i+1)*44100/search.HZ)
  best=seed.copy()
  if i>=48 and any(seed[8:11]):
   expected=np.r_[np.pad(target[max(0,lo-1024):lo],(max(0,1024-lo),0)),target[lo:hi]]
   # Ramp in over 0.2 s; preserve the end's natural volume decay.
   level=max(min(15,v) for v in seed[8:11])
   floor=max(0,level-2);ramp=min(1,(i-47)/12)
   floor=round(min(seed[10],15)*(1-ramp)+floor*ramp)
   choices=[]
   for noise in range(1,32):
    for volume in range(floor,min(15,floor+2)+1):
     r=seed.copy();r[6]=noise;r[7]=(r[7]|4)&~32;r[10]=volume;choices.append(r)
   waves=sim.evaluate(choices,hi-lo)
   c=search.score_components(context,waves,expected)
   costs=c['spectrum']+2*c['periodicity']+.05*c['roughness']
   best=choices[int(np.argmin(costs))]
  audio=sim.evaluate([best],hi-lo)[0];sim.command(1,0)
  context=np.r_[context,audio][-1024:];chosen.append(best)
 after=search.render(sim,chosen)
finally:sim.close()
assert chosen[:48]==rows[:48]
assert all(all(a[k]==b[k] for k in [0,1,2,3,8,9,11,12,13]) and (a[7]&27)==(b[7]&27) for a,b in zip(chosen,rows))
assert np.array_equal(before[:round(48*44100/search.HZ)],after[:round(48*44100/search.HZ)])
gain=.9/max(np.max(abs(before)),np.max(abs(after)),np.max(abs(target)))
for name,audio in [('before',before),('noisier',after),('original',target)]:
 with wave.open(str(out/(name+'.wav')),'wb') as w:
  w.setparams((1,2,44100,0,'NONE','not compressed'));w.writeframes(np.clip(audio*gain*32767,-32768,32767).astype('<i2').tobytes())
payload=bytes(v for r in chosen for v in r);(out/'noisier.ay').write_bytes(payload)
report=dict(frames=len(chosen),unchanged_opening_frames=48,pitched_channels_unchanged=True,noise_ramp_seconds=[48/search.HZ,60/search.HZ],changed_frames=sum(a!=b for a,b in zip(chosen,rows)),sha256=hashlib.sha256(payload).hexdigest(),production_unchanged=True)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(out/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Optimized roar with stronger noise</title><style>body{font:18px system-ui;background:#111722;color:#eee;max-width:740px;margin:40px auto;padding:20px}audio{width:100%}p{line-height:1.5}</style><h1>More noise as the roar rises</h1><p>The first 0.8 seconds are unchanged. Noise ramps in over the next 0.2 seconds. Two optimized pitch channels keep their exact frequencies, volumes and envelope settings; the third channel supplies stronger fitted noise.</p><h2>Revised: stronger noise</h2><audio controls src="noisier.wav"></audio><h2>Previous full-optimizer result</h2><audio controls src="before.wav"></audio><h2>Original recording</h2><audio controls src="original.wav"></audio><p>Same gain and AY model for both synthesized versions. Complete duration retained. Listening preview; the cartridge remains unchanged.</p></html>''',encoding='utf-8')
print(report,flush=True)
