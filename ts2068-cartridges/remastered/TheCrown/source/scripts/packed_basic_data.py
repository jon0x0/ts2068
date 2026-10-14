"""Encode mixed Sinclair DATA with an indexed, ROM-readable stream."""
import struct


def pack_data(values, line_indexes):
    table_bytes=2+4*len(line_indexes)
    data=bytearray(); offsets=[]
    for _,value in values:
        offsets.append(table_bytes+len(data))
        v=value.constant
        if isinstance(v,str):
            raw=v.encode('ascii'); data+=bytes((3,len(raw)))+raw
        elif isinstance(v,int) and -128<=v<=127: data+=bytes((0,v&255))
        elif isinstance(v,int) and -32768<=v<=32767: data+=bytes((1,))+struct.pack('<h',v)
        else:
            raw=format(float(v),'.15f').rstrip('0').rstrip('.').encode('ascii')
            data+=bytes((2,len(raw)))+raw
    end=table_bytes+len(data); data.append(255)
    table=bytearray(struct.pack('<H',len(line_indexes)))
    for line,index in line_indexes: table+=struct.pack('<HH',line,offsets[index] if index<len(offsets) else end)
    return bytes(table+data),offsets,end


def pointer(offset):
    return [f'POKE 63456,MOD({offset},256)',f'POKE 63457,DIV({offset},256)']


def reader_source(count, first, end):
    return [
        'PROC QZREAD(QZARG):','QZK = 0','QZT = USR(62464)',
        'IF QZT = 255 THEN','PRINT "OUT OF DATA"','END','ENDIF',
        'IF QZT = 0 THEN','QZN = USR(62464)','IF QZN >= 128 THEN','QZN = QZN - 256','ENDIF','ENDIF',
        'IF QZT = 1 THEN','QZN = USR(62464)+256*USR(62464)',
        'IF QZN >= 32768 THEN','QZN = QZN-65536','ENDIF','ENDIF',
        'IF QZT >= 2 THEN','QZLEN = USR(62464)','QZS$ = ""',
        'FOR QZDI = 1 TO QZLEN','QZS$ = QZS$+CHR$(USR(62464))','NEXT QZDI',
        'IF QZT = 2 THEN','QZN = VAL(QZS$)','ELSE','QZK = 1','ENDIF','ENDIF','ENDP',
        'PROC QZRESTORE(QZRL):','QZLO = 0','QZHI = QZCOUNT-1','QZO = QZBASE+QZEND',
        'QZRLOOP:','IF QZLO > QZHI THEN GOTO QZRFOUND',
        'QZMID = DIV(QZLO+QZHI,2)','QZIX = QZBASE+2+4*QZMID',
        *pointer('QZIX'),'QZLINE = USR(62464)+256*USR(62464)','QZOFF = USR(62464)+256*USR(62464)',
        'IF QZLINE >= QZRL THEN','QZO = QZBASE+QZOFF','QZHI = QZMID-1','ELSE','QZLO = QZMID+1','ENDIF',
        'GOTO QZRLOOP','QZRFOUND:',*pointer('QZO'),'ENDP',
    ]
