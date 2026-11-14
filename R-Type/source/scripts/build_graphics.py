"""Reproducible R-Type arcade ROM -> legal TS2068 ECM graphics proof.

Reuses Sinistar's finite mask/pixel phase contract and the graphics skill's
scalar Sierra Lite stencil. No AI-generated or invented arcade colours.
"""
import hashlib
import json
import math
from pathlib import Path
import struct
import zipfile

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/graphics'
CAP = ROOT / 'build/arcade_capture'
PALETTE = np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205),
                    (0,0,0),(0,0,255),(255,0,0),(255,0,255),(0,255,0),(0,255,255),(255,255,0),(255,255,255)], dtype=float)
PAIRS = [(b*8+p,b*8+i) for b in range(2) for p in range(8) for i in range(p+1,8)]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def screen_offset(y):
    return ((y & 192)<<5) | ((y & 7)<<8) | ((y & 56)<<2)


def palette_ram(path):
    words = np.frombuffer(path.read_bytes(), dtype='<u2')
    channels = np.array([words[:256],words[512:768],words[1024:1280]]).T & 31
    return ((channels << 3) | (channels >> 2)).astype(np.uint8)


def decode_roms():
    with zipfile.ZipFile(ROOT/'arcade/rtype.zip') as z:
        read = lambda name: z.read(name)
        planes = []
        for n in range(4):
            first = read(f'rt_r-{n}0.' + ('1h','1k','3h','3k')[n])
            tail = read(f'rt_r-{n}1.' + ('1j','1l','3j','3l')[n])
            planes.append(first+tail+tail)  # MAME's documented mirrored tail
        def decode(planes, size):
            count = len(planes[0])//(size*size//8)
            result = np.zeros((count,size,size), dtype=np.uint8)
            for bit, data in enumerate(planes):
                raw = np.frombuffer(data,dtype=np.uint8)
                if size == 16:
                    raw = raw.reshape(count,2,16).transpose(0,2,1)
                else:
                    raw = raw.reshape(count,8,1)
                result |= np.unpackbits(raw, axis=2) << bit
            return result
        sprites = decode(planes,16)
        tiles = []
        for bank in ('a','b'):
            names = [n for n in z.namelist() if n.startswith('rt_b-'+bank)]
            planes = [read(next(n for n in names if n.startswith('rt_b-'+bank+str(i)+'.'))) for i in range(4)]
            tiles.append(decode(planes,8))
    return sprites, tiles


def fit_pairs(rgb, mode='cell', black=False):
    h,w,_ = rgb.shape
    if mode == 'standard':
        blocks = rgb.reshape(h//8,8,w//8,8,3).transpose(0,2,1,3,4).reshape(-1,64,3)
    elif mode == 'row':
        blocks = rgb.reshape(h,w,3)
    else:
        blocks = rgb.reshape(-1,8,3)
    candidates = [(p,q) for p,q in PAIRS if not black or p in (0,8)]
    best = np.full(len(blocks), np.inf)
    selected = np.zeros(len(blocks),dtype=int)
    for i,(p,q) in enumerate(candidates):
        delta = PALETTE[q]-PALETTE[p]
        coverage = np.clip(((blocks-PALETTE[p])*delta).sum(2)/(delta*delta).sum(),0,1)
        error = ((blocks-(PALETTE[p]+coverage[:,:,None]*delta))**2).sum((1,2))
        take = error < best
        selected[take] = i
        best[take] = error[take]
    pairs = np.array(candidates,dtype=np.uint8)[selected]
    if mode == 'standard':
        pairs = np.repeat(pairs.reshape(h//8,w//8,2),8,axis=0)
    elif mode == 'row':
        pairs = np.repeat(pairs[:,None,:],w//8,axis=1)
    else:
        pairs = pairs.reshape(h,w//8,2)
    return pairs


def quantize(image, mode='cell', dither='sierra', pairs=None, black=False):
    rgb = np.asarray(image.convert('RGB'),dtype=float)
    h,w,_ = rgb.shape
    pairs = fit_pairs(rgb,mode,black) if pairs is None else pairs
    p = np.repeat(PALETTE[pairs[:,:,0]],8,axis=1)
    q = np.repeat(PALETTE[pairs[:,:,1]],8,axis=1)
    v = q-p
    coverage = np.clip(((rgb-p)*v).sum(2)/(v*v).sum(2),0,1)
    bits = np.zeros((h,w),dtype=np.uint8)
    if dither == 'ordered':
        matrix = (np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])+.5)/16
        bits = (coverage > np.tile(matrix,(math.ceil(h/4),math.ceil(w/4)))[:h,:w]).astype(np.uint8)
    else:
        for y in range(h):
            direction = -1 if y&1 else 1
            for x in (range(w-1,-1,-1) if direction<0 else range(w)):
                value = int(coverage[y,x] >= .5)
                bits[y,x] = value
                err = coverage[y,x]-value
                for dx,dy,fraction in ((direction,0,.5),(-direction,1,.25),(0,1,.25)):
                    xx,yy=x+dx,y+dy
                    if 0<=xx<w and yy<h:
                        coverage[yy,xx] += err*fraction
    attrs = (((pairs[:,:,0] >= 8).astype(np.uint8)<<6) | ((pairs[:,:,0]&7)<<3) | (pairs[:,:,1]&7))
    preview = np.where(bits[:,:,None] != 0,q,p).astype(np.uint8)
    return bits,attrs,Image.fromarray(preview)


def pack(bits,attrs):
    h,w = bits.shape
    assert (h,w)==(192,256) and attrs.shape==(192,32)
    bitmap,colors=bytearray(6144),bytearray(6144)
    rows=np.packbits(bits,axis=1)
    for y in range(192):
        at=screen_offset(y)
        bitmap[at:at+32]=rows[y].tobytes()
        colors[at:at+32]=attrs[y].tobytes()
    return bytes(bitmap),bytes(colors)


def unpack(bitmap,colors):
    result=np.zeros((192,256,3),dtype=np.uint8)
    for y in range(192):
        at=screen_offset(y)
        for x in range(32):
            a=colors[at+x]
            for bit in range(8):
                color=(a&7) if bitmap[at+x]&(128>>bit) else ((a>>3)&7)
                result[y,x*8+bit]=PALETTE[color+(8 if a&64 else 0)]
    return Image.fromarray(result)


def scene_frame(path):
    # Uniform scaling preserves arcade pixel proportions; deliberate letterbox.
    im=Image.open(path).convert('RGB')
    scaled=im.resize((256,round(im.height*256/im.width)),Image.Resampling.NEAREST)
    frame=Image.new('RGB',(256,192));frame.paste(scaled,(0,(192-scaled.height)//2))
    return frame


def sprite_image(sprites,code,palette,width=2,height=1):
    pixels=np.zeros((16*height,16*width),dtype=np.uint8)
    for x in range(width):
        for y in range(height):
            pixels[y*16:(y+1)*16,x*16:(x+1)*16]=sprites[code+8*x+y]
    rgba=np.dstack((palette[pixels],np.where(pixels==0,0,255).astype(np.uint8)))
    return Image.fromarray(rgba),pixels


def sprite_phases(name,image):
    rgb=Image.new('RGBA',image.size,(0,0,0,255));rgb=Image.alpha_composite(rgb,image).convert('RGB')
    bits,attrs,_=quantize(rgb,mode='row',black=True)
    alpha=np.asarray(image)[:,:,3]!=0
    phases=[];animation=[]
    for phase in range(8):
        h,w=bits.shape;stride=math.ceil((w+phase)/8)
        b=np.zeros((h,stride*8),dtype=np.uint8);visible=np.zeros_like(b)
        b[:,phase:phase+w]=bits;visible[:,phase:phase+w]=alpha
        mask=np.packbits(1-visible,axis=1);pixels=np.packbits(b,axis=1)
        a=np.repeat(attrs[:,:1],stride,axis=1)
        blob=np.stack((mask,pixels,a),axis=2).tobytes()
        filename=f'{name}_phase{phase}.bin';(OUT/filename).write_bytes(blob)
        assert np.all(visible[:,:phase]==0) and np.all(visible[:,phase+w:]==0)
        assert np.array_equal(b[:,phase:phase+w],bits)
        # Every fully transparent cell preserves the background in both planes.
        phases.append(dict(phase=phase,stride=stride,bytes=len(blob),file=filename,sha256=sha(blob)))
        ar=np.repeat(a,8,axis=1)
        ink=(ar&7)+np.where(ar&64,8,0);paper=((ar>>3)&7)+np.where(ar&64,8,0)
        rgb=PALETTE[np.where(b!=0,ink,paper)].astype(np.uint8)
        preview=Image.new('RGB',(40,h));preview.paste(Image.fromarray(rgb),(0,0))
        animation.append(preview.resize((320,h*8),Image.Resampling.NEAREST))
    animation[0].save(OUT/f'{name}_rigid_phases.gif',save_all=True,append_images=animation[1:]+animation[-2:0:-1],duration=160,loop=0)
    return dict(layout='row-major interleaved preserve-mask, bitmap, attribute; 1-mask preserves background; skip attributes for FF masks',
                palette_policy='row-coherent, black-paper, quantized once; mixed coloured-background cells require recomposition',
                cartridge_phase_assumption='four-phase candidate requires two-pixel motion and fixed parity; otherwise use all eight',
                cartridge_phases=[0,2,4,6],cartridge_bytes=sum(x['bytes'] for x in phases if x['phase']%2==0),
                tspico_bytes=sum(x['bytes'] for x in phases),phases=phases)


def proof_cartridge(frames):
    # Resident DOCK4; seven data chunks. 256-byte transfers use a HOME bounce
    # buffer outside the selected source chunk. No stack access while mapped.
    banks=[0,1,2,3,5,6,7]
    flat=bytearray(b'\xff'*65536)
    descriptors=[]; logical=0
    for bitmap,attrs in frames:
        entries=bytearray()
        for plane,destination in ((bitmap,0x4000),(attrs,0x6000)):
            for offset in range(0,6144,256):
                if logical < 7*8192:
                    chunk=banks[logical//8192]; source=chunk*8192+logical%8192
                else:
                    chunk=4; source=0x8800+logical-7*8192
                flat[source:source+256]=plane[offset:offset+256]
                bounce=0x7b00 if chunk==2 else 0x5b00
                entries.extend(struct.pack('<HBHH',source,0x10|(1<<chunk),destination+offset,bounce))
                logical+=256
        descriptors.append(entries)
    code=bytearray(bytes.fromhex('02 02 08 80 ef 01 00 00'))
    labels={};fix=[]
    def emit(hextext):code.extend(bytes.fromhex(hextext))
    def mark(name):labels[name]=0x8000+len(code)
    def ref(op,name):code.append(op);fix.append((len(code),name));code.extend(b'\x00\x00')
    emit('f3 31 ff 7f af d3 fe 3e 02 d3 ff')
    mark('cycle')
    for n in range(len(frames)):
        emit('dd 21');fix.append((len(code),f'data{n}'));emit('00 00')
        ref(0xcd,'copy')
        mark(f'ready{n}')
        ref(0xcd,'delay')
    ref(0xc3,'cycle')
    mark('copy');emit('06 30')
    mark('packet');emit('c5 dd 6e 00 dd 66 01 dd 5e 05 dd 56 06 dd 7e 02 01 f4 00 ed 79')
    emit('01 00 01 ed b0 3e 10 0e f4 ed 79')
    emit('dd 6e 05 dd 66 06 dd 5e 03 dd 56 04 01 00 01 ed b0 11 07 00 dd 19 c1 05')
    ref(0xc2,'packet');emit('c9')
    mark('delay');emit('16 06')
    mark('delayblock');emit('01 00 00')
    mark('delayword');emit('0b 78 b1');ref(0xc2,'delayword')
    emit('15');ref(0xc2,'delayblock');emit('c9')
    for n,entry in enumerate(descriptors):
        mark(f'data{n}');code.extend(entry)
    assert len(code)<0x800 and logical<=7*8192+0x1800
    for pos,label in fix:code[pos:pos+2]=labels[label].to_bytes(2,'little')
    (OUT/'proof_descriptors.bin').write_bytes(b''.join(descriptors))
    (OUT/'proof_resident.bin').write_bytes(code)
    flat[0x8000:0x8000+len(code)]=code
    raw=bytes(flat);dck=bytes([0]+[2]*8)+raw
    (OUT/'RType_ECM_graphics_proof.bin').write_bytes(raw)
    (OUT/'RType_ECM_graphics_proof.dck').write_bytes(dck)
    (OUT/'proof_manifest.json').write_text(json.dumps(dict(labels=labels,code_bytes=len(code),
        frame_count=len(frames),raw_frame_bytes=logical,rom_bytes=65536,dck_bytes=len(dck),
        bin_sha256=sha(raw),dck_sha256=sha(dck),
        limitation='Static graphics comparison viewer, NOT the playable R-Type port. IRQ disabled; no gameplay/audio timing claim.'),indent=2))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    sprites,tiles=decode_roms()
    palette=palette_ram(CAP/'frame1320_palette_sprite.bin')
    np.savez_compressed(OUT/'decoded_indexed.npz',sprites=sprites,tiles0=tiles[0],tiles1=tiles[1],palette=palette)
    samples={}
    for name,code,color in [('ship',34,0),('enemy',54,5)]:
        im,indices=sprite_image(sprites,code,palette[color*16:(color+1)*16])
        im.save(OUT/f'{name}_arcade.png');im.resize((256,128),Image.Resampling.NEAREST).save(OUT/f'{name}_arcade_large.png')
        samples[name]=dict(code=code,palette=color,**sprite_phases(name,im))
    # Validate decoding/plane significance/palette against original game pixels.
    ship=np.asarray(Image.open(OUT/'ship_arcade.png'))
    actual=np.asarray(Image.open(CAP/'frame1320.png').convert('RGB'))[102:118,123:155]
    covered=ship[:,:,3]!=0
    match=float(np.mean(np.all(actual[covered]==ship[:,:,:3][covered],axis=1)))
    if match<.90:raise SystemExit(f'Arcade sprite/palette decode mismatch: {match:.3f}')
    source=scene_frame(CAP/'frame1560.png');source.save(OUT/'arcade_reference.png')
    variants=[('spectrum_8x8','standard','sierra'),('ecm_sierra','cell','sierra'),('ecm_ordered','cell','ordered'),('ecm_row_coherent','row','sierra')]
    report={};packed={};images={}
    for name,mode,dither in variants:
        bits,attrs,preview=quantize(source,mode,dither)
        bitmap,colors=pack(bits,attrs)
        assert np.array_equal(np.asarray(unpack(bitmap,colors)),np.asarray(preview))
        assert len(bitmap)==len(colors)==6144 and not any(a&128 for a in colors)
        (OUT/f'{name}.pix').write_bytes(bitmap);(OUT/f'{name}.atr').write_bytes(colors)
        preview.save(OUT/f'{name}.png');packed[name]=(bitmap,colors);images[name]=preview
        mse=float(np.mean((np.asarray(source,dtype=float)-np.asarray(preview,dtype=float))**2))
        report[name]=dict(mse=mse,colours=len(preview.getcolors(49152)),attribute_pairs=len(set(colors)),
                          bitmap_sha256=sha(bitmap),attributes_sha256=sha(colors))
    rgb=np.asarray(source,dtype=float)
    luminance=(rgb*np.array([.2126,.7152,.0722])).sum(2,keepdims=True)
    boosted=Image.fromarray(np.clip(luminance+2.5*(rgb-luminance),0,255).astype(np.uint8))
    boosted.save(OUT/'chroma_emphasis_source.png')
    bits,attrs,preview=quantize(boosted)
    bitmap,colors=pack(bits,attrs)
    (OUT/'ecm_colour_emphasis.pix').write_bytes(bitmap);(OUT/'ecm_colour_emphasis.atr').write_bytes(colors)
    preview.save(OUT/'ecm_colour_emphasis.png');packed['ecm_colour_emphasis']=(bitmap,colors)
    report['ecm_colour_emphasis']=dict(source_adjustment='2.5x chroma around Rec.709 luma; artistic alternative, not exact arcade RGB',
        colours=len(preview.getcolors(49152)),attribute_pairs=len(set(colors)),bitmap_sha256=sha(bitmap),attributes_sha256=sha(colors))
    sheet=Image.new('RGB',(792,224),(20,24,30));draw=ImageDraw.Draw(sheet)
    for i,(title,image) in enumerate([('ARCADE REFERENCE',source),('ECM / PRESERVE PALETTE',images['ecm_sierra']),('ECM / COLOUR EMPHASIS',preview)]):
        draw.text((8+i*264,5),title,fill='white');sheet.paste(image,(8+i*264,24))
    sheet.resize((1584,448),Image.Resampling.NEAREST).save(OUT/'colour_comparison.png')
    title=scene_frame(CAP/'frame0540.png');title.save(OUT/'arcade_title_reference.png')
    title_images=[]
    for mode,name in [('standard','title_spectrum_8x8'),('cell','title_ecm_sierra')]:
        bits,attrs,preview=quantize(title,mode)
        bitmap,colors=pack(bits,attrs)
        (OUT/f'{name}.pix').write_bytes(bitmap);(OUT/f'{name}.atr').write_bytes(colors)
        preview.save(OUT/f'{name}.png');packed[name]=(bitmap,colors);title_images.append(preview)
    sheet=Image.new('RGB',(792,224),(20,24,30));draw=ImageDraw.Draw(sheet)
    for i,(label,image) in enumerate(zip(('ARCADE TITLE','8x8 COLOUR LIMIT','ECM / SIERRA LITE'),[title]+title_images)):
        draw.text((8+i*264,5),label,fill='white');sheet.paste(image,(8+i*264,24))
    sheet.resize((1584,448),Image.Resampling.NEAREST).save(OUT/'title_comparison.png')
    for name,keys in [('comparison',['arcade','spectrum_8x8','ecm_sierra']),('dither_comparison',['ecm_sierra','ecm_ordered','ecm_row_coherent'])]:
        sheet=Image.new('RGB',(792,224),(20,24,30));draw=ImageDraw.Draw(sheet)
        for i,key in enumerate(keys):
            title={'arcade':'ARCADE REFERENCE','spectrum_8x8':'8x8 COLOUR LIMIT','ecm_sierra':'ECM / SIERRA LITE','ecm_ordered':'ECM / ORDERED','ecm_row_coherent':'ECM / ROW-COHERENT'}[key]
            draw.text((8+i*264,5),title,fill='white');sheet.paste(source if key=='arcade' else images[key],(8+i*264,24))
        sheet.resize((1584,448),Image.Resampling.NEAREST).save(OUT/f'{name}.png')
    proof_cartridge([packed[n] for n in ('ecm_colour_emphasis','ecm_sierra','spectrum_8x8','ecm_ordered','title_ecm_sierra')])
    report.update(sprite_samples=samples,arcade_sprite_pixel_match=match,
                  source_capture='scene frame1560; ship/palette frame1320; title frame0540; original palette RAM',
                  dithering='scalar coverage Sierra Lite, serpentine 1/2 + 1/4 + 1/4; ordered 4x4 comparison',
                  reuse='Sinistar preserve-mask/bitmap/attribute records, finite phases; TS2068 graphics skill scalar diffusion and row palettes')
    (OUT/'graphics_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Arcade sprite pixel match:',match)
    print('Converted comparisons, finite masked phases and 64 KB graphics proof')


if __name__=='__main__':main()
