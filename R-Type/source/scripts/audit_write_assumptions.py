"""Triage memory writers in the existing partial native disassembly."""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1];rows=[]
for line in (R/'build/native/reachable_disassembly.txt').read_text().splitlines():
 a,t=line.split(': ',1)
 if re.match(r'(LD|INC|DEC|SET|RES|RL|RR|SLA|SRA|SRL|RLC|RRC) \(',t) or t.startswith(('LDIR','LDDR','LDI','LDD','EX (SP)')):rows.append(dict(pc=int(a,16),instruction=t))
direct=[]
for row in rows:
 m=re.match(r'LD \(0x([0-9a-f]+)\),',row['instruction'])
 if m and int(m[1],16)<0x4000:direct.append(row)
bc=[v for v in rows if v['instruction']=='LD (BC),A']
out=R/'build/diagnostics/write_assumption_audit';out.mkdir(parents=True,exist_ok=True)
report=dict(static_writer_candidates=len(rows),direct_low_stores=direct,bc_stores=bc,bc_triage={'9C3E':'Confirmed ROM-ignore assumption, fixed r41','BF3C':'Star attribute store, B derived from row metadata; retain runtime range checks'},limitations='Existing5483-instruction partial native reachability only; indirect dispatch, selfmodification and later-level code are not exhaustively decoded.')
(out/'static.json').write_text(json.dumps(report,indent=2));print(report)
