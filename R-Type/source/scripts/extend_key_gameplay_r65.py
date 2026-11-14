from pathlib import Path
p=Path('scripts/verify_key_definition_r65.mjs');s=p.read_text();s=s.replace('const result={passed:finished===3', '''let live=-1,x0=null,x1=null;
for(let t=0;t<1400;t++){frame++;m.keyMatrix.fill(31);joy.fill(255);if(t>=300&&t<350)m.keyMatrix[7]&=~1;if(m.ram[0x5bc2]&&m.dock[3][0x1aa4]>0&&live<0){live=t;x0=m.dock[7][0x1680];}if(live>=0){m.dock[3][0x1a98]=1;if(t-live<40)m.keyMatrix[1]&=~1;else{x1=m.dock[7][0x1680];break;}}api.runFrame(m);}
assert(live>=0&&x1>x0,JSON.stringify({live,x0,x1,pc:m.cpu.pc}));
const result={custom_keys_start_and_move:true,x0,x1,passed:finished===3''');p.write_text(s)
