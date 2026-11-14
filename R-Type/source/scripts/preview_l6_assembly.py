from pathlib import Path
import sys,json,hashlib,ast
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_graphics import decode_roms,palette_ram,quantize
from decode_arcade_objects import render
from boss_motion_assets_r60 import decode,PALETTE
from preview_enemy_sierra import convert
OUT=ROOT/'build/graphics/l6_assembly_review';OUT.mkdir(parents=True,exist_ok=True)
tree=ast.parse((ROOT/'scripts/preview_l6_corrected.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'preview_helpers','exec'))
SP,_=decode_roms();pal=palette_ram(ROOT/'build/fullgame/arcade_reference/frame048000_palette_sprite.bin')[80:96]
heads=[];small=[];large=[]
for i,code in enumerate([224,226,228,230]):
 a=np.block([[SP[code],SP[code+8]],[SP[code+1],SP[code+9]]]);source=Image.fromarray(np.concatenate([pal[a],np.where(a[:,:,None],255,0)],2).astype('uint8'));heads.append(source)
 small.append(save_pixels(f'head24_pose{i}',preview(source,(24,24),blue_metal=True)));large.append(save_pixels(f'head32_pose{i}',preview(source,(32,32),blue_metal=True)))
for name,frames in [('head_arcade.gif',heads),('head_current.gif',[Image.fromarray(PALETTE[decode(6,i)[0]].astype('uint8'))for i in range(9,14)]),('head24.gif',small),('head32.gif',large),('walker_unmatched.gif',[Image.fromarray(PALETTE[decode(6,i)[0]].astype('uint8'))for i in range(5,9)])]:gif(name,frames)

def material_preview(canvas):
 a=np.array(canvas);rgb=a[:,:,:3].astype(float);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];visible=(a[:,:,3]>=96)&(rgb.max(2)>12);out=np.zeros_like(rgb)
 gold=(r>.7*g)&(g>.7*r)&(b<.65*g)&visible
 red=(r>1.45*g)&visible&~gold
 glass=(b>1.2*r)&visible&~gold&~red
 metal=visible&~gold&~red&~glass;lum=rgb.mean(2)
 for mask,color in [(gold&(lum<95),(0,205,0)),(gold&(lum>=95)&(lum<185),(205,205,0)),(gold&(lum>=185),(205,205,205)),(red&(b<r*.65),(205,0,0)),(red&(b>=r*.65),(205,0,205)),(glass&(g<130),(0,0,205)),(glass&(g>=130),(0,205,205)),(metal&(lum<105),(0,0,205)),(metal&(lum>=105)&(lum<175),(0,205,205)),(metal&(lum>=175),(205,205,205))]:out[mask]=color
 a[:,:,:3]=out.astype('uint8');a[:,:,3]=visible.astype('uint8')*255
 return preview(Image.fromarray(a),canvas.size,blue_metal=True)

paired=[];provenance=[]
for fr,left,right in [(48300,320,324),(48900,1476,336),(48600,1488,340)]:
 rows=render(fr,SP)[1];ld,li=next((d,im)for d,im in rows if d['code']==left);rd,ri=next((d,im)for d,im in rows if d['code']==right and d['x']==ld['x']+32 and d['y']==ld['y']);assert ld['colour']==rd['colour']
 full=Image.new('RGBA',(64,64));full.alpha_composite(li,(0,0));full.alpha_composite(ri,(32,0));assert full.getbbox()[3]==48;full=full.crop((0,0,64,48));paired.append(full);full.save(OUT/f'arcade_pair_{left}_{right}.png');li.save(OUT/f'arcade_left_{left}.png');ri.save(OUT/f'arcade_right_{right}.png');provenance.append({'capture_frame':fr,'codes':[left,right],'positions':[[ld['x'],ld['y']],[rd['x'],rd['y']]],'visible_size':[64,48]})
sheet=Image.new('RGB',(900,690),(18,18,18));draw=ImageDraw.Draw(sheet)
for i,(full,meta)in enumerate(zip(paired,provenance)):
 y=i*230;draw.text((4,y+3),f"ARCADE: {meta['codes'][0]} + {meta['codes'][1]}, adjacent32px /sameY",fill='white')
 for x,code,side in [(4,meta['codes'][0],'left'),(230,meta['codes'][1],'right')]:sheet.paste(enlarged(Image.open(OUT/f'arcade_{side}_{code}.png'),3).convert('RGB'),(x,y+30))
 sheet.paste(enlarged(full,3).convert('RGB'),(460,y+30));draw.text((460,y+16),'Complete assembly',fill='cyan')
sheet.save(OUT/'paired_source_comparison.png')
sizes=[(32,24,32,24),(43,32,48,32),(48,36,48,40)];outputs={};checks=[]
def place(source,vw,vh,w,h):
 im=source.resize((vw,vh),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(w,h));canvas.alpha_composite(im,((w-vw)//2,h-vh));return canvas
for vw,vh,w,h in sizes:
 key=f'{w}x{h}'
 for i,full in enumerate(paired):save_pixels(f'assembly_{key}_pose{i}',preview(place(full,vw,vh,w,h),(w,h)))
 raw=np.asarray(paired[0]).copy();rgb=raw[:,:,:3];glass=(rgb[:,:,2]>=rgb[:,:,0])&(rgb[:,:,1]>rgb[:,:,0])&(rgb[:,:,0]>=70)&(raw[:,:,3]>0);roi=np.zeros(glass.shape,bool);roi[:,34:56]=True;glass&=roi
 top=glass.copy();top[24:]=False;bottom=glass.copy();bottom[:24]=False;masks=[]
 for mask in [top,bottom]:
  mm=Image.fromarray((mask*255).astype('uint8')).resize((vw,vh),Image.Resampling.NEAREST);canvas=Image.new('L',(w,h));canvas.paste(mm,((w-vw)//2,h-vh));projected=np.array(canvas)>0;masks.append(np.repeat(projected.reshape(h,w//8,8).any(2),8,axis=1))
 frames=[];arrays=[];state_sources=[]
 for state in range(4):
  a=raw.copy();lum=rgb.astype(float).mean(2)
  for k,mask in enumerate([top,bottom]):
   on=bool(state&(1<<k));colors=[(0,115,155),(0,205,225),(220,255,255)]if on else[(0,0,120),(0,75,155),(0,150,180)]
   for test,color in [(lum<105,colors[0]),((lum>=105)&(lum<165),colors[1]),(lum>=165,colors[2])]:a[:,:,:3][mask&test]=color
  state_sources.append(Image.fromarray(a));arr=preview(place(state_sources[-1],vw,vh,w,h),(w,h))
  if state==0:base=arr.copy()
  else:
   allowed=(masks[0]if state&1 else np.zeros_like(masks[0]))|(masks[1]if state&2 else np.zeros_like(masks[1]));arr[~allowed]=base[~allowed]
  if state==3:
   arr=base.copy();arr[masks[0]]=arrays[1][masks[0]];arr[masks[1]]=arrays[2][masks[1]]
  arrays.append(arr);frames.append(save_pixels(f'assembly_{key}_light{state}',arr))
 assert len({a.tobytes()for a in arrays})==4
 assert not np.any((arrays[1]!=arrays[0])&~masks[0]);assert not np.any((arrays[2]!=arrays[0])&~masks[1])
 gif(f'assembly_{key}_lights.gif',[frames[i]for i in [0,1,3,2]]);gif(f'assembly_{key}_sourceposes.gif',[Image.open(OUT/f'assembly_{key}_pose{i}.png')for i in [0,1,2,1]])
 marrays=[];mframes=[]
 for state,source in enumerate(state_sources):
  arr=material_preview(place(source,vw,vh,w,h))
  if state==0:mbase=arr.copy()
  else:
   allowed=(masks[0]if state&1 else np.zeros_like(masks[0]))|(masks[1]if state&2 else np.zeros_like(masks[1]));arr[~allowed]=mbase[~allowed]
  if state==3:
   arr=mbase.copy();arr[masks[0]]=marrays[1][masks[0]];arr[masks[1]]=marrays[2][masks[1]]
  marrays.append(arr);mframes.append(save_pixels(f'material_{key}_light{state}',arr))
 assert len({a.tobytes()for a in marrays})==4
 assert not np.any((marrays[1]!=marrays[0])&~masks[0]);assert not np.any((marrays[2]!=marrays[0])&~masks[1])
 gif(f'material_{key}_lights.gif',[mframes[i]for i in [0,1,3,2]])
 outputs[key]=frames;outputs['material_'+key]=mframes;checks.append({'storage':[w,h],'fitted_source':[vw,vh],'colors_per_light_frame':[len(set(map(int,a.flat)))-int(0 in a)for a in arrays],'lighting_shape':'Original source glass mask; no spheres added','independent_glass_cells':True,'material_shading_colors':[len(set(map(int,a.flat)))-int(0 in a)for a in marrays]})
sheet=Image.new('RGB',(1000,840),(18,18,18));draw=ImageDraw.Draw(sheet)
for state in range(4):
 for j,((vw,vh,w,h),label)in enumerate(zip(sizes,['32x24 source ratio','48x32storage /43x32fit','48x40storage /48x36fit'])):
  x=j*330;y=state*210;draw.text((x+4,y+3),label,fill='white');draw.text((x+4,y+17),['BOTH DIM','UPPER GLASS LIT','LOWER GLASS LIT','BOTH LIT'][state],fill='cyan');sheet.paste(enlarged(outputs[f'{w}x{h}'][state]).convert('RGB'),(x+4,y+35))
sheet.save(OUT/'whole_unit_comparison.png')
material_sheet=Image.new('RGB',(1000,840),(18,18,18));draw=ImageDraw.Draw(material_sheet)
for state in range(4):
 for j,(vw,vh,w,h)in enumerate(sizes):
  x=j*330;y=state*210;draw.text((x+4,y+3),f'{w}x{h}storage - solid material shading',fill='white');draw.text((x+4,y+17),['BOTH DIM','UPPER GLASS LIT','LOWER GLASS LIT','BOTH LIT'][state],fill='cyan');material_sheet.paste(enlarged(outputs['material_'+f'{w}x{h}'][state]).convert('RGB'),(x+4,y+35))
material_sheet.save(OUT/'material_comparison.png')
trace=json.loads((OUT/'native_components.json').read_text());examples=[r for r in trace['rows']if 14<=r['id']<=17];actor=examples[0]['iy'];cycle=[r for r in examples if r['iy']==actor][:20]
archive=ROOT/'build/fullgame/force_loading_r62/RType_TS2068_r62.zip';sha=hashlib.sha256(archive.read_bytes()).hexdigest();assert sha=='e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574'
(OUT/'validation.json').write_text(json.dumps({'preview_only':True,'arcade_pairings':provenance,'geometry_and_lighting':checks,'native_trace_updates':trace['updates'],'native_turret_cycle':cycle,'head_family_placement':'User proposes224..230fornative9..13; exactposemappingunverified','walker5_8':'Unmatched; prior224..230mapping rejected','legal8x1':True,'r62_zip_sha256':sha,'timing':'Illustrative280ms, not native timing'},indent=2))
(OUT/'index.html').write_text('''<meta charset=utf-8><title>L6 complete assemblies</title><style>body{background:#151515;color:white;font:18px system-ui;max-width:1200px;margin:24px auto;padding:16px}img{image-rendering:pixelated;max-width:100%}.row{display:flex;gap:28px;align-items:end;flex-wrap:wrap}figure{margin:10px}figcaption{margin-bottom:12px}a{color:cyan}</style><h1>L6: compare the complete pieces</h1><h2>#5-8 walker: still unmatched</h2><p>The224-family proposal has been removed from this group. Current native sequence:</p><img src=walker_unmatched.gif><h2>#9-13: the family you identified</h2><p>The previous spherical walking-head source now sits alongside this native family. This is a family comparison; four arcade cels have not yet been assigned to the five native poses.</p><div class=row><figure><figcaption>Current native9-13</figcaption><img src=head_current.gif></figure><figure><figcaption>Arcade224/226/228/230</figcaption><img src=head_arcade.gif></figure><figure><figcaption>24x24 conversion</figcaption><img src=head24.gif></figure><figure><figcaption>32x32 conversion</figcaption><img src=head32.gif></figure></div><h2>#14 family: yes, a companion piece</h2><p>The arcade unit is two adjacent32-pixel-wide objects. The old crop dropped much of the body/mounting section. These original paired poses show the full64x48visible assembly:</p><img src=paired_source_comparison.png><p>The native trace shows a15-16-17-16 cycle. The prior labels assigning native14-17 to four independent lamps were unsupported and are withdrawn. Source-pose animation and lighting studies below are separate.</p><h2>Complete machinery, original shallow glass profiles</h2><p>These conversions retain the source glass outlines rather than adding round bulbs. Full source aspect is preserved; padding is storage only. The lighting study recolours original upper/lower glass regions. Changes are restricted to their8x1cells, leaving the remaining housing stable.</p><div class=row><figure><figcaption>Full unit32x24</figcaption><img src=assembly_32x24_lights.gif></figure><figure><figcaption>Full unit43x32 in48x32storage</figcaption><img src=assembly_48x32_lights.gif></figure><figure><figcaption>Full unit48x36 in48x40storage</figcaption><img src=assembly_48x40_lights.gif></figure></div><img src=whole_unit_comparison.png><h2>Solid material shading alternative</h2><p>Same complete assembly and shallow source glass. Green/yellow armour, cool metal shadows and lit highlights are planned before ECM fitting to avoid invented black dithering holes in opaque surfaces. This is an authored material alternative; compare with Sierra above.</p><img src=material_48x32_lights.gif><img src=material_comparison.png><h2>Actual paired arcade poses, converted together</h2><img src=assembly_48x32_sourceposes.gif><p>Asset review only. Native pairing/collision integration and precise frame mapping remain to be designed. Runtime files unchanged. Animation cadence illustrative. See<a href=validation.json>source and validation details</a>.</p>''',encoding='utf-8')
print(json.dumps(checks))
