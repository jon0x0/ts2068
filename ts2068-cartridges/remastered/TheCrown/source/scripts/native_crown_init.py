"""Native Crown setup: immutable DATA tables prepared on PC, random state on Z80."""
import struct

def adapt(source):
    a=source.index('QL3500:\n'); b=source.index('BORDER 0\nQV23 = 1',a)
    source=source[:a]+'QL3500:\nQV55$ = "          "\nQV53$ = "               "\nQZINTRO = USR(63500)\n'+source[b:]
    a=source.index('QL3406:\n');b=source.index('QL3500:\n',a)
    source=source[:a]+'QL3406:\nQZINTRO = USR(63503)\nQR35:\nGOTO QZRETURN\n'+source[b:]
    a=source.index('QL3190:\n'); b=source.index('QL3200:\n',a)
    source=source[:a]+'QL3190:\nQZINTRO = USR(63506)\nGOTO QZRETURN\n'+source[b:]
    source=source.replace('CALL QZLEVEL(1)','QV23 = 1\nCALL QZLEVEL(1)',1)
    a=source.index('FOR QZCG = 0 TO 167\n');b=source.index('NEXT QZCG\n',a)+len('NEXT QZCG\n')
    source=source[:a]+'QZINTRO = USR(63509)\n'+source[b:]
    return source

def tables(data, symbols):
    def index(name,kind): return next(s['index'] for s in symbols if s['name']==name and s['kind']==kind)
    def records(base,line,count):
        n=struct.unpack_from('<H',data,base)[0]
        rows=[struct.unpack_from('<HH',data,base+2+4*i) for i in range(n)]
        pos=base+next(off for ln,off in rows if ln>=line)
        out=[]
        for _ in range(count):
            tag=data[pos];pos+=1
            if tag==0: v=struct.unpack_from('<b',data,pos)[0];pos+=1
            elif tag==1: v=struct.unpack_from('<h',data,pos)[0];pos+=2
            else:
                size=data[pos];pos+=1;v=data[pos:pos+size];pos+=size
                if tag==2: v=float(v)
            out.append(v)
        return out
    def numeric(name,values):
        blob=struct.pack('<'+'h'*len(values),*values)
        return bytes([index(name,2),0])+struct.pack('<H',len(blob))+blob
    def strings(name,values,width):
        blob=b''.join(bytes([width])+v[:width].ljust(width,b' ') for v in values)
        return bytes([index(name,3),1])+struct.pack('<H',len(blob))+blob
    result={}
    for level,base in enumerate((0,6867,13938),1):
        values=records(base,9200,120)
        coords=values[:80]; monsters=values[80:]
        result[f'init-level-{level}']=(numeric('QA41',coords[::2])+numeric('QA42',coords[1::2])+strings('QA24',monsters[::4],15)+numeric('QA27',monsters[1::4])+numeric('QA21',monsters[2::4])+numeric('QA17',monsters[3::4])+bytes([255]))
    for level,offset in enumerate((6699,13770,20509),1): result[f'init-glyph-{level}']=data[offset:offset+168]
    result['init-items']=strings('QA43',records(0,9310,25),12)+numeric('QA39',[13,11,11,11,13,12,8,13,13])+bytes([255])
    assert all(len(blob)<=512 for blob in result.values()), 'Native tables exceed DATA cache'
    return result

def equs(symbols):
    needed=[('QA40',2),('QA12',2),('QA11',2),('QA16',2),('QA41',2),('QA42',2),('QA27',2),('QA21',2),('QA17',2),('QA38',2),('QA39',2),('QA43',3),('QA24',3),('QV23',0)]
    return ''.join(f'NATIVE_{name} EQU {next(s["index"] for s in symbols if s["name"]==name and s["kind"]==kind)}\n' for name,kind in needed)
