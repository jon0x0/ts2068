"""Fit complete roar with pitched A/B and noise C; preserve existing voice codec.

Uses speech2ay's stateful Ayumi search, including the actual per-refresh holds.
Original harmonic stream remains an eligible choice on every frame.
"""
from pathlib import Path
import os, sys, shutil, subprocess, json, wave, hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
TOOLKIT=ROOT.parents[1]/'speech2ay'
sys.path.insert(0,str(TOOLKIT))
from tsaudio import search
from tsaudio.codecs import source
from tsaudio.dsp import resample

def main():
    out=ROOT/'port/build/roar-audio-v28';out.mkdir(parents=True,exist_ok=True)
    baseline=ROOT/'port/revisions/playable-piece-removal-v27/build/mining-assets.json'
    rows=next(a['data'] for a in json.loads(baseline.read_text()) if a['kind']=='speech' and a['index']==2)
    rows=np.asarray(rows,dtype=np.uint8).reshape(-1,14).tolist()
    gcc=shutil.which('gcc');assert gcc
    ayumi=ROOT.parents[1]/'audio2ay-master/ayumi';exe=out/'ay-worker.exe'
    subprocess.run([gcc,'-O2','-std=c99','-I'+str(ayumi),str(TOOLKIT/'tsaudio/ay_optimizer_worker.c'),str(ayumi/'ayumi.c'),'-lm','-o',str(exe)],check=True)
    env=dict(os.environ);env['PATH']=str(Path(gcc).parent)+os.pathsep+env['PATH']
    sim=search.Simulator(exe,env,11702.57,7.8)
    target=ROOT/'assets/sinistar-roar-arcade.wav'
    rate,x=source(target);audio=np.asarray(resample(x,rate,44100))
    before=search.render(sim,rows);audio=np.pad(audio,(0,max(0,len(before)-len(audio))))[:len(before)]
    audio*=np.std(before)/(np.std(audio)+1e-12)
    sim.command(2);context=np.zeros(1024);chosen=[];old_cost=[];new_cost=[]
    try:
        for i,seed in enumerate(rows):
            lo=round(i*44100/search.HZ);hi=round((i+1)*44100/search.HZ)
            expected=np.r_[np.pad(audio[max(0,lo-1024):lo],(max(0,1024-lo),0)),audio[lo:hi]]
            choices=[seed.copy()]
            for noise in range(1,32):
                for volume in range(4,16):
                    r=seed.copy();r[4]=noise;r[5]=0;r[6]=noise;r[7]=52;r[10]=volume
                    choices.append(r)
            def cost(waves):
                c=search.score_components(context,waves,expected)
                return c['spectrum']+2*c['periodicity']+.05*c['roughness']
            costs=cost(sim.evaluate(choices,hi-lo));best=choices[int(np.argmin(costs))]
            old_cost.append(float(costs[0]))
            # Refine the two pitched levels without changing their frequencies.
            for ch in (8,9):
                trials=[]
                for volume in range(16):
                    r=best.copy();r[ch]=volume;trials.append(r)
                costs=cost(sim.evaluate(trials,hi-lo));best=trials[int(np.argmin(costs))]
            new_cost.append(float(min(costs)))
            wavelet=sim.evaluate([best],hi-lo)[0];sim.command(1,0)
            context=np.r_[context,wavelet][-1024:];chosen.append(best)
        after=search.render(sim,chosen)
    finally:sim.close()
    payload=bytes(v for r in chosen for v in r)
    (ROOT/'assets/sinistar-roar.ay').write_bytes(payload)
    gain=.9/max(np.max(abs(before)),np.max(abs(after)),np.max(abs(audio)))
    for name,data in [('before',before),('after',after),('source',audio),('comparison',np.r_[before,np.zeros(22050),after])]:
        with wave.open(str(out/(name+'.wav')),'wb') as w:
            w.setparams((1,2,44100,0,'NONE','not compressed'))
            w.writeframes(np.clip(data*gain*32767,-32768,32767).astype('<i2').tobytes())
    report=dict(frames=len(rows),source_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),ay_sha256=hashlib.sha256(payload).hexdigest(),noise_frames=sum(r[7]==52 for r in chosen),mean_seed_cost=float(np.mean(old_cost)),mean_fitted_cost=float(np.mean(new_cost)),note='Objective improvement is not proof of perceived quality; compare the rendered audio.')
    (out/'fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(report)
def render_native():
    out=ROOT/'port/build/roar-audio-v28'
    env=dict(os.environ);env['PATH']=str(Path(shutil.which('gcc')).parent)+os.pathsep+env['PATH']
    sim=search.Simulator(out/'ay-worker.exe',env,11702.57,7.8)
    try:
        rows=json.loads((ROOT/'port/build/roar-live-frames.json').read_text())
        data=search.render(sim,rows)
        raw=(ROOT/'assets/sinistar-roar.ay').read_bytes()
        solo=search.render(sim,np.frombuffer(raw,dtype=np.uint8).reshape(-1,14).tolist())
    finally:sim.close()
    # Same amplitude scale as the earlier solo preview, not separate normalization.
    with wave.open(str(out/'after.wav'),'rb') as w:
        previous=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')/32767
    gain=np.max(abs(previous))/np.max(abs(solo))
    with wave.open(str(out/'hybrid.wav'),'wb') as w:
        w.setparams((1,2,44100,0,'NONE','not compressed'))
        w.writeframes(np.clip(data*gain*32767,-32768,32767).astype('<i2').tobytes())
    print('Rendered native AY writes: two bomb hits during one uninterrupted roar.')

if __name__=='__main__':
    if '--render-native' in sys.argv:render_native()
    else:main()
