"""Twenty reproducible AY death-effect alternatives; no cartridge changes."""
from pathlib import Path
import json,hashlib,wave,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/audio/death_20';OUT.mkdir(exist_ok=True)
LEVEL=np.array([0,.0137,.0205,.0291,.0423,.0618,.0847,.1369,.1691,.2647,.3527,.4499,.5704,.6873,.8482,1.])
def volume(x):return int(np.argmin(abs(LEVEL-max(0,min(1,x)))))
def period(f):return int(np.clip(round(1764750/(16*max(27,f))),1,4095))
def frame(pa=0,pb=0,noise=8,va=0,vb=0,ta=False,tb=False,na=True,nb=False):
 r=[0]*11;r[0:2]=[pa&255,pa>>8];r[2:4]=[pb&255,pb>>8];r[6]=int(np.clip(noise,1,31));r[7]=0x80|0x20|(0 if ta else 1)|(0 if tb else 2)|(0 if na else 8)|(0 if nb else 16);r[8]=volume(va);r[9]=volume(vb);return r
source=json.loads((ROOT/'build/audio/goodboy_sfx_reference.json').read_text())
effect=next(e for e in source['effects']if e['id']==11);state=[0]*11;imported=[]
for writes in effect['frames']:
 for reg,value in writes:
  assert reg<11;state[reg]=value
 imported.append(state.copy())
fitted=json.loads((ROOT/'build/audio/death_noise_r17/frames.json').read_text())['register_frames']
manifest=json.loads((ROOT/'build/audio/speech2ay_candidates/manifest.json').read_text())
def converted(ch):
 e=next(e for e in manifest if e['command']==53 and e['channels']==ch);rows=e['register_frames'];return [rows[min(len(rows)-1,int(i*60.1145/50))].copy()for i in range(round(len(rows)*50/60.1145))]
with wave.open(str(ROOT/'build/audio/speech2ay_candidates/arcade_command53.wav'))as w:
 rate=w.getframerate();pcm=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
env=[];noise=[]
for i in range(65):
 x=pcm[round(i*rate/50):round((i+1)*rate/50)];env.append(float(np.sqrt(np.mean(x*x)))if len(x)else 0)
 spec=abs(np.fft.rfft(x*np.hanning(len(x))))if len(x)else np.zeros(1);freq=np.fft.rfftfreq(len(x),1/rate)if len(x)else np.zeros(1);centroid=float(np.sum(spec*freq)/(np.sum(spec)+1e-12));noise.append(int(np.clip(round(1764750/(16*max(100,centroid)*3)),1,31)))
env=np.asarray(env);env=env/max(max(env),1e-12)*.8
def imp_at(t,speed=1):return imported[min(len(imported)-1,max(0,int(t*50*speed)))].copy()
def fit_at(t):return fitted[min(len(fitted)-1,int(t*50))].copy()
entries=[]
def add(name,group,description,rows,channels):
 rows=[list(map(int,r))for r in rows]
 # Always release the effect; chip register C and joystick ports are reserved.
 for r in rows:r[4:6]=[0,0];r[10]=0;r[7]=(r[7]&0x1b)|0xa0
 end=rows[-1].copy();end[8]=end[9]=0;rows.append(end)
 for r in rows:assert len(r)==11 and all(0<=x<256 for x in r)and r[1]<16 and r[3]<16 and r[8]<16 and r[9]<16 and not(r[7]&64)
 n=len(entries)+1;stem=f'{n:02d}';(OUT/(stem+'.json')).write_text(json.dumps({'tick_hz':50,'channels':channels,'register_frames':rows},indent=2));entries.append(dict(id=n,name=name,group=group,description=description,channels=channels,seconds=len(rows)/50,frames=len(rows),register_sha256=hashlib.sha256(bytes(x for r in rows for x in r)).hexdigest(),file=stem))
add('Imported AY — original','Imported 2019 AY','Unmodified 2019 effect11 note/noise sequence, plus an explicit final mute.',imported,1)
rows=[]
for i in range(60):
 r=imp_at(i/50,.72);p=min(4095,(r[0]|r[1]<<8)*2);r[0:2]=[p&255,p>>8];rows.append(r)
add('Imported AY — deeper and slower','Imported 2019 AY','Octave lower, stretched attack/tail; keeps the imported character.',rows,1)
rows=[]
for i in range(36):
 r=imp_at(i/50,1.2);p=min(4095,round((r[0]|r[1]<<8)*(1+i/28)));r[0:2]=[p&255,p>>8];r[8]=max(0,r[8]-i//9);rows.append(r)
add('Imported AY — falling percussion','Imported 2019 AY','Faster imported sequence with an increasingly deep pitch and shorter decay.',rows,1)
rows=[]
for i in range(len(imported)):
 r=imp_at(i/50);r[6]=int(8+23*i/max(1,len(imported)-1));r[7]=0xb9;rows.append(r)
add('Imported envelope — noise only','Imported 2019 AY','Retains imported amplitude timing but replaces the melodic tone with darkening noise.',rows,1)
add('Arcade — harmonic, one voice','Arcade-derived','The previous one-channel speech2ay conversion, retained for comparison.',converted(1),1)
add('Arcade — harmonic, two voices','Arcade-derived','Original two-channel speech2ay analysis; compare its pitch/noise balance.',converted(2),2)
add('Arcade — r17 fitted noise','Arcade-derived','Current noise-first Ayumi fit, with gated second noise voice.',fitted,2)
add('Arcade envelope — broad noise','Arcade-derived','Measured arcade RMS envelope and spectral-colour curve, without speech pitch tracking.',[frame(noise=noise[i],va=env[i],vb=env[i]*.4,nb=True)for i in range(65)],2)
for kind,name,desc,duration in [
 ('deep','Deep heavy blast','Dark shared noise with a slow gated low rumble.',1.1),
 ('bright','Short sharp blast','Bright broadband initial burst, rapid darkening and fast decay.',.58),
 ('chunky','Chunky stepped blast','Stepped noise colour and a descending gated second layer.',.9),
 ('rolling','Long rolling explosion','Longer uneven noise decay, with a low second burst.',1.55)]:
 rows=[]
 for i in range(round(duration*50)):
  t=i/50;u=t/duration
  if kind=='deep':amp=.9*math.exp(-3.3*u);n=round(20+11*u);f=48-20*u;gate=True;ratio=.6
  elif kind=='bright':amp=.95*math.exp(-5*u);n=round(1+16*u);f=180-100*u;gate=False;ratio=.35
  elif kind=='chunky':amp=.85*math.exp(-3*u)*(1 if i%7<5 else .55);n=[6,13,23,31][min(3,int(u*4))];f=240*(1-u)+35;gate=True;ratio=.55
  else:amp=min(.95,.8*math.exp(-3*u)+.3*math.exp(-((u-.4)/.12)**2));n=round(6+25*u);f=90-60*u;gate=True;ratio=.6
  rows.append(frame(pb=period(f),noise=n,va=amp,vb=amp*ratio,tb=gate,nb=True))
 add(name,'Explosion-designed',desc,rows,2)
rows=[]
for i in range(65):
 t=i/50;r=imp_at(t);r[6]=noise[i];r[7]=(r[7]&1)|0xa0|2|8;r[9]=volume(env[i]*.7);rows.append(r)
add('Imported tone + arcade noise','Hybrid','Original AY tone on A; measured arcade noise/envelope on B.',rows,2)
rows=[]
for i in range(65):
 r=imp_at(i/50,.85);p=min(4095,2*(r[0]|r[1]<<8));r[0:2]=[p&255,p>>8];r[6]=noise[i];r[7]=0xa0;r[8]=max(0,r[8]-2);r[9]=volume(env[i]*.7);rows.append(r)
add('Deep imported tone inside noise','Hybrid','Lower imported sequence gated by noise, with a separate noise body.',rows,2)
rows=[]
for i in range(65):
 a=fit_at(i/50);tone=imp_at(i/50);a[2:4]=tone[0:2];a[9]=max(0,tone[8]-5);a[7]=0xb1;rows.append(a)
add('Fitted explosion + faint AY motif','Hybrid','Fitted noise on A, quieter imported tone on B.',rows,2)
rows=[]
for i in range(65):
 t=i/50;r=imp_at(t);fade=max(0,1-t/.3);r[8]=volume(LEVEL[r[8]]*fade);r[6]=noise[i];r[7]=(r[7]&1)|0xaa;r[9]=volume(env[i]*min(1,t/.18));rows.append(r)
add('AY attack into arcade-noise tail','Hybrid','Imported attack dissolves into noise over the first300ms.',rows,2)
for kind,name,desc,duration in [
 ('thump','Noise + deep downward thump','Explosion noise with a short80-to28Hz falling tone.',1.05),
 ('whistle','Noise + falling whistle','Bright impact plus a brief1000-to100Hz tone falling into the noise.',.9),
 ('double','Double detonation','Two noise hits with a low gated resonant second voice.',1.2),
 ('metal','Metallic shrapnel','Short irregular tone fragments over a darkening noise cloud.',1.05)]:
 rows=[]
 for i in range(round(duration*50)):
  t=i/50;u=t/duration
  if kind=='thump':amp=.8*math.exp(-3.7*u);tone=.65*math.exp(-t*12);freq=80-52*min(1,t/.28);n=round(8+23*u);gate=False
  elif kind=='whistle':amp=.8*math.exp(-4*u);tone=.36*math.exp(-t*9);freq=1000*(.1**min(1,t/.4));n=round(2+26*u);gate=False
  elif kind=='double':amp=min(.95,.8*math.exp(-t*7)+.75*math.exp(-max(0,t-.22)*8)*(t>=.22));tone=amp*.55;freq=150-110*u;n=round(5+26*u);gate=True
  else:amp=.8*math.exp(-3.8*u);tone=.3*math.exp(-t*5)*(1 if i%5<2 else .2);freq=[770,431,211,593,113][i%5]*(1-.65*u);n=round(3+28*u);gate=False
  rows.append(frame(pb=period(freq),noise=n,va=amp,vb=tone,tb=True,nb=gate))
 add(name,'Explosion + tone',desc,rows,2)
assert len(entries)==20 and len({e['register_sha256']for e in entries})==20
source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [ROOT/'build/audio/goodboy_sfx_reference.json',ROOT/'build/audio/death_noise_r17/frames.json',ROOT/'build/audio/speech2ay_candidates/arcade_command53.wav']}
(OUT/'manifest.json').write_text(json.dumps(dict(tick_hz=50,sample_rate=22050,source_hashes=source_hashes,entries=entries),indent=2))
print('Generated20 distinct register sequences; max2effectchannels, musicCreserved')
