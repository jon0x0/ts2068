"""Three genuine SCLD modes, ten regions per line, stationary artwork."""
from pathlib import Path
import json,struct,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
VALUES={'H':0x36,'E':2,'N':0}
STARTS=list(range(0,28,3))
def row(y):return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
def modes(y):return [('H','E','N') if (y//32)%2==0 else ('N','E','H')][0]
def pad(t):
 for n in range(t//7+1):
  if (t-7*n)%4==0:return bytes((0x3e,0))*n+bytes((t-7*n)//4)
 raise ValueError(t)
def delay(t):
 out=bytearray()
 while t>3350:out+=bytes((6,255,0x10,0xfe));t-=3317
 for n in range(255,0,-1):
  if t>=13*n+2:
   try:rest=pad(t-13*n-2)
   except ValueError:continue
   return out+bytes((6,n,0x10,0xfe))+rest
 return out+pad(t)
def artwork():
 ram=bytearray(65536);glyphs=(ROOT/'timex-font-8x8.bin').read_bytes()
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',8)
 panels=[]
 for band in range(6):
  order=modes(band*32)
  for panel,start in enumerate(STARTS):
   end=STARTS[panel+1] if panel+1<len(STARTS) else 32
   mode=order[panel%3];width=(end-start)*(16 if mode=='H' else 8)
   im=Image.new('1',(width,32));d=ImageDraw.Draw(im)
   def text(s,y):
    x=(width-len(s)*8)//2
    for ch in s:
     for v in range(8):
      bits=glyphs[(ord(ch)-32)*8+v]
      for u in range(8):
       if bits&(128>>u) and 0<=x+u<width:im.putpixel((x+u,y+v),1)
     x+=8
   text({'H':'HIRES','E':'ECM','N':'STD'}[mode],0)
   if mode=='H':
    label='512x192';box=d.textbbox((0,0),label,font=font)
    d.text(((width-box[2]+box[0])//2,8-box[1]),label,font=font,fill=1)
    for yy in range(19,29):
     for xx in range(2,width-2):
      if (xx+yy)&1:im.putpixel((xx,yy),1)
    d.line((2,16,width-3,16),fill=1)
    d.line((2,30,width-3,30),fill=1)
    # A solid paper cutout and white/yellow bar expose the checker contrast.
    d.rectangle((width//3,22,width*2//3,25),fill=0)
   else:text('8x1' if mode=='E' else '8x8',8)
   for dy in range(32):
    y=band*32+dy
    for c in range(start,end):
     k=row(y)+c
     if mode=='H':
      for plane in range(2):
       bits=0
       for b in range(8):
        x=(c-start)*16+plane*8+b
        if im.getpixel((x,dy)):bits|=128>>b
       ram[0x4000+plane*0x2000+k]=bits
     else:
      bits=sum(128>>b for b in range(8) if im.getpixel(((c-start)*8+b,dy)))
      if dy<16:
       ink=7 if mode=='N' else [2,6,4,5,1,3,7,5][dy%8]
       attribute=ink|64
      elif mode=='E':
       color=(dy-16+(c-start)*3)%16;attribute=(color&7)*9+(64 if color&8 else 0)
       if c==end-1 and dy>=24:
        ink=(color&7);paper=(ink+3)%8;attribute=ink|(paper<<3)|64;bits=0xaa if y%2==0 else 0x55
      else:
       color=((dy//8)+(c-start)+band*3+panel)%16
       attribute=(color&7)*9+(64 if color&8 else 0)
      ram[0x4000+k]=bits
      if mode=='E':ram[0x6000+k]=attribute
      else:ram[0x5800+(y//8)*32+c]=attribute
   panels.append(dict(band=band,start=start,end=end,mode=mode))
 (ROOT/'panels.json').write_text(json.dumps(panels,indent=2))
 return ram
def build():
 ram=artwork();rom=bytearray(8192);pc=0x100;labels={};events=[];fixes=[]
 def emit(*v):
  nonlocal pc
  rom[pc:pc+len(v)]=bytes(v);pc+=len(v)
 def mark(name):labels[name]=pc
 def jump(op,name):emit(op,0,0);fixes.append((pc-2,name))
 rom[:3]=bytes((0xc3,0,1));rom[0x38]=0xc9
 emit(0xf3,0x31,0,0xff,0xed,0x56,1,0xff,0,0x16,0x36,0x1e,2,0x26,0,0x3e,4,0xd3,0xfe)
 mark('frame');emit(0xfb,0x76,0xf3)
 # IRQ acknowledgement + RET + DI =27T. OUT (C),r performs its I/O cycle 8T after instruction start.
 emit(*delay(40*224-27))
 regs={'H':0x51,'E':0x59,'N':0x61} # OUT (C),D/E/H, 12T each.
 for y in range(192):
  order=modes(y);sequence=[order[i%3] for i in range(10)]
  for i,mode in enumerate(sequence):
   if i==1:emit(*pad(24))
   phase=8 if i==0 else 44+(i-1)*12
   events.append(dict(time=(40+y)*224+phase,value=VALUES[mode],mode=mode,row=y,region=i))
   emit(0xed,regs[mode])
  emit(*delay(70))
  if y==191:jump(0xc3,'frame')
  else:emit(0xc3,(pc+3)&255,(pc+3)>>8)
 assert pc<8192,pc
 for at,n in fixes:struct.pack_into('<H',rom,at,labels[n])
 # Return to standard mode in the lower border; the final row already ends N.
 dck=bytes((255,2,0,3,3,0,0,0,0))+rom+ram[0x4000:0x8000]
 (ROOT/'triple-personality-mosaic.dck').write_bytes(dck)
 (ROOT/'initial-ram.bin').write_bytes(ram)
 (ROOT/'mode-events.json').write_text(json.dumps(events))
 (ROOT/'labels.json').write_text(json.dumps(labels,indent=2))
 print('Built',len(dck),'bytes; ROM code ends',hex(pc),'mode writes/frame',len(events))
if __name__=='__main__':build()
