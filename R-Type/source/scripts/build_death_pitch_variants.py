"""Arcade spectral-pitch guides + 33noise /37envelope; candidates41–52."""
from pathlib import Path
import numpy as np,json,wave,hashlib,math
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/audio/death_pitch_variants';OUT.mkdir(exist_ok=True)
LEVEL=np.array([0,.0137,.0205,.0291,.0423,.0618,.0847,.1369,.1691,.2647,.3527,.4499,.5704,.6873,.8482,1.]);CLOCK=1764750
def volume(x):return int(np.argmin(abs(LEVEL-np.clip(x,0,1))))
def period(f):return int(np.clip(round(CLOCK/(16*max(27,f))),1,4095))
src=ROOT/'build/audio/speech2ay_candidates/arcade_command53.wav'
with wave.open(str(src))as w:rate=w.getframerate();pcm=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
parent33=ROOT/'build/audio/death_14_variants/33.json';parent37=ROOT/'build/audio/death_14_variants/37.json';rows33=json.loads(parent33.read_text())['register_frames'];rows37=json.loads(parent37.read_text())['register_frames']
# Track a continuous harmonic/tonal spectral ridge, permitting both rises and falls.
# Whitening reduces broad-band noise dominance. This is a guide, not a recovered FM score.
grid=np.geomspace(75,1800,144);logs=np.log2(grid);scores=[];features=[]
for i in range(68):
 centre=round((i+.5)*rate/50);half=round(rate*.032);x=pcm[max(0,centre-half):min(len(pcm),centre+half)];x=np.pad(x,(max(0,half-centre),max(0,centre+half-len(pcm))));x=x-x.mean();spec=abs(np.fft.rfft(x*np.hanning(len(x)),16384));freq=np.fft.rfftfreq(16384,1/rate)
 floor=np.convolve(spec,np.ones(151)/151,'same')+np.max(spec)*.025+1e-10;white=np.minimum(8,spec/floor);salience=np.zeros(len(grid))
 for harmonic,weight in [(1,1),(2,.48),(3,.27),(4,.16)]:salience+=weight*np.interp(grid*harmonic,freq,white)
 salience=np.log(.05+salience);salience=(salience-salience.mean())/(salience.std()+1e-12);scores.append(salience)
 rms=float(np.sqrt(np.mean(x*x)));centroid=float(np.sum(freq*spec)/(np.sum(spec)+1e-12));features.append(dict(time=i/50,rms=rms,centroid_hz=centroid))
scores=np.array(scores);transition=1.8*abs(logs[:,None]-logs[None,:])+8*np.maximum(0,abs(logs[:,None]-logs[None,:])-.3)**2
cost=scores[0].copy();backs=[]
for i in range(1,len(scores)):
 candidate=cost[:,None]-transition;back=np.argmax(candidate,axis=0);cost=scores[i]+candidate[back,np.arange(len(grid))];backs.append(back)
indices=[int(np.argmax(cost))]
for back in reversed(backs):indices.append(int(back[indices[-1]]))
indices=indices[::-1];ridge=grid[indices];smooth=np.exp(np.convolve(np.pad(np.log(ridge),(1,1),mode='edge'),np.ones(3)/3,'valid'))
rms=np.array([f['rms']for f in features]);env=rms/max(rms.max(),1e-12);last=int(np.flatnonzero(env>.04)[-1]);ridge[last+1:]=ridge[last];smooth[last+1:]=smooth[last]
for i,f in enumerate(features):f.update(raw_pitch_guide_hz=float(ridge[i]),smooth_pitch_guide_hz=float(smooth[i]))
direction=np.diff(np.log2(ridge[:last+1]));assert np.any(direction>.02)and np.any(direction<-.02),'guide must contain rises and falls'
(OUT/'arcade_pitch_analysis.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),method='Whitened harmonic spectral ridge; dynamic-programming continuity permits up/down movement; not an FM note transcription',grid_hz=[75,1800],hop_hz=50,window_ms=64,active_frames=last+1,rises=int(sum(direction>.02)),falls=int(sum(direction<-.02)),features=features),indent=2))
configs=[
 ('33 — arcade up/down pitch','Pitch guide',dict(depth=1,smoothing=False),'33noise sweep,37contour; A follows the measured arcade ridge directly.'),
 ('33 — smoother arcade pitch','Pitch guide',dict(depth=1,smoothing=True,pure_tone=True),'Clearer A tone over noise B; same guide with three-frame logarithmic smoothing; no imposed falling ramp.'),
 ('33 — arcade pitch octave down','Pitch guide',dict(depth=1,smoothing=True,octave=-1),'Keeps arcade rises/falls, one octave lower, with33noise.'),
 ('33 — deeper noisy pitch body','Pitch guide',dict(depth=1,smoothing=False,octave=-.5,noise_mix=.25),'Half-octave lower with more of33’s noise-colour movement.'),
 ('33 — stronger arcade pitch swings','Pitch emphasis',dict(depth=1.35,smoothing=True),'Expands the measured rises and falls around their geometric centre.'),
 ('33 — restrained arcade pitch swings','Pitch emphasis',dict(depth=.7,smoothing=True,pure_tone=True),'Same rises/falls with a narrower range and a stronger noisy body.'),
 ('33 — slightly quicker pitch movement','Pitch emphasis',dict(depth=1,smoothing=False,speed=1.08),'The measured contour runs8%quicker; noise/envelope remain source-aligned.'),
 ('33 — slightly slower pitch movement','Pitch emphasis',dict(depth=1,smoothing=True,speed=.92),'Measured pitch shifts stretched slightly; original33/37body retained.'),
 ('33 /37 — bright explosive attack','Noise / envelope',dict(depth=1,smoothing=True,attack=.045,attack_gain=1.45,noise_mix=.55,pure_tone=True),'Sharper broad-band opening over arcade-guided tone and37loudness.'),
 ('33 /37 — fuller arcade loudness','Noise / envelope',dict(depth=1,smoothing=False,env_mix=.9,noise_mix=.7),'More of37’s arcade-weighted loudness and changing noise colour.'),
 ('33 /37 — low gated noisy body','Noise / envelope',dict(depth=1,smoothing=True,bgate=True,noise_mix=.4),'Arcade-guided tone onA; noisy B gains a descending low-frequency gate.'),
 ('33 /37 — articulated tone and crack','Noise / envelope',dict(depth=1.2,smoothing=True,attack=.03,attack_gain=1.6,tone_weight=.8,pure_tone=True),'More audible arcade pitch movement after a short sharp noise attack.')]
entries=[]
for j,(name,group,cfg,desc)in enumerate(configs):
 rows=[];guide=smooth if cfg.get('smoothing')else ridge;centre=float(np.exp(np.mean(np.log(guide[:last+1]))))
 for i in range(65):
  t=i/50;idx=min(len(rows33)-2,i);a=rows33[idx];b=rows37[min(len(rows37)-2,i)];g=float(np.exp(np.interp(i*cfg.get('speed',1),np.arange(len(guide)),np.log(guide))));g=centre*(g/centre)**cfg.get('depth',1)*2**cfg.get('octave',0);pa=period(g)
  weight=cfg.get('noise_mix',.4);n=int(np.clip(round((1-weight)*a[6]+weight*b[6]),1,31));body=cfg.get('env_mix',.65);va=(1-body)*LEVEL[a[8]]+body*max(LEVEL[b[8]],env[i]*.65);vb=(1-body)*LEVEL[a[9]]+body*LEVEL[b[9]];va*=cfg.get('tone_weight',.7)
  burst=cfg.get('attack_gain',1.25)*math.exp(-t/cfg.get('attack',.055));va=max(va,.45*burst);vb=max(vb,.75*burst)
  if t<cfg.get('attack',.055):n=max(1,round(1+(n-1)*t/cfg.get('attack',.055)))
  r=a.copy();r[0:2]=[pa&255,pa>>8];r[4:6]=[0,0];r[6]=n;r[7]=0xa8 if cfg.get('pure_tone')and t>.08 else 0xa0;r[8]=volume(va);r[9]=volume(vb);r[10]=0
  if cfg.get('bgate'):
   pb=period(95-60*min(1,t/1.3));r[2:4]=[pb&255,pb>>8]
  rows.append(r)
 end=rows[-1].copy();end[8]=end[9]=0;rows.append(end);ident=41+j;stem=str(ident)
 (OUT/(stem+'.json')).write_text(json.dumps(dict(tick_hz=50,channels=2,parents=[33,37],parameters=cfg,register_frames=rows),indent=2));entries.append(dict(id=ident,file=stem,name=name,group=group,description=desc,channels=2,frames=len(rows),seconds=len(rows)/50,register_sha256=hashlib.sha256(bytes(v for r in rows for v in r)).hexdigest(),parameters=cfg,optimized=False))
(OUT/'manifest.json').write_text(json.dumps(dict(tick_hz=50,sample_rate=22050,parents=[33,37],source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),parent_hashes={str(n):hashlib.sha256(p.read_bytes()).hexdigest()for n,p in [(33,parent33),(37,parent37)]},entries=entries),indent=2))
print('Built41–52; arcade spectral guide has',sum(direction>.02),'rises and',sum(direction<-.02),'falls across',last+1,'active frames')
