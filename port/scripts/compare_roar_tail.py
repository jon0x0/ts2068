"""Listening experiments only: leave the installed cartridge/audio untouched."""
from pathlib import Path
import json,os,sys,shutil,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
from tsaudio import search
from tsaudio.codecs import source
from tsaudio.dsp import resample

out=ROOT/'port/build/roar-tail-comparison';out.mkdir(parents=True,exist_ok=True)
old=json.loads((ROOT/'port/revisions/playable-roar-mix-v28/build/mining-assets.json').read_text())
rows=np.asarray(next(a['data'] for a in old if a['kind']=='speech' and a['index']==2),dtype=np.uint8).reshape(-1,14).tolist()
env=dict(os.environ);env['PATH']=str(Path(shutil.which('gcc')).parent)+os.pathsep+env['PATH']
sim=search.Simulator(ROOT/'port/build/roar-audio-v28/ay-worker.exe',env,11702.57,7.8)
before=search.render(sim,rows)
rate,x=source(ROOT/'assets/sinistar-roar-arcade.wav')
target=np.asarray(resample(x,rate,44100));target=np.pad(target,(0,max(0,len(before)-len(target))))[:len(before)]
target*=np.std(before[:44100])/(np.std(target[:44100])+1e-12)
results={'v28':before,'original':target};reports={}
try:
 for name,mixer in [('deeper',52),('roughened',4)]:
  sim.command(2);context=np.zeros(1024);chosen=[]
  for i,seed in enumerate(rows):
   lo=round(i*44100/search.HZ);hi=round((i+1)*44100/search.HZ)
   expected=np.r_[np.pad(target[max(0,lo-1024):lo],(max(0,1024-lo),0)),target[lo:hi]]
   def costs(waves):
    c=search.score_components(context,waves,expected)
    return c['spectrum']+4*c['periodicity']+.05*c['roughness']
   best=seed.copy()
   if i>=60:
    choices=[]
    for factor in (1.5,2,3):
     for noise in range(8,32,2):
      for vol in range(8,16):
       r=seed.copy();r[4]=r[6]=noise;r[5]=0;r[7]=mixer;r[10]=vol
       for ch,limit in [(0,2047),(1,1023)]:
        p=min(limit,max(1,round((r[2*ch]+256*r[2*ch+1])*factor)))
        r[2*ch:2*ch+2]=[p&255,p>>8]
        r[8+ch]=min(seed[8+ch],max(0,vol-4)) if mixer==52 else seed[8+ch]
       choices.append(r)
    values=costs(sim.evaluate(choices,hi-lo));best=choices[int(np.argmin(values))]
    for ch in (8,9,10):
     choices=[]
     for vol in range(16):
      if mixer==52 and ch<10 and vol>max(0,best[10]-4):continue
      if mixer==52 and ch==10 and vol<max(best[8:10])+4:continue
      r=best.copy();r[ch]=vol;choices.append(r)
     values=costs(sim.evaluate(choices,hi-lo));best=choices[int(np.argmin(values))]
   w=sim.evaluate([best],hi-lo)[0];sim.command(1,0)
   context=np.r_[context,w][-1024:];chosen.append(best)
  results[name]=search.render(sim,chosen)
  assert chosen[:60]==rows[:60]
  assert np.array_equal(results[name][:round(60*44100/search.HZ)],before[:round(60*44100/search.HZ)])
  (out/(name+'.ay')).write_bytes(bytes(v for r in chosen for v in r))
  reports[name]={'frames':len(chosen),'unchanged_opening_frames':60,'tail_mixer':mixer,'tail_rms':float(np.std(results[name][44100:]))}
  print(name,reports[name],flush=True)
finally:sim.close()
gain=.9/max(float(np.max(abs(x))) for x in results.values())
for name,data in results.items():
 with wave.open(str(out/(name+'.wav')),'wb') as w:
  w.setparams((1,2,44100,0,'NONE','not compressed'))
  w.writeframes(np.clip(data*gain*32767,-32768,32767).astype('<i2').tobytes())
reports['note']='Same gain and AY/filter model for every preview. Source is level-matched by its first second. Listening experiments, not installed cartridge streams.'
(out/'report.json').write_text(json.dumps(reports,indent=2)+'\n',encoding='utf-8')
(out/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Sinistar roar tail experiments</title><style>body{font:18px system-ui;background:#121620;color:#eee;max-width:760px;margin:40px auto;padding:20px}audio{width:100%}p{line-height:1.5}</style><h1>Roar: stronger, rougher tail</h1><p>Both experiments preserve the first second exactly. After that, the pitched channels are lowered and pure-tone-only frames are eliminated. All previews use the same gain.</p><h2>Current v28</h2><audio controls src="v28.wav"></audio><h2>A: deeper, noise-heavy tail</h2><audio controls src="deeper.wav"></audio><p>Quiet lower tones beneath a dominant noise channel.</p><h2>B: roughened growl</h2><audio controls src="roughened.wav"></audio><p>Noise also gates the two lower pitched channels, breaking up their clean tones.</p><h2>Original recording</h2><audio controls src="original.wav"></audio><p>These are AY synthesis approximations. The saved game remains unchanged while these alternatives are evaluated.</p></html>''',encoding='utf-8')
