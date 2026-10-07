"""Source-derived QBANG/FNOISE reconstruction, then speech2ay harmonic1.

Boundary timing is approximate, not a 6800/circuit emulation. Existing effects
retain their original AY frames; only the storage format changes losslessly.
"""
from pathlib import Path
import hashlib,json,sys,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
from tsaudio.codecs import encode

def cannon():
    # CANNON: SAMPC=1000, DSFLG=1, FDFLG=1, FMAX=255, FLO=0.
    freq=255<<8; hi=0; lo=1; a=0; clock=0; events=[]
    while freq>7:
        remaining=1000
        while remaining:
            carry=((a>>3)^lo)&1
            oldhi=hi
            hi=(hi>>1)|(carry<<7)
            lo=(lo>>1)|((oldhi&1)<<7)
            slope=(((freq>>8)&hi)<<8)|(freq&255)
            b=freq&255
            up=a<=lo
            while remaining:
                remaining-=1
                if not remaining: break
                clock+=38
                events.append((clock,a))
                value=(a<<8)|b
                value=value+slope if up else value-slope
                a=(value>>8)&255; b=value&255
                if value<0 or value>65535 or (a>lo if up else a<=lo):break
            a=lo;clock+=62;events.append((clock,a))
        freq-=freq>>3
    rate=22050
    times=np.array([t for t,v in events])/(3579545/4)
    t=np.arange(int(times[-1]*rate)+1)/rate
    values=np.array([v for t,v in events])
    pcm=values[np.maximum(0,np.searchsorted(times,t,side='right')-1)].astype(float)
    pcm-=pcm.mean();pcm/=max(1,abs(pcm).max())
    return rate,pcm

if __name__=='__main__':
    rate,pcm=cannon()
    target=ROOT/'assets/sfx-explosion.wav'
    with wave.open(str(target),'wb') as w:
        w.setparams((1,2,rate,0,'NONE','not compressed'))
        w.writeframes((pcm*28000).astype('<i2').tobytes())
    raw,count,info=encode(target,'harmonic1')
    from fit_explosion_noise import fit_noise
    raw,fit=fit_noise(target,raw,ROOT/'port/build/explosion-audio-v22')
    target.with_suffix('.ay').write_bytes(raw)
    report=json.loads((ROOT/'assets/sfx-manifest.json').read_text())
    report['effects']=[e for e in report['effects'] if e['name']!='explosion']
    report['effects'].append(dict(name='explosion',preset='QBANG/CANNON/FNOISE',frames=count,seconds=len(pcm)/rate,wav_sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    total=0
    for effect in report['effects']:
        raw=(ROOT/f"assets/sfx-{effect['name']}.ay").read_bytes()
        rows=np.frombuffer(raw,dtype=np.uint8).reshape(-1,14)
        assert np.all(rows[:,[9,10]]==0) and np.all(rows[:,8]<16)
        assert np.all(rows[:,1]<16) and np.all(rows[:,6]<32) and np.all(rows[:,7]&0x36==0x36)
        step=3 if effect['name']=='explosion' else 1
        selected=rows[::step]
        packed=np.column_stack([selected[:,0],selected[:,1]*16+selected[:,8],selected[:,6]*4+(selected[:,7]&1)+((selected[:,7]&8)>>2)]).astype(np.uint8).tobytes()
        (ROOT/f"assets/sfx-{effect['name']}.packed").write_bytes(packed)
        effect.update(frames=len(selected),source_frames=len(rows),refresh_step=step,bytes=len(packed))
        total+=len(packed)
    assert total<=0x260,(total,'SFX must not overlap radar queue')
    report['format']='3 bytes: tone low, tone high/volume, noise/mixer; explosion holds each sample three refreshes'
    report['explosion_method']='QBANG filtered-noise reconstruction; speech2ay/Ayumi noise-aware fit to the actual 3-refresh register holds'
    report['explosion_fit']=fit
    (ROOT/'assets/sfx-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(cache_bytes=total,effects=report['effects']),indent=2))
