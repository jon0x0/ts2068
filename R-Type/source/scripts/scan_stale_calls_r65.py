from pathlib import Path
import json
b=Path('build/fullgame/hardware_fire_r65/boot_region.bin').read_bytes();mem=bytes(32768)+b[0x4000:0x8000]+b[0xa000:0xe000];hits=[]
for a in range(0x8000,0xc4ac):
 if mem[a] in [0xcd,0xc3,0xc4,0xcc,0xd4,0xdc,0xe4,0xec,0xf4,0xfc,0xc2,0xca,0xd2,0xda,0xe2,0xea,0xf2,0xfa]:
  target=int.from_bytes(mem[a+1:a+3],'little')
  if 0xfdc3<=target<0xfe03:hits.append({'address':hex(a),'opcode':hex(mem[a]),'target':hex(target)})
print(hits);Path('build/fullgame/hardware_fire_r65/stale_call_scan.json').write_text(json.dumps({'scope':'conservative direct transfer byte candidates HOME8000..C4AE; data may create false positives','force_overwritten_range':['FDC3','FE03'],'remaining_candidates':hits,'fixed_key_clear':'BFA9 CALL FDEF -> CALL 0072'},indent=2))
