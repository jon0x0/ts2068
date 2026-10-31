"""Package the current native demo and its emulator-captured preview."""
from pathlib import Path
from PIL import Image
import json, zipfile

r=Path(__file__).resolve().parent
validation=json.loads((r/'validation.json').read_text())
order=[(1,0,0),(3,1,0),(1,1,1),(3,0,1)]
frames=[];durations=[];preview=Image.new('RGB',(1024,768))
for n,((phase,pic,hi),direction) in enumerate(zip(order,validation['directions'])):
    d=int(direction=='up')
    splits=range(192,-1,-2) if d else range(0,193,2)
    for k,split in enumerate(splits):
        p=r/'prover-frames'/f'{phase}-{pic}-{hi}-{d}-{split:03}.ppm'
        im=Image.open(p).crop((64,24,576,216)).resize((512,384),Image.Resampling.NEAREST)
        frames.append(im)
        durations.append(4000 if k==0 else [30,30,40][(k-1)%3])
        if split==96:preview.paste(im,((n%2)*512,(n//2)*384))
frames[0].save(r/'timex-ecm-highres-reveal.gif',save_all=True,
    append_images=frames[1:],duration=durations,loop=0,optimize=True)
preview.save(r/'four-screen-preview.png')
files=['timex-ecm-highres-reveal.dck','build_demo.py','morpho1.tap','frog.tap',
       'README.md','highres-title-512x192.png','highres-title-preview.png',
       'highres-title-2-512x192.png','highres-title-2-preview.png',
       'four-screen-preview.png','validation.json','test_demo.mjs',
       'capture_demo.mjs','fetch_tsrun.py','timex-font-8x8.bin','package_demo.py',
       'render_scene.py','scene-grayscale.png','scene-dithered-512x84.png']
with zipfile.ZipFile(r/'timex-ecm-highres-reveal-source.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(r/f,'timex-reveal/'+f)
print('Packaged white-reference demo, source, and preview')
