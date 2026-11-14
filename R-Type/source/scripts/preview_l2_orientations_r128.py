from pathlib import Path
import json,zipfile,numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();G=R/'build/graphics/l2_orientations_r128';ct=json.loads((R/'build/fullgame/l2_orientations_r128/L2_actor_contract.json').read_text());old=json.loads((R/'build/fullgame/l2_roles_restore_r127/L2_actor_contract.json').read_text());z=zipfile.ZipFile(R/'convref/rtype-l2-art-assets_v2.zip');pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],np.uint8)
def image(v,n):
 a=np.frombuffer(v,np.uint8).reshape(5,40,2).copy()
 if n&1:
  a=a[::-1].copy();a[:,:,0]=np.array([int(f'{int(x):08b}'[::-1],2)for x in a[:,:,0].ravel()],np.uint8).reshape(5,40)
 if n&2:a=a[:,::-1].copy()
 out=np.zeros((40,40,3),np.uint8)
 for x in range(5):
  for y in range(40):
   bits,attr=map(int,a[x,y]);out[y,x*8:(x+1)*8]=pal[[(attr&7)if bits&(128>>k)else(attr>>3)&7 for k in range(8)]]
 return Image.fromarray(out)
board=Image.new('RGB',(1400,680),'#171b24');d=ImageDraw.Draw(board);d.text((8,8),'Corrected headings - false X: right; false Y: down. All ten chosen frames retained.',fill='white')
compare=Image.new('RGB',(1400,350),'#171b24');dc=ImageDraw.Draw(compare);dc.text((8,8),'Before / corrected, all posed heading right/down. Frames2 and5 were reversed.',fill='white')
for direction in range(4):
 label=['Right / Down','Left / Down','Right / Up','Left / Up'][direction];d.text((4,40+direction*160),label,fill='white')
 for f in range(10):
  raw=z.read(f'scorpion/frame_{f:02d}.pairs.bin');(G/f'export_{f:02d}.pairs.bin').write_bytes(raw);im=image(raw,ct['scorpion_normalize_flips'][f]^(direction^3));im.resize((120,120),Image.Resampling.NEAREST).save(G/f'frame_{f:02d}_direction_{direction}.png');board.paste(im.resize((120,120),Image.Resampling.NEAREST),(120+128*f,40+direction*160));d.text((122+128*f,162+direction*160),f'Frame {f}',fill='white')
for row,settings in enumerate([old,ct]):
 dc.text((4,40+row*160),['Before','Corrected'][row],fill='white')
 for f in range(10):
  raw=z.read(f'scorpion/frame_{f:02d}.pairs.bin');im=image(raw,settings['scorpion_normalize_flips'][f]^3);compare.paste(im.resize((120,120),Image.Resampling.NEAREST),(120+128*f,40+row*160));dc.text((122+128*f,162+row*160),f'Frame {f}',fill='white')
board.save(G/'headings.png');compare.save(G/'comparison.png')
html="""<!doctype html><meta charset=utf-8><title>L2 orientations r128</title><style>body{background:#171b24;color:#eee;font:16px system-ui;margin:24px}img{max-width:100%;image-rendering:pixelated}button,select{font:inherit;padding:8px}.frames{display:flex;gap:12px;flex-wrap:wrap}.frames img{width:120px}.card{text-align:center}</style><h1>Corrected L2 scorpion headings</h1><p>FlipX=false means head right. FlipY=false means head down. No resizing or new conversion settings.</p><img src="comparison.png"><h2>Animate all ten frames with a fixed heading</h2><select id="direction"><option value="0">False X / False Y: right/down</option><option value="1">True X / False Y: left/down</option><option value="2">False X / True Y: right/up</option><option value="3">True X / True Y: left/up</option></select> <button id="toggle">Pause</button><p id="label"></p><img id="anim" width="240" height="240"><h2>All headings</h2><img src="headings.png"><p>Frame3 uses false X / true Y: its original64x64arcade pixels are an exact vertical flip of Frame9, which you identified as false/false.</p><h2>Snake order</h2><p>Head - existing neck segment - four spiny sections - nine round body segments - tail. Native head/tail orientations and dimensions unchanged.</p><script>const order=[6,2,7,8,9,5,1,3,0,4];let i=0,run=true;const dir=document.querySelector('#direction'),im=document.querySelector('#anim'),lab=document.querySelector('#label');function draw(){const f=order[i];im.src='frame_'+String(f).padStart(2,'0')+'_direction_'+dir.value+'.png';lab.textContent='Frame '+f+' (same heading throughout)'}dir.onchange=draw;document.querySelector('#toggle').onclick=e=>{run=!run;e.target.textContent=run?'Pause':'Play'};setInterval(()=>{if(run){i=(i+1)%order.length;draw()}},180);draw()</script>"""
(G/'index.html').write_text(html,encoding='utf-8');print(G/'index.html')
