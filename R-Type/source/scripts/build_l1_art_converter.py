from pathlib import Path
import sys,json,base64,hashlib,shutil,numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from build_graphics import decode_roms,palette_ram,sprite_image;from decode_arcade_objects import render
O=R/'build/graphics/l1_art_converter';O.mkdir(exist_ok=True)
def frame(im,label):
 im=im.convert('RGBA');return dict(w=im.width,h=im.height,rgba=base64.b64encode(im.tobytes()).decode(),label=label)
sp,_=decode_roms();pal=palette_ram(R/'build/fullgame/arcade_reference/frame003300_palette_sprite.bin')[112:128];walk=[]
for c in [256,258]:walk.append(frame(sprite_image(sp,c,pal,2,2)[0],f'Arcade walking cel {c}'))
extra=[]
for k in range(2):
 im=sprite_image(sp,[256,258][k],pal,2,2)[0];a=np.array(im);old=a[23:].copy();a[23:]=0;delta=1 if k==0 else -1
 for x in range(32):
  xx=x+delta if x<16 else x-delta
  if 0<=xx<32:a[23:,xx]=old[:,x]
 extra.append(frame(Image.fromarray(a),f'Authored intermediate {k+1}'))
sheet=Image.open(R/'build/graphics/walker_review_r85/ai_round_sheet.png');ai=[frame(sheet.crop((k*sheet.width//4,0,(k+1)*sheet.width//4,sheet.height)),f'Earlier AI-assisted pose {k+1}')for k in range(4)]
current=[frame(Image.open(R/f'build/graphics/l1_walker_snake_r105/current_{k}.png'),f'Installed native {53+k}')for k in range(4)]
canvas,objs=render(4800,sp);snake=[];assembly=[];known={}
for d,im in objs:
 if d['colour']!=10 or not (400<=d['code']<448 or d['code']==2708):continue
 key=hashlib.sha256(im.tobytes()).hexdigest()
 if key not in known:known[key]=len(snake);snake.append(frame(im,f'Arcade joint {d["code"]}'))
 assembly.append(dict(x=d['x'],y=d['y'],frame=known[key],code=d['code']))
assert len(snake)>=4
import walker_review_r85 as native;native.B=R/'build/fullgame/full_plume_r104';oldSnake=[frame(native.current(1,i)[0],f'Installed native {i}')for i in [16,17,18,19]]
def image64(path):return 'data:image/png;base64,'+base64.b64encode(Path(path).read_bytes()).decode()
data=dict(title='R-Type L1 art converter',walker=dict(title='Round walker',native=[53,54,55,56],current=current,sources=[dict(id='ai',label='Earlier gold/steel design ? 4 authored poses',provenance='AI-assisted design used in r86; remove its source margins before resizing.',frames=ai),dict(id='arcade4',label='Arcade + intermediates ? 4 poses',provenance='ROM cels256/258, palette7 from frame003300, plus two explicitly authored leg intermediates.',frames=[walk[0],extra[0],walk[1],extra[1]]),dict(id='arcade2',label='Arcade walking originals ? 2 poses',provenance='Unmodified original ROM cels256/258. No boost cels mislabelled as walking.',frames=walk),dict(id='current',label='Installed artwork ? 4 poses',provenance='Actual r104 runtime family, 24x24 with only15-16x15 visible pixels.',frames=current)]),snake=dict(title='L1 snake',native=[16,17,18,19],current=oldSnake,sources=[dict(id='arcade',label=f'Arcade joints ? {len(snake)} captured orientations',provenance='Original ROM-decoded M72 objects and palette10 from actual L1 frame004800. These are orientations, not an invented gait.',frames=snake,assembly=assembly),dict(id='current',label='Installed grey-loop joints ? 4 orientations',provenance='Current native16-19 source artwork, preserved for comparison.',frames=oldSnake)]),references=dict(snake=image64(R/'build/fullgame/arcade_reference/frame004800.png'),walker=image64(R/'build/fullgame/arcade_reference/frame003300.png')))
(O/'data.json').write_text(json.dumps(data,separators=(',',':')))
worker=(R/'build/graphics/walker_candidates_r88/worker.js').read_text(encoding='utf-8-sig')
worker=worker.replace("'sierra-lite':new Float32Array([1,0,.5,-1,1,.25,0,1,.25])","'sierra-lite':new Float32Array([1,0,.5,-1,1,.25,0,1,.25]),'floyd-steinberg':new Float32Array([1,0,7/16,-1,1,3/16,0,1,5/16,1,1,1/16])")
worker=worker.replace('for(let q=1;q<8;q++){let e=0;','for(let q=1;q<8;q++){if(p.palette&&!p.palette[q])continue;let e=0;')
worker=worker.replace('const n=p.w*p.h;alphaMask=mask;','const n=p.w*p.h;p.palette=settings.palette;alphaMask=mask;')
worker=worker.replace("const work=context.conversionPipelineState.work;","const work=context.conversionPipelineState.work;for(let k=0;k<n;k++)if(!mask[k])work.fill(0,k*3,k*3+3);")
worker=worker.replace('masks=[Array(8).fill(true),Array(8).fill(p.bright)]','masks=[settings.palette||Array(8).fill(true),(settings.palette||Array(8).fill(true)).map(v=>!!v&&p.bright)]')
worker=worker.replace("const result=new Float32Array(n*3);context.conversionPipelineState=", "const result=new Float32Array(n*3);if(settings.dither==='none'||settings.dither==='ordered'){result.set(work);}else{context.conversionPipelineState=")
worker=worker.replace("kernel:context.DIFFUSION_KERNELS['sierra-lite']","kernel:context.DIFFUSION_KERNELS[settings.dither==='floyd-steinberg'?'floyd-steinberg':'sierra-lite']")
worker=worker.replace('context.pipelineStageDitherDiffusionRows(1);','context.pipelineStageDitherDiffusionRows(1);}')
worker=worker.replace('const ink=e0<=e1;',"let ink=e0<=e1;if(settings.dither==='ordered'){const bayer=[0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5];let num=0,den=0;for(let c=0;c<3;c++){const d=c0[c]-c1[c];num+=(work[k*3+c]-c1[c])*d;den+=d*d;}ink=den>0&&num/den>(bayer[(y&3)*4+(x&3)]+.5)/16;}")
worker=worker.replace('if(p.strategy===\'segment-coverage\')',"if(!candidates.length)throw Error('Enable at least one nonblack palette colour');if(p.strategy==='segment-coverage')")
worker=worker.replace('bits,attrs,clashes};','bits,attrs,preserve,clashes};')
(O/'worker.js').write_bytes(worker.encode('utf-8'));shutil.copy2(R/'build/graphics/arcade_rpc_comparison_r68/RPC_LICENSE.txt',O/'RPC_LICENSE.txt')
manifest=dict(rpc_upstream='Local RetroPixelConverter snapshot ../../retropixel/index.html',rpc_upstream_sha256=hashlib.sha256((R/'../../retropixel/index.html').read_bytes()).hexdigest(),core_source='walker_candidates_r88/worker.js; actual RPC CPU adjustment/pair/diffusion functions',worker_sha256=hashlib.sha256(worker.encode()).hexdigest(),adaptations=['UI crop/scale before conversion','transparent pixels stay normal black','bright-black excluded','palette subset','Sierra Lite/Floyd-Steinberg kernels use RPC diffusion','Bayer4 and nearest-pair adapters','coherent horizontal-gap option'],sources='Original local arcade ROM and captured palette/object RAM; prior AI-assisted walker explicitly labelled',status='Offline artwork editor, never writes game files')
(O/'provenance.json').write_text(json.dumps(manifest,indent=2))
# Bundle only after the UI sources are present. Everything is embedded for file:// operation.
if (R/'src/l1_art_converter.js').exists():
 html=(R/'src/l1_art_converter.html').read_text(encoding='utf-8-sig');html=html.replace('/*STYLE*/',(R/'src/l1_art_converter.css').read_text(encoding='utf-8-sig')).replace('/*DATA*/',json.dumps(data,separators=(',',':')).replace('<','\\u003c')).replace('/*WORKER*/',json.dumps(worker).replace('<','\\u003c')).replace('/*PROVENANCE*/',json.dumps(manifest)).replace('/*APP*/',(R/'src/l1_art_converter.js').read_text(encoding='utf-8-sig'));(O/'index.html').write_text(html,encoding='utf-8')
print('Sources:',len(ai),'walker poses;',len(snake),'snake orientations;',len(assembly),'assembly joints. Ready:',(O/'index.html').exists())
