from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/audio/death_triangle_trials';OUT.mkdir(exist_ok=True);CLOCK=1764750
entries=[]
specs=[(61,50,'ideal',1,'50 — ideal triangle reference'),(62,59,'ideal',1,'59 — ideal triangle reference'),(63,50,'envelope',1,'50 — AY triangle-envelope tone'),(64,59,'envelope',1,'59 — AY triangle-envelope tone'),(65,50,'gated',1,'50 — noise-gated AY triangle envelope'),(66,59,'gated',1,'59 — noise-gated AY triangle envelope'),(67,50,'envelope',.5,'50 — lower-octave AY triangle envelope'),(68,59,'envelope',.5,'59 — lower-octave AY triangle envelope')]
parents={}
for ident,parent,kind,scale,name in specs:
 p=ROOT/f'build/audio/death_pitch_variants/{parent}.json';source=json.loads(p.read_text())['register_frames'];parents[parent]=hashlib.sha256(p.read_bytes()).hexdigest();rows=[];triangle=[];errors=[]
 for i,s in enumerate(source):
  frequency=CLOCK/(16*max(1,s[0]|s[1]<<8))*scale;r=s.copy()+[1,0,255]
  if kind=='ideal':r[8]=0;triangle.append(dict(hz=frequency,volume=s[8]))
  else:
   ep=max(1,min(65535,round(CLOCK/(512*frequency))));r[11:13]=[ep&255,ep>>8];r[13]=14 if i==0 else 255;r[8]=16 if s[8]>=4 else 0;r[7]=(s[7]|1)&(~8 if kind=='gated' else 255)
   if kind!='gated':r[7]|=8
   r[9]=min(15,s[9]+1)if s[9]else 0
   errors.append(abs(CLOCK/(512*ep)/frequency-1))
  r[4:6]=[0,0];r[10]=0;rows.append(r)
 rows[-1][8]=rows[-1][9]=0
 entry=dict(id=ident,file=str(ident),parent=parent,name=name,kind=kind,channels=2,frames=len(rows),seconds=len(rows)/50,hardware_feasible=kind!='ideal',octave_scale=scale,description=('Software-only linear triangle on A with parent B noise; preserves parent A loudness curve. Not a native AY waveform.'if kind=='ideal'else 'Native repeating AY envelope on A; stepped/logarithmic triangle-like shape, fixed peak while enabled. B retains noise contour; C reserved for music.'),max_envelope_pitch_error=max(errors)if errors else None)
 (OUT/f'{ident}.json').write_text(json.dumps(dict(tick_hz=50,register_frames=rows,ideal_triangle=triangle or None,R13_255_means_skip=True),indent=2));entries.append(entry)
(OUT/'manifest.json').write_text(json.dumps(dict(tick_hz=50,sample_rate=22050,parents=parents,envelope_formula='Triangle full-cycle frequency=AYclock/(512*period); shape14; logarithmic16-step DAC is not an ideal linear triangle',entries=entries),indent=2));print('Built8triangle trials:2software references,6native envelope variants')
