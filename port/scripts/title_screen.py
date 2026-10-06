"""Decode the pinned arcade marquee and font; emit a native boot-only screen."""
import re
from pathlib import Path
from PIL import Image

def build(root, banks, cursor):
    source=(root/'reference/original/MICA/MARQUEE.SRC').read_text()
    data=[int(v,16) for v in re.findall(r'\$([0-9A-F]{2})',source.split('MARKEY\tFCB',1)[1].split('ENDIF',1)[0])]
    pixels=[[0]*256 for _ in range(192)]
    x=42;y=55
    for value in data:
        if not value: break
        length=value&63
        # The 6809 draws column runs on even boundaries, padding odd runs
        # with one pixel of the opposite color (MARQUEE.SRC, label 3$).
        for n in range(length):
            if value&64:pixels[y+n][x]=1
        if length&1:
            if not value&64:pixels[y+length][x]=1
            length+=1
        y+=length
        if value&128:x+=1;y=55
    assert x==213, x
    font=(root/'reference/original/SAM/MESSAGE.SRC').read_text()
    letters={}
    for match in re.finditer(r'LETTER\s+(S\w+),(\d+),(\d+)(.*?)(?=\n\s*LETTER|\Z)',font,re.S):
        name,h,w,body=match.groups();w=int(w);h=int(h)
        rows=re.findall(r'^\s*PACK\s+([^\r\n]+)',body,re.M)
        raw=[int(v,16) for row in rows for v in re.findall(r'\$([01]{2})',row)][:w*h]
        if len(raw)==w*h: letters[name]=(w,h,raw)
    def text(line,y):
        width=lambda c: letters.get({'O':'S0','S':'S5',' ':'SSPC'}.get(c,'S'+c),(3,0,[]))[0]+1
        x=(256-sum(width(c) for c in line))//2
        for char in line:
            name={'O':'S0','S':'S5',' ':'SSPC'}.get(char,'S'+char)
            if name in letters:
                w,h,raw=letters[name]
                for cx in range(w):
                    for cy in range(h*2):
                        if raw[cx*h+cy//2] & (16 if cy%2==0 else 1):pixels[y+(h*2-1-cy)][x+cx]=1
            x+=width(char)
    text('1982 WILLIAMS ELECTRONICS INC',135)
    text('PRESS FIRE TO START',156)
    raw=bytearray(6144)
    for y,row in enumerate(pixels):
        for x,p in enumerate(row):
            if p:raw[((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|(x>>3)]|=128>>(x&7)
    encoded=bytearray();i=0
    while i<len(raw):
        n=1
        while i+n<len(raw) and raw[i+n]==raw[i] and n<127:n+=1
        if n>=3:
            encoded.extend((128|n,raw[i]));i+=n
        else:
            start=i;i+=n
            while i<len(raw) and i-start<127:
                if i+2<len(raw) and raw[i]==raw[i+1]==raw[i+2]:break
                i+=1
            encoded.append(i-start);encoded.extend(raw[start:i])
    encoded.append(0)
    out=root/'build'
    (out/'title-bitmap.bin').write_bytes(raw)
    preview=Image.new('RGB',(256,192));preview.putdata([(255,0,0) if p else (0,0,0) for row in pixels for p in row]);preview.resize((768,576),Image.Resampling.NEAREST).save(out/'title-preview.png')
    address=0x6000+cursor[3]
    (out/'title-origin.asm').write_text(f'title_source EQU {address}\n')
    (out/'title-rle.bin').write_bytes(encoded)
    return address,len(encoded)
