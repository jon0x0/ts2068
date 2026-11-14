"""Partial recursive native audit; never classify raw data bytes as proven code."""
import sys,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'elite/tmp/pydeps'))
from z80dis.z80 import decode,disasm,OPER_TYPE
out=ROOT/'build/native'
m=bytearray(65536);m[0x4000:]=(out/'snapshot.bin').read_bytes();code=(out/'input.bin').read_bytes();m[0x1a00:0x1a00+len(code)]=code
seeds=[0x8634,0x8383,0xbe23,0x8b06,0x8b0a,0x8b14,0x8b19,0x8b2d,0xc011,0x8f1f,0xfe03,0x1a00]
m=bytes(m);pending=seeds[:];reachable={};indirect=[];low=[];io=[];overlap=[]
while pending:
 pc=pending.pop()
 while (0x7000<=pc<65536 or 0x1a00<=pc<0x1a00+len(code)) and pc not in reachable:
  i=decode(m[pc:],pc)
  if i.len<1:break
  name=i.op.name;text=disasm(m[pc:],pc);reachable[pc]=text
  targets=[a[1] for a in i.operands if a[0]==OPER_TYPE.ADDR]
  if name in ('JP','JR','CALL','DJNZ'):
   pending.extend(t for t in targets if 0<=t<65536)
   for t in targets:
    if t<0x4000:low.append(dict(address=pc,target=t,instruction=text,status='Native input ROM' if t==0x1a00 else 'Native key-release wrapper' if t==0x1b00 else 'UNCONVERTED Spectrum tape entry' if t==0x562 else 'Self-modified dispatch operand; written at $9455/$FF48 before CALL' if pc in (0x9460,0xff52) else 'Requires review'))
   conditional=any(a[0]==OPER_TYPE.COND for a in i.operands)
   if name in ('JP','JR') and not conditional:
    if not targets:indirect.append(dict(address=pc,instruction=text))
    break
  if name in ('RET','RETI','RETN') and not i.operands:break
  if name in ('IN','OUT','IM','HALT','RST'):io.append(dict(address=pc,instruction=text))
  if name=='RST':break
  addresses=[int(x,16) for x in re.findall(r'0x([0-9a-f]+)',text)]
  if any(0x6000<=a<0x7800 for a in addresses):overlap.append(dict(address=pc,instruction=text))
  pc+=i.len
report=dict(seeds=seeds,instruction_count=len(reachable),low_branches=low,indirect_jumps=indirect,hardware=io,ecm_overlap_references=overlap,limitations='Partial static reachability only; indirect dispatch, self modification, data embedded after CALL, and later-level overlays need runtime tracing. Uses existing local z80dis tooling from Elite without modifying it.')
(out/'compatibility_audit.json').write_text(json.dumps(report,indent=2))
(out/'reachable_disassembly.txt').write_text('\n'.join(f'{a:04X}: {reachable[a]}' for a in sorted(reachable)))
print('Decoded',len(reachable),'instructions;',len(overlap),'candidate ECM-plane references')
print('Low branches:',low)


