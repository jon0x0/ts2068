"""Encode the archived Beware! I Live! clip using the local speech2ay codec."""
from pathlib import Path
import sys,json,hashlib
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root.parents[1]/'speech2ay'))
from tsaudio.codecs import encode
source=root/'assets/beware-i-live-arcade.wav'
raw,count,info=encode(source,'harmonic3')
(root/'assets/beware-i-live.ay').write_bytes(raw)
(root/'assets/beware-i-live.json').write_text(json.dumps(dict(frames=count,bytes=len(raw),source='https://seanriddle.com/bewareil.wav',sha256=hashlib.sha256(source.read_bytes()).hexdigest(),seconds=info['seconds'],source_seconds=info['source_seconds']),indent=2),encoding='utf-8')
print(count,len(raw))
