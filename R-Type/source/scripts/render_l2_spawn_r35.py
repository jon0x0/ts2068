from pathlib import Path
import sys
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r/'scripts'))
from build_graphics import unpack
from PIL import Image,ImageDraw
def render():
 d=r/'build/diagnostics/l2_spawn_r35'
 for p in d.glob('*.home.bin'):
  b=p.read_bytes();unpack(b[0x4000:0x5800],b[0x6000:0x7800]).resize((768,576),Image.Resampling.NEAREST).save(p.with_suffix('.png'))
 if (d/'old_pose.home.png').exists():
  im=Image.new('RGB',(400,210));dr=ImageDraw.Draw(im)
  for x,name,label in [(0,'old_pose','OLD TABLE'),(200,'fixed_pose','RESTORED TABLE')]:
   a=Image.open(d/(name+'.home.png')).crop((14*24,12*24,19*24,17*24)).resize((160,160),Image.Resampling.NEAREST);im.paste(a,(x+15,30));dr.text((x+15,8),label,fill='white')
  im.save(d/'table_comparison.png')
if __name__=='__main__':render()
