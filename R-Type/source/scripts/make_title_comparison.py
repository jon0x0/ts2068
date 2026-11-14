"""Compare actual native ECM title captures with arcade and legacy colours."""
from pathlib import Path
from PIL import Image,ImageDraw
from build_graphics import unpack,screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/ecm_native';ram=(out/'probe_3000.bin').read_bytes();attrs=bytearray(6144)
 for y in range(192):attrs[screen_offset(y):screen_offset(y)+32]=ram[6144+(y//8)*32:6144+(y//8+1)*32]
 legacy=unpack(ram[:6144],attrs);legacy.save(out/'title_legacy_reference.png')
 sheet=Image.new('RGB',(528,164),(16,20,25));draw=ImageDraw.Draw(sheet)
 for i,(label,im) in enumerate([('ARCADE REFERENCE',Image.open(ROOT/'build/graphics/arcade_title_reference.png')),('ORIGINAL 8x8 COLOUR',legacy),('ECM / PRESERVE PALETTE',Image.open(out/'probe_3000_preserve.png')),('ECM / COLOUR EMPHASIS',Image.open(out/'probe_3000.png'))]):
  x=4+(i%2)*264;y=4+(i//2)*82;draw.text((x,y),label,fill='white');sheet.paste(im.crop((0,96,256,152)),(x,y+18))
 sheet.resize((1056,328),Image.Resampling.NEAREST).save(out/'title_r6_comparison.png')
if __name__=='__main__':main()
