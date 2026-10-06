"""Fit full archival recordings with speech2ay's stateful AY optimizer."""
from pathlib import Path
from argparse import Namespace
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
from tsaudio.optimizer import optimize
args=Namespace(profile='filtered',search_mode='conservative',low=80,high=6500,
    gcc='gcc',ayumi=str(ROOT.parents[1]/'audio2ay-master/ayumi'),
    feedback_cutoff=11702.57,feedback_gain=7.8,objective='joint',passes=4)
metadata=[]
for name in ['run-coward','i-hunger']:
    source=ROOT/f'assets/{name}-arcade.wav'
    out=ROOT/'build/audio-fit'/name;out.mkdir(parents=True,exist_ok=True)
    raw,count,info=optimize(source,3,args,out)
    (ROOT/f'assets/{name}.ay').write_bytes(raw)
    (out/'report.json').write_text(json.dumps(info,indent=2))
    metadata.append(dict(name=name,count=count,bytes=len(raw),seconds=info['seconds'],
        source=source.name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        source_seconds=info['source_seconds'],codec='speech2ay harmonic3 + conservative ayfit',
        optimizer=info['optimizer']))
    print(name,info['optimizer'],flush=True)
(ROOT/'assets/audio.json').write_text(json.dumps(metadata,indent=2))
