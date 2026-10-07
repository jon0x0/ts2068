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
        width=lambda c: letters.get({'O':'S0','S':'S5',' ':'SSPC','-':'SDSH','=':'SEQU',')':'SBRKR'}.get(c,'S'+c),(3,0,[]))[0]+1
        x=(256-sum(width(c) for c in line))//2
        for char in line:
            name={'O':'S0','S':'S5',' ':'SSPC','-':'SDSH','=':'SEQU',')':'SBRKR'}.get(char,'S'+char)
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
    # Column order makes identical vertical bytes share runs; transpose at title time.
    packed_raw=bytes(raw[((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x] for x in range(32) for y in range(192))
    encoded=bytearray();i=0
    while i<len(packed_raw):
        n=1
        while i+n<len(packed_raw) and packed_raw[i+n]==packed_raw[i] and n<127:n+=1
        if n>=3:
            encoded.extend((128|n,packed_raw[i]));i+=n
        else:
            start=i;i+=n
            while i<len(packed_raw) and i-start<127:
                if i+2<len(packed_raw) and packed_raw[i]==packed_raw[i+1]==packed_raw[i+2]:break
                i+=1
            encoded.append(i-start);encoded.extend(packed_raw[start:i])
    encoded.append(0)
    out=root/'build'
    # Six scanline glyphs from the arcade MESSAGE.SRC for the native score table.
    glyphs=bytearray()
    for char in ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-=)':
        name={'O':'S0','S':'S5',' ':'SSPC','-':'SDSH','=':'SEQU',')':'SBRKR'}.get(char,'S'+char)
        w,h,raw_glyph=letters[name]
        for y in range(6):
            cy=5-y
            glyphs.append(sum(128>>x for x in range(w) if cy<h*2 and raw_glyph[x*h+cy//2]&(16 if cy%2==0 else 1)))
    alphabet=' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-=)'
    # Pack pairs of six-row font bytes through a nibble dictionary.
    rows=list(dict.fromkeys(glyphs));assert len(rows)<=16
    packed=bytes(rows.index(glyphs[i])|(rows.index(glyphs[i+1])<<4) for i in range(0,len(glyphs),2))
    glyphs=bytearray(rows+[0]*(16-len(rows)))+packed
    offsets={}
    for label,text_value in [('heading','SINIMMORTALS'),('prompt','B LAUNCHES SINIBOMBS'),('name_prompt','ENTER INITIALS'),('name_keys','O P CHANGE ENTER OR FIRE'),('today','SURVIVORS TODAY'),('hero','SINI-STAR')]:
        offsets[label]=len(glyphs)
        glyphs.extend(alphabet.index(c) for c in text_value);glyphs.append(255)
    (out/'frontend-font-offsets.json').write_text(__import__('json').dumps(offsets))
    (out/'frontend-font.bin').write_bytes(glyphs)
    # ATTMSGS original line grouping and red emphasis; TS2068 coordinates.
    pages=[[(28,28,6,'BLAST CRYSTALS OFF PLANETOIDS'),(20,37,6,'PICK UP CRYSTALS TO FILL BOMBBAY WITH SINIBOMBS')],
           [(20,28,6,'FIRING DOES NOT AFFECT THE MIGHTY'),(160,28,2,'SINISTAR'),(32,37,6,'ONLY SINIBOMBS CAN AFFECT THIS NEMESIS')],
           [(24,28,6,'ONCE THE'),(62,28,2,'SINISTAR'),(100,28,6,'IS BUILT YOU MUST DESTROY IT'),(124,37,6,'OR'),(88,46,6,'YOU HAD BETTER'),(152,46,2,'RUN')]]
    help_encoded=[]
    for lines in pages:
        data=bytearray()
        for x,y,ink,line in lines:data.extend([x,y,ink,*[alphabet.index(c) for c in line],255])
        data.append(255);help_encoded.append(data)
    (out/'frontend-help.bin').write_bytes(help_encoded[0])
    (out/'frontend-instructions.asm').write_text(''.join(label+':\n DB '+','.join(map(str,data))+'\n' for label,data in zip(['front_firing_help','front_sinistar_help'],help_encoded[1:])))
    initials='SAM KVD N-F KJF KAG FRG YAK JJK KFL PJM DOC JLM E-Z =M= TIM JRN TOM PFZ RTP BFD MBS MRS EJS STU WIT MOM FAC GOD KAY HEC'.split()
    seeds=bytearray()
    for i,name in enumerate(initials):
        score=30000+(90-3*i)*100+(45+35*i)%100
        seeds.extend((score//5).to_bytes(2,'little'));seeds.extend(alphabet.index(c) for c in name)
    (out/'frontend-seeds.bin').write_bytes(seeds)
    (out/'title-bitmap.bin').write_bytes(raw)
    preview=Image.new('RGB',(256,192));preview.putdata([(255,0,0) if p else (0,0,0) for row in pixels for p in row]);preview.resize((768,576),Image.Resampling.NEAREST).save(out/'title-preview.png')
    address=0x6000+cursor[3]
    (out/'title-origin.asm').write_text(f'title_source EQU {address}\n')
    (out/'title-rle.bin').write_bytes(encoded)
    return address,len(encoded)
