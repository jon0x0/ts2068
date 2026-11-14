"""20 new sound14 derivatives guided by arcade53 attack/spectral evolution."""
from pathlib import Path
import json,hashlib,wave,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/audio/death_14_variants';OUT.mkdir(exist_ok=True)
parent_path=ROOT/'build/audio/death_20/14.json';parent=json.loads(parent_path.read_text())['register_frames'];LEVEL=np.array([0,.0137,.0205,.0291,.0423,.0618,.0847,.1369,.1691,.2647,.3527,.4499,.5704,.6873,.8482,1.]);clock=1764750
def vol(x):return int(np.argmin(abs(LEVEL-np.clip(x,0,1))))
def period(f):return int(np.clip(round(clock/(16*max(27,f))),1,4095))
source=ROOT/'build/audio/speech2ay_candidates/arcade_command53.wav'
with wave.open(str(source))as w:rate=w.getframerate();pcm=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
features=[];previous=140.
for i in range(70):
 centre=round((i+.5)*rate/50);half=round(rate*.025);x=np.pad(pcm[max(0,centre-half):min(len(pcm),centre+half)],(max(0,half-centre),max(0,centre+half-len(pcm))));x=x-x.mean();nfft=8192;spec=abs(np.fft.rfft(x*np.hanning(len(x)),nfft));freq=np.fft.rfftfreq(nfft,1/rate);smooth=np.convolve(spec,np.ones(9)/9,'same');band=np.flatnonzero((freq>=70)&(freq<=1800));peaks=band[1:-1][(smooth[band[1:-1]]>=smooth[band[:-2]])&(smooth[band[1:-1]]>smooth[band[2:]])];peaks=sorted(peaks,key=lambda p:smooth[p],reverse=True)[:12]
 if peaks:
  # Continuity-weighted spectral peaks, not a claim of recovered FM notes.
  p=max(peaks,key=lambda p:smooth[p]/(1+.22*abs(math.log2(freq[p]/previous))));low=float(freq[p]);previous=low
 else:low=previous
 upper=np.flatnonzero((freq>=600)&(freq<=3500));high=float(freq[upper[np.argmax(smooth[upper])]])if len(upper)else low
 rms=float(np.sqrt(np.mean(x*x)));centroid=float(np.sum(freq*spec)/(np.sum(spec)+1e-12));flat=float(np.exp(np.mean(np.log(spec[band]+1e-12)))/(np.mean(spec[band])+1e-12));features.append(dict(time=i/50,rms=rms,low_peak_hz=low,upper_peak_hz=high,centroid_hz=centroid,flatness=flat))
peak=max(f['rms']for f in features);(OUT/'arcade_features.json').write_text(json.dumps({'method':'50Hz RMS + continuous low spectral peak and upper spectral peak from50ms windows; spectral evidence, not transcription','features':features},indent=2))
configs=[
 ('14 + sharp explosive front','Attack',dict(attack=.055,brightness=2,boost=1.45),'Short bright noise attack, then the original14 body.'),
 ('14 + double crack','Attack',dict(attack=.09,brightness=2,boost=1.5,double=True),'Two fast noise hits38ms apart, retaining14’s tone.'),
 ('14 + heavy low attack','Attack',dict(attack=.09,brightness=9,boost=1.35,b_gate=True,b_hz=65),'Thicker attack and a65Hz gated body under14.'),
 ('14 + dry punch','Attack',dict(attack=.035,brightness=1,boost=1.6,duration=.95),'Very short noise crack; compressed14 envelope.'),
 ('14 / arcade tone blend25%','Arcade tone tracking',dict(blend=.25,attack=.06),'Mostly14’s tone, with mild arcade spectral-peak movement.'),
 ('14 / arcade tone blend50%','Arcade tone tracking',dict(blend=.5,attack=.06),'Equal log-frequency blend of14 and arcade low spectral peaks.'),
 ('14 / arcade tone blend75%','Arcade tone tracking',dict(blend=.75,attack=.065),'Arcade peak movement dominates;14’s noise-gated texture remains.'),
 ('14 / arcade tone, octave lower','Arcade tone tracking',dict(blend=.85,pitch=.5,attack=.08),'Lower arcade-informed tone shifts with14’s noisy body.'),
 ('14 + high-to-low arcade shift','Tone stages',dict(blend=.65,upper_attack=True,attack=.055),'Upper spectral peak for the first120ms, then the lower body peak.'),
 ('14 + longer high-to-low shift','Tone stages',dict(blend=.75,upper_attack=True,shift=.22,attack=.08),'Longer bright tonal front before a darker arcade-guided body.'),
 ('14 + falling arcade body','Tone stages',dict(blend=.65,fall=1.2,attack=.055),'Arcade-informed tone decays downward through the noise.'),
 ('14 + gated second tonal layer','Tone stages',dict(blend=.5,b_gate=True,b_track=True,attack=.06),'Two gated layers:14/arcade blend onA and a low second layer onB.'),
 ('14 + bright-to-dark noise sweep','Noise evolution',dict(noise_sweep='wide',attack=.065),'Large noise-colour sweep from a bright crack to dark tail.'),
 ('14 + rapid noise cascade','Noise evolution',dict(noise_sweep='steps',attack=.05),'Four deliberate noise-period stages;14’s tone stays recognizable.'),
 ('14 + turbulent noisy body','Noise evolution',dict(noise_sweep='turbulent',attack=.07),'Deterministic irregular noise-colour/envelope movement after impact.'),
 ('14 + long debris tail','Noise evolution',dict(duration=1.55,noise_sweep='dark',attack=.06,tail=True),'Longer low-level noise debris under the14-derived tone path.'),
 ('14 + arcade-weighted impact','Balanced hybrids',dict(blend=.45,env_blend=.85,attack=.065,brightness=2,boost=1.35),'Arcade loudness contour drives a stronger14-based explosion.'),
 ('14 + compact arcade blast','Balanced hybrids',dict(blend=.6,duration=.85,attack=.04,env_blend=.75),'Fast attack and rapid arcade-guided tone/noise collapse.'),
 ('14 + heavy two-voice blast','Balanced hybrids',dict(blend=.55,b_gate=True,b_hz=48,attack=.085,boost=1.5,env_blend=.65),'Broad noisy attack plus a48Hz gated low layer.'),
 ('14 + shifting explosion / shrapnel','Balanced hybrids',dict(blend=.7,upper_attack=True,shift=.10,noise_sweep='turbulent',attack=.05,shrapnel=True),'Arcade-guided opening shift, irregular gated fragments and noisy decay.')]
entries=[]
for j,(name,group,cfg,description)in enumerate(configs):
 duration=cfg.get('duration',1.3);rows=[]
 for i in range(round(duration*50)):
  t=i/50;u=t/duration;source_t=u*1.3;old=parent[min(len(parent)-2,int(source_t*50))].copy();f=features[min(len(features)-1,int(source_t*50))];arc_amp=f['rms']/peak*.8;env_blend=cfg.get('env_blend',.45);base_amp=LEVEL[old[8]];noise_amp=LEVEL[old[9]];attack=cfg.get('attack',0);boost=cfg.get('boost',1.2);burst=math.exp(-t/max(.01,attack))if attack else 0
  if cfg.get('double'):burst=max(burst,.85*math.exp(-max(0,t-.038)/.035)if t>=.038 else 0)
  ampA=(1-env_blend)*base_amp+env_blend*arc_amp*.65;ampB=(1-env_blend)*noise_amp+env_blend*arc_amp*.85;ampA=max(ampA,burst*.65*boost);ampB=max(ampB,burst*.85*boost)
  base_f=clock/(16*max(1,old[0]|old[1]<<8));tone=f['low_peak_hz'];shift=cfg.get('shift',.12)
  if cfg.get('upper_attack')and t<shift:tone=f['upper_peak_hz']*(.5 if t>shift*.5 else 1)
  blend=cfg.get('blend',0);freq=base_f**(1-blend)*tone**blend*cfg.get('pitch',1)*2**(-cfg.get('fall',0)*u);pa=period(freq)
  n=old[6];sweep=cfg.get('noise_sweep')
  if sweep=='wide':n=round(1+30*u**.55)
  elif sweep=='steps':n=[2,7,17,30][min(3,int(u*4))]
  elif sweep=='turbulent':n=int(np.clip(n+[0,4,-3,7,-5,2,-1][i%7],1,31));ampB*= [.85,1,.65,.95,1,.75,.9][i%7]
  elif sweep=='dark':n=round(12+19*u)
  if t<attack:n=round(cfg.get('brightness',3)+(n-cfg.get('brightness',3))*(t/max(attack,.001)))
  if cfg.get('tail'):ampB=max(ampB,.17*math.exp(-max(0,t-.8)*5))
  old[0:2]=[pa&255,pa>>8];old[6]=int(np.clip(n,1,31));old[7]=0xa0;old[8]=vol(ampA);old[9]=vol(ampB)
  # Keep14's gated A and noisy B core; selected variants give B a slower gate.
  if cfg.get('b_gate'):
   bf=cfg.get('b_hz',70)*(1-.4*u)
   if cfg.get('b_track'):bf=max(30,f['low_peak_hz']*.35)
   pb=period(bf);old[2:4]=[pb&255,pb>>8]
  if cfg.get('shrapnel')and t>.1:
   pb=period([433,191,757,97,281][i%5]*(1-.6*u));old[2:4]=[pb&255,pb>>8];old[9]=vol(ampB*(.7 if i%4 else 1))
  old[4:6]=[0,0];old[10]=0;rows.append(old)
 end=rows[-1].copy();end[8]=end[9]=0;rows.append(end)
 ident=21+j;stem=f'{ident:02d}';digest=hashlib.sha256(bytes(v for a in rows for v in a)).hexdigest();assert all(len(a)==11 and a[10]==0 and not(a[7]&64)and a[1]<16 and a[3]<16 and a[8]<16 and a[9]<16 for a in rows)
 (OUT/(stem+'.json')).write_text(json.dumps(dict(tick_hz=50,channels=2,parent_choice=14,parameters=cfg,register_frames=rows),indent=2));entries.append(dict(id=ident,file=stem,name=name,group=group,description=description,channels=2,frames=len(rows),seconds=len(rows)/50,register_sha256=digest,parent_choice=14,parameters=cfg))
assert len(entries)==20 and len({e['register_sha256']for e in entries})==20
old=json.loads((ROOT/'build/audio/death_20/manifest.json').read_text());assert not set(e['register_sha256']for e in entries)&set(e['register_sha256']for e in old['entries'])
(OUT/'manifest.json').write_text(json.dumps(dict(tick_hz=50,sample_rate=22050,parent_choice=14,parent_sha256=hashlib.sha256(parent_path.read_bytes()).hexdigest(),arcade_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),entries=entries),indent=2))
print('Generated20new derivatives of14, numbered21–40; all distinct from original set')
