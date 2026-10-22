"""Strict standard CPC DSK adapter for our 40-track Oliger CP/M media."""
import os

class DskVolume:
    def __init__(self,path):
        self.path=path
        with open(path,'rb') as f:
            h=f.read(256)
            if len(h)!=256 or h[:34]!=b'MV - CPCEMU Disk-File\r\nDisk-Info\r\n':raise OSError('expected standard DSK')
            sides=h[49]
            if h[48]!=40 or sides not in (1,2) or h[50:52]!=b'\x00\x11':raise OSError('unsupported Oliger geometry')
            for index in range(40*sides):
                cylinder,head=divmod(index,sides);t=f.read(256)
                if len(t)!=256 or t[:12]!=b'Track-Info\r\n' or t[16:18]!=bytes((cylinder,head)) or t[20:22]!=bytes((1,16)):raise OSError('invalid DSK track')
                for sector in range(16):
                    if t[24+sector*8:30+sector*8]!=bytes((cylinder,head,sector+1,1,0,0)):raise OSError('unsupported DSK sector')
                if len(f.read(4096))!=4096:raise OSError('truncated DSK')
            if f.read(1):raise OSError('extra DSK data')
        self.sectors=1280*sides
        with open(path,'r+b'):pass
    def read(self,lba):
        if not 0<=lba<self.sectors:raise OSError('DSK sector out of range')
        with open(self.path,'rb') as f:
            f.seek(512+(lba//32)*4352+(lba%32)*128);data=f.read(128)
        if len(data)!=128:raise OSError('short DSK sector')
        return data
    def write(self,lba,data):
        if not 0<=lba<self.sectors or len(data)!=128:raise OSError('invalid DSK write')
        with open(self.path,'r+b') as f:
            f.seek(512+(lba//32)*4352+(lba%32)*128)
            if f.write(data)!=128:raise OSError('short DSK write')
            f.flush()

def save_dsk(volume,path):
    if volume.sectors not in (1280,2560):raise OSError('unsupported DSK geometry')
    temporary=path+'.TMP'
    for name in (path,temporary):
        try:os.stat(name)
        except OSError:continue
        raise OSError('export already exists')
    sides=volume.sectors//1280
    try:
        with open(temporary,'wb') as f:
            h=bytearray(256);h[:34]=b'MV - CPCEMU Disk-File\r\nDisk-Info\r\n';h[34:48]=b'CPM2068       '
            h[48:52]=bytes((40,sides,0,17));f.write(h)
            for index in range(40*sides):
                c,s=divmod(index,sides);t=bytearray(256);t[:12]=b'Track-Info\r\n'
                t[16:24]=bytes((c,s,1,2,1,16,42,229))
                for sector in range(16):t[24+sector*8:32+sector*8]=bytes((c,s,sector+1,1,0,0,0,0))
                f.write(t)
                for sector in range(32):
                    data=volume.read(index*32+sector)
                    if len(data)!=128:raise OSError('short export sector')
                    f.write(data)
        DskVolume(temporary);os.rename(temporary,path)
    except Exception:
        try:os.remove(temporary)
        except OSError:pass
        raise
