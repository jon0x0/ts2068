"""Ten source-pitch experiments, each fitted by stock six-pass free ayfit."""
from pathlib import Path
from argparse import Namespace
from concurrent.futures import ProcessPoolExecutor,as_completed
import os,sys,json,shutil,subprocess,hashlib,wave,math
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
from tsaudio.optimizer import optimize
from tsaudio import search
from tsaudio.dsp import read_wav,resample
NARROW='--narrow' in sys.argv
OUT=ROOT/('port/build/roar-up-6-to-10' if NARROW else 'port/build/roar-ten-variations')
SOURCE=ROOT/'assets/sinistar-roar-arcade.wav'
# Knots use normalized clip time and frequency multipliers, not semitones.
VARIANTS=[
 ('01','Down 15%',[(0,.85),(1,.85)]),
 ('02','Down 10%',[(0,.90),(1,.90)]),
 ('03','Down 5%',[(0,.95),(1,.95)]),
 ('04','Up 5%',[(0,1.05),(1,1.05)]),
 ('05','Up 10%',[(0,1.10),(1,1.10)]),
 ('06','Up 15%',[(0,1.15),(1,1.15)]),
 ('07','Threatening rise',[(0,.85),(.25,.90),(.75,1.10),(1,1.00)]),
 ('08','Descending growl',[(0,1.10),(.25,1.05),(.75,.90),(1,.85)]),
 ('09','Rise then growl',[(0,.90),(.25,.95),(.60,1.15),(.90,.90),(1,.85)]),
 ('10','Deep growl',[(0,.90),(.30,.85),(.65,.95),(1,.80)]),
]
if NARROW:
 VARIANTS=[
  ('01','Steady +6%',[(0,1.06),(1,1.06)]),
  ('02','Steady +8%',[(0,1.08),(1,1.08)]),
  ('03','Steady +10%',[(0,1.10),(1,1.10)]),
  ('04','Slow rise',[(0,1.06),(1,1.10)]),
  ('05','Slow fall',[(0,1.10),(1,1.06)]),
  ('06','Middle crest',[(0,1.06),(.55,1.10),(1,1.06)]),
  ('07','Middle dip',[(0,1.10),(.55,1.06),(1,1.10)]),
  ('08','Early crest',[(0,1.06),(.25,1.10),(.70,1.08),(1,1.06)]),
  ('09','Late crest',[(0,1.06),(.55,1.07),(.85,1.10),(1,1.08)]),
  ('10','Rise and settle',[(0,1.08),(.35,1.10),(.75,1.06),(1,1.07)]),
 ]

def pitch_at(t,knots):
 for (a,x),(b,y) in zip(knots,knots[1:]):
  if t<=b:
   f=max(0,min(1,(t-a)/(b-a)));f=f*f*(3-2*f)
   return x+(y-x)*f
 return knots[-1][1]

def work(item):
 ident,label,knots=item;out=OUT/ident;out.mkdir(parents=True,exist_ok=True)
 reportfile=out/'report.json'
 if reportfile.exists() and (out/'render.npy').exists():
  cached=json.loads(reportfile.read_text())
  assert cached['pitch_knots']==[list(k) for k in knots] and cached['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'Cached conversion has different input'
  return cached
 print(f'{ident}: fitting {label}',flush=True)
 with wave.open(str(SOURCE),'rb') as w:duration=w.getnframes()/w.getframerate()
 samples=round(duration*44100)
 changes=[(i*.04,pitch_at(i*.04/duration,knots)) for i in range(1,math.ceil(duration/.04))]
 (out/'pitch.commands').write_text(''.join(f'{t:.5f} rubberband@roar pitch {p:.8f};\n' for t,p in changes),encoding='utf-8')
 filters=f'aresample=44100,asendcmd=f=pitch.commands,rubberband@roar=pitch={knots[0][1]}:tempo=1,apad,atrim=end_sample={samples}'
 source=out/'source.wav'
 subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(SOURCE),'-af',filters,'-ac','1','-c:a','pcm_s16le',str(source)],cwd=out,check=True)
 with wave.open(str(source),'rb') as w:assert w.getnframes()==samples
 args=Namespace(profile='filtered',search_mode='free',low=80,high=6500,gcc='gcc',
  ayumi=str(ROOT.parents[1]/'audio2ay-master/ayumi'),feedback_cutoff=11702.57,feedback_gain=7.8,objective='joint',passes=6)
 raw,count,info=optimize(source,3,args,out)
 (out/'optimized.ay').write_bytes(raw)
 env=dict(os.environ);env['PATH']=str(Path(shutil.which('gcc')).parent)+os.pathsep+env['PATH']
 sim=search.Simulator(out/'ay-worker.exe',env,11702.57,7.8)
 try:audio=search.render(sim,np.frombuffer(raw,dtype=np.uint8).reshape(-1,14).tolist())
 finally:sim.close()
 np.save(out/'render.npy',audio)
 r=dict(id=ident,label=label,pitch_knots=knots,pitch_method='Rubber Band, tempo 1, smoothstep-interpolated commands every 40 ms',
  source_seconds=duration,frames=count,optimizer=info['optimizer'],source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
  transformed_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),ay_sha256=hashlib.sha256(raw).hexdigest())
 reportfile.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 print(f'{ident}: complete; {count} frames',flush=True)
 return r

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if NARROW:
  assert all(1.06<=pitch_at(t,knots)<=1.10 for _,_,knots in VARIANTS for t in np.linspace(0,1,1001))
  # Same source, pitch transform and six-pass settings: reuse the exact +10%
  # conversion already auditioned instead of rerunning an identical search.
  prior=ROOT/'port/build/roar-ten-variations/05'
  if not (OUT/'03/report.json').exists():
   cached=json.loads((prior/'report.json').read_text())
   assert cached['pitch_knots']==[[0,1.1],[1,1.1]] and cached['optimizer']['passes']==6 and cached['optimizer']['search_mode']=='free'
   assert cached['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
   (OUT/'03').mkdir(exist_ok=True)
   for name in ['source.wav','optimized.ay','render.npy','pitch.commands']:shutil.copy2(prior/name,OUT/'03'/name)
   cached.update(id='03',label='Steady +10%',reused_from='../roar-ten-variations/05')
   (OUT/'03/report.json').write_text(json.dumps(cached,indent=2)+'\n',encoding='utf-8')
   print('03: reusing verified steady +10% conversion',flush=True)
 reports=[]
 with ProcessPoolExecutor(max_workers=3) as pool:
  for f in as_completed([pool.submit(work,item) for item in VARIANTS]):reports.append(f.result())
 reports.sort(key=lambda r:r['id'])
 signals={}
 for r in reports:
  ident=r['id'];signals[ident+'/ay.wav']=np.load(OUT/ident/'render.npy')
  rate,x=read_wav(OUT/ident/'source.wav');signals[ident+'/listen-source.wav']=np.asarray(resample(x,rate,44100))
 rate,x=read_wav(SOURCE);signals['original.wav']=np.asarray(resample(x,rate,44100))
 # Equal full-clip RMS, then one common peak safety factor. No per-frame AGC.
 for name,audio in signals.items():
  audio=audio-np.mean(audio);signals[name]=audio/max(float(np.std(audio)),1e-12)
 gain=.9/max(float(np.max(abs(a))) for a in signals.values())
 for name,audio in signals.items():
  with wave.open(str(OUT/name),'wb') as w:
   w.setparams((1,2,44100,0,'NONE','not compressed'));w.writeframes(np.clip(audio*gain*32767,-32768,32767).astype('<i2').tobytes())
 (OUT/'manifest.json').write_text(json.dumps(dict(variants=reports,production_unchanged=True,level_matching='Full-clip RMS matched; common peak safety factor',optimizer='stock free search, three channels, six passes, joint objective'),indent=2)+'\n',encoding='utf-8')
 cards=[]
 for ident,label,knots in VARIANTS:
  contour=' → '.join(f'{round((v-1)*100):+d}%' for _,v in knots)
  if knots[0][1]==knots[-1][1] and len(knots)==2:contour=f'{round((knots[0][1]-1)*100):+d}% throughout'
  cards.append(f'<section id="v{ident}"><h2>{ident}. {label}</h2><p>{contour}</p><button onclick="play(\'{ident}/ay.wav\',\'{ident} AY\')">Play AY</button> <button onclick="play(\'{ident}/listen-source.wav\',\'{ident} source\')">Play source</button> <label>Verdict <select data-id="{ident}"><option value="">Unrated</option><option>Keep</option><option>Maybe</option><option>No</option></select></label></section>')
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ten Sinistar roar variations</title><style>body{background:#111722;color:#edf1fa;font:17px system-ui;max-width:960px;margin:auto;padding:24px}p{line-height:1.5;color:#bec9de}.player{position:sticky;top:0;background:#1b2537;padding:16px;border-radius:12px;z-index:1}audio{width:100%;margin-top:10px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}section{background:#1b2537;padding:18px;border-radius:12px}h2{font-size:20px;margin-top:0}button,select{background:#30476b;color:white;border:1px solid #6782aa;border-radius:6px;padding:8px;font:inherit;cursor:pointer}label{display:block;margin-top:14px}.active{outline:2px solid #8bd5ff}a{color:#a7ceff}</style><h1>Ten Sinistar roar variations</h1><p>Six small pitch shifts and four roar contours, all made from the complete original recording with its duration preserved. Each receives the same six-pass free AY optimization. Listen to AY first; source lets you hear the transformation before conversion.</p><div class="player"><strong id="now">Choose a variation</strong><audio id="audio" controls></audio><button onclick="playAll()">Play all ten AY versions</button> <button onclick="stop()">Stop</button> <button onclick="play('original.wav','Original recording')">Original</button></div><p>Levels are matched across clips. Keep / Maybe / No choices are saved in this browser. The playable game is unchanged.</p><div class="grid">CARDS</div><p><a href="manifest.json">Conversion settings and reports</a></p><script>
const a=document.getElementById('audio');let queue=[];
function start(file,label){a.src=file;document.getElementById('now').textContent=label;document.querySelectorAll('section').forEach(s=>s.classList.toggle('active',s.id==='v'+file.slice(0,2)));a.play().catch(()=>document.getElementById('now').textContent='Press play: '+label)}
function play(file,label){queue=[];start(file,label)}
function playAll(){queue=Array.from({length:10},(_,i)=>String(i+1).padStart(2,'0'));next()}
function next(){if(queue.length){const n=queue.shift();start(n+'/ay.wav',n+' AY')}else document.getElementById('now').textContent='Finished'}
a.addEventListener('ended',()=>{if(queue.length)next()});function stop(){queue=[];a.pause();a.currentTime=0}
document.querySelectorAll('select').forEach(s=>{try{s.value=localStorage.getItem('roar-ten-'+s.dataset.id)||''}catch{}s.onchange=()=>{try{localStorage.setItem('roar-ten-'+s.dataset.id,s.value)}catch{}}});
</script></html>'''.replace('CARDS',''.join(cards))
 if NARROW:
  page=page.replace('Ten Sinistar roar variations','Sinistar roar: +6% to +10%')
  page=page.replace('Six small pitch shifts and four roar contours','Three steady pitches and seven smooth contours, all confined to +6% through +10%')
  page=page.replace("'roar-ten-'","'roar-six-ten-'")
 (OUT/'index.html').write_text(page,encoding='utf-8')
 print('All ten previews ready: '+str(OUT/'index.html'),flush=True)

if __name__=='__main__':main()
