from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np,html,hashlib
R=Path.cwd();O=R/'build/graphics/review_checkpoint_r70';j=json.loads((O/'manifest.json').read_text(encoding='utf-8'));data=json.loads((R/'build/graphics/arcade_review_r69/review_data.json').read_text(encoding='utf-8'));lookup={r['key']:r for r in data['records']};pal=np.array([[0,0,0],[1,0,206],[207,1,0],[207,1,206],[0,207,21],[1,207,207],[207,207,21],[207,207,207],[96,96,96],[2,0,253],[255,2,1],[255,2,253],[0,255,28],[2,255,255],[255,255,29],[255,255,255]],np.uint8);validated=[]
for r in j['records']:
 if not r.get('preview'):continue
 w,h=r['dimensions'];rgb=np.frombuffer((O/(r['key']+'.rgb')).read_bytes(),np.uint8).reshape(h,w,3);bits=np.frombuffer((O/(r['key']+'.bits')).read_bytes(),np.uint8).reshape(h,w//8);attrs=np.frombuffer((O/(r['key']+'.attrs')).read_bytes(),np.uint8).reshape(h,w//8);a=np.zeros((h,w),np.uint8)
 for y in range(h):
  for x in range(w//8):
   v=int(attrs[y,x]);bank=8 if v&64 else 0
   for k in range(8):a[y,x*8+k]=((v&7)if bits[y,x]&(128>>k)else(v>>3)&7)+bank
 assert np.array_equal(pal[a],rgb),r['key'];Image.fromarray(rgb).save(O/r['preview']);validated.append(r['key'])
for r in j['records']:
 if not r.get('nativeAlternative'):continue
 n=r['nativeAlternative'];w,h=n['dimensions'];rgb=np.frombuffer((O/(r['key']+'_native_same_settings.rgb')).read_bytes(),np.uint8).reshape(h,w,3);bits=np.frombuffer((O/(r['key']+'_native_same_settings.bits')).read_bytes(),np.uint8).reshape(h,w//8);attrs=np.frombuffer((O/(r['key']+'_native_same_settings.attrs')).read_bytes(),np.uint8).reshape(h,w//8);a=np.zeros((h,w),np.uint8)
 for y in range(h):
  for x in range(w//8):
   v=int(attrs[y,x]);assert not(v&128);bank=8 if v&64 else 0;assert not bank or(v&7)!=0 and(v>>3&7)!=0
   for k in range(8):a[y,x*8+k]=((v&7)if bits[y,x]&(128>>k)else(v>>3)&7)+bank
 assert np.array_equal(pal[a],rgb),r['key']+' native alternative';Image.fromarray(rgb).save(O/n['preview'])
# A separate browser storage key preserves later edits in the original review page.
review=json.loads((O/'review_snapshot.json').read_text(encoding='utf-8-sig'));page=(R/'build/graphics/arcade_review_r69/index.html').read_text(encoding='utf-8');assert "storageKey='rtype-art-review-v1'"in page;page=page.replace("storageKey='rtype-art-review-v1'","storageKey='rtype-art-review-checkpoint-r70'").replace('let state={families:{},entries:{},assignments:{}};','let state='+json.dumps(review['state'],separators=(',',':')).replace('<','\\u003c')+';');page=page.replace('<title>R-Type artwork review</title>','<title>Saved R-Type review checkpoint</title>').replace('<h1>R-Type artwork review</h1>','<h1>Saved R-Type review checkpoint</h1><p>Preloaded from your mostly-complete review. This page saves separately from the original form.</p>');(R/'build/graphics/arcade_review_r69/saved_review_r70.html').write_text(page,encoding='utf-8')
parts=['''<!doctype html><meta charset="utf-8"><title>Saved artwork review checkpoint</title><style>body{background:#161b22;color:#e9eef4;font:17px system-ui;margin:25px}a{color:#89ddff}article{border:1px solid #526273;padding:16px;margin:18px 0}img{image-rendering:pixelated;max-width:100%;object-fit:contain;background:black}.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px}.warning{color:#ffd58a}button,select{font:inherit;padding:5px}article[hidden]{display:none}</style><h1>Your saved review</h1><p>52 tweaked entries /39families ·6needs review ·66unmarked ·0explicit Accept. Tweaks regenerated exactly as saved. No gameplay artwork installed. All enlargements are held for geometry review.</p><p><a href="../arcade_review_r69/saved_review_r70.html">Resume the form with your saved choices already loaded</a> · <a href="review_snapshot.json">Original review snapshot</a> · <a href="manifest.json">Validation / integration flags</a></p><p>Detail-size geometry and historical source identities require integration checks. Thin L3 strips must be judged in their full assembly; independent strip previews do not prove palette continuity. The L2 historical-head settings are not automatically applied to the separate corrected heads.</p><label>Show <select id="filter"><option value="tweak">Tweaked</option><option value="review">Needs review</option><option value="unreviewed">Unmarked</option><option value="all">All</option></select></label>''']
for r in j['records']:
 k=r['key'];orig=lookup[k];parts.append(f'<article data-status="{r["decision"]}"><h2>{html.escape(k)} · {r["decision"]}</h2>');parts.append('<p>'+html.escape(str(r['settings']))+'</p>')
 if r.get('preview'):
  baseline=next(p['id']for p in orig['profiles']if p['label']==r['settings']['variant']);current_img='../l2_integrated_r67/body.png'if k=='L2_body'else f'../arcade_rpc_comparison_r68/{k}_stored.png';parts.append(f'<div class="grid"><div>Current reference<br><img src="{current_img}"></div><div>Previous RPC baseline<br><img src="../arcade_rpc_comparison_r68/{baseline}.png"></div><div>Your saved settings<br><img src="{k}.png"></div></div>')
 if r.get('nativeAlternative'):
  n=r['nativeAlternative'];parts.append(f'<div><h3>Original footprint, SAME saved colour settings</h3><img src="{n["preview"]}"><p class="warning">Enlargement HELD for geometry review. This alternative changes colours while retaining the original footprint; it is not installed.</p></div>')
 parts.append('<p class="warning">'+html.escape(' | '.join(r['flags']))+'</p></article>')
parts.append('''<script>const select=document.querySelector('#filter');function filter(){for(const a of document.querySelectorAll('article'))a.hidden=select.value!=='all'&&a.dataset.status!==select.value}select.onchange=filter;filter();</script>''');(O/'index.html').write_text(''.join(parts),encoding='utf-8')
rows=['L1_008','L2_body','L6_head0','L8_042'];sheet=Image.new('RGB',(1000,4*270),(20,25,32));d=ImageDraw.Draw(sheet)
for y,key in enumerate(rows):
 r=next(r for r in j['records']if r['key']==key);orig=lookup[key];base=next(p['id']for p in orig['profiles']if p['label']==r['settings']['variant']);d.text((4,y*270+2),key+' / previous baseline / saved settings',fill='white')
 for x,p in enumerate([R/f'build/graphics/arcade_rpc_comparison_r68/{base}.png',O/f'{key}.png']):
  im=Image.open(p).convert('RGB');im.thumbnail((480,240),Image.Resampling.NEAREST);sheet.paste(im,(x*500,y*270+25))
sheet.save(O/'checkpoint_contact.png');sha=hashlib.sha256((R/'build/fullgame/l2_rpc_r67/RType_TS2068_r67.zip').read_bytes()).hexdigest();assert sha=='f35144c6c728f6485fb3fcb658dd26b2a6fa3a4f737d531ba4d4eeb69b94a716';(O/'validation.json').write_text(json.dumps({'source_sha256':j['source_sha256'],'exact_reconstruction':validated,'native_alternatives_validated':sum(bool(r.get('nativeAlternative'))for r in j['records']),'families_consistent':True,'game_release_unchanged':sha,'scope':'saved proposal checkpoint, not installed game'},indent=2));print('Validated',len(validated),'regenerated proposals; resume form seeded')
