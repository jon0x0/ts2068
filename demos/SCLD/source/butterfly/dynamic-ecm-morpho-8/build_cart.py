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
    assert (magic,version,count,palette,width,height,rows,split,bmp_len,attr_len,sched_len)==(b'TDEC',3,8,1,256,192,192,0,6144,6144,4608),'Unsupported TDEC profile'
    payload=container[32:];assert len(payload)==bmp_len+attr_len+sched_len and zlib.crc32(payload)==crc,'TDEC size/CRC failure'
    records=payload[12288:];schedule=[dict(columns=list(records[y*24:y*24+8]),old=list(records[y*24+8:y*24+16]),new=list(records[y*24+16:y*24+24]),splits=[2,6]*4) for y in range(192)]
    assert schedule==json.loads((ROOT/'schedule.json').read_text())
    code=bytearray();events=[];before=[];after=[]
    column_start=schedule[0]['columns'][0];kernel_start=8889+column_start*4
    for y,s in enumerate(schedule):
        rowevents=[];cols=s['columns'];assert cols==[column_start+c for c in (0,3,7,10,14,17,21,24)]
        values=list(dict.fromkeys(s['new']));assert len(values)<=2
        if len(values)==1:values*=2
        for i,(c,value) in enumerate(zip(cols[:4],s['old'][:4])):
            addr=0x6000+row(y)+c;code+=bytes((0x3e,value,0x32))+word(addr)
            rowevents.append(dict(address=addr,value=value,time=-64+column_start*4+i*20))
        # Four resets per row are prestaged outside active display. Pack the
        # split asymmetrically to fit the two unequal blanking intervals.
        for i in range(4,8):
            target=before if i in (4,5) or (i==6 and y<48) else after
            target.append(dict(address=0x6000+row(y)+cols[i],value=s['old'][i]))
        addr=0x6000+row(y)+cols[0]
        code+=bytes((6,values[0],14,values[1],0x21))+word(addr)
        for i,(c,value) in enumerate(zip(cols,s['new'])):
            if i:code+=bytes((0x2e,(row(y)+c)&255))
            addr=0x6000+row(y)+c;code+=bytes((0x70 if value==values[0] else 0x71,))
            rowevents.append(dict(address=addr,value=value,time=33+column_start*4+i*14))
        # OR 1 in the dynamic frame dispatcher clears Z. All kernel operations
        # preserve flags, so this conditional RET is always not-taken (5T).
        code+=bytes((0xc8,))
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
    # 432 reset stores: 8640T; CALL+RET:27T. The profile selects the raster phase.
    emit(*delay(kernel_start-89-27-8640-10),0xc3,0,0x80)
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
    (ROOT/'timex-dynamic-ecm-morpho-8.dck').write_bytes(home+db)
    (ROOT/'initial-ram.bin').write_bytes(ram);(ROOT/'write-events.json').write_text(json.dumps(events));(ROOT/'labels.json').write_text(json.dumps(labels,indent=2))
    for i,event in enumerate(before):event['time']=113+i*20
    for i,event in enumerate(after):event['time']=kernel_start+192*224+7+i*20
    (ROOT/'blanking-events.json').write_text(json.dumps(dict(before=before,after=after)))
    print('Built',len(home+db),'bytes; raster kernel',len(code),'bytes; SPACE compares ECM/Dynamic ECM')
if __name__=='__main__':build()
