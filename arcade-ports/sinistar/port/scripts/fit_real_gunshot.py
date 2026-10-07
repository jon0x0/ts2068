"""Fit a recorded gunshot to channel-A noise at native refresh cadence.

Source: RemingtonGunshot.wav by fastson, Freesound 50618, CC BY 3.0.
Uses the downloaded public preview, with no game asset replacement.
"""
from pathlib import Path
import os, sys, json, wave, shutil, hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
from tsaudio import search
out=ROOT/'port/build/real-gunshot'
meta=json.loads((out/'analysis.json').read_text())
with wave.open(str(out/'analysis.wav'),'rb') as w:
    rate=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
assert rate==44100
start=round(meta['onset_seconds']*rate)
x=x[start:start+round(30*rate/search.HZ)]
env=dict(os.environ);env['PATH']=str(Path(shutil.which('gcc')).parent)+os.pathsep+env['PATH']
sim=search.Simulator(ROOT/'port/build/explosion-audio-v22/ay-worker.exe',env,11702.57,7.8)
# No tone or hardware envelope: noise A only, B/C muted, R13 skip sentinel.
choices=[[1,0,1,0,1,0,noise,55,vol,0,0,1,0,255] for noise in range(1,32) for vol in range(16)]
try:
    calibration=search.render(sim,[[1,0,1,0,1,0,12,55,15,0,0,1,0,255]]*4)
    target=x*(np.std(calibration)*.9/max(np.std(x[:len(calibration)]),1e-9))
    sim.command(2);context=np.zeros(1024);rows=[];costs=[]
    for i in range(30):
        lo=round(i*rate/search.HZ);hi=round((i+1)*rate/search.HZ)
        expected=np.r_[np.pad(target[max(0,lo-1024):lo],(max(0,1024-lo),0)),target[lo:hi]]
        waves=sim.evaluate(choices,hi-lo)
        parts=search.score_components(context,waves,expected)
        cost=parts['spectrum']+2*parts['periodicity']+.05*parts['roughness']
        best=int(np.argmin(cost));rows.append(choices[best].copy());costs.append(float(cost[best]))
        sim.command(1,best);context=np.r_[context,waves[best]][-1024:]
    audio=search.render(sim,rows)
finally:
    sim.close()
gain=.85/max(np.max(abs(audio)),np.max(abs(target)),1e-9)
def wav(name,samples):
    with wave.open(str(out/name),'wb') as w:
        w.setparams((1,2,rate,0,'NONE','not compressed'))
        w.writeframes(np.clip(samples*gain*32767,-32768,32767).astype('<i2').tobytes())
wav('recorded-reference.wav',target);wav('ay-noise-fit.wav',audio)
wav('ay-noise-fit-short.wav',audio[:round(12*rate/search.HZ)])
presets_path=ROOT/'port/ay-editor/presets.json'
presets=json.loads(presets_path.read_text(encoding='utf-8'))
for name,count,label in [('real-gunshot',12,'Real gunshot - fitted noise attack (0.20 s)'),('real-gunshot-full',30,'Real gunshot - fitted noise decay (0.50 s)')]:
    chosen=rows[:count];raw=bytes(v for r in chosen for v in r)
    packed=bytes(v for r in chosen for v in [r[0],r[1]*16+r[8],r[6]*4+(r[7]&1)+((r[7]&8)>>2)])
    (out/(name+'.ay')).write_bytes(raw);(out/(name+'.packed')).write_bytes(packed)
    presets=[p for p in presets if p['id']!=name]
    presets.append(dict(id=name,label=label,rows=chosen))
presets_path.write_text(json.dumps(presets),encoding='utf-8')
report=dict(source=meta['source'],author='fastson',license='CC BY 3.0',source_sha256=hashlib.sha256((out/'analysis.wav').read_bytes()).hexdigest(),onset_seconds=start/rate,method='Stateful speech2ay/Ayumi noise-only search: 31 noise periods x 16 fixed volumes per frame; spectral/energy and periodicity cost',frames=30,hz=search.HZ,short_frames=12,short_packed_bytes=36,rows=rows,costs=costs,note='Approximation of MP3 field-recording preview. Numerical fitting is not a listening-quality guarantee; cartridge unchanged.')
(out/'ay-fit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(noise=[r[6] for r in rows],volume=[r[8] for r in rows],short_bytes=36)))
