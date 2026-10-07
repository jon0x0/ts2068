"""Run the stock speech2ay free optimizer on the complete original recording.

No handcrafted tail, pitch shift, fixed mixer, or cartridge packing constraints.
This produces a listening experiment without changing production assets.
"""
from pathlib import Path
from argparse import Namespace,ArgumentParser
import hashlib,json,os,shutil,sys,wave,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
from tsaudio.optimizer import optimize
from tsaudio import search
from tsaudio.codecs import encode,source
from tsaudio.dsp import resample

parser=ArgumentParser()
parser.add_argument('--pitch-ratio',type=float,default=1.0)
options=parser.parse_args()
assert options.pitch_ratio in (1.0,.7), 'Supported comparisons: original and 30% lower pitch'
shifted=options.pitch_ratio!=1
out=ROOT/('port/build/roar-pitch-down-30' if shifted else 'port/build/roar-full-optimizer');out.mkdir(parents=True,exist_ok=True)
original=ROOT/'assets/sinistar-roar-arcade.wav'
wav=original
if shifted:
    with wave.open(str(original),'rb') as w:duration=w.getnframes()/w.getframerate()
    wav=out/'pitched-source.wav'
    samples=round(duration*44100)
    subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(original),
        '-af',f'aresample=44100,rubberband=pitch={options.pitch_ratio}:tempo=1,apad,atrim=end_sample={samples}',
        '-ac','1','-c:a','pcm_s16le',str(wav)],check=True)
    with wave.open(str(wav),'rb') as w:assert w.getnframes()==samples and w.getframerate()==44100
args=Namespace(profile='filtered',search_mode='free',low=80,high=6500,
    gcc='gcc',ayumi=str(ROOT.parents[1]/'audio2ay-master/ayumi'),
    feedback_cutoff=11702.57,feedback_gain=7.8,objective='joint',passes=6)
print(f'Starting stock optimizer: pitch ratio {options.pitch_ratio}, free search, 3 channels, 6 passes, joint objective.',flush=True)
raw,count,info=optimize(wav,3,args,out)
(out/'optimized.ay').write_bytes(raw)
baseline,_,_=encode(wav,'harmonic3',args.low,args.high,args.profile)
assets=json.loads((ROOT/'port/revisions/playable-roar-mix-v28/build/mining-assets.json').read_text())
current=bytes(next(a['data'] for a in assets if a['kind']=='speech' and a['index']==2))
rows=lambda b:np.frombuffer(b,dtype=np.uint8).reshape(-1,14).tolist()
env=dict(os.environ);env['PATH']=str(Path(shutil.which('gcc')).parent)+os.pathsep+env['PATH']
sim=search.Simulator(out/'ay-worker.exe',env,args.feedback_cutoff,args.feedback_gain)
try:
    rendered={name:search.render(sim,rows(data)) for name,data in [('optimized',raw),('harmonic-baseline',baseline),('current-v28',current)]}
    if shifted:
        rendered['previous-optimizer']=search.render(sim,rows((ROOT/'port/build/roar-full-optimizer/optimized.ay').read_bytes()))
finally:sim.close()
# Direct original WAV for the listening reference, no pitch/time modification.
from tsaudio.dsp import read_wav
rate,audio=read_wav(wav);audio=np.asarray(resample(audio,rate,44100))
audio*=np.std(rendered['harmonic-baseline'])/(np.std(audio)+1e-12)
rendered['original']=audio
if shifted:
    rate,unshifted=read_wav(original);unshifted=np.asarray(resample(unshifted,rate,44100))
    unshifted*=np.std(audio)/(np.std(unshifted)+1e-12)
    rendered['unshifted-source']=unshifted
gain=.9/max(float(np.max(abs(a))) for a in rendered.values())
for name,audio in rendered.items():
    with wave.open(str(out/(name+'.wav')),'wb') as w:
        w.setparams((1,2,44100,0,'NONE','not compressed'))
        w.writeframes(np.clip(audio*gain*32767,-32768,32767).astype('<i2').tobytes())
r=rows(raw)
report=dict(source=str(wav),source_sha256=hashlib.sha256(wav.read_bytes()).hexdigest(),frames=count,
    original_source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),pitch_ratio=options.pitch_ratio,
    pitch_method='FFmpeg Rubber Band, tempo=1, original duration preserved' if shifted else 'none',
    seconds=count/search.HZ,ay_sha256=hashlib.sha256(raw).hexdigest(),settings=vars(args),
    optimizer=info['optimizer'],changed_frames=sum(a!=b for a,b in zip(r,rows(baseline))),
    mixer_values=sorted(set(x[7] for x in r)),noise_periods=sorted(set(x[6] for x in r)),
    envelope_frames=sum(any(v==16 for v in x[8:11]) for x in r),
    envelope_shape_writes=sum(x[13]!=255 for x in r),production_unchanged=True,
    note='Numerical acceptance is not a subjective listening verdict. Current cartridge packing and playback do not support all free-search envelope/routing states.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(out/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Original roar — full AY optimizer</title><style>body{font:18px system-ui;background:#111722;color:#eee;max-width:780px;margin:40px auto;padding:20px}audio{width:100%}p{line-height:1.5}a{color:#8cf}</style><h1>Original roar: full optimizer</h1><p>The complete original recording, processed by the stock speech2ay free optimizer: three channels, six search passes, joint spectral/waveform objective. Tone frequencies, volumes, noise routing and envelopes are free to change. No manual pitch shift or sustained tail.</p><h2>Full optimizer result</h2><audio controls src="optimized.wav"></audio><h2>Original recording</h2><audio controls src="original.wav"></audio><h2>Current v28</h2><audio controls src="current-v28.wav"></audio><h2>Optimizer's harmonic starting point</h2><audio controls src="harmonic-baseline.wav"></audio><p>All synthesized previews use the same AY/filter model and gain. The original is level-matched to the harmonic starting point. These are listening previews; the playable cartridge remains unchanged. <a href="report.json">Settings and numerical results</a>.</p></html>''',encoding='utf-8')
print(json.dumps(report,indent=2),flush=True)
if shifted:
    page=(out/'index.html').read_text(encoding='utf-8')
    page=page.replace('Original roar: full optimizer','Roar pitched down 30%: full optimizer')
    page=page.replace('No manual pitch shift or sustained tail.','The whole original recording was first lowered to 70% pitch using Rubber Band, with its duration preserved. No hand-edited tail or forced noise routing.')
    page=page.replace('Original recording</h2>','Pitch-lowered source recording</h2>')
    page=page.replace('<h2>Current v28</h2><audio controls src="current-v28.wav"></audio>', '<h2>Previous optimizer at original pitch</h2><audio controls src="previous-optimizer.wav"></audio><h2>Unmodified source recording</h2><audio controls src="unshifted-source.wav"></audio>')
    (out/'index.html').write_text(page,encoding='utf-8')
