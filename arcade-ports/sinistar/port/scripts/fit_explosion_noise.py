"""Noise-aware explosion fitting using speech2ay's stateful Ayumi simulator.

Fits the actual three-refresh register holds. No extra runtime work or channels.
"""
from pathlib import Path
import os,sys,subprocess,shutil,json,wave,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
TOOLKIT=ROOT.parents[1]/'speech2ay'
sys.path.insert(0,str(TOOLKIT))
from tsaudio import search
from tsaudio.codecs import source
from tsaudio.dsp import resample

def fit_noise(target,baseline,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    gcc=shutil.which('gcc');assert gcc,'GCC is required for the offline Ayumi fit'
    ayumi=ROOT.parents[1]/'audio2ay-master/ayumi'
    exe=out/'ay-worker.exe'
    subprocess.run([gcc,'-O2','-std=c99','-I'+str(ayumi),str(TOOLKIT/'tsaudio/ay_optimizer_worker.c'),str(ayumi/'ayumi.c'),'-lm','-o',str(exe)],check=True)
    env=dict(os.environ);env['PATH']=str(Path(gcc).parent)+os.pathsep+env['PATH']
    sim=search.Simulator(exe,env,11702.57,7.8)
    rows=np.frombuffer(baseline,dtype=np.uint8).reshape(-1,14).tolist()
    old=[rows[(i//3)*3] for i in range(len(rows))]
    old_audio=search.render(sim,old)
    rate,x=source(target)
    target_audio=np.asarray(resample(x,rate,44100))
    target_audio=np.pad(target_audio,(0,max(0,len(old_audio)-len(target_audio))))[:len(old_audio)]
    target_audio*=np.std(old_audio)/(np.std(target_audio)+1e-12)
    sim.command(2);context=np.zeros(1024);chosen=[];old_errors=[];new_errors=[]
    def scores(waves,expected):
        parts=search.score_components(context,waves,expected)
        # Explosion phase is stochastic. Penalize unwanted periodicity instead
        # of forcing correlation with a particular source-noise realization.
        return parts['spectrum']+2*parts['periodicity']+.05*parts['roughness']
    try:
        for i in range(0,len(rows),3):
            lo=round(i*44100/search.HZ);hi=round(min(i+3,len(rows))*44100/search.HZ)
            expected=np.r_[np.pad(target_audio[max(0,lo-1024):lo],(max(0,1024-lo),0)),target_audio[lo:hi]]
            seed=rows[i].copy();choices=[]
            for noise in range(1,32):
                for volume in range(16):
                    r=seed.copy();r[6]=noise;r[7]=0x37;r[8]=volume;choices.append(r)
            waves=sim.evaluate(choices,hi-lo);cost=scores(waves,expected)
            best=choices[int(np.argmin(cost))]
            # A slow tone gate can approximate the filtered-noise tail, while
            # the noise generator stays enabled in every non-silent frame.
            choices=[best]
            for period in np.unique(np.rint(np.geomspace(32,4095,18)).astype(int)):
                for noise in sorted({max(1,best[6]-3),best[6],min(31,best[6]+3)}):
                    for volume in range(max(0,best[8]-2),min(15,best[8]+2)+1):
                        r=best.copy();r[0]=int(period)&255;r[1]=int(period)>>8;r[6]=noise;r[7]=0x36;r[8]=volume;choices.append(r)
            waves=sim.evaluate(choices,hi-lo);cost=scores(waves,expected);best=choices[int(np.argmin(cost))]
            old_errors.append(float(scores(sim.evaluate([seed],hi-lo),expected)[0]));new_errors.append(float(min(cost)))
            audio=sim.evaluate([best],hi-lo)[0];sim.command(1,0)
            context=np.r_[context,audio][-1024:];chosen.extend([best]*min(3,len(rows)-i))
        new_audio=search.render(sim,chosen)
    finally:sim.close()
    gain=.90/max(np.max(abs(old_audio)),np.max(abs(new_audio)),1e-9)
    def wav(name,data):
        with wave.open(str(out/name),'wb') as w:
            w.setparams((1,2,44100,0,'NONE','not compressed'));w.writeframes(np.clip(data*gain*32767,-32768,32767).astype('<i2').tobytes())
    wav('before.wav',old_audio);wav('after.wav',new_audio)
    wav('comparison.wav',np.r_[old_audio,np.zeros(22050),new_audio])
    report=dict(method='speech2ay Ayumi noise-aware restricted search; 3-refresh stateful blocks',source_sha256=hashlib.sha256(Path(target).read_bytes()).hexdigest(),frames=len(rows),noise_frames=sum(not(r[7]&8) and r[8]>0 for r in chosen),mean_seed_cost=float(np.mean(old_errors)),mean_fitted_cost=float(np.mean(new_errors)),cost_note='Per-block costs use the candidate stream history; objective scores do not establish perceived quality.',register_periods=sorted({r[6] for r in chosen}))
    (out/'fit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)
    return bytes(v for r in chosen for v in r),report
