from pathlib import Path
import json,zipfile,hashlib,sys,base64
from PIL import Image,ImageDraw
sys.path.insert(0,'scripts');import walker_review_r85 as n
from build_graphics import decode_roms,palette_ram,sprite_image
R=Path.cwd();O=R/'build/graphics/l7_wall_assembled';n.B=R/'build/fullgame/highscore_r138';O.mkdir(exist_ok=True)
manifest=[]
for key,name in [('walker','rtype-l7-walker-assets.zip'),('round','rtype-l1-walker-assets.redyelgrn.zip'),('orb','L7asteroid.rtype-l1-walker-assets.zip'),('emergence','L7emergingmech.rtype-l1-walker-assets.zip')]:
 p=R/'convref'/name;dest=O/'selected'/key;dest.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(p)as z:
  assert z.testzip()is None;doc=json.loads(z.read('choices.json'));fam=doc['families']['walker'];frames=[]
  for q in fam['frames']:
   k=q['frame'];stem=f'walker/frame_{k:02d}';w,h=q['width'],q['height'];bits=z.read(stem+'.bits.bin');attrs=z.read(stem+'.attrs.bin');pairs=z.read(stem+'.pairs.bin');assert len(bits)==len(attrs)==w*h//8 and len(pairs)==w*h//4;assert not any(a&128 for a in attrs);assert all(not(a&64)or(a&7 and a>>3&7)for a in attrs)
   for ext in ['png','bits.bin','attrs.bin','preserve.bin','pairs.bin']:(dest/f'frame_{k:02d}.{ext}').write_bytes(z.read(stem+'.'+ext))
   frames.append(dict(frame=k,width=w,height=h,pairs_sha256=hashlib.sha256(pairs).hexdigest()))
  (dest/'choices.json').write_text(json.dumps(doc,indent=2));manifest.append(dict(key=key,file=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),native=fam['nativeDescriptors'],settings=fam['settings'],frames=frames))
(O/'selected_manifest.json').write_text(json.dumps(manifest,indent=2))
def rgba(im):
 im=im.convert('RGBA');p=im.load()
 for y in range(im.height):
  for x in range(im.width):
   if p[x,y][:3]==(0,0,0):p[x,y]=(0,0,0,0)
 return im
sp,_=decode_roms();pal=palette_ram(R/'build/fullgame/arcade_reference/frame061800_palette_sprite.bin')[176:192];body,_=sprite_image(sp,704,pal,2,4);arm,_=sprite_image(sp,692,pal,2,4)
# Both records are32x64 and adjacent; preserve all transparent padding.
arc=Image.new('RGBA',(64,64));arc.alpha_composite(arm,(0,0));arc.alpha_composite(body,(32,0));arc.save(O/'arcade_assembled_61800.png')
natives=[];derived=[]
for i,angle in zip(range(42,46),[0,-18,-36,-54]):
 im=Image.new('RGBA',(32,32));im.alpha_composite(rgba(n.current(7,i)[0]),(0,0));im.alpha_composite(rgba(n.current(7,41)[0]),(16,0));im.save(O/f'native_assembled_{i}.png');natives.append(im)
 # Reconstruction: a rotating arm derived from one captured arm cel, not new captured arcade frames.
 canvas=Image.new('RGBA',(128,128));canvas.alpha_composite(arm,(32,32));canvas=canvas.rotate(angle,Image.Resampling.BICUBIC,center=(64,80));out=canvas.crop((32,32,96,96));out.alpha_composite(body,(32,0));out.save(O/f'derived_assembled_{i}.png');derived.append(out)
# Preserve chosen walker exactly, add an optional cool-armour material variant.
walk=O/'selected/walker';selected=[];blue=[]
for p in sorted(walk.glob('frame_*.png')):
 im=Image.open(p).convert('RGBA');selected.append(im);cool=im.copy();px=cool.load()
 for y in range(cool.height):
  for x in range(cool.width):
   r,g,b,a=px[x,y]
   if a and max(r,g,b)-min(r,g,b)<32 and r>50:px[x,y]=(0,205,205,a) if r>180 else(0,0,205,a)
 cool.save(walk/(p.stem+'_cool_proposal.png'));blue.append(cool)
sheet=Image.new('RGB',(960,700),'#141923');d=ImageDraw.Draw(sheet);d.text((10,4),'Wall enemy: original components assembled (41 + 42/43/44/45)',fill='white')
for k,im in enumerate(natives):im=im.resize((160,160));sheet.paste(im,(k*210+10,25),im)
d.text((10,200),'Arcade: actual adjacent692+704 (left). Reconstructed articulation proposal (right).',fill='white');im=arc.resize((192,192));sheet.paste(im,(10,225),im)
for k,im in enumerate(derived):im=im.resize((160,160));sheet.paste(im,(220+k*180,225),im)
d.text((10,440),'Chosen walker (top) / optional cool-armour proposal (bottom); original export retained.',fill='white')
for k,(a,b)in enumerate(zip(selected,blue)):
 for y,im in [(470,a),(580,b)]:im=im.resize((96,96));sheet.paste(im,(10+k*140,y),im)
sheet.save(O/'assembly_and_walker_comparison.png')
# Reuse tested editor but supply complete assembled frames and explicit provenance.
def f(im,label):return dict(w=im.width,h=im.height,rgba=base64.b64encode(im.tobytes()).decode(),label=label)
data=dict(title='L7 wall enemy - assembled interactive conversion',walker=dict(title='L7 wall enemy: body41 plus moving42-45',native=[41,42,43,44,45],current=[f(im,f'Native assembly41+{i}')for i,im in zip(range(42,46),natives)],sources=[dict(id='arcade',label='Captured arcade assembly692+704',provenance='Actual frame61800 objects:692 at380,88 and704 at412,88; both32x64,palette11. Full assembly64x64. Body outside visible playfield was omitted by the earlier gallery.',frames=[f(arc,'Captured assembly692+704')]),dict(id='articulated',label='Articulation proposal - derived, not captured frames',provenance='One real arm cel rotated about its joint; fixed704body. Four reconstructed poses to compare with the four native states. Exact arcade per-pose artwork mapping remains under review.',frames=[f(im,f'Derived pose{i} - reconstructed rotation')for i,im in zip(range(42,46),derived)]),dict(id='current',label='Original assembled native animation',provenance='Native41fixedbody beside42..45moving section; arm IDs actually traced2123..2400 with42,43,44,45,44,43,42 sequence. Playback uses traced42/43/44/45/44/43 order and26:1 resting hold ratio; playback speed is adjustable, not a measured hardware cadence.',frames=[f(im,f'Native41+{i}')for i,im in zip(range(42,46),natives)])]),references=dict(walker='data:image/png;base64,'+base64.b64encode((O/'assembly_and_walker_comparison.png').read_bytes()).decode()))
(O/'data.json').write_text(json.dumps(data,separators=(',',':')))
app=(R/'src/l7_walker_converter.js').read_text().replace('rtype-l7-walker','rtype-l7-wall-assembled').replace('width:24,height:24','width:32,height:32').replace('trim:true','trim:false')
a=app.index("$('referenceText').textContent=");z=app.index(';for(const b of document.querySelectorAll(',a);app=app[:a]+"$('referenceText').textContent='Assembly uses adjacent parts before ECM conversion. Actual captured view, original native animation and explicitly reconstructed articulation are separate options. Controls apply to the whole selected sequence.'"+app[z:]
app=app.replace("setInterval(()=>{if(playing&&performance.now()-lastTick>=Number($('speed').value)){lastTick=performance.now();frameIndex=(frameIndex+1)%source().frames.length;paint();}},30);", "let wallStep=0;setInterval(()=>{const seq=[0,1,2,3,2,1],holds=[26,1,1,1,1,1],assembled=['current','articulated'].includes(source().id),delay=Number($('speed').value)*(assembled?holds[wallStep]:1);if(playing&&performance.now()-lastTick>=delay){lastTick=performance.now();if(assembled){wallStep=(wallStep+1)%seq.length;frameIndex=seq[wallStep];}else frameIndex=(frameIndex+1)%source().frames.length;paint();}},30);")
html=(R/'src/l7_walker_converter.html').read_text();a=html.index('<details open class="source-gallery">');z=html.index('<main>',a);html=html[:a]+'<details open class="source-gallery"><summary>Assembly and chosen walker comparison</summary><img style="max-width:100%;image-rendering:pixelated" src="'+data['references']['walker']+'"><p>Arcade frame61800: moving section left, lens body right. Derived rotations are proposals, not captured animation.</p></details>'+html[z:];html=html.replace('L7 armoured walker converter','L7 assembled wall-enemy converter').replace('L7 armoured walker: native14-17','L7 assembled wall enemy').replace('24x24 current footprint','24x24 whole-enemy proposal').replace('32x32 source detail','32x32 native assembly footprint');worker=(R/'build/graphics/l1_art_converter/worker.js').read_text();prov=dict(json.loads((R/'build/graphics/l1_art_converter/provenance.json').read_text()),status='Asset review only; exact captured assembly and labelled reconstructed poses',assembly=[dict(code=692,x=380,y=88),dict(code=704,x=412,y=88)],capture=61800,palette=11)
html=html.replace('/*STYLE*/',(R/'src/l1_art_converter.css').read_text()).replace('/*DATA*/',json.dumps(data).replace('<','\u003c')).replace('/*WORKER*/',json.dumps(worker).replace('<','\u003c')).replace('/*PROVENANCE*/',json.dumps(prov)).replace('/*APP*/',app);(O/'index.html').write_text(html,encoding='utf-8')
print(O/'index.html')
