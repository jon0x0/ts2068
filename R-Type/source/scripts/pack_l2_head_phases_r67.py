from pathlib import Path
import sys,json,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import pack,unpack
O=R/'build/graphics/l2_actors_r67';pal=np.array([[0,0,0],[1,0,206],[207,1,0],[207,1,206],[0,207,21],[1,207,207],[207,207,21],[207,207,207],[0,0,0],[2,0,253],[255,2,1],[2,255,253],[0,255,28],[2,255,255],[255,255,29],[255,255,255]],float)
candidates=[(0,q)for q in range(1,8)]+[(p,q)for bank in[0,8]for p in range(1+bank,8+bank)for q in range(p+1,8+bank)]
payload=bytearray();table=bytearray();ptrs={};report=[]
for n in range(3,7):
 bits=np.frombuffer((O/f'H{n}.bits').read_bytes(),np.uint8).reshape(40,5);attrs=np.frombuffer((O/f'H{n}.attrs').read_bytes(),np.uint8).reshape(40,5);im=np.zeros((40,40),np.uint8)
 for y in range(40):
  for x in range(5):
   a=int(attrs[y,x]);p=(a>>3&7)+(8 if a&64 else 0);q=(a&7)+(8 if a&64 else 0)
   for k in range(8):im[y,x*8+k]=q if bits[y,x]&(128>>k)else p
 phaseptr=[]
 for shift in[0,2,4,6]:
  dst=np.zeros((40,48),np.uint8);dst[:,shift:shift+40]=im;raw=bytearray()
  for x in range(6):
   for y in range(40):
    row=dst[y,x*8:x*8+8];col=pal[row];opts=[v for v in candidates if not(row==0).any()or v[0]==0]
    p,q=min(opts,key=lambda v:np.minimum(((col-pal[v[0]])**2).sum(1),((col-pal[v[1]])**2).sum(1)).sum());sel=((col-pal[q])**2).sum(1)<((col-pal[p])**2).sum(1)
    if p==0:sel[row!=0]=True
    a=(p&7)*8+(q&7)+(64 if p>=8 else 0);raw.extend([sum(128>>k for k in range(8)if sel[k]),a])
  compressed=pack(raw);assert unpack(compressed)==raw
  if compressed not in ptrs:ptrs[compressed]=0x2400+len(payload);payload.extend(compressed)
  phaseptr.append(ptrs[compressed])
 table.extend(bytes([n,5,5])+b''.join(v.to_bytes(2,'little')for v in phaseptr));report.append({'id':n,'ptrs':phaseptr})
assert len(payload)<=0xfe6,len(payload)
(O/'head_phases.bin').write_bytes(payload);(O/'head_table.bin').write_bytes(table);(O/'head_phases.json').write_text(json.dumps({'bytes':len(payload),'source_bank':1,'source_start':0x2400,'source_limit':0x33e6,'decode_bank':6,'decode_end':0xc1e0,'sprites':report},indent=2));print('Head phases',len(payload))
