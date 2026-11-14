from pathlib import Path
p=Path('scripts/verify_startup_queue_r66.mjs');s=p.read_text().replace("const{m,joy,controller:c}=demandFixture();", "const level=Number(process.env.TEST_LEVEL||1),{m,joy,controller:c}=demandFixture();")
s=s.replace('if(latched<0&&m.ram[0xd623]===1)latched=frame;', "if(latched<0&&m.ram[0xd623]===1){latched=frame;fs.writeFileSync(path.join(out,`queue_L${level}.home.bin`),m.ram);}if(latched>=0&&level!==1&&frame-latched>15&&frame-latched<35)m.keyMatrix[3]&=~(1<<(level-1));")
s=s.replace('assert.equal(c.region,0);','assert.equal(c.region,level-1);').replace("'initial_shift_L.json'",'`initial_shift_L${level}.json`');p.write_text(s)
for a,b in [('verify_key_definition_r65','verify_key_definition_r66')]:
 s=Path('scripts/'+a+'.mjs').read_text().replace('boss_motion_fixture_r65','boss_motion_fixture_r66');Path('scripts/'+b+'.mjs').write_text(s)
