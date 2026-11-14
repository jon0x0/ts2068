from pathlib import Path
import json,collections,hashlib
r=Path(__file__).resolve().parents[1]
out=r/"build/audio"
reference=json.loads((out/'music_probe_0.json').read_text());assert reference['loop']=={'start':0,'end':2305}
state=[0]*14;frames=[];sequence=[]
for f in [reference['init']]+reference['frames']:
 changes=[]
 for reg,value in f:
  assert reg<14
  if state[reg]!=value or reg==13:changes.extend([reg,value]);state[reg]=value
 record=bytes([len(changes)//2])+bytes(changes)
 if record not in frames:frames.append(record)
 sequence.append(frames.index(record))
pairs=[];leaves=len(frames)
while len(sequence)>1:
 pair,count=collections.Counter(zip(sequence,sequence[1:])).most_common(1)[0]
 if count<4:break
 new=[];i=0
 while i<len(sequence):
  if i+1<len(sequence) and tuple(sequence[i:i+2])==pair:new.append(leaves+len(pairs));i+=2
  else:new.append(sequence[i]);i+=1
 pairs.append(pair);sequence=new
data={'leaves':leaves,'frames':[list(f)for f in frames],'pairs':pairs,'sequence':sequence+[65535],'source_ticks':len(reference['frames']),'source_loop':reference['loop'],'source_sha256':hashlib.sha256((r/'build/research/goodboy2019/player_bank7.bin').read_bytes()).hexdigest()}
(out/'music_grammar.json').write_text(json.dumps(data))
