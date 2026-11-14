"""Correct legacy public-root deployment; leave verified loader/game bytes intact."""
from pathlib import Path
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 source=ROOT/'build/fullgame/loading_text_r28/RType_TS2068_fullgame_r28.zip'
 out=ROOT/'build/fullgame/disk_layout_r30';out.mkdir(parents=True,exist_ok=True)
 target=out/'RType_TS2068_disk_r30.zip';records=[]
 readme='R-Type TS2068 disk game\n\nExtract this ZIP to the SD card root, preserving TAP/RTYPE.\nLoad RTFULL.TAP from TAP/RTYPE. Keep RTFG00.TAP through RTFG0F.TAP beside it.\nThe firmware public root is the TAP directory, not the physical SD root.\nIf an older RTYPE directory was copied to the card root, move that complete directory into TAP instead.\nRequires512KB expansion RAM. All levels preload before play.\nAt title press1-8, release, then Fire or keyboard0. M toggles music.\nERROR03 before PAGE00 means directory selection failed on the reviewed firmware. Check TAP/RTYPE.\nNo firmware changes are required for this packaging correction. Physical loading confirmation remains pending.\n'
 with zipfile.ZipFile(source)as old,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED)as new:
  for name in old.namelist():
   data=old.read(name)
   if name.startswith('RTYPE/'):
    name='TAP/'+name
    if name.endswith('README.txt'):data=readme.encode()
   new.writestr(name,data)
   if name.endswith('.TAP'):records.append(dict(file=name,sha256=hashlib.sha256(data).hexdigest()))
  new.writestr('INSTALL.txt',readme)
 with zipfile.ZipFile(source)as old,zipfile.ZipFile(target)as new:
  for r in records:assert new.read(r['file'])==old.read(r['file'][4:])
  assert len(records)==17
 # Keep future reproducible package instructions consistent with firmware.
 for file in ['scripts/build_fullgame_package.py','scripts/build_loading_text.py']:
  p=ROOT/file;s=p.read_text();s=s.replace('Copy the RTYPE folder to the SD root.','Copy the RTYPE folder into the SD card TAP folder.').replace('Copy RTYPE to the SD root','Copy RTYPE into the SD card TAP folder');p.write_text(s)
 (out/'manifest.json').write_text(json.dumps(dict(scope='Deployment path correction only; all17 TAP files byte-identical to r28',public_root='/sd/TAP',install_directory='TAP/RTYPE',files=records),indent=2));print(target)
if __name__=='__main__':main()
