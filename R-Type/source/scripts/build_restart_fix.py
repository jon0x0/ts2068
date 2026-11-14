"""Route all native full-game load callers through the resident bank gateway."""
from pathlib import Path
import zipfile,json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1]
def block(payload):
 crc=255
 for v in payload:crc^=v
 return struct.pack('<H',len(payload)+2)+bytes([255])+payload+bytes([crc])
def main():
 old=ROOT/'build/fullgame/true_black_r31';out=ROOT/'build/fullgame/restart_r32';out.mkdir(parents=True,exist_ok=True)
 image=bytearray((old/'RType_TS2068_true_black_r31.ram512').read_bytes());changes=[]
 for level in range(8):
  for offset in (0x4631,0x52b8):
   at=level*65536+offset;assert image[at:at+3]==bytes.fromhex('cd 03 fe');image[at:at+3]=bytes.fromhex('cd 08 0a');changes.append(at)
 assert bytes.fromhex('cd 03 fe')not in image
 (out/'RType_TS2068_restart_r32.ram512').write_bytes(image)
 with zipfile.ZipFile(old/'RType_TS2068_disk_r31.zip')as source,zipfile.ZipFile(out/'RType_TS2068_disk_r32.zip','w',zipfile.ZIP_DEFLATED)as dest:
  for name in source.namelist():
   data=source.read(name)
   if '/RTFG' in name and name.endswith('.TAP'):
    volume=int(Path(name).stem[-2:],16);at=0;idx=0;result=b''
    while at<len(data):
     length=int.from_bytes(data[at:at+2],'little');result+=data[at:at+2+length]if idx%2==0 else block(image[(volume*4+idx//2)*8192:(volume*4+idx//2+1)*8192]);at+=length+2;idx+=1
    data=result
   dest.writestr(name,data)
  dest.writestr('RESTART_FIX.txt','Full disk game: game-over restart and native reinitialization use the resident level-bank handler. Single-level preview files remain single-level. Black-display correction retained. No on-demand disk-loader change.\n')
 (out/'manifest.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),patched_calls=changes,scope='Full disk image only; preserve r31 normal black and native new-game selection',status='Candidate pending restart verification'),indent=2))
 # Make the main source builder reproduce the missing caller fixes too.
 p=ROOT/'scripts/build_fullgame_image.py';text=p.read_text();needle="  assert json.loads((folder/'compiled_ship.json').read_text())['bytes']<=224"
 if 'for restart_offset in (0x4631,0x52b8)'not in text:
  assert needle in text;text=text.replace(needle,"  for restart_offset in (0x4631,0x52b8):\n   assert game[restart_offset:restart_offset+3]==bytes.fromhex('cd 03 fe')\n   game[restart_offset:restart_offset+3]=bytes.fromhex('cd 08 0a')\n"+needle);p.write_text(text)
 # Isolated model, keeping earlier validation reports unchanged.
 fixture=(ROOT/'scripts/true_black_fixture.mjs').read_text().replace('true_black_r31/RType_TS2068_true_black_r31.ram512','restart_r32/RType_TS2068_restart_r32.ram512')
 (ROOT/'scripts/restart_fixture.mjs').write_text(fixture)
 print(out)
if __name__=='__main__':main()
