"""Minimal typed r145 TAP overlay. Originals and RAM/bank layouts unchanged."""
from pathlib import Path
import shutil,json,hashlib,functools
from normal_black_policy import patch_score,patch_exact
R=Path(__file__).resolve().parents[1];B=R/'build/fullgame/visible_hits_r145';O=R/'build/fullgame/normal_black_r161';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ('.bin','.sym','.asm','.json') and not any(k in p.name for k in ('validation','summary','trace','release_manifest','fail','actual','expected_common','bad_cache')):shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
def blocks(data):
 p=0;out=[]
 while p<len(data):
  n=int.from_bytes(data[p:p+2],'little');v=data[p+2:p+2+n];assert len(v)==n and functools.reduce(int.__xor__,v)==0;out.append((v[0],v[1:-1]));p+=n+2
 assert p==len(data);return out
def tape(parts):
 out=bytearray()
 for flag,payload in parts:
  v=bytes([flag])+payload;out+=(len(v)+1).to_bytes(2,'little')+v+bytes([functools.reduce(int.__xor__,v)])
 return bytes(out)
changes=[]
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';before=p.read_bytes();b=bytearray(before);patch_score(b,0x76cb,'f0fd');init=b.find(bytes.fromhex('3e40d3ff'),0x1900,0x19a0);assert init>=0;patch_exact(b,init,'3e40d3ff','3e42d3ff');
 if n==7:
  at=b.find(bytes.fromhex('3647edb0'),0xdf50,0xe000);assert at>=0;patch_exact(b,at,'3647edb0','3607edb0')
 p.write_bytes(b)
 diff=[i for i,(x,y)in enumerate(zip(before,b))if x!=y];assert all(i in[init+1,0x76d5,0x76e7]or(n==7 and i==at+1)for i in diff);changes.append(dict(level=n,offsets=diff))
 for name,parts in [(f'LEVEL{n:02d}.TAP',[b[k*8192:(k+1)*8192]for k in range(8)]),(f'START{n:02d}.TAP',[b[k*8192+t*1024:k*8192+(t+1)*1024]for k in [0,1,4,5,6,7]for t in range(8)])]:
  old=blocks((O/'rtype'/name).read_bytes());it=iter(parts);new=[(flag,next(it)if flag==255 else payload)for flag,payload in old];assert next(it,None)is None;(O/'rtype'/name).write_bytes(tape(new))
p=O/'rtype/RTCORE.TAP';parts=blocks(p.read_bytes());before=b''.join(v for flag,v in parts if flag==255);b=bytearray(before)
needle=bytes.fromhex('210058e5012000c52c3e47cd7300');at=b.find(needle);assert at>=0 and b.count(needle)==1;patch_score(b,at,'7300')
needle=bytes.fromhex('2100580100033e47cd7300');at=b.find(needle);assert at>=0 and b.count(needle)==1;patch_exact(b,at,needle.hex(),needle.replace(bytes.fromhex('3e47'),bytes.fromhex('3e07')).hex())
it=iter([b[i:i+1024]for i in range(0,len(b),1024)]);p.write_bytes(tape([(flag,next(it)if flag==255 else payload)for flag,payload in parts]));assert next(it,None)is None
changes.append(dict(file='RTCORE.TAP',payload_offsets=[i for i,(x,y)in enumerate(zip(before,b))if x!=y]))
# Display version identifies this actual overlay; no loader code relocation.
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R145',b'R161'))
p=O/'rtype/rt.tap';p.write_bytes(tape([(flag,payload.replace(b'R145',b'R161'))for flag,payload in blocks(p.read_bytes())]))
count=0
for p in (O/'rtype').glob('*'):
 if p.suffix.lower()!='.tap':continue
 parts=blocks(p.read_bytes());count+=1;data=b''.join(v for flag,v in parts if flag==255)
 if p.stem.startswith('LEVEL'):assert data==(O/f'level{int(p.stem[-2:]):02d}_region.bin').read_bytes()
 if p.stem.startswith('START'):
  reg=(O/f'level{int(p.stem[-2:]):02d}_region.bin').read_bytes();assert data==b''.join(reg[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
assert count==20
(O/'normal_black_contract.json').write_text(json.dumps(dict(changes=changes,tap_files=count,policy='Bright black remains a valid hardware colour. Score text has normal-black paper; seven-colour animation preserved. Existing normal-black ECM artwork and renderer unchanged. No encoded palette IDs normalized.',bank_layout_changed=False,gameplay_code_changed=False,hardware_tested=False),indent=2))
print(O)
