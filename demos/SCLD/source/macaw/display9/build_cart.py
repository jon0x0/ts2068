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
    container=(ROOT/'image.tdec').read_bytes()
    magic,version,bmp_len,attr_len,sched_len,crc=struct.unpack('<4sB3xIIII',container[:24])
    payload=container[24:]
    assert (magic,version,bmp_len,attr_len)==(b'TDEC',4,6144,6144)
    assert len(payload)==12288+sched_len and zlib.crc32(payload)==crc
    meta=json.loads(payload[12288:]);schedule=meta['schedule']
    assert meta['profile']=='adaptive-9-independent'
    assert schedule==json.loads((ROOT/'schedule.json').read_text())
    packing=json.loads((ROOT/'restore-plan.json').read_text())
    code=bytearray();events=[];kernel_start=8921
    columns=[0,4,8,12,15,19,23,27,31]
    for y,s in enumerate(schedule):
        rowevents=[];by_slot={slot:i for i,slot in enumerate(s['slots'])}
        inline=list(range(min(2,len(s['columns']))))
        addr=0x6000+row(y)+(s['columns'][0] if inline else 0)
        code+=bytes((0x21,))+word(addr)
        for k in range(2):
            if k<len(inline):
                i=inline[k];addr=0x6000+row(y)+s['columns'][i]
                if k:code+=bytes((0x2e,addr&255))
                code+=bytes((0x36,s['old'][i]))
                rowevents.append(dict(address=addr,value=s['old'][i],time=-29+k*17))
            else:code+=pad(10 if k==0 else 17)
        registers={2:0,3:1,4:2,7:3}
        for slot,reg in registers.items():
            value=s['new'][by_slot[slot]] if slot in by_slot else 0
            code+=bytes(([6,14,22,30][reg],value))
        t=33
        for slot,c in enumerate(columns):
            duration=14 if slot in registers else 17
            if slot in by_slot:
                i=by_slot[slot];addr=0x6000+row(y)+c
                code+=bytes((0x2e,addr&255))
                code+=bytes((0x70+registers[slot],)) if slot in registers else bytes((0x36,s['new'][i]))
                rowevents.append(dict(address=addr,value=s['new'][i],time=t))
            elif duration==14:code+=bytes((0x3e,0,0x3e,0))
            else:
                # 17T padding that preserves BC/DE and flags.
                code+=bytes((0x3e,0,0xc3))+word(0x8000+len(code)+5)
            t+=duration
        code+=bytes((0,0)) # 8T tail.
        code+=bytes((0xc3,))+word(0x8000+len(code)+3)
        events.append(rowevents)
    assert len(code)<0x3800,len(code)
    def restores(groups):
        block=bytearray();writes=[];t=0
        for y,slots in groups:
            s=schedule[y];lookup={slot:i for i,slot in enumerate(s['slots'])}
            for k,slot in enumerate(slots):
                i=lookup[slot];addr=0x6000+row(y)+s['columns'][i]
                if k==0:block+=bytes((0x21,))+word(addr);t+=10
                else:block+=bytes((0x2e,addr&255));t+=7
                writes.append(dict(address=addr,value=s['old'][i],time=t))
                block+=bytes((0x36,s['old'][i]));t+=10
        return block,writes,t
    before_code,before,bt=restores(packing['before'])
    after_code,after,at=restores(packing['after'])
    assert bt==packing['beforeT'] and at==packing['afterT']
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
    # Image-specific fast grouped restores; CALL+RET contributes 27T.
    emit(*delay(kernel_start-89-27-packing['beforeT']-10),0xc3,0,0x80)
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
    mark('reset_before')
    emit(*before_code,0xc9)
    mark('reset_after')
    emit(*after_code)
    jump(0xc3,'frame');assert pc<8192,pc
    for at,n in fixes:struct.pack_into('<H',rom,at,labels[n])
    code[-2:]=word(labels['reset_after']);ram=bytearray(65536);ram[0x8000:0x8000+len(code)]=code
    assets=(ROOT/'ecm-bitmap.bin').read_bytes()+(ROOT/'ecm-attributes.bin').read_bytes()+payload[:12288]
    dock=bytearray(65536);dock[0x2000:0x4000]=assets[:8192];dock[0xc000:]=assets[8192:]
    home=bytes((255,2,0,3,3,3,3,0,0))+rom+ram[0x4000:0xc000]
    db=bytes((0,0,2,0,0,0,0,2,2))+dock[0x2000:0x4000]+dock[0xc000:]
    (ROOT/'timex-dynamic-ecm-macaw-9.dck').write_bytes(home+db)
    (ROOT/'initial-ram.bin').write_bytes(ram);(ROOT/'write-events.json').write_text(json.dumps(events));(ROOT/'labels.json').write_text(json.dumps(labels,indent=2))
    for event in before:event['time']+=106
    for event in after:event['time']+=kernel_start+192*224
    (ROOT/'blanking-events.json').write_text(json.dumps(dict(before=before,after=after)))
    print('Built',len(home+db),'bytes; raster kernel',len(code),'bytes; SPACE compares ECM/Dynamic ECM')
if __name__=='__main__':build()
