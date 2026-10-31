"""Space toggles a static ECM conversion and a timed Dynamic ECM conversion."""
from pathlib import Path
import struct,json,zlib
ROOT=Path(__file__).resolve().parent
MODE=0xb800
def word(x):return bytes((x&255,x>>8))
def row(y):return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
def pad(t):
    for sixes in range(4):
        for sevens in range(5):
            rest=t-6*sixes-7*sevens
            if rest>=0 and rest%4==0:return bytes((3,))*sixes+bytes((0x3e,0))*sevens+bytes(rest//4)
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
def build():
    container=(ROOT/'image.tdec').read_bytes();header=struct.unpack('<4sBBBBHHHHIIII',container[:32])
    magic,version,count,palette,dither,width,height,rows,split,bmp_len,attr_len,sched_len,crc=header
    assert (magic,version,count,palette,width,height,rows,split,bmp_len,attr_len,sched_len)==(b'TDEC',2,7,1,256,192,192,4,6144,6144,4032),'Unsupported TDEC profile'
    payload=container[32:];assert len(payload)==bmp_len+attr_len+sched_len and zlib.crc32(payload)==crc,'TDEC size/CRC failure'
    records=payload[12288:];schedule=[dict(columns=list(records[y*21:y*21+7]),old=list(records[y*21+7:y*21+14]),new=list(records[y*21+14:y*21+21])) for y in range(192)]
    assert schedule==json.loads((ROOT/'schedule.json').read_text())
    code=bytearray();events=[];before=[];after=[]
    for y,s in enumerate(schedule):
        rowevents=[];cols=s['columns'];assert len(cols)==7 and all(b-a>=5 for a,b in zip(cols,cols[1:]))
        for i,(c,value) in enumerate(zip(cols[:3],s['old'][:3])):
            addr=0x6000+row(y)+c;code+=bytes((0x3e,value,0x32))+word(addr)
            rowevents.append(dict(address=addr,value=value,time=-36+i*20))
        # Four resets per row are prestaged outside active display. Pack the
        # split asymmetrically to fit the two unequal blanking intervals.
        for i in range(3,7):
            target=before if i in (3,4) or (i==5 and y<48) else after
            target.append(dict(address=0x6000+row(y)+cols[i],value=s['old'][i]))
        code+=pad(10+4*cols[0])
        for i,(c,value) in enumerate(zip(cols,s['new'])):
            if i:code+=bytes(cols[i]-cols[i-1]-5)
            addr=0x6000+row(y)+c;code+=bytes((0x3e,value,0x32))+word(addr)
            rowevents.append(dict(address=addr,value=value,time=34+c*4))
        code+=bytes(31-cols[-1])
        code+=bytes((0xc3,))+word(0x8000+len(code)+3)
        events.append(rowevents)
    assert len(code)<0x3800,len(code)
    rom=bytearray(8192);rom[:3]=bytes((0xc3,0,1));rom[0x38]=0xc9
    pc=0x100;labels={};fixes=[]
    def emit(*v):
        nonlocal pc
        rom[pc:pc+len(v)]=bytes(v);pc+=len(v)
    def mark(n):labels[n]=pc
    def jump(op,n):emit(op,0,0);fixes.append((pc-2,n))
    def load(addr):emit(0x3a,addr&255,addr>>8)
    def save(addr):emit(0x32,addr&255,addr>>8)
    emit(0xf3,0x31,0xff,0xbf,0xed,0x56,0x3e,1);save(MODE);jump(0xcd,'load_image');jump(0xc3,'frame')
    mark('frame');emit(0xfb,0x76,0xf3)
    # 27T IRQ/RET/DI + 35T keyboard check + 27T mode check = 89T.
    emit(0x3e,0x7f,0xdb,0xfe,0xe6,1);jump(0xca,'toggle')
    load(MODE);emit(0xb7);jump(0xca,'static')
    jump(0xcd,'reset_before')
    # 432 reset stores: 8640T; CALL+RET:27T. Kernel begins at line 40,T-43.
    emit(*delay(8917-89-27-8640-10),0xc3,0,0x80)
    mark('static');jump(0xc3,'frame')
    mark('toggle');load(MODE);emit(0xee,1);save(MODE);jump(0xcd,'load_image')
    mark('release');emit(0xfb,0x76,0xf3,0x3e,0x7f,0xdb,0xfe,0xe6,1);jump(0xca,'release');jump(0xc3,'frame')
    mark('load_image');emit(0x3e,0,0xd3,0xff,0x3e,0xc2,0xd3,0xf4)
    load(MODE);emit(0xb7);jump(0xca,'load_ecm')
    emit(0x21,0,0xd0,0x11,0,0x40,1,0,0x18,0xed,0xb0,
         0x21,0,0xe8,0x11,0,0x60,1,0,0x18,0xed,0xb0)
    emit(0x3e,4);jump(0xc3,'loaded')
    mark('load_ecm');emit(0x21,0,0x20,0x11,0,0x40,1,0,0x18,0xed,0xb0,
                          0x21,0,0x38,0x11,0,0x60,1,0,8,0xed,0xb0,
                          0x21,0,0xc0,0x11,0,0x68,1,0,0x10,0xed,0xb0,0x3e,1)
    mark('loaded');emit(0xd3,0xfe,0x3e,0,0xd3,0xf4,0x3e,2,0xd3,0xff,0xc9)
    assert len(before)==432 and len(after)==336
    mark('reset_before')
    for event in before:emit(0x3e,event['value'],0x32,*word(event['address']))
    emit(0xc9)
    mark('reset_after')
    for event in after:emit(0x3e,event['value'],0x32,*word(event['address']))
    jump(0xc3,'frame');assert pc<8192,pc
    for at,n in fixes:struct.pack_into('<H',rom,at,labels[n])
    code[-2:]=word(labels['reset_after']);ram=bytearray(65536);ram[0x8000:0x8000+len(code)]=code
    assets=(ROOT/'ecm-bitmap.bin').read_bytes()+(ROOT/'ecm-attributes.bin').read_bytes()+payload[:12288]
    dock=bytearray(65536);dock[0x2000:0x4000]=assets[:8192];dock[0xc000:]=assets[8192:]
    home=bytes((255,2,0,3,3,3,3,0,0))+rom+ram[0x4000:0xc000]
    db=bytes((0,0,2,0,0,0,0,2,2))+dock[0x2000:0x4000]+dock[0xc000:]
    (ROOT/'timex-dynamic-ecm-morpho-7.dck').write_bytes(home+db)
    (ROOT/'initial-ram.bin').write_bytes(ram);(ROOT/'write-events.json').write_text(json.dumps(events));(ROOT/'labels.json').write_text(json.dumps(labels,indent=2))
    for i,event in enumerate(before):event['time']=113+i*20
    for i,event in enumerate(after):event['time']=51932+i*20
    (ROOT/'blanking-events.json').write_text(json.dumps(dict(before=before,after=after)))
    print('Built',len(home+db),'bytes; raster kernel',len(code),'bytes; SPACE compares ECM/Dynamic ECM')
if __name__=='__main__':build()
