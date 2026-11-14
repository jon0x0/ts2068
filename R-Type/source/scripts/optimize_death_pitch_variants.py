"""speech2ay/Ayumi stateful bounded fits for53–60; preserve arcade pitch guide."""
from pathlib import Path
import sys,json,hashlib,os,shutil,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/audio/death_pitch_variants';tool=ROOT/'../../speech2ay';sys.path.insert(0,str(tool))
from tsaudio import search
from tsaudio.codecs import source
from tsaudio.dsp import resample
ayumi=ROOT/'../../audio2ay-master/ayumi';gcc=shutil.which('gcc');exe=OUT/'ay-worker.exe';assert gcc
subprocess.run([gcc,'-O2','-std=c99','-I'+str(ayumi),str(tool/'tsaudio/ay_optimizer_worker.c'),str(ayumi/'ayumi.c'),'-lm','-o',str(exe)],check=True)
env=dict(os.environ);env['PATH']=str(Path(gcc).parent)+os.pathsep+env['PATH']
rate,target=source(ROOT/'build/audio/speech2ay_candidates/arcade_command53.wav');target=np.asarray(resample(target,rate,44100))
manifest=json.loads((OUT/'manifest.json').read_text());manifest['entries']=[e for e in manifest['entries']if e['id']<=52];reports=[]
specs=[(53,41,'Pitch locked / spectrum',0,.25),(54,42,'Pitch locked / texture',0,1),(55,45,'Pitch locked / wide contour',0,.5),(56,46,'Pitch locked / clear tone',0,.8),(57,49,'Fine pitch / explosive attack',.02,.35),(58,50,'Fine pitch / loudness contour',.02,.6),(59,51,'Fine pitch / low noise gate',.02,1.2),(60,52,'Fine pitch / articulated crack',.02,.5)]
for ident,parent,label,tolerance,pweight in specs:
 base=json.loads((OUT/(str(parent)+'.json')).read_text())['register_frames'];seed=[r+[1,0,255]for r in base];sim=search.Simulator(exe,env,11702.57,7.8)
 def render(rows):
  sim.command(2);a=[]
  for r in rows:a.extend(sim.evaluate([r],882)[0]);sim.command(1,0)
  return np.asarray(a)
 baseline=render(seed);expected=np.pad(target,(0,max(0,len(baseline)-len(target))))[:len(baseline)];expected=expected*np.std(baseline)/(np.std(expected)+1e-12);sim.command(2);context=np.zeros(1024);chosen=[];costs=[];oldcosts=[];max_pitch_error=0;sample_candidates=0
 try:
  for i,r in enumerate(seed):
   lo=i*882;hi=lo+882;goal=np.r_[np.pad(expected[max(0,lo-1024):lo],(max(0,1024-lo),0)),expected[lo:hi]];choices=[r.copy()];pa=r[0]|r[1]<<8
   if r[8]or r[9]:
    for n in sorted({max(1,r[6]-3),r[6],min(31,r[6]+3)}):
     for va in sorted({max(1,r[8]-1)if r[8]else 0,r[8],min(15,r[8]+1)if r[8]else 0}):
      for vb in sorted({max(1,r[9]-1)if r[9]else 0,r[9],min(15,r[9]+1)if r[9]else 0}):
       c=r.copy();c[6]=n;c[8]=va;c[9]=vb;choices.append(c)
    for factor in ([1-tolerance,1+tolerance]if tolerance else []):
     c=r.copy();p=int(np.clip(round(pa*factor),1,4095));c[0:2]=[p&255,p>>8];choices.append(c)
    for mask in [r[7]|2,r[7]&~2]:
     c=r.copy();c[7]=mask;choices.append(c)
   choices=list(dict.fromkeys(tuple(c)for c in choices));sample_candidates+=len(choices);waves=sim.evaluate(choices,882);parts=search.score_components(context,waves,goal);cost=parts['spectrum']+pweight*parts['periodicity']+.08*parts['roughness'];idx=int(np.argmin(cost));best=list(choices[idx]);audio=waves[idx];sim.command(1,idx);context=np.r_[context,audio][-1024:];chosen.append(best[:11]);costs.append(float(cost[idx]));oldcosts.append(float(cost[0]));bp=best[0]|best[1]<<8;max_pitch_error=max(max_pitch_error,abs(bp/max(1,pa)-1))
   # No I/O, third-channel or envelope ownership may leak into the effect.
   assert best[4:6]==[0,0]and best[10]==0 and not(best[7]&64)
   if i%20==0:print(ident,'frame',i,'/',len(seed),flush=True)
 finally:sim.close()
 assert max_pitch_error<=tolerance+.012,'bounded pitch changed too far'
 assert np.all(np.asarray(costs)<=np.asarray(oldcosts)+1e-10)
 entry=dict(id=ident,file=str(ident),name=label+' — optimized'+str(parent),group='speech2ay / Ayumi optimized',description=f'Actual stateful fit of{parent}: noise/levels and B gate optimized against arcade53; '+('A pitch locked exactly.'if tolerance==0 else 'A pitch held within2% plus register quantization.'),channels=2,frames=len(chosen),seconds=len(chosen)/50,register_sha256=hashlib.sha256(bytes(v for r in chosen for v in r)).hexdigest(),optimized=True,optimized_from=parent,optimizer='speech2ay search.Simulator / score_components, stateful Ayumi',pitch_tolerance=tolerance)
 (OUT/(str(ident)+'.json')).write_text(json.dumps(dict(tick_hz=50,channels=2,parents=[33,37],optimized_from=parent,register_frames=chosen),indent=2));manifest['entries'].append(entry);report=dict(id=ident,seed=parent,frames=len(chosen),evaluated_candidates=sample_candidates,pitch_tolerance=tolerance,max_register_pitch_error=max_pitch_error,mean_seed_cost_in_selected_history=float(np.mean(oldcosts)),mean_selected_cost=float(np.mean(costs)),objective='spectrum + weighted periodicity +.08roughness; scores do not prove listening quality',same_anchor_per_candidate=True,passed=True);reports.append(report);(OUT/'optimization.json').write_text(json.dumps(dict(method='Maintained speech2ay stateful Ayumi evaluation, 882samples/tick=50Hz',tool_hashes={n:hashlib.sha256((tool/'tsaudio'/n).read_bytes()).hexdigest()for n in ['search.py','ay_optimizer_worker.c']},results=reports),indent=2));(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('Completed',ident,'cost',report['mean_seed_cost_in_selected_history'],'->',report['mean_selected_cost'],flush=True)
assert len(manifest['entries'])==20 and len({e['register_sha256']for e in manifest['entries']})==20
print('Eight actual bounded Ayumi fits complete; twenty choices41–60ready')
