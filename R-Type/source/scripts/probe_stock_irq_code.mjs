import fs from'node:fs';import{stockFixture}from'./stock_fixture.mjs';const{m,out}=stockFixture(1);fs.writeFileSync(out+'/irq_inspect.home.bin',m.ram);
