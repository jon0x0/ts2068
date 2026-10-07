"""Fetch archived arcade clips and encode full recordings for the native AY ISR."""
from pathlib import Path
import hashlib
import json
import sys
import subprocess

root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root.parents[1]/'speech2ay'))
from tsaudio.codecs import encode

for name,url in [('i-am-sinistar','https://seanriddle.com/iamsinis.wav'),
                 ('sinistar-roar','https://seanriddle.com/aargh.wav')]:
    source=root/'assets'/f'{name}-arcade.wav'
    if not source.exists():
        subprocess.run(['curl.exe','--fail','--location','--max-time','30',
                        '--user-agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                        '--referer','https://seanriddle.com/willy2.html',
                        '--output',str(source),url],check=True)
    raw,count,info=encode(source,'harmonic3')
    (root/'assets'/f'{name}.ay').write_bytes(raw)
    report=dict(frames=count,bytes=len(raw),source=url,
                sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                seconds=info['seconds'],source_seconds=info['source_seconds'])
    (root/'assets'/f'{name}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(name,report)
