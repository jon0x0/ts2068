"""Measure exact TAP fractional-frame factorization; never changes shipped artwork."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'build/cartridges/integration_work'
def dense(frame):
 rows=[];p=0
 for pi in frame['rows']:
  if pi<0:assert frame['bits'][p]==54;p+=1;rows.append([0]*8)
  else:rows.append(frame['bits'][p+1:p+9]);p+=9
 assert p==len(frame['bits'])
 return [[rows[(y//8)*frame['w']+x][y%8]for x in range(frame['w'])]for y in range(frame['h']*8)]
def attrs(frame,palette):return [([7]*8 if pi<0 else palette[pi])for pi in frame['rows']]
reports=[]
for n in range(2,9):
 path=O/f'L{n}_tap_motion_frames.json';j=json.loads(path.read_text());index={(v['id'],v['anim'],v['px'],v['py'],v['flip']):v for v in j['variants']};plans=[];fail=[];parents=set();pairs=set();patterns=set();checked=0
 for v in j['variants']:
  f=j['frames'][v['frame']];parent_v=index[(v['id'],v['anim'],v['px'],0,v['flip'])];parent=j['frames'][parent_v['frame']];a=dense(f);b=dense(parent);dy=((8-v['py']*2)%8 if v['flip']&2 else v['py']*2);parents.add(parent_v['frame']);pa=attrs(parent,j['palette']);ta=attrs(f,j['palette']);recipes=[]
  equal=f['w']==parent['w'] and all(a[y][x]==(b[y-dy][x]if 0<=y-dy<len(b)else 0)for y in range(len(a))for x in range(f['w']))
  if not equal:fail.append(dict(v,reason='bitmap is not translated horizontal parent'))
  else:
   for cy in range(f['h']):
    for cx in range(f['w']):
     pi=f['rows'][cy*f['w']+cx]
     if pi<0:recipes.append(None);continue
     previous=tuple(pa[(cy-1)*parent['w']+cx])if cy>0 and cy-1<parent['h']else (7,)*8
     current=tuple(pa[cy*parent['w']+cx])if cy<parent['h']else (7,)*8
     pattern=previous[8-dy:]+current[:8-dy]if dy else current
     exact_visible=True
     for sy in range(8):
      bits=a[cy*8+sy][cx];actual=ta[cy*f['w']+cx][sy];expected=pattern[sy]
      # Normal black ignores brightness; compare the colors actually painted.
      for bit in range(8):
       av=((actual&7)if bits&(128>>bit)else ((actual>>3)&7));ev=((expected&7)if bits&(128>>bit)else ((expected>>3)&7))
       if av!=ev or av and (actual^expected)&64:exact_visible=False
       checked+=1
     if not exact_visible:fail.append(dict(v,reason='translated palette differs',cell=[cx,cy]));break
     patterns.update((previous,current));pairs.add((previous,current));recipes.append([list(previous),list(current),dy])
  plans.append(dict(v,parent=parent_v['frame'],dy=dy,bitmap_exact=equal,recipes=recipes))
 report=dict(level=n,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),variants=len(plans),frames=len(j['frames']),horizontal_parent_frames=len(parents),parent_patterns=len(patterns),parent_pairs=len(pairs),pixel_color_checks=checked,failures=fail,passed=not fail,scope='Exact offline factorization of captured TAP motion frames; not yet a cartridge runtime or performance result')
 (O/f'L{n}_motion_factorization.json').write_text(json.dumps(dict(report=report,plans=plans)));reports.append(report);print(n,{k:report[k]for k in ('frames','horizontal_parent_frames','parent_patterns','parent_pairs','pixel_color_checks','passed')},'failures',len(fail),flush=True)
(O/'motion_factorization_summary.json').write_text(json.dumps(reports,indent=2))
