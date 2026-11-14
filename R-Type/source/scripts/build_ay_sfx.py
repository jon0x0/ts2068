"""Pack single-channel speech2ay conversions of authentic arcade effects."""
from pathlib import Path
import json,hashlib
MAPPING={1:48,2:50,3:52,4:48,5:49,6:80,7:43,8:99,9:48,10:50,11:53,12:50,13:48,14:80,15:43,16:43,17:99,18:49,19:50,20:99,21:99}
def build(root):
 out=root/'build/audio';candidates=json.loads((out/'speech2ay_candidates/manifest.json').read_text());streams={};reference={}
 for command in set(MAPPING.values()):
  entry=next(e for e in candidates if e['command']==command and e['channels']==1)
  source=entry['register_frames'];assert len(source)==entry['frames'];assert entry['source_rms']>1
  assert all(len(f)==11 and 0<=f[1]<16 and 0<=f[8]<16 for f in source)
  frames=[]
  for i in range(round(len(source)*50/60.1145)):
   f=source[min(len(source)-1,int(i*60.1145/50))];frames.append([f[0],f[1],f[6],0xB0|(f[7]&9),f[8]])
  if command==53:
   fitted=json.loads((out/'death_triangle_trials/65.json').read_text())['register_frames']
   frames=[[f[0],f[1],f[6],f[7],f[8],f[2],f[3],f[9],f[11],f[12],f[13]]for f in fitted]
  while frames and frames[-1][4]==0 and (len(frames[-1])<8 or frames[-1][7]==0):frames.pop()
  assert frames,command
  runs=[]
  for frame in frames:
   if runs and runs[-1][1]==frame and runs[-1][0]<255:runs[-1][0]+=1
   else:runs.append([1,frame])
  data=bytearray();previous=None
  for duration,frame in runs:
   mask=sum(1<<i for i in range(min(8,len(frame)))if previous is None or frame[i]!=previous[i]);data.extend([duration,mask]);data.extend(frame[i]for i in range(min(8,len(frame)))if mask&(1<<i));
   if command==53:data.extend(frame[8:11])
   previous=frame
  data.append(0);streams[command]=bytes(data);reference[command]=frames
 print("arcade effect bytes",{k:len(v)for k,v in streams.items()})
 segments=[[0x04C2,0x08C0],[0x1254,0x1400],[0x8634,0x8727]];writes=[];pointers={};records=[]
 for command,data in sorted(streams.items(),key=lambda e:-len(e[1])):
  segment=next((s for s in segments if s[1]-s[0]>=len(data)),None);assert segment is not None,(command,len(data),segments)
  a=segment[0];segment[0]+=len(data);writes.append((a,data));pointers[command]=a;records.append(dict(command=command,pointer=a,bytes=len(data),frames=len(reference[command])))
 directory=bytearray(66)
 for event,command in MAPPING.items():
  a=pointers[command];directory[event*3:event*3+3]=bytes([16 if a>=0x8000 else 0])+a.to_bytes(2,'little')
 writes.append((0x480,directory))
 # ROM0 helper consumes the three death-only envelope trailer bytes. R13=255
 # is a skip sentinel: retriggering the triangle each tick destroys its pitch.
 import subprocess,re
 assembler=root.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
 helper=out/'death_envelope.bin'
 result=subprocess.run([str(assembler),f'--raw={helper}',str(root/'src/death_envelope.asm')],cwd=root,capture_output=True,text=True)
 assert result.returncode==0,result.stdout+result.stderr
 writes.append((0x0BC0,helper.read_bytes()))
 group=out/'terrain_groups.bin'
 from fullgame_context import FULL,layout
 source=root/'src/terrain_groups.asm'
 if FULL:
  spec=json.loads((root/'build/art_assets/terrain_groups.json').read_text());text=(root/'src/terrain_groups_full.asm').read_text();d=layout()
  text=text.replace('$D9',f'${d["terrain_start"]>>8:02X}').replace('$E6',f'${(d["map_start"]>>8)+1:02X}')
  symbols={n:int(v,16)for n,v in re.findall(r'(\w+): EQU 0x([0-9a-fA-F]+)',(root/'build/ecm_native/renderer.sym').read_text())}
  text=text.replace('initial_group_attribute:\n','initial_group_attribute:\n        CALL FULL_RETAINED_ATTRIBUTE\n        RET C\n')
  text=text.replace('        BIT 7,A\n        JR Z,apply_group_skip','        CP $80\n        JR C,apply_group_skip\n        CP $90\n        JR NC,apply_group_skip')
  source=out/'terrain_groups_full.asm';source.write_text(f'FULL_RETAINED_ATTRIBUTE EQU ${symbols["full_retained_attribute"]:04X}\nGROUP_DICTIONARY EQU ${spec["dictionary"]:04X}\n'+text)
 result=subprocess.run([str(assembler),f'--raw={group}',str(source)],cwd=root,capture_output=True,text=True)
 assert result.returncode==0,result.stdout+result.stderr
 writes.append((0x08C0,group.read_bytes()))
 if FULL:writes.append((0x0200,(root/'build/art_assets/terrain_group_full.bin').read_bytes()))
 (out/'arcade_sfx_packed_r17.json').write_text(json.dumps(dict(events=MAPPING,effects=records,bytes=sum(map(len,streams.values())),tick_hz=50,channels=1,death_channels=2,free_segments=segments),indent=2))
 (out/'arcade_sfx_reference_r17.json').write_text(json.dumps(dict(events=MAPPING,frames=reference)))
 return writes
