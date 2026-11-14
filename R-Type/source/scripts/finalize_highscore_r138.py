from pathlib import Path
import sys,numpy as np,json,zipfile,hashlib,functools
from PIL import Image
sys.path.insert(0,'scripts');from build_graphics import screen_offset,PALETTE
p=Path('build/fullgame/highscore_r138');b=(p/'L7_scores.home.bin').read_bytes();a=np.zeros((192,256),np.uint8)
for y in range(192):
 for x in range(32):
  bits=b[0x4000+screen_offset(y)+x];at=b[0x5800+(y//8)*32+x];assert at==(0 if x in[0,31]else 71);br=(at>>6&1)*8;a[y,x*8:x*8+8]=[(at&7)+br if bits&(128>>z)else((at>>3)&7)+br for z in range(8)]
Image.fromarray(PALETTE[a].astype('uint8')).resize((768,576),Image.Resampling.NEAREST).save(p/'L7_scores.png')
for q in (p/'rtype').glob('*.TAP'):
 src=q.read_bytes();pos=0
 while pos<len(src):
  n=int.from_bytes(src[pos:pos+2],'little');v=src[pos+2:pos+2+n];assert functools.reduce(int.__xor__,v)==0;pos+=n+2
 assert pos==len(src)
text='''R-Type TS2068 r138 candidate: L7 post-death high-score display repair.
Replace the complete rtype folder, reset, launch rtype/rt.tap.
Post-death score entry now uses the existing standard-video restore in all levels.
The shared restore clears stale gameplay attributes to white on normal black.
The existing 17-byte helper is replaced in place; no new allocations.
All artwork and prior r137 L4 fixes retained. No new walker artwork installed.
Tests: cold startup and 20 game updates on all eight levels, then actual
post-death score-display caller with entry mapping normalized to 09; mode/banks verified. L7 standard attributes
checked and rendered. This is an injected transition probe, not a full natural
death/name-entry playthrough or hardware confirmation. TAP checksums pass.
Stable r100 and prior archives unchanged.
'''
(p/'README.txt').write_text(text);(p/'rtype/README.txt').write_text(text)
assert json.loads((p/'highscore_validation.json').read_text())['passed']
manifest={q.name:hashlib.sha256(q.read_bytes()).hexdigest()for q in sorted((p/'rtype').iterdir())if q.is_file()};(p/'release_manifest.json').write_text(json.dumps(manifest,indent=2))
z=p/'RType_TS2068_r138.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED)as f:
 for q in sorted((p/'rtype').iterdir()):
  if q.is_file():f.write(q,'rtype/'+q.name)
 for name in ['README.txt','highscore_contract.json','highscore_validation.json','release_manifest.json','L7_scores.png']:f.write(p/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z,hashlib.sha256(z.read_bytes()).hexdigest())


B=Path('build/fullgame/l4_openings_r137')
for i in range(1,9):
 name=f'level{i:02d}_region.bin';a=(B/name).read_bytes();b=(p/name).read_bytes();diff=[k for k,(x,y)in enumerate(zip(a,b))if x!=y];assert all(0x19d2<=k<0x19e3 or 0x52ef<=k<0x52f2 or a[max(0,k-3):k+1].endswith(b'R137')for k in diff),(name,diff)
