from pathlib import Path
import json,base64,hashlib,shutil
import numpy as np
from PIL import Image
R=Path.cwd();B=R/'build/graphics/arcade_rpc_comparison_r68';O=R/'build/graphics/arcade_review_r69';O.mkdir(exist_ok=True);j=json.loads((B/'inputs.json').read_text(encoding='utf-8-sig'));data={'records':j['records'],'profiles':{},'contexts':{},'defaults':{'brightness':44,'contrast':54,'saturation':71,'gamma':.98,'variant':'N','scroll':False}}
def family(r):
 n,i=r['level'],r['descriptor'];k=r['key']
 if k.startswith('L6_head'):return 'L6-corrected-head-9-13'
 if k.startswith('L6_assembly'):return 'L6-corrected-paired-machinery'
 if k.endswith('_corrected'):return 'L2-corrected-worm-heads'
 if k=='L2_body':return 'L2-organic-body'
 groups={2:[(3,6),(22,23),(25,30),(41,44)],3:[(101,106)],4:[(25,26)],5:[(9,26)],6:[(18,25)],7:[(49,54)],8:[(42,46)]}
 for lo,hi in groups.get(n,[]):
  if lo<=i<=hi:return f'L{n}-poses-{lo}-{hi}'
 h=hashlib.sha256((B/f'{k}_source.png').read_bytes()).hexdigest()[:10];return f'L{n}-source-{h}'
for r in data['records']:
 r['family']=family(r);r['strip']=r['size'][0]>=r['size'][1]*3;r['source_image']=f'../arcade_rpc_comparison_r68/{r["key"]}_source.png';r['current_image']=f'../arcade_rpc_comparison_r68/{r["key"]}_stored.png'
 if r['key']=='L2_body':r['current_image']='../l2_integrated_r67/body.png';r['current_kind']='r67 installed192x104 terrain body (enlarged reference)';r['stored_size']=[192,104]
 for p in r['profiles']:
  q=next(x for x in j['profiles']if x['id']==p['id']);scaled=np.array(Image.open(B/(p['id']+'_scaled.png')).convert('RGBA'));m=np.frombuffer((B/(p['id']+'.mask')).read_bytes(),np.uint8).reshape(q['h'],q['w']);input_rgb=np.round(scaled[:,:,:3].astype(float)*scaled[:,:,3:4]/255).astype('uint8');input_rgb[m==0]=0;data['profiles'][p['id']]={**q,'raw':base64.b64encode(input_rgb.tobytes()).decode(),'mask':base64.b64encode((B/(p['id']+'.mask')).read_bytes()).decode()}
# Context is original native map geometry, not a claim about current ECM appearance.
layouts=json.loads((R/'build/fullgame/foundation/manifest.json').read_text(encoding='utf-8-sig'))['levels'];frames=[10200,17400,26400,36600,44700,54000,60300,72900]
for n,l in enumerate(layouts,1):
 raw=(R/f'build/fullgame/foundation/level{n:02d}.raw').read_bytes();mem=bytes(0x4000)+raw;cols=l['map_columns'];a=np.zeros((160,cols*32),np.uint8)
 for x in range(cols):
  for y in range(5):
   value=mem[l['map_start']+x*5+y];id=value&63;ptr=l['map_start']-(id+1)*144;tile=np.zeros((32,32),np.uint8)
   if ptr<l['terrain_start']or ptr+144>l['map_start']:continue
   for cy in range(4):
    for cx in range(4):
     p=ptr+(cy*4+cx)*9
     for yy in range(8):tile[cy*8+yy,cx*8:cx*8+8]=np.unpackbits(np.array([mem[p+1+yy]],np.uint8))
   if value&64:tile=tile[:,::-1]
   if value&128:tile=tile[::-1]
   a[y*32:y*32+32,x*32:x*32+32]=tile
 Image.fromarray(a*200).save(O/f'level{n}_geometry.png');data['contexts'][n]={'map':f'level{n}_geometry.png','width':cols*32,'arcade':f'../../fullgame/arcade_reference/frame{frames[n-1]:06d}.png','label':'Original Spectrum map geometry (monochrome), not current ECM colours. Arcade image is boss-area reference.'}
(O/'review_data.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8');shutil.copy2(B/'RPC_LICENSE.txt',O/'RPC_LICENSE.txt')
# Reuse actual converter body in a worker; retain baseline byte parity.
s=(R/'scripts/convert_arcade_rpc_r68.mjs').read_text(encoding='utf-8-sig');start=s.index(' const linearRGBA=');end=s.index(" fs.writeFileSync(path.join(out,p.id+'.preserve')",start);body=s[start:end]
body=body.replace('brightness:44*.02-1,contrast:54*.02,saturation:71*.02,gamma:.98','brightness:settings.brightness*.02-1,contrast:settings.contrast*.02,saturation:settings.saturation*.02,gamma:settings.gamma')
# Optional scroll policy replaces independently chosen pairs with source-gap runs.
needle=' const result=new Float32Array(n*3);';body=body.replace(needle,' if(settings.scroll)applyScrollPairs(work,mask,p,attrs,colors,palettes);\n'+needle)
header='''// Actual RPC CPU conversion functions. GPL-3.0; see RPC_LICENSE.txt.
let alphaMask;
Object.assign(globalThis,{RGB_DISTANCE_WEIGHT_R:.2126**2,RGB_DISTANCE_WEIGHT_G:.7152**2,RGB_DISTANCE_WEIGHT_B:.0722**2,DIFFUSION_KERNELS:{'sierra-lite':new Float32Array([1,0,.5,-1,1,.25,0,1,.25])},pipelineIsCurrent:()=>true,pipelineWorkDeadline:()=>Infinity,pipelineShouldYield:()=>false,finishPrepareLinearWork:()=>{},pipelineStageFinishDitherPass:()=>{},pipelineFail:(id,e)=>{throw e}});
'''+(B/'rpc_core_extracted.js').read_text(encoding='utf-8-sig')+'''
const normal=[[0,0,0],[1,0,206],[207,1,0],[207,1,206],[0,207,21],[1,207,207],[207,207,21],[207,207,207]],bright=[[96,96,96],[2,0,253],[255,2,1],[255,2,253],[0,255,28],[2,255,255],[255,255,29],[255,255,255]];
function applyScrollPairs(work,mask,p,attrs,colors,palettes){
 for(let y=0;y<p.h;y++){
  const occupied=[];for(let x=0;x<p.w;x++)if(mask[y*p.w+x])occupied.push(x);
  const runs=[];for(const x of occupied){let r=runs.at(-1);if(!r||x-r[1]-1>=8)runs.push([x,x]);else r[1]=x;}
  for(const [left,right]of runs){
   // Moving silhouette edges and internal holes require true normal black.
   let ink=1,best=Infinity;
   for(let q=1;q<8;q++){let e=0;for(let x=left;x<=right;x++){const k=(y*p.w+x)*3;let a=0,b=0;for(let c=0;c<3;c++){a+=work[k+c]**2;b+=(work[k+c]-palettes[0][q][c])**2;}e+=Math.min(a,b);}if(e<best){best=e;ink=q;}}
   for(let bx=Math.floor(left/8);bx<=Math.floor(right/8);bx++){attrs[y*p.w/8+bx]=ink;colors[y][bx]=[palettes[0][ink],palettes[0][0]];}
  }
 }
}
function convert(p,raw,mask,settings){const n=p.w*p.h;alphaMask=mask;const context=globalThis;context.CPU_PREP_PIXEL_CHUNK=n;context.DITHER_ROW_CHUNK=p.h;
'''
footer='''
 const indices=new Uint8Array(n);for(let y=0;y<p.h;y++)for(let x=0;x<p.w;x++){const a=attrs[y*p.w/8+(x>>3)],bank=a&64?8:0;indices[y*p.w+x]=(bits[y*p.w/8+(x>>3)]&(128>>(x&7)))?((a&7)+bank):(((a>>3)&7)+bank);}
 let clashes=0;if(settings.scroll)for(let shift=0;shift<8;shift++)for(let y=0;y<p.h;y++)for(let bx=0;bx<Math.ceil((p.w+8)/8);bx++){const values=new Set();for(let k=0;k<8;k++){const x=bx*8+k-shift;values.add(x>=0&&x<p.w?indices[y*p.w+x]:0);}if(values.size>2)clashes++;}
 if(settings.scroll&&clashes)throw Error('Scrolling palette conflict '+clashes);
 return {id:p.id,w:p.w,h:p.h,rgb,indices,bits,attrs,clashes};}
function from64(s){return Uint8Array.from(atob(s),x=>x.charCodeAt(0));}
if(typeof self!=='undefined')self.onmessage=e=>{const {token,items,settings}=e.data;try{for(const p of items){const result=convert(p,from64(p.raw),from64(p.mask),settings);self.postMessage({token,result});}self.postMessage({token,done:true});}catch(error){self.postMessage({token,error:String(error.stack||error)});}};
'''
(O/'worker.js').write_text(header+body+footer,encoding='utf-8');print('records',len(data['records']),'families',len(set(r['family']for r in data['records'])))
