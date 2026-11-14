"""Reproducible text-only overlay for preserved cartridge/disk releases."""
from pathlib import Path
import hashlib,json,zipfile,struct
ROOT=Path(__file__).resolve().parents[1]
REPLACEMENTS={
 'REWIND SIDE 2 THEN PRESS ANY KEY':'LEVEL READY - PRESS ANY KEY',
 'REWIND TAPE':'PLEASE WAIT',
 'STOP TAPE':'DATA OK',
 'START TAPE':'READ DATA',
 'SEARCHING FOR ':'SELECTING DATA',
}
def encoded(s):
 b=bytearray(s.encode('ascii'));b[-1]|=128;return bytes(b)
def patch(data):
 result=bytearray(data);records=[]
 for old,new in REPLACEMENTS.items():
  assert len(new)<=len(old),(old,new)
  before=encoded(old);after=encoded(new.ljust(len(old)))
  pos=0
  while True:
   at=data.find(before,pos)
   if at<0:break
   assert result[at:at+len(before)]==before
   result[at:at+len(before)]=after;records.append(dict(offset=at,old=old,new=new));pos=at+len(before)
 assert len(result)==len(data)
 allowed=set(i for r in records for i in range(r['offset'],r['offset']+len(r['old'])))
 assert all(i in allowed for i,(a,b)in enumerate(zip(data,result))if a!=b)
 for r in records:
  b=result[r['offset']:r['offset']+len(r['old'])]
  assert b[-1]&128 and not any(v&128 for v in b[:-1])
 return bytes(result),records
def tap(payload):
 flag=255;check=flag
 for v in payload:check^=v
 return struct.pack('<H',len(payload)+2)+bytes([flag])+payload+bytes([check])
def main():
 base=ROOT/'build/fullgame';out=base/'loading_text_r28';out.mkdir(parents=True,exist_ok=True)
 image=(base/'RType_TS2068_ECM_fullgame_TSPico512_r27.ram512').read_bytes()
 assert hashlib.sha256(image).hexdigest()=='741ad3721c27166265d4c260235f10b8919f9f36e9ee5951702c35135ddc87a1'
 fixed,changes=patch(image);assert changes
 (out/'RType_TS2068_fullgame_r28.ram512').write_bytes(fixed)
 manifest=dict(scope='Text-only overlay on r27; no graphics/runtime code changes',image_sha256=hashlib.sha256(fixed).hexdigest(),image_changes=changes,files=[])
 def record(name,data,changes):
  manifest['files'].append(dict(file=name,sha256=hashlib.sha256(data).hexdigest(),changes=changes))
 with zipfile.ZipFile(base/'RType_TS2068_ECM_fullgame_TSPico512_r27.zip')as source,zipfile.ZipFile(out/'RType_TS2068_fullgame_r28.zip','w',zipfile.ZIP_DEFLATED)as dest:
  for name in source.namelist():
   if name=='RTYPE/RTFULL.TAP':dest.writestr(name,source.read(name))
   elif name.startswith('RTYPE/RTFG')and name.endswith('.TAP'):
    volume=int(Path(name).stem[-2:],16);old=source.read(name);pos=0;blocks=[];idx=0
    while pos<len(old):
     size=int.from_bytes(old[pos:pos+2],'little');block=old[pos+2:pos+2+size];assert len(block)==size
     assert __import__('functools').reduce(int.__xor__,block)==0
     if idx%2==0:blocks.append(old[pos:pos+2+size])
     else:
      page=volume*4+idx//2;assert block[0]==255 and block[1:-1]==image[page*8192:(page+1)*8192]
      blocks.append(tap(fixed[page*8192:(page+1)*8192]))
     pos+=size+2;idx+=1
    assert idx==8;data=b''.join(blocks);dest.writestr(name,data);record(name,data,[])
   elif name.startswith('Fuse-level-previews/')and name.endswith('.dck'):
    old=source.read(name);data,c=patch(old);dest.writestr(name,data)
    path=out/Path(name).name;path.write_bytes(data);record(path.name,data,c)
  readme='Copy RTYPE into the SD card TAP folder and load RTFULL.TAP using the normal LOAD command. Requires the512KB RAM disk-loading setup. All levels are preloaded; no tape rewind is required between levels. Press1-8 at the title, release, then press Fire or keyboard0. M toggles music. Single-level Fuse DCK previews do not load the following stage. The64KB cartridge contains level1 only. Hardware remains untested. This revision changes loading messages only.\n'
  dest.writestr('RTYPE/README.txt',readme)
 # Separate read-only level-one cartridge: retain the accepted ROM layout.
 rompath=ROOT/'build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r24.rom'
 rom,c=patch(rompath.read_bytes());assert len(rom)==65536 and c
 (out/'RType_level1_cartridge_r28.rom').write_bytes(rom);record('RType_level1_cartridge_r28.rom',rom,c)
 (out/'RType_level1_cartridge_r28.dck').write_bytes(bytes([0,2,2,2,2,2,2,2,2])+rom)
 checked=0
 with zipfile.ZipFile(out/'RType_TS2068_fullgame_r28.zip')as archive:
  for name in archive.namelist():
   if not name.startswith('RTYPE/RTFG'):continue
   data=archive.read(name);at=0;idx=0;volume=int(Path(name).stem[-2:],16)
   while at<len(data):
    size=int.from_bytes(data[at:at+2],'little');block=data[at+2:at+2+size]
    assert __import__('functools').reduce(int.__xor__,block)==0
    if idx%2:
     page=volume*4+idx//2
     assert block[1:-1]==fixed[page*8192:(page+1)*8192];checked+=1
    at+=size+2;idx+=1
 assert checked==64
 manifest['verified_disk_pages']=checked
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
 print('Text overlay complete:',len(changes),'full-image replacements;',len(c),'cartridge replacements')
if __name__=='__main__':main()
