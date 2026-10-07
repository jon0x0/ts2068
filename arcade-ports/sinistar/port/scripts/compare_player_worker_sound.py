"""Audition source-derived FNOISE variants; no cartridge/asset changes."""
from pathlib import Path
import wave,json,shutil
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/prepare_explosion_sfx.py').read_text()
fn=source[source.index('def cannon():'):source.index("if __name__")]
fn=fn.replace('def cannon():','def cannon(samples=1000, distortion=True, maximum=255):').replace('freq=255<<8','freq=maximum<<8').replace('remaining=1000','remaining=samples').replace('((freq>>8)&hi)','((freq>>8)&hi if distortion else (freq>>8))')
ns={'np':np};exec(fn,ns)
render=ns['cannon'];rate,worker=render();_,impact=render(128,False,192);_,blast=render(4000,True,255)
# QPLDIE issues 07, waits 0C ticks, then issues 08. Model command replacement.
attack=np.zeros(round(rate*12/60.1145));attack[:min(len(impact),len(attack))]=impact[:len(attack)]
player=np.concatenate([attack,blast])
out=ROOT/'build/player-worker-sound-comparison';out.mkdir(exist_ok=True)
def save(name,data):
 with wave.open(str(out/name),'wb') as w:
  w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes((np.clip(data,-1,1)*24000).astype('<i2').tobytes())
save('worker-source.wav',worker);save('player-source.wav',player)
shutil.copy2(ROOT/'build/explosion-audio-v22/after.wav',out/'current-worker-ay.wav')
meta={'worker_seconds':len(worker)/rate,'player_seconds':len(player)/rate,'method':'Source-derived approximate FNOISE reconstruction, not an arcade recording; fixed initial noise seed; isolated full decay with no later sound commands. Player includes 12-tick impact-to-explosion command delay.'}
(out/'manifest.json').write_text(json.dumps(meta,indent=2))
(out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Player vs worker explosions</title><style>body{background:#111;color:#eee;font:18px system-ui;max-width:800px;margin:40px auto;padding:20px}section{background:#222;padding:20px;margin:20px 0;border-radius:12px}audio{width:100%}p{line-height:1.5}</style><h1>Player vs worker explosions</h1><p>The first two clips reconstruct the original arcade sound routines. They are approximations, not arcade recordings or AY conversions. Both play their full isolated decay; later game sounds can interrupt them.</p><section><h2>Worker — original routine</h2><p>One distorted CANNON blast.</p><audio controls src="worker-source.wav"></audio></section><section><h2>Player — original two-part routine</h2><p>A short GUNSHOT impact, followed after 12 game ticks by the longer C4NNON blast.</p><audio controls src="player-source.wav"></audio></section><section><h2>Current port — AY explosion</h2><p>The sound currently reused for worker and player-death explosions. This is an isolated AY preview; actual gameplay may interrupt or retrigger it.</p><audio controls src="current-worker-ay.wav"></audio></section><script>for(const a of document.querySelectorAll('audio'))a.addEventListener('play',()=>{for(const b of document.querySelectorAll('audio'))if(a!==b)b.pause()})</script>''',encoding='utf-8')
print(json.dumps(meta))
