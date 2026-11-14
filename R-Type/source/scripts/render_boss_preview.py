from pathlib import Path
from PIL import Image,ImageDraw
from build_graphics import unpack
out=Path(__file__).resolve().parents[1]/'build/fullgame/boss_preview_r42'
sheet=Image.new('RGB',(1024,420));draw=ImageDraw.Draw(sheet)
for n in range(1,9):
    data=(out/f'boss_level{n}.home.bin').read_bytes()
    image=unpack(data[0x4000:0x5800],data[0x6000:0x7800]);image.save(out/f'level{n}.png')
    x=(n-1)%4*256;y=(n-1)//4*210;sheet.paste(image,(x,y+15));draw.text((x,y),f'Level {n}',fill='white')
sheet.save(out/'contact.png')
