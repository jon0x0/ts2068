"""Stage immutable cartridge references and audited r145 per-level compressed inputs.
This is a porting input builder, NOT a publisher of updated playable ROMs.
"""
from pathlib import Path
import sys,json,hashlib,shutil
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal;from boss_motion_assets_r60 import unpack
B=R/'build/fullgame/visible_hits_r145';O=R/'build/cartridges/r146_work';O.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def tape_data(p):
 s=p.read_bytes();at=0;out=[]
 while at<len(s):
  n=int.from_bytes(s[at:at+2],'little');q=s[at+2:at+2+n];assert len(q)==n and __import__('functools').reduce(int.__xor__,q)==0
  if q[0]==255:out.append(q[1:-1])
  at+=n+2
 return b''.join(out)
core=tape_data(B/'rtype/RTCORE.TAP');cores=[core[a:a+8192]for a in range(0,len(core),8192)];shared=O/'packed_inputs/shared';shared.mkdir(parents=True,exist_ok=True);csize=0
for i,b in enumerate(cores):
 v=pack_optimal(b);assert unpack(v)==b;(shared/f'core{i}.lz').write_bytes(v);csize+=len(v)
records=[]
for n in range(1,9):
 folder=O/f'packed_inputs/level{n:02d}';folder.mkdir(parents=True,exist_ok=True);b=(B/f'level{n:02d}_region.bin').read_bytes();sizes=[]
 for k in[0,1,4,5,6,7]:
  raw=b[k*8192:(k+1)*8192];v=pack_optimal(raw);assert unpack(v)==raw;(folder/f'dock{k}.lz').write_bytes(v);sizes.append(len(v))
 ref=R/f'build/fullgame/foundation/level{n:02d}.dck';v=ref.read_bytes();assert len(v)==65545 and v[:9]==bytes([0]+[2]*8)
 d=O/'native_reference_only';d.mkdir(exist_ok=True);shutil.copy2(ref,d/f'level{n:02d}.dck')
 records.append(dict(level=n,current_region_sha256=sha(b),packed_payload_bytes=csize+sum(sizes),rom64_remaining_before_bootstrap=65536-csize-sum(sizes),input_pages=[0,1,4,5,6,7],source_ram_banks=[2,3],reference_native_rom_sha256=sha(v[9:]),updated_stock_rom_ready=False))
 print(n,records[-1]['packed_payload_bytes'],flush=True)
manifest=dict(status='PORTING INPUTS ONLY - not updated PicoROM outputs',latest_game='r145',shared_packed_core_bytes=csize,levels=records,stock_layout='Previous ECM ROM uses ROM0/ROM1 with workspace6000-77FF relocatedA600-BDFF; latest expanded engines/retained buffers still need stock adapters',proof='All input streams roundtrip through existing codec; all8 original native DCKs are ROM-only; separate ECM previews use writable banks')
(O/'manifest.json').write_text(json.dumps(manifest,indent=2))
(O/'README.txt').write_text('Cartridge port work area r146\n\nNOT a release of updated cartridges. packed_inputs contains exact r145 inputs\ncompressed with the existing Z80 LZ format, all roundtrip verified.\nNative references are the earlier original-graphics ROM-only level foundations;\nthey do not contain the current ECM artwork or r145 gameplay updates.\nUpdated stock48KB RAM layout and cartridge runtime adapters remain unfinished.\nNo .rom files are emitted until those runtime checks pass.\n')
