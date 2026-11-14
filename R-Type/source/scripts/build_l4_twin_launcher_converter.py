from pathlib import Path
import sys,json,base64,hashlib,shutil,re
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from decode_arcade_objects import render;from build_graphics import decode_roms;import walker_review_r85 as native
O=R/'build/graphics/l4_twin_launcher_converter';O.mkdir(exist_ok=True);native.B=R/'build/fullgame/l4_shared_r131';sp,_=decode_roms()
def frame(im,label):
 im=im.convert('RGBA');return dict(w=im.width,h=im.height,rgba=base64.b64encode(im.tobytes()).decode(),label=label)
cur=[frame(native.current(4,i)[0],f'L4 native{i},24x24; original red/cyan twin-launcher family')for i in[52,53,54]];records=[];images=[]
for fr,code,pal in[(30300,1538,4),(33000,1538,1),(30300,1042,4)]:
 _,objs=render(fr,sp);d,im=next((d,i)for d,i in objs if d['code']==code and d['colour']==pal);words=(R/f'build/fullgame/arcade_reference/frame{fr:06d}_sprites.bin').read_bytes();flags=int.from_bytes(words[d['offset']*2+4:d['offset']*2+6],'little');records.append(dict(capture=fr,**d,flags=flags,flipX=bool(flags&0x800),flipY=bool(flags&0x400)));images.append(frame(im,f'Arcade{code}/p{pal},capture{fr},actual facing'));im.save(O/f'arcade_{code}_{fr}.png')
ref=Image.open(R/'build/fullgame/arcade_reference/frame030300.png').convert('RGB').resize((768,512),Image.Resampling.NEAREST);dr=ImageDraw.Draw(ref)
for r,col in[(records[0],'yellow'),(records[2],'cyan')]:
 x,y=r['x']*2,r['y']*2;dr.rectangle((x,y,x+r['width']*2,y+r['height']*2),outline=col,width=2);dr.text((x,y+r['height']*2+2),str(r['code']),fill=col)
ref.save(O/'arcade_reference_annotated.png');refurl='data:image/png;base64,'+base64.b64encode((O/'arcade_reference_annotated.png').read_bytes()).decode()
data=dict(title='R-Type L4 twin rocket launcher converter',launcher=dict(title='Red twin-rocket launcher craft',native=[52,53,54],current=cur,sources=[dict(id='arcade',label='1538 - your closest match, single captured view',provenance='User identified the left1538image as closest to the craft with two red rockets/nozzles. Actual30300capture/palette4. Kept separate from1540/1542/1554; these are NOT assumed to be its animation frames. Native52..54 is the red/cyan twin-launcher comparison family; exact pose mapping remains pending.',frames=[images[0]]),dict(id='facings',label='1538 - two actual captured horizontal facings',provenance='Actual object1538 captures30300/p4 and33000/p1, including captured flips. Facing alternatives, not a two-frame gait. Compare before choosing.',frames=images[:2]),dict(id='upright',label='1042 - upright twin-launcher candidate for comparison',provenance='Actual30300/p4 object1042, two red/orange barrels with silver nozzles and green centre. Candidate comparison only: not proven to be a rotated1538; pixels are not identical under rotation.',frames=[images[2]]),dict(id='current',label='Current red/cyan craft - native52/53/54',provenance='Actual r131 L4 source artwork for the red angular craft, cyan centre, two red launcher units. Original native poses shown without new frame mapping.',frames=cur)]),references=dict(launcher=refurl));(O/'data.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
worker=(R/'build/graphics/l1_art_converter/worker.js').read_text(encoding='utf-8-sig');(O/'worker.js').write_text(worker,encoding='utf-8');shutil.copy2(R/'build/graphics/l1_art_converter/RPC_LICENSE.txt',O/'RPC_LICENSE.txt');prov=json.loads((R/'build/graphics/l1_art_converter/provenance.json').read_text());prov.update(sources='Original local arcade ROM/captured object and palette RAM; user-selected1538 primary,1042 labelledcandidate; no AI assets.',sprite_objects=records,unverified_excluded=[1540,1542,1554],native_pose_mapping='Pending review; do not infer animation from adjacent ROM codes',status='Offline interactive art preview; no game files changed',worker_sha256=hashlib.sha256(worker.encode()).hexdigest());(O/'provenance.json').write_text(json.dumps(prov,indent=2))
app=(R/'src/ghost_art_converter.js').read_text(encoding='utf-8-sig').replace('ghost','launcher').replace('rtype-launcher-art-converter-v1','rtype-l4-twin-launcher-converter-v1').replace('rtype-launcher-art-review/1','rtype-l4-twin-launcher-review/1').replace('version:112','version:133').replace('rtype-l1-launcher-assets.zip','rtype-l4-twin-launcher-assets.zip').replace('rtype-l1-launcher-choices.json','rtype-l4-twin-launcher-choices.json').replace('frameIndex=2,playing=false','frameIndex=0,playing=false').replace('brightness:52,contrast:59,saturation:82,gamma:.87,width:32,height:32','brightness:44,contrast:54,saturation:71,gamma:.98,width:24,height:24').replace('scale:100,trim:false','scale:100,trim:true').replace('Ghost asset pack','Launcher asset pack').replace('Play animation','Cycle views').replace('Pause animation','Stop cycling').replace('Export launcher asset pack','Export launcher asset pack')
a=app.index("$('referenceText').textContent=");z=app.index(';for(const b of document.querySelectorAll(',a);app=app[:a]+"$('referenceText').textContent='Actual arcade L4 frame030300. Yellow box:1538, your selected closest view. Cyan box:1042, upright twin-launcher candidate. Distinct candidate views are not grouped as an animation;1540/1542/1554 excluded pending identification.'"+app[z:];(R/'src/l4_twin_launcher_converter.js').write_text(app,encoding='utf-8')
sheet=Image.new('RGB',(900,340),(18,22,28));dr=ImageDraw.Draw(sheet)
for row,(fs,label)in enumerate([(cur,'Current L4 red/cyan twin-launcher family:52 /53 /54'),(images,'Arcade:1538 selected /1538 other captured facing /1042 upright candidate')]):
 dr.text((10,row*165+5),label,fill='white')
 for i,f in enumerate(fs):
  im=Image.frombytes('RGBA',(f['w'],f['h']),base64.b64decode(f['rgba']));im=im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST);sheet.paste(im,(10+i*270,row*165+25),im)
sheet.save(O/'identity_comparison.png');html=(R/'src/ghost_art_converter.html').read_text(encoding='utf-8-sig').replace('White ghost enemy converter','Twin rocket launcher converter').replace('Export ghost asset pack','Export launcher asset pack').replace('data-family="ghost"','data-family="launcher"').replace('L1 ghost: native35-37','L4 red twin-launcher craft').replace('Play animation','Cycle views').replace('Saved C settings - 52 / 59 / 82 / 0.87','Higher contrast - 52 / 59 / 82 / 0.87');html=re.sub(r'<title>.*?</title>','<title>R-Type twin rocket launcher converter</title>',html);html=html.replace('<main>','<details open class="source-gallery"><summary>Selected match and separate comparison views</summary><img src="MATCH_IMAGE" alt="Red craft comparison and selected1538arcadeview" style="max-width:100%;image-rendering:pixelated"><p>Default is the1538view you identified. The other1538facing and upright1042are separate source choices. No1540/1542/1554animation is assumed. Settings apply to every view in the selected set; export the launcher asset pack when ready.</p></details><main>');html=html.replace('MATCH_IMAGE','data:image/png;base64,'+base64.b64encode((O/'identity_comparison.png').read_bytes()).decode());(R/'src/l4_twin_launcher_converter.html').write_text(html,encoding='utf-8');html=html.replace('/*STYLE*/',((R/'src/l1_art_converter.css').read_text(encoding='utf-8-sig')+'.transport label{max-width:100%;flex-wrap:wrap}#frameName{overflow-wrap:anywhere;min-width:0}')).replace('/*DATA*/',json.dumps(data,separators=(',',':')).replace('<','\\u003c')).replace('/*WORKER*/',json.dumps(worker).replace('<','\\u003c')).replace('/*PROVENANCE*/',json.dumps(prov)).replace('/*APP*/',app);(O/'index.html').write_text(html,encoding='utf-8');print(O/'index.html')

# Shape-preserving assist: palette materials and symmetric edge lighting, no geometry synthesis.
data['launcher']['sources'].append(dict(id='assisted',label='Spectrum silhouettes + arcade-inspired symmetric shading (all 3 poses)',provenance='Native52 upright,53 diagonal,54 horizontal. Exact original alpha/holes; algorithmic material ramps and paired rim lighting inspired by arcade red barrels, jade core and silver nozzles. These are enhanced Spectrum poses, not extracted arcade animation.',frames=cur))
assist=r"""
function assistedPixels(f,s){
 const a=bytes64(f.rgba),original=a.slice(),w=f.w,h=f.h,t=s.assist/100;
 const solid=(x,y)=>x>=0&&y>=0&&x<w&&y<h&&original[(y*w+x)*4+3]>0&&Math.max(original[(y*w+x)*4],original[(y*w+x)*4+1],original[(y*w+x)*4+2])>0;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){
  const i=(y*w+x)*4;if(!a[i+3])continue;
  const r=a[i],g=a[i+1],b=a[i+2];if(!(r||g||b)){a[i+3]=0;continue;}let material;
  if(r>g*1.5&&r>b*1.5)material='red';else if(g>r*1.5&&b>r*1.5)material='core';else if(Math.max(r,g,b)-Math.min(r,g,b)<45&&r>60)material='metal';else continue;
  let edge=5;for(let dy=-4;dy<=4;dy++)for(let dx=-4;dx<=4;dx++)if(!solid(x+dx,y+dy))edge=Math.min(edge,Math.hypot(dx,dy));
  const v=Math.max(0,Math.min(1,(edge-1)/3));
  // Identical edge distances get identical light: paired barrels remain balanced even diagonally.
  const ramps={red:[[255,180,85],[235,55,20],[95,8,18]],core:[[150,255,220],[15,175,115],[0,50,65]],metal:[[250,250,255],[125,165,190],[30,50,85]]};
  const stops=ramps[material],q=v<.5?v*2:(v-.5)*2,j=v<.5?0:1;
  for(let c=0;c<3;c++)a[i+c]=Math.round(original[i+c]*(1-t)+(stops[j][c]*(1-q)+stops[j+1][c]*q)*t);
 }return a;
}
"""
app=app.replace('const defaults=k=>({','const defaults=k=>({assist:80,')
app=app.replace('const numFields={','const numFields={assist:[0,100],')
app=app.replace("const sliderDefs=[","const sliderDefs=[['assist','Symmetric material shading',0,100,1],")
# Presets continue addressing the four original RPC fields.
app=app.replace('sliderDefs.forEach((v,i)=>states[active][v[0]]=a[i])',"sliderDefs.filter(v=>v[0]!=='assist').forEach((v,i)=>states[active][v[0]]=a[i])")
app=app.replace('function sourcePixels(f,s){const a=bytes64(f.rgba);',"function sourcePixels(f,s){const a=s.source==='assisted'?assistedPixels(f,s):bytes64(f.rgba);")
app=app.replace('function sourcePixels',assist+'\nfunction sourcePixels',1)
# Re-embed the new controls/data; preserve the existing autosave key and original choices.
html=html.replace('/*APP*/',app) if '/*APP*/' in html else html
base=(R/'src/l4_twin_launcher_converter.html').read_text(encoding='utf-8')
base=base.replace('No1540/1542/1554animation is assumed.', 'Native53 includes the original diagonal view. Select Spectrum silhouettes + arcade-inspired symmetric shading for all three native poses. The extra shading slider changes material lighting without moving pixels or filling holes. No1540/1542/1554animation is assumed.')
html=base.replace('/*STYLE*/',((R/'src/l1_art_converter.css').read_text(encoding='utf-8-sig')+'.transport label{max-width:100%;flex-wrap:wrap}#frameName{overflow-wrap:anywhere;min-width:0}')).replace('/*DATA*/',json.dumps(data,separators=(',',':')).replace('<','\\u003c')).replace('/*WORKER*/',json.dumps(worker).replace('<','\\u003c')).replace('/*PROVENANCE*/',json.dumps(prov)).replace('/*APP*/',app)
(O/'data.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
(O/'index.html').write_text(html,encoding='utf-8')
(R/'src/l4_twin_launcher_converter.js').write_text(app,encoding='utf-8')
