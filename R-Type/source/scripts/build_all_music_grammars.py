"""Bound the native RePair decoder's pending stack while preserving every tick."""
from pathlib import Path
import json,collections,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/fullgame/audio';summary=[]
 for entry in range(16):
  source=json.loads((out/f'music_probe_{entry}.json').read_text());state=[0]*14;frames=[];sequence=[]
  for writes in [source['init']]+source['frames']:
   changes=[]
   for reg,value in writes:
    assert reg in [0,1,2,3,4,5,7,8,9,10]
    if state[reg]!=value:changes.extend([reg,value]);state[reg]=value
   frame=bytes([len(changes)//2])+bytes(changes)
   if frame not in frames:frames.append(frame)
   sequence.append(frames.index(frame))
  leaves=len(frames);pairs=[];depth=[0]*leaves
  while len(sequence)>1:
   ranked=collections.Counter(zip(sequence,sequence[1:])).most_common();candidate=next(((pair,count)for pair,count in ranked if count>=4 and 1+max(depth[pair[0]],depth[pair[1]])<=22),None)
   if candidate is None:break
   pair,count=candidate;new=[];i=0
   while i<len(sequence):
    if i+1<len(sequence) and tuple(sequence[i:i+2])==pair:new.append(leaves+len(pairs));i+=2
    else:new.append(sequence[i]);i+=1
   depth.append(1+max(depth[pair[0]],depth[pair[1]]));pairs.append(pair);sequence=new
  data=dict(leaves=leaves,frames=[list(f)for f in frames],pairs=pairs,sequence=sequence+[65535],source_ticks=len(source['frames']),source_loop=source['loop'],max_tree_depth=max(depth),pending_stack_bound_bytes=2*max(depth),source_sha256=hashlib.sha256((ROOT/'build/research/goodboy2019/player_bank7.bin').read_bytes()).hexdigest())
  (out/f'music_grammar_{entry}.json').write_text(json.dumps(data));summary.append(dict(entry=entry,loop=source['loop'],depth=max(depth),stack_bound=data['pending_stack_bound_bytes'],bytes=sum(map(len,frames))+leaves*2+len(pairs)*4+(len(sequence)+1)*2));print(summary[-1],flush=True)
 (out/'grammar_inventory.json').write_text(json.dumps(summary,indent=2))
if __name__=='__main__':main()
