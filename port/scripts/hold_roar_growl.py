"""Sustain the established ~0.75-second AY timbre; change only tail levels.

Listening preview, no production asset or cartridge changes.
"""
from pathlib import Path
import os,sys,json,shutil,wave,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
from tsaudio import search

out=ROOT/'port/build/roar-sustained-growl';out.mkdir(parents=True,exist_ok=True)
baseline=ROOT/'port/revisions/playable-roar-mix-v28/build/mining-assets.json'
rows=np.asarray(next(a['data'] for a in json.loads(baseline.read_text()) if a['kind']=='speech' and a['index']==2),dtype=np.uint8).reshape(-1,14).tolist()
# Frame 47 (~0.78 seconds) already contains both the strong pitch and noise.
# Hold one actual state, not a short loop that adds a repeating rasp.
anchor=rows[47].copy();assert anchor[7]==52
chosen=[r.copy() for r in rows[:48]]
count=round(2*search.HZ)
for frame in range(48,count):
    r=anchor.copy();t=frame/search.HZ
    drop=0 if t<1.55 else min(3,int((t-1.55)/.1)+1)
    r[8:11]=[max(0,v-drop) for v in anchor[8:11]]
    if t>=1.9:
        fade=max(0,(count-1-frame)/(count-1-round(1.9*search.HZ)))
        r[8:11]=[round(v*fade) for v in r[8:11]]
    chosen.append(r)
assert all(r[:8]==anchor[:8] and r[11:]==anchor[11:] for r in chosen[48:])
assert chosen[:48]==rows[:48] and chosen[-1][8:11]==[0,0,0]
env=dict(os.environ);env['PATH']=str(Path(shutil.which('gcc')).parent)+os.pathsep+env['PATH']
sim=search.Simulator(ROOT/'port/build/roar-audio-v28/ay-worker.exe',env,11702.57,7.8)
try:
    before=search.render(sim,rows);after=search.render(sim,chosen)
finally:sim.close()
opening=round(48*44100/search.HZ);assert np.array_equal(before[:opening],after[:opening])
gain=.9/max(np.max(abs(before)),np.max(abs(after)))
for name,audio in [('current',before),('sustained',after)]:
    with wave.open(str(out/(name+'.wav')),'wb') as w:
        w.setparams((1,2,44100,0,'NONE','not compressed'))
        w.writeframes(np.clip(audio*gain*32767,-32768,32767).astype('<i2').tobytes())
raw=bytes(v for r in chosen for v in r);(out/'sustained.ay').write_bytes(raw)
report=dict(anchor_frame=47,anchor_seconds=47/search.HZ,anchor_registers=anchor,frames=count,duration=count/search.HZ,unchanged_opening_frames=48,tail_changes='volume only; no sample loop, pitch change, mixer change, or noise-period change',ay_sha256=hashlib.sha256(raw).hexdigest(),production_unchanged=True)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(out/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Sustained Sinistar growl</title><style>body{background:#111722;color:#eee;font:18px system-ui;max-width:740px;margin:40px auto;padding:20px}audio{width:100%}p{line-height:1.5}</style><h1>Sustain the established growl</h1><p>The opening is unchanged. At 0.80 seconds the sound holds the actual AY tone/noise state from 0.78 seconds. Only the volume changes afterwards: a gentle taper after 1.55 seconds and a short fade to silence at 2 seconds. No short repeating loop.</p><h2>New sustained growl</h2><audio controls src="sustained.wav"></audio><h2>Current v28 reference</h2><audio controls src="current.wav"></audio><p>Both use the same AY model and gain. This is a listening preview; the playable cartridge is unchanged.</p></html>''',encoding='utf-8')
print(json.dumps(report,indent=2))
