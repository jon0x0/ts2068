"""Ayumi audition of the cartridge's packed attack and existing explosion."""
from pathlib import Path
import os, sys, shutil, wave
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
from tsaudio import search
out=ROOT/'port/build/player-impact-audio';out.mkdir(exist_ok=True)
env=dict(os.environ);env['PATH']=str(Path(shutil.which('gcc')).parent)+os.pathsep+env['PATH']
sim=search.Simulator(ROOT/'port/build/explosion-audio-v22/ay-worker.exe',env,11702.57,7.8)
attack=np.frombuffer((ROOT/'assets/sfx-player-impact.ay').read_bytes(),dtype=np.uint8).reshape(-1,14).tolist()
raw=np.frombuffer((ROOT/'assets/sfx-explosion.ay').read_bytes(),dtype=np.uint8).reshape(-1,14).tolist()
blast=[raw[(i//3)*3] for i in range(len(raw))]
try:
    sounds={'existing':search.render(sim,blast),'with-impact':search.render(sim,attack+blast)}
finally:sim.close()
gain=.90/max(np.max(np.abs(v)) for v in sounds.values())
for name,data in sounds.items():
    with wave.open(str(out/(name+'.wav')),'wb') as w:
        w.setparams((1,2,44100,0,'NONE','not compressed'))
        w.writeframes(np.clip(data*gain*32767,-32768,32767).astype('<i2').tobytes())
(out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Player death impact</title><style>body{background:#111;color:#eee;font:18px system-ui;max-width:760px;margin:40px auto;padding:20px}audio{width:100%}</style><h1>Player death: short initial impact</h1><p>Actual AY register previews, using the same volume scale. The new source-derived GUNSHOT attack lasts twelve refreshes (0.20 seconds), then the existing explosion begins. These play one uninterrupted blast; the in-game death animation retriggers later bursts. Speech retains priority.</p><h2>Existing explosion</h2><audio controls src="existing.wav"></audio><h2>With new player impact</h2><audio controls src="with-impact.wav"></audio><script>for(const a of document.querySelectorAll('audio'))a.addEventListener('play',()=>{for(const b of document.querySelectorAll('audio'))if(a!==b)b.pause()})</script>''',encoding='utf-8')
print(out/'index.html')
