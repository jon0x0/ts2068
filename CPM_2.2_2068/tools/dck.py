"""Strict Warajevo DCK reader, shared by artifact inspection and tests."""
from pathlib import Path
import argparse,json
def parse(data):
    pos=0;blocks=[];seen=set()
    while pos<len(data):
        if pos+9>len(data): raise ValueError('truncated header')
        bank=data[pos]; kinds=list(data[pos+1:pos+9]);pos+=9
        if bank not in (0,254,255) or bank in seen: raise ValueError('invalid/duplicate bank')
        seen.add(bank); pages=[]
        for kind in kinds:
            if kind not in (0,1,2,3):raise ValueError('invalid page type')
            size=8192 if kind in (2,3) else 0
            if pos+size>len(data):raise ValueError('truncated payload')
            pages.append(data[pos:pos+size]);pos+=size
        blocks.append((bank,kinds,pages))
    if not blocks: raise ValueError('empty cartridge')
    return blocks
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('file',type=Path);a=p.parse_args()
    print(json.dumps([{'bank':b,'types':k,'payload_bytes':sum(map(len,p))} for b,k,p in parse(a.file.read_bytes())],indent=2))
