"""Inspect/check TAP framing and recover level DATA and original UDG planes."""
from pathlib import Path
import argparse
import json
import struct
import hashlib

TOKENS={0xE4:'DATA',0xB0:'VAL',0xEA:'REM'}


def listing(payload):
    rows=[]; i=0; prev=-1
    while i+4<=len(payload):
        n=int.from_bytes(payload[i:i+2],'big'); length=int.from_bytes(payload[i+2:i+4],'little')
        if n>9999 or n<=prev or length<1 or i+4+length>len(payload): break
        body=payload[i+4:i+4+length]
        if body[-1]!=13: break
        result=[]; j=0; quote=False
        while j<len(body)-1:
            b=body[j]
            if b==14 and not quote: j+=6; continue
            if b==34: quote=not quote
            if b in TOKENS and not quote: result.append(TOKENS[b]+' ')
            elif 32<=b<127: result.append(chr(b))
            elif b in (127,): result.append(' ')
            else: result.append(f'\\x{b:02x}')
            j+=1
        rows.append((n,''.join(result).strip())); i+=4+length; prev=n
    return rows,i


def extract(source,out):
    raw=source.read_bytes(); i=0; blocks=[]; pending=None; charset_index=0
    out.mkdir(parents=True,exist_ok=True)
    while i<len(raw):
        if i+2>len(raw): raise ValueError('Truncated TAP length')
        length=struct.unpack_from('<H',raw,i)[0]; i+=2
        block=raw[i:i+length]; i+=length
        if len(block)!=length: raise ValueError('Truncated TAP block')
        checksum=0
        for b in block: checksum^=b
        if checksum: raise ValueError(f'Checksum failure in block {len(blocks)}')
        if length==19 and block[0]==0:
            pending={'name':block[2:12].decode('ascii').rstrip(),'type':block[1],
                     'length':int.from_bytes(block[12:14],'little'),'address':int.from_bytes(block[14:16],'little')}
        elif block[0]==255 and pending:
            data=block[1:-1]
            if len(data)!=pending['length']: raise ValueError('Header/data length mismatch')
            record=dict(pending,sha256=hashlib.sha256(data).hexdigest())
            if pending['name'].startswith('LEVEL'):
                rows,used=listing(data)
                if not rows or any(not text.startswith(('DATA','REM')) for _,text in rows):
                    raise ValueError('Expected a level BASIC DATA overlay')
                path=out/(pending['name']+'.bas')
                path.write_text(''.join(f'{n} {text}\n' for n,text in rows))
                record.update(lines=len(rows),decoded_bytes=used,listing=str(path.resolve()))
            if len(data)==168 and (pending['name']=='CHAR SET' or pending['type']==3):
                charset_index+=1; path=out/f'charset-{charset_index}.bin'; path.write_bytes(data)
                record['charset']=str(path.resolve())
            blocks.append(record); pending=None
    (out/'tap-inventory.json').write_text(json.dumps({'source':str(source.resolve()),'files':blocks},indent=2)+'\n')
    return blocks


if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('source',type=Path); ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    for file in extract(args.source,args.output): print(file)
