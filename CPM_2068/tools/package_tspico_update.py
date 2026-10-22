"""Package cartridge and small utility TAPs without replacing any user disks."""
from pathlib import Path
import zipfile,hashlib
from tspico_ram_image import tap_code
ROOT=Path(__file__).resolve().parents[1]
b=ROOT/'build';profile=b/'profiles/tspico-dual'
files={'TAP/CPM/CPM.DCK':(profile/'ts2068-cpm.dck').read_bytes()}
for name,alias in [('VIDEO','VIDEOCOM'),('COLOR','COLORCOM'),('COLUMNS','COLSCOM')]:
 binary=(b/(name+'.COM')).read_bytes()
 files['host/'+name+'.COM']=binary
 data=tap_code(name,binary)
 for folder in ('TAP/CPM/','TAP/CPM/SAVE/'):files[folder+alias+'.TAP']=data
files['README.txt']=b"""Merge TAP into the SD card. No disk image or saved chunk is replaced.
Power-cycle and load CPM.DCK into SRAM slot 4.
At A>, import the small utility TAPs using the existing TPLOAD:
REN VIDEO.OLD=VIDEO.COM   (only if VIDEO.COM exists; use another backup name if needed)
TPLOAD VIDEOCOM.TAP VIDEO.COM
REN COLOR.OLD=COLOR.COM
TPLOAD COLORCOM.TAP COLOR.COM
REN COLUMNS.OLD=COLUMNS.COM
TPLOAD COLSCOM.TAP COLUMNS.COM
VIDEO
COLUMNS 80
COLOR 0
Preserve previous .OLD backups; choose another backup extension if already used.
The TAPs are in CPM and CPM/SAVE because reload can leave either current directory.
For RAMDisk, run TPSAVE when finished to preserve imported utilities and your files.
For native FILES mode, copy host/*.COM into your CP/M FILES directory instead.
VIDEO reports 7F=version, 40=enable, 41=mode and 43=mirror in hex.
7F=10 matches older V4 firmware: its 80-column renderer is inactive and
banked writes can corrupt its displayed copy. See picovideo.md for evidence.
"""
for name in ('picovideo.md','tspico-ram.md'):files[name]=(ROOT/'docs'/name).read_bytes()
files['checksums.txt']=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(files.items())).encode()
output=b/'ts2068-cpm-tspico-display-update.zip'
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as archive:
 for name,data in sorted(files.items()):archive.writestr(name,data)
print(output)
