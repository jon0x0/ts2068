from pathlib import Path
import json,html,shutil,hashlib,collections
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();O=R/'build/graphics/arcade_rpc_comparison_r68';j=json.loads((O/'inputs.json').read_text());pal=np.array([[0,0,0],[1,0,206],[207,1,0],[207,1,206],[0,207,21],[1,207,207],[207,207,21],[207,207,207],[96,96,96],[2,0,253],[255,2,1],[255,2,253],[0,255,28],[2,255,255],[255,255,29],[255,255,255]],np.uint8)
checks=[]
for p in j['profiles']:
 id=p['id'];w,h=p['w'],p['h'];bits=np.frombuffer((O/f'{id}.bits').read_bytes(),np.uint8).reshape(h,w//8);attrs=np.frombuffer((O/f'{id}.attrs').read_bytes(),np.uint8).reshape(h,w//8);mask=np.frombuffer((O/f'{id}.mask').read_bytes(),np.uint8).reshape(h,w);rgb=np.frombuffer((O/f'{id}.rgb').read_bytes(),np.uint8).reshape(h,w,3);a=np.zeros((h,w),np.uint8)
 assert not (attrs&128).any()
 for y in range(h):
  for x in range(w//8):
   t=int(attrs[y,x]);b=8 if t&64 else 0;ink=(t&7)+b;paper=(t>>3&7)+b;assert not b or (ink!=8 and paper!=8)
   for k in range(8):a[y,x*8+k]=ink if bits[y,x]&(128>>k)else paper
 assert np.array_equal(pal[a],rgb),id
 assert not rgb[mask==0].any(),id
 assert not (np.unpackbits(bits,axis=1)[mask==0]).any(),id
 Image.fromarray(rgb).save(O/f'{id}.png');checks.append({'id':id,'legal_8x1':True,'exact_byte_roundtrip':True,'normal_black_space':True,'bytes':bits.size+attrs.size})
shutil.copy2(R/'build/graphics/l2_rpc_settings/RPC_LICENSE.txt',O/'RPC_LICENSE.txt')
records=sorted(j['records'],key=lambda r:(r['level'],0 if ('Corrected' in r['status']or'Accepted' in r['status'])else 1,r['descriptor'],r['key']))
page=['''<!doctype html><meta charset="utf-8"><title>R-Type arcade RPC comparisons</title><style>body{background:#15191f;color:#e3e8ee;font:16px system-ui;margin:24px}a{color:#80dfff}header{position:sticky;top:0;background:#15191ff5;padding:12px;z-index:2}select,input,button{font:inherit;padding:5px}article{border:1px solid #52606b;padding:16px;margin:18px 0}article h2{margin:0 0 8px}.grid{display:grid;grid-template-columns:repeat(4,minmax(160px,1fr));gap:16px}.pic{background:#000;min-height:120px;display:flex;align-items:center;justify-content:center;overflow:auto}.pic img{image-rendering:pixelated;max-width:100%;object-fit:contain}small{color:#b9c6d2}.warn{color:#ffd88c}body.checker .pic{background:repeating-conic-gradient(#303640 0% 25%,#10141a 0% 50%) 0/16px 16px}@media(max-width:850px){.grid{grid-template-columns:1fr 1fr}}</style>
<header><h1>Arcade artwork: RPC comparison</h1><p>124 source entries / 248 conversions. Brightness44 · Contrast54 · Saturation71 · Gamma0.98 · Sierra Lite · legal8×1 ECM. Black space stays normal black.</p><label>Level <select id="level"><option value="all">All</option>''']
page.extend(f'<option>{n}</option>'for n in range(1,9));page+=['''</select></label> <label>Show <select id="status"><option value="all">All sources</option><option value="corrected">Corrected / accepted sources</option><option value="historical">Historical matches to review</option></select></label> <input id="query" placeholder="Search e.g. L3_101"> <button onclick="document.body.classList.toggle('checker')">Background contrast</button><p id="count"></p></header><p class="warn">Asset previews only. No game assets replaced. Historical descriptor numbers do not prove a correct arcade match. Corrected L2/L6 sources appear first in their levels. L6 old matches include withdrawn identities.</p><p>Current column shows an extracted r67 phase0 cache where available, otherwise its stored native source. It is not a complete composited gameplay screenshot. The L5 core reference is the accepted packed96×96 core; the complete boss also contains separate organic spheres. <a href="../bellmite_complete_preview/index.html">Accepted complete L5 assembly</a> · <a href="../l2_integrated_r67/index.html">Playable L2 reference</a>. Detailed candidates enlarge artwork by1.3× before conversion; dimensions include8-pixel storage padding. Collision boxes and runtime costs are not approved by these previews.</p>''']
for r in records:
 k=r['key'];safe=html.escape;corrected=('Corrected' in r['status']or'Accepted' in r['status']);page.append(f'<article data-level="{r["level"]}" data-status="{"corrected"if corrected else"historical"}" data-key="{k.lower()}"><h2>L{r["level"]} #{r["descriptor"]} — {k}</h2><p class="warn">{safe(r["status"])}</p><div class="grid">')
 items=[('Arcade source',k+'_source.png',None),('Current reference',k+'_stored.png',r.get('current_kind','Reference unavailable'))]+[(('N · Native footprint'if p['label']=='N'else'D · 1.3× detail'),p['id']+'.png',str(p['size'][0])+'×'+str(p['size'][1]))for p in r['profiles']]
 for title,file,detail in items:
  if not(O/file).exists():page.append('<div><h3>'+title+'</h3><p>Current reference unavailable; conversion still available.</p></div>');continue
  im=Image.open(O/file);displayw=min(im.width*3,500);page.append(f'<div><h3>{title}</h3><div class="pic"><a href="{file}"><img loading="lazy" src="{file}" style="width:{displayw}px" alt="{safe(k+" "+title)}"></a></div><small>{safe(detail or str(im.width)+"×"+str(im.height))}</small></div>')
 page.append('</div></article>')
page.append('''<script>const all=[...document.querySelectorAll('article')];function filter(){let n=0;for(const a of all){let show=(level.value==='all'||a.dataset.level===level.value)&&(statusSelect.value==='all'||a.dataset.status===statusSelect.value)&&a.dataset.key.includes(query.value.toLowerCase());a.hidden=!show;if(show)n++}count.textContent=n+' comparisons shown'}const level=document.querySelector('#level'),statusSelect=document.querySelector('#status'),query=document.querySelector('#query'),count=document.querySelector('#count');for(const e of[level,statusSelect,query])e.addEventListener('input',filter);filter();</script>''');(O/'index.html').write_text(''.join(page),encoding='utf-8')
# Small contact sheets for visual QA; complete gallery links retain native pixels.
for n in range(1,9):
 rr=[r for r in records if r['level']==n][:5];sheet=Image.new('RGB',(1000,len(rr)*190),(20,24,30));d=ImageDraw.Draw(sheet)
 for i,r in enumerate(rr):
  d.text((4,i*190+3),r['key'],fill='white')
  files=[r['key']+'_source.png',r['key']+'_stored.png']+[p['id']+'.png'for p in r['profiles']]
  for col,file in enumerate(files):
   if not(O/file).exists():continue
   im=Image.open(O/file).convert('RGBA');im.thumbnail((240,155),Image.Resampling.NEAREST);sheet.paste(im,(col*250,i*190+25),im)
 sheet.save(O/f'contact_L{n}.png')
sha=hashlib.sha256((R/'build/fullgame/l2_rpc_r67/RType_TS2068_r67.zip').read_bytes()).hexdigest();assert sha=='f35144c6c728f6485fb3fcb658dd26b2a6fa3a4f737d531ba4d4eeb69b94a716';report={'comparisons':len(records),'conversions':len(checks),'validation':checks,'current_references':dict(collections.Counter(r.get('current_kind','unavailable')for r in records)),'playable_r67_unchanged':sha,'scope':'offline conversion/inspection only; no installed replacements or performance claim'};(O/'validation.json').write_text(json.dumps(report,indent=2));print(report['comparisons'],report['conversions'],report['current_references'])
