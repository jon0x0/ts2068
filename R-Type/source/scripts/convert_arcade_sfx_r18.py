from pathlib import Path
import sys,wave,json,hashlib
import numpy as np
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'../../speech2ay'))
from tsaudio.codecs import encode
o=r/'build/audio/speech2ay_candidates';o.mkdir(exist_ok=True)
with wave.open(str(r/'build/audio/arcade/isolated.wav')) as w:rate=w.getframerate();pcm=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,w.getnchannels()).mean(1)
report=[]
for i,id in enumerate([53,38,43,48,49,50,52,54,55,56,57,58,80,99]):
 start=(360+i*180)/55.017606
 clip=pcm[round(start*rate):round((start+2)*rate)].astype('<i2');source=o/f'arcade_command{id}.wav'
 with wave.open(str(source),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(clip.tobytes())
 if np.sqrt(np.mean(clip.astype(float)**2))<1: continue
 for channels in ([1,2] if id in [53,43,99] else [1]):
  raw,n,info=encode(source,f'harmonic{channels}',profile='filtered');assert len(raw)==n*14;name=f'command{id}_harmonic{channels}';(o/(name+'.bin')).write_bytes(raw)
  report.append(dict(name=name,command=id,channels=channels,frames=n,register_frames=[list(raw[p:p+11])for p in range(0,len(raw),14)],source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_rms=float(np.sqrt(np.mean(clip.astype(float)**2))),seconds=info['seconds'],conversion='speech2ay harmonic, filtered profile, 80–6500Hz',status='default in-game one-channel replacement' if channels==1 and id in [99,43,48,49,50,80,52,53] else 'comparison alternative'))
(o/'manifest.json').write_text(json.dumps(report,indent=2));print('Converted',len(report),'one/two-channel original arcade candidates')

(r/"build/audio/speech2ay_tool_provenance.json").write_text(json.dumps({n:hashlib.sha256((r/"../../speech2ay/tsaudio"/n).read_bytes()).hexdigest() for n in ["codecs.py","harmonic.py","bands.py","dsp.py"]},indent=2))
