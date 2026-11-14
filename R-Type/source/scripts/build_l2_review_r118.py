from pathlib import Path
import sys,json,zipfile,base64,hashlib,shutil,re
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from decode_arcade_objects import render;from build_graphics import decode_roms
B=R/'build/graphics/l2_review_r117';O=R/'build/graphics/l2_review_r118';O.mkdir(exist_ok=True);data=json.loads((B/'data.json').read_text());z=zipfile.ZipFile(R/'convref/rtype-l2-art-assets.zip');choices=json.loads(z.read('choices.json'));(O/'imported_choices.json').write_text(json.dumps(choices,indent=2));sp,_=decode_roms()
def fr(im,label):
 im=im.convert('RGBA');return dict(w=im.width,h=im.height,rgba=base64.b64encode(im.tobytes()).decode(),label=label)
poses=[];seen=set();records=[]
for f in [12300,12600,12900,13200,13500,13800,14100,14400]:
 _,obs=render(f,sp)
 for d,im in obs:
  if not 1200<=d['code']<1340 or d['colour']!=1:continue
  pair=next(((e,jm)for e,jm in obs if e['offset']==d['offset']+8 and e['x']==d['x']+32 and e['y']==d['y'] and e['colour']==d['colour'] and 1200<=e['code']<1340),None)
  if not pair:continue
  e,jm=pair;full=Image.new('RGBA',(64,64));full.alpha_composite(im);full.alpha_composite(jm,(32,0));sha=hashlib.sha256(full.tobytes()).hexdigest()
  if sha in seen:continue
  seen.add(sha);idx=len(poses);full.save(O/f'scorpion_complete_{idx}.png');poses.append(fr(full,f"Captured {d['code']}+{e['code']}, frame{f}, at{d['x']},{d['y']}"));records.append(dict(frame=f,left=d,right=e,sha256=sha))
data['scorpion']['sources']=[dict(id='arcade',label='Complete captured scorpions - paired objects',provenance='Each64x64pose assembled from adjacent captured32x64objects with equal y/palette and consecutive object offsets. Actual captured flips retained. Ordering is capture inventory, not a claimed gait.',frames=poses),data['scorpion']['sources'][-1]];data['scorpion']['notes']='Corrected half-object error. Full square64x64arcadeassembly scales into existing40x40target without squashing half an object. Compare poses/shape against context; do not animate inventory order as verified gait.'
_,obs=render(15900,sp);chain=[(d,im)for d,im in obs if 124<=d['offset']<=292 and 2440<=d['code']<2500];frames=[];layout=[];seen={};canvas=Image.new('RGBA',(200,256))
for d,im in chain:
 key=hashlib.sha256(im.tobytes()).hexdigest()
 if key not in seen:seen[key]=len(frames);frames.append(fr(im,f"Snake captured cel{d['code']} p{d['colour']}, offset{d['offset']}"))
 layout.append(dict(x=d['x'],y=d['y'],frame=seen[key],code=d['code'],palette=d['colour'],offset=d['offset']));canvas.alpha_composite(im,(d['x'],d['y']))
canvas.save(O/'snake_captured_assembly.png');data['snake']['sources']=[dict(id='arcade',label='Actual captured snake: head, body and tail orientations',provenance='Frame15900objects offsets124..292 form visible chain. Repeated2450/2454body objects, terminal/head2480/2496/2482/2464. Deduplicated exact capturedRGBA, preserving actual flips and palette. Assembly uses captured positions; these are parts/orientations, not a gait cycle.',frames=frames,assembly=layout),data['snake']['sources'][-1]];data['snake']['notes']='Withdrawn wrong skeletal-chain identification. This source now comes from the actual visible arcade snake chain. Inspect Connected snake preview and original full scene. Native22..30orientation mapping still requires separate runtime analysis.'
detail=Image.open(R/'build/graphics/l2_integrated_r67/body.png').convert('RGBA').resize((192,104),Image.Resampling.NEAREST);data['boss']['current']=[fr(detail,'Previous detailed boss palette,192x104')]
# User notes/settings retained, no silently accepted review entries.
for k,v in choices['families'].items():data[k]['userReview']=dict(settings=v['settings'],decision=v['decision'],notes=v['notes'])
data['walker']['notes']+=' Your note retained: reuse existing conversion. The source IS exact approved C/L6_head artwork already installed for L1 inr110, not newly generated.'
data['boss']['notes']+=' Your selected scroll-safe entrance is preserved. Staged comparison dissolves to Current game family after movement stops; this is an offline animation prototype, not an implemented gameplay fix.'
# Use r117 established app with exported settings as initial defaults, isolated autosave.
app=(R/'src/l2_art_review_r117.js').read_text(encoding='utf-8').replace('rtype-l2-review-r117','rtype-l2-review-r118').replace('version:117','version:118');app=app.replace("const d=defaults(k);for(const [id", "const d=defaults(k);for(const [id")
needle="let states=Object.fromEntries(families.map(k=>[k,defaults(k)])),active='terrain'";assert needle in app;app=app.replace(needle,"let states=Object.fromEntries(families.map(k=>[k,{...defaults(k),...USER_CHOICES.families[k].settings,...(['scorpion','snake'].includes(k)?{cropX:0,cropY:0,cropW:0,cropH:0}:{} )}])),active='scorpion'")
# Prevent crop64tallfromoldhalfscorpion; correctedsourcecube handles allposes.
app=app.replace("$('assemblyPanel').hidden=active!=='snake'","$('assemblyPanel').hidden=active!=='snake'")
# Staged boss demo from exact exported moving pairs and exact old stationary reference.
insert="""
let bossPhase=0;setInterval(()=>{if(active!=='boss')return;const c=$('bossStage'),ctx=c.getContext('2d'),safe=canvasFor(BOSS_SAFE),detail=canvasFor(ART_DATA.boss.current[0]);c.width=256;c.height=160;const t=bossPhase++%180,x=Math.max(64,256-t*4);ctx.clearRect(0,0,256,160);ctx.drawImage(safe,x,56);if(x===64){const dissolve=Math.min(1,Math.max(0,(t-58)/40));const dctx=detail.getContext('2d'),a=dctx.getImageData(0,0,192,104);const threshold=Math.floor(dissolve*64);for(let y=0;y<104;y++)for(let x=0;x<192;x++){const rank=(((x>>3)&7)*17+(y&7)*29)%64;if(rank>=threshold)a.data[(y*192+x)*4+3]=0;}const temp=makeCanvas(192,104);temp.getContext('2d').putImageData(a,0,0);ctx.drawImage(temp,64,56);}$('bossStageInfo').textContent=x>64?'Moving: exact exported scroll-safe entrance':'Stopped: dissolve to previous detailed palette (offline prototype; whole8x1cells switch together)';},65);
"""
app=app.replace("$('engine').textContent=",insert+"$('engine').textContent=");safe=Image.open(z.open('boss/frame_00.png'));app='const USER_CHOICES='+json.dumps(choices,separators=(',',':'))+';\nconst BOSS_SAFE='+json.dumps(fr(safe,'Exact user export moving boss'))+';\n'+app
html=(R/'src/l2_art_review_r117.html').read_text(encoding='utf-8').replace('r117','r118');html=html.replace('Single-pixel scroll colour test','Single-pixel scroll colour test').replace('<section class="review">','<section><h2>Boss entrance / stationary dissolve prototype</h2><canvas id="bossStage" style="width:100%;image-rendering:pixelated"></canvas><p id="bossStageInfo">Select boss tab to play. Offline prototype only.</p></section><section class="review">');# original gallery retained plus corrected assemblies
html=html.replace('<main>','<details open><summary>Corrected source assembly evidence</summary><p>Scorpion halves paired from actual capture coordinates, not stretched individually. Snake source reconstructed from captured chain objects. Original tentative matches withdrawn.</p><img src="snake_captured_assembly.png" style="height:512px;image-rendering:pixelated"><img src="scorpion_pair_evidence.png" style="max-width:100%;image-rendering:pixelated"></details><main>')
sheet=Image.new('RGB',(800,((len(poses)+5)//6)*150),(15,18,22));dr=ImageDraw.Draw(sheet)
for i,p in enumerate(poses):
 x=i%6*132;y=i//6*150;dr.text((x,y),f"{records[i]['left']['code']}+{records[i]['right']['code']}",fill='white');im=Image.open(O/f'scorpion_complete_{i}.png').resize((128,128),Image.Resampling.NEAREST);sheet.paste(im,(x,y+20),im)
sheet.save(O/'scorpion_pair_evidence.png');(O/'assembly_evidence.json').write_text(json.dumps(dict(scorpions=records,snake_frame=15900,snake_layout=layout),indent=2));(O/'data.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8');prov=json.loads((B/'provenance.json').read_text())if(B/'provenance.json').exists()else choices['rpc'];prov['sprite_objects']=[];prov['status']='Corrected full-object L2 assembly review; gameplay unchanged';(O/'provenance.json').write_text(json.dumps(prov,indent=2));worker=(B/'worker.js').read_text(encoding='utf-8');shutil.copy2(B/'RPC_LICENSE.txt',O/'RPC_LICENSE.txt');(R/'src/l2_art_review_r118.js').write_text(app,encoding='utf-8');(R/'src/l2_art_review_r118.html').write_text(html,encoding='utf-8');html=html.replace('/*STYLE*/',(R/'src/l1_art_converter.css').read_text(encoding='utf-8-sig')).replace('/*DATA*/',json.dumps(data,separators=(',',':')).replace('<','\\u003c')).replace('/*WORKER*/',json.dumps(worker).replace('<','\\u003c')).replace('/*PROVENANCE*/',json.dumps(prov)).replace('/*APP*/',app);(O/'index.html').write_text(html,encoding='utf-8');print('Complete scorpion poses',len(poses),'snake pieces',len(frames),'captured placements',len(layout))
