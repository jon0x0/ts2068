import{stockFixture}from './stock_fixture.mjs';const{m}=stockFixture(4);console.log(Buffer.from(m.ram.slice(0xbe23,0xbe65)).toString('hex'));
