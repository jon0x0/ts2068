"""Streaming 160KB/320KB CP/M TAP disk compatibility; no whole-image RAM buffer."""
import os
try:
    import hashlib
except ImportError:
    import uhashlib as hashlib

MAGIC=b'CPMRAM1\0\0\x0a\x28\x20'

def xor(data):
    value=0
    for byte in data:value^=byte
    return value

def header(name,length):
    return bytes((3,))+name.encode().ljust(10,b' ')+bytes((length&255,length>>8,0,160,0,128))

def code_header(f,name,length):
    data=bytes((0,))+header(name,length)
    f.write(bytes((19,0))+data+bytes((xor(data),)))

class TapVolume:
    sectors=2560
    def __init__(self,path):
        self.path=path;self.pages=[];pages=40
        self.sectors=2560
        with open(path,'rb') as f:
            page=-1
            while page<pages:
                n=f.read(2)
                if n!=b'\x13\0':raise OSError('invalid TAP header length')
                h=f.read(19)
                name='CPMRAM' if page<0 else 'CPM%02d'%page
                length=128 if page<0 else 8192
                if len(h)!=19 or xor(h) or h[0]!=0 or h[1:]!=header(name,length)+bytes((xor(header(name,length)),)):
                    raise OSError('invalid TAP CODE header/name')
                n=f.read(2)
                if len(n)!=2 or n[0]+256*n[1]!=length+2 or f.read(1)!=b'\xff':
                    raise OSError('invalid TAP data length')
                offset=f.tell();crc=255
                for i in range(0,length,128):
                    data=f.read(128)
                    if len(data)!=128:raise OSError('short TAP data')
                    crc^=xor(data)
                    if page<0:
                        if data[:12] not in (MAGIC,MAGIC[:9]+bytes((5,20,16))):raise OSError('incompatible TAP disk geometry')
                        pages=data[10];self.sectors=pages*64
                stored=f.read(1)
                if len(stored)!=1 or stored[0]!=crc:raise OSError('TAP checksum mismatch')
                if page>=0:self.pages.append(offset)
                page+=1
            if f.read(1):raise OSError('extra TAP blocks; expected one CP/M disk')
        with open(path,'r+b'):pass

    def read(self,lba):
        if not 0<=lba<self.sectors:raise OSError('sector outside TAP disk')
        with open(self.path,'rb') as f:
            f.seek(self.pages[lba//64]+(lba%64)*128)
            data=f.read(128)
        if len(data)!=128:raise OSError('short TAP sector')
        return data

    def write(self,lba,data):
        if not 0<=lba<self.sectors or len(data)!=128:raise OSError('invalid TAP write')
        base=self.pages[lba//64];position=base+(lba%64)*128
        with open(self.path,'r+b') as f:
            f.seek(position);old=f.read(128)
            f.seek(base+8192);crc=f.read(1)
            if len(old)!=128 or len(crc)!=1:raise OSError('short TAP sector')
            f.seek(position)
            if f.write(data)!=128:raise OSError('short TAP write')
            f.seek(base+8192);f.write(bytes((crc[0]^xor(old)^xor(data),)));f.flush()

def save_tap(volume,path):
    """Export any compatible 320KB volume; publish only a complete new file."""
    if volume.sectors not in (1280,2560):raise OSError('unsupported TAP geometry')
    temporary=path+'.TMP'
    for name in (path,temporary):
        try:os.stat(name)
        except OSError:continue
        raise OSError('export already exists; choose a new TAP filename')
    try:
        with open(temporary,'wb') as f:
            code_header(f,'CPMRAM',128);f.write(bytes((130,0,255)))
            metadata_offset=f.tell();f.write(bytes(129))
            digest=hashlib.sha256()
            for page in range(volume.sectors//64):
                code_header(f,'CPM%02d'%page,8192);f.write(bytes((2,32,255)));crc=255
                for sector in range(64):
                    data=volume.read(page*64+sector)
                    if len(data)!=128:raise OSError('short export sector')
                    digest.update(data);crc^=xor(data);f.write(data)
                f.write(bytes((crc,)))
            metadata=(MAGIC[:9]+bytes((volume.sectors//256,volume.sectors//64,volume.sectors//80))+bytes(4)+digest.digest()).ljust(128,b'\0')
            f.seek(metadata_offset);f.write(metadata+bytes((255^xor(metadata),)));f.flush()
        TapVolume(temporary) # Validate complete output before publishing it.
        os.rename(temporary,path)
    except Exception:
        try:os.remove(temporary)
        except OSError:pass
        raise
