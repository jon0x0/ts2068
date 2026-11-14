import fs from'node:fs';import assert from'node:assert/strict';import{stockFixture}from'./stock_fixture.mjs';import{off,rev}from'./r22_test_machine.mjs';
const f=stockFixture(5),{m,call,out}=f,c=JSON.parse(fs.readFileSync(out+'/overlap_contract.json')),sy=Object.fromEntries([...fs.readFileSync(out+'/stock_overlap_compositor.sym','utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(v=>[v[1],parseInt(v[2],16)])),r=JSON.parse(fs.readFileSync(out+'/player_ram_layout.json')),k=JSON.parse(fs.readFileSync(out+'/shared_cache_layout.json')).symbols,j=JSON.parse(fs.readFileSync(out+'/combined_frames.json')),ws=c.state[0],ctx=r.allocations.context_and_stack[0],cache=r.allocations.sprite_cache[0];
function blend(ob,oa,sb,sa){const oi=oa&7,op=oa>>3&7,si=sa&7,sp=sa>>3&7;if(oi&&op)return[ob,oa];const fm=op?(~ob&255):oi?ob:0;if(!fm)return[sb,sa];if(fm===255)return[ob,oa];const sm=sp?(si?255:~sb&255):si?sb:0;if((fm|sm)===255){const back=!sp?si:!si?sp:(fm|sb)===255?si:sp;return[fm,(op||oi)|(back<<3)];}return[op?ob&(~sm&255):ob|sm,oa];}
let rows=0;const values=[0,255,85,170,129,126];for(let oa=0;oa<64;oa++)for(let sa=0;sa<64;sa++)for(let p=0;p<values.length;p++){const ob=values[p],sb=values[(p+sa)%values.length],want=blend(ob,oa,sb,sa);m.ram.set([ob,oa,sb,sa,ob,oa],ws+48);call(sy.BLEND_ROW??sy.blend_row);assert.deepEqual(Array.from(m.ram.slice(ws+52,ws+54)),want,JSON.stringify({ob,oa,sb,sa}));rows++;}
// Bulk foreground palette reads must retain native raw/terrain and reversed dictionary policies.
let paletteCases=0;for(const flags of [0,0x40,0x20,0xa0])for(const token of [0,7,63,127]){
 const cell=2*32+10;m.ram[0x7800+cell]=token;m.ram[0x8100+cell]=flags;m.ram[ws+8]=(0x7e00+cell)&255;m.ram[ws+9]=(0x7e00+cell)>>8;
 const expected=[];for(let y=0;y<8;y++){call(0x0206,{h:(0x4000+off(16)+10+y*256)>>8,l:(off(16)+10)&255});expected.push(m.cpu.a);}
 call(sy.read_old_row);assert.deepEqual(Array.from(m.ram.slice(ws+64,ws+72)),expected,JSON.stringify({flags,token}));paletteCases++;
}
const initial=Buffer.from(m.ram);let cells=0;for(let n=0;n<128;n++)for(let flip=0;flip<4;flip++){
 m.ram.set(initial);call(c.code+3);m.ram.fill(0,0x7e00,0x8080);m.ram.fill(0,0x8100,0x8380);m.ram.fill(0,...r.allocations.backing_attributes);const oldPi=(n*7+11)%j.palette.length,sourcePi=(n*13+3)%j.palette.length,old=j.palette[oldPi],source=j.palette[sourcePi];const oldBits=Array.from({length:8},(_,y)=>(n*17+y*41)&255),srcBits=Array.from({length:8},(_,y)=>(n*29+y*13)&255),row=2,col=10,p=off(row*8)+col,cell=row*32+col;
 m.ram[0x7800+cell]=oldPi&255;m.ram[0x8100+cell]=0x20|((oldPi>>8)<<2);m.ram[0x7e00+cell]=0x81;m.ram[ctx+24]=33;m.ram[ctx+25]=0;m.ram[ctx+4]=(cache+3)&255;m.ram[ctx+5]=(cache+3)>>8;m.ram.set([1,1,1,sourcePi&255,sourcePi>>8,0,...srcBits],cache);m.ram[0x8eb1]=0;m.ram[0x8ebf]=0xa6;m.ram[r.clock_flags[0]+13]=0;
 for(let y=0;y<8;y++)m.ram[0xa600+p+y*256]=oldBits[y];call([0x8cfd,0x8d65,0x8dd3,0x8e29][flip],{b:row,c:col,d:1,e:1,h:(cache+5)>>8,l:(cache+5)&255});
 for(let y=0;y<8;y++){const sy=flip&2?7-y:y,sb=flip&1?rev(srcBits[sy]):srcBits[sy],want=blend(oldBits[y],old[y],sb,source[sy]);assert.equal(m.ram[0xa600+p+y*256],want[0],JSON.stringify({n,flip,y,oldPi,sourcePi,kind:'bits'}));call(0x0206,{h:(0x4000+p+y*256)>>8,l:p&255});assert.equal(m.cpu.a,want[1],JSON.stringify({n,flip,y,oldPi,sourcePi,kind:'attrs'}));}
 assert.equal(m.ram[0x7e00+cell],0x81);assert.equal(m.ram[r.clock_flags[0]+13],0);assert.equal(m.ram[ws+2],0);cells++;
}
// Fully covered foreground cells must avoid decoding/drawing another rear layer.
let occlusionCases=0;for(const [attr,bits] of [[7,255],[56,0],[15,85]]){
 m.ram.set(initial);call(c.code+3);m.ram.fill(0,0x8100,0x8380);m.ram.fill(0,0x7e00,0x8080);
 const row=2,col=10,cell=row*32+col,p=off(row*8)+col;m.ram.set(Array(8).fill(attr),ws+24);call(sy.find_pattern);const slot=m.cpu.a;
 m.ram[0x7800+cell]=slot;m.ram[0x8100+cell]=0x30;m.ram[0x7e00+cell]=0x81;m.ram[ctx+24]=33;m.ram[ctx+25]=0;m.ram[ctx+4]=(cache+3)&255;m.ram[ctx+5]=(cache+3)>>8;m.ram.set([1,1,1,0,0,0,...Array(8).fill(170)],cache);m.ram[0x8eb1]=0;m.ram[0x8ebf]=0xa6;
 for(let y=0;y<8;y++)m.ram[0xa600+p+y*256]=bits;
 const paint=()=>call(0x8cfd,{b:row,c:col,d:1,e:1,h:(cache+5)>>8,l:(cache+5)&255});paint();assert(m.ram[0x8100+cell]&64,'Opaque output marker missing');
 let lookups=0;const read=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&a===k.stock_colour)lookups++;return read(a);};paint();m.bus.read=read;assert.equal(lookups,0,'Hidden rear frame still resolved');for(let y=0;y<8;y++)assert.equal(m.ram[0xa600+p+y*256],bits);occlusionCases++;
}
const result={passed:true,level:5,rows,cells,paletteCases,occlusionCases,allFourFlips:true,foregroundOwnerPreserved:true,palettePoolOverflows:0,romWrites:f.romWrites,scope:'Actual native painters/overlap hook and clean attribute reader vs independent TAP pair-rule reference; runtime composition and timing checked separately'};fs.writeFileSync(out+'/overlap_validation.json',JSON.stringify(result,null,2));console.log(result);
