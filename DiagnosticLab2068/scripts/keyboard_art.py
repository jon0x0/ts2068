"""Adapt Josef Jelinek's TSRun keyboard art into native, live-highlightable keys.

The original image is preserved verbatim in assets/keyboard; its hash was
verified against the user-specified published URL. All conversion is host-side.
Fixed target rectangles align to attribute cells so neighboring keys never
share a highlight. Main key labels are replaced with readable TS2068 glyphs.
"""
from pathlib import Path
import hashlib, json
from PIL import Image
from generate_design_assets import offset

ROOT=Path(__file__).resolve().parents[1]

def face_mask(cap):
    """Extract the source's white key-face contour and remove tiny legends.

    Use its largest connected white region; fill its horizontal spans so the
    printed BASIC words do not turn into misleading speckles after reduction.
    """
    width,height=cap.size
    remaining={(x,y) for y in range(height) for x in range(width) if cap.getpixel((x,y))>=240}
    largest=set()
    while remaining:
        seed=remaining.pop();component={seed};pending=[seed]
        while pending:
            x,y=pending.pop()
            for point in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if point in remaining:remaining.remove(point);component.add(point);pending.append(point)
        if len(component)>len(largest):largest=component
    assert largest
    left=min(x for x,y in largest);right=max(x for x,y in largest)+1
    top=min(y for x,y in largest);bottom=max(y for x,y in largest)+1
    mask=Image.new('L',(right-left,bottom-top),0)
    for y in range(top,bottom):
        xs=[x for x,yy in largest if yy==y]
        if xs:
            for x in range(min(xs),max(xs)+1):mask.putpixel((x-left,y-top),255)
    return mask,(left,top,right,bottom)

def draw_keyboard(pixels,attrs,font):
    source=ROOT/'assets/keyboard/TSRun-keyboard.png'
    provenance=json.loads((source.parent/'provenance.json').read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest()==provenance['source_sha256']
    art=Image.open(source).convert('L');assert art.size==(533,191)
    specs=[]
    rows=[list('1234567890'),list('QWERTYUIOP'),list('ASDFGHJKL')+['EN'],['CS']+list('ZXCVBNM')+['SY','BR','CS'],['SPACE']]
    for row,labels in enumerate(rows):
        sx=[14,36,47,14,113][row];sy=[7,44,81,118,155][row]
        widths=([43]*10 if row<2 else [43]*9+[76] if row==2 else [54]+[43]*9+[54] if row==3 else [307])
        for col,(name,width) in enumerate(zip(labels,widths)):
            if row<2: cx=3*col+row;w=2
            elif row==2:cx=2+3*col;w=3 if name=='EN' else 2
            elif row==3:
                cx=[0,3,6,9,12,15,18,21,24,27,29][col]
                w=3 if name in ('CS','SY') else 2
            else:cx=7;w=18
            cy=5+3*row
            specs.append(dict(name=name,source=[sx,sy,width,36],target=[cx,cy,w,2]))
            sx+=width+1
    coords={};occupied=set()
    def pixel(x,y,on):
        at=offset(x//8,y);mask=128>>(x&7)
        if on:pixels[at]|=mask
        else:pixels[at]&=~mask
    for spec in specs:
        name=spec['name'];sx,sy,sw,sh=spec['source'];cx,cy,w,h=spec['target']
        assert 0<=cx<cx+w<=32 and 5<=cy<cy+h<=19
        cells={(yy,xx) for yy in range(cy,cy+h) for xx in range(cx,cx+w)}
        assert not occupied&cells,('neighboring key attributes overlap',name)
        occupied|=cells;coords.setdefault(name,[]).append((cy,cx,w))
        cap=art.crop((sx,sy,sx+sw,sy+sh))
        # The source SYMBOL SHIFT key has a black face. Use the neighboring
        # white-face contour for its reduction, then retain inverse colors.
        if name=='SY':cap=art.crop((36,44,79,80))
        cap,bounds=face_mask(cap);spec['face_bounds']=list(bounds)
        cap=cap.resize((w*8-2,h*8-2),Image.Resampling.BOX)
        for y in range(h*8):
            for x in range(w*8):
                interior=0<x<w*8-1 and 0<y<h*8-1
                face=interior and cap.getpixel((x-1,y-1))>=128
                pixel(cx*8+x,cy*8+y,not face or name=='SY')
        for yy,xx in cells:attrs[yy*32+xx]=0x78 # Black ink / bright white paper.
        label=name;x0=cx*8+(w*8-len(label)*8)//2;y0=cy*8+4
        # SYMBOL SHIFT is black in the original: retain reversed lettering.
        reverse=name=='SY'
        for y in range(8):
            for x in range(len(label)*8):pixel(x0+x,y0+y,reverse)
        for n,ch in enumerate(label):
            for y,bits in enumerate(font[(ord(ch)-32)*8:(ord(ch)-31)*8]):
                for x in range(8):pixel(x0+n*8+x,y0+y,bool(bits&(128>>x))^reverse)
    coords['BREAK']=coords['BR']
    (ROOT/'build/keyboard-art-layout.json').write_text(json.dumps(dict(author=provenance['author'],source_sha256=provenance['source_sha256'],
        palette={'unseen':0x78,'held':0x60,'released':0x68},keys=specs),indent=2)+'\n')
    return coords
