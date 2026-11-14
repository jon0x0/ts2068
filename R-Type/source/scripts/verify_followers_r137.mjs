import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api,root,z}from'./r16_test_machine.mjs';import{demandFixture}from'./boss_motion_fixture_r137.mjs';
const O=path.join(root,'build/fullgame/l4_openings_r137'),C=JSON.parse(fs.readFileSync(path.join(O,'l4_shared_contract.json'))),walk=JSON.parse(fs.readFileSync(path.join(O,'walker_runtime.json'))),w=walk.find(v=>v.level===4),meta=JSON.parse(fs.readFileSync(path.join(O,'generic_manifest.json'))).find(v=>v.level===4),region=fs.readFileSync(path.join(O,'level04_region.bin')),expected=fs.readFileSync(path.join(O,'L4_runtime_art.bin')),cache=fs.readFileSync(path.join(O,'L4_expected_cache.bin'));const{m,joy,controller:c}=demandFixture();let last=-1,boot=-1,u=0,loaded=0,preloaded=0,after=0;const seen=new Set(),rd=m.bus.read;
m.bus.read=a=>{if(a===m.cpu.pc&&m.stepAdded===0&&last!==m.tstates){last=m.tstates;
 if(c.region===3&&a===w.extension.load_new_art&&!m.dock[7][0x3f0]){const got=Buffer.from(m.dock[5].slice(C.external_source-0xa000,C.external_end-0xa000)),want=region.subarray(C.external_source,C.external_end);if(!got.equals(want)){const d=[];for(let k=0;k<got.length;k++)if(got[k]!==want[k])d.push([k+C.external_source,want[k],got[k]]);throw Error('External source changed '+JSON.stringify(d.slice(0,20)));}}if(c.region===3&&a===w.extension.art_after_preload){assert(Buffer.from(m.ram.slice(C.aux_home_backup,C.aux_home_backup+C.aux_bytes)).equals(region.subarray(C.aux_file_source,C.aux_file_source+C.aux_bytes)),'Aux packet must be present in HOME source backup');if(!Buffer.from(m.dock[6].slice(0,cache.length)).equals(cache)){const d=[];for(let i=0;i<cache.length;i++)if(m.dock[6][i]!==cache[i])d.push([i,cache[i],m.dock[6][i]]);console.log({cacheDiff:d.length,first:d.slice(0,12),map:m.portF4,pretab:region.subarray(C.pretab,C.pretab+9).toString('hex')});throw Error('Boss cache differs');}preloaded++;}
 if(c.region===3&&a===0xa19d){assert(Buffer.from(m.dock[5].slice(C.rawbase-0xa000,C.rawend-0xa000)).equals(expected),'All live sprite art exact after both streams expand');loaded++;}
 if(a===0x8634)m.ram[0x91f2]=201;
 if(a===0x94f1&&rd(0x7aa4)>0){u++;m.dock[3][0x1a98]=255;}
 if(c.region===3&&a===w.extension.hook_done)seen.add(rd(0xdf3e));
 if(a===0x868c&&u===500){fs.writeFileSync(path.join(O,'L4_ordinary_500.home.bin'),m.ram);}
 }return rd(a);};
for(let f=0;f<16000&&(u<160);f++){m.keyMatrix.fill(31);joy.fill(255);if(c.booted&&m.ram[0x5bc2]===1)m.ram[0x5bc4]=0;if(c.booted&&boot<0)boot=f;if(boot<0&&f>8&&m.ram[0xd610]===1)m.keyMatrix[3]&=~8;if(boot>=0&&f-boot>=800&&f%60<12&&rd(0x7aa4)<2)joy[0]=127;if(rd(0x7aa4)>=2&&u>100&&f%24<8)joy[0]=127;api.runFrame(m);assert(!c.fatalSeen);}
console.log({loaded,preloaded,u,boot,region:c.region,pc:m.cpu.pc,map:m.portF4,game:rd(0x7aa4)});assert(loaded&&preloaded&&u>=160);m.dock[3].set([254,2,254,4,254,8,254,16,127,1,127,2],0x1780);m.bus.read=rd;



function invoke(pc){m.portF4=9;Object.assign(m.cpu,{pc,sp:0xffe0,iff1:false,iff2:false});m.ram[0xffe0]=0;m.ram[0xffe1]=0xf0;let steps=0;while(m.cpu.pc!==0xf000&&steps++<300000)z.runZ80(m.cpu,m.bus,1,m);assert(steps<300000,'native call hung');}
const q=m.dock[3];const saved={ram:Buffer.from(m.ram),dock:m.dock.map(b=>Buffer.from(b))};
for(let k=0;k<4;k++){m.ram[0x83da+k*2]=4;m.ram[0x83db+k*2]=10;}
const history=[];for(let k=0;k<8;k++){q[0x1a89]=k;q[0x1aa1]=4+k*2;q[0x1aa2]=10;invoke(0x99da);history.push(m.cpu.e);if(k>0)assert.equal(m.cpu.e,4+(k-1)*2+1,'one-update Bits history');}
m.ram.set(saved.ram);m.dock.forEach((b,i)=>b.set(saved.dock[i]));q[0x1aa8]=6;q[0x1aa9]=20;q[0x1aaa]=15;q[0x1abe]=1;q[0x1aa3]=0;q[0x1aab]=0;q[0x1aae]=0;q[0x1aa1]=4;q[0x1aa2]=10;
const recall=[];for(let k=0;k<4;k++){q[0x1a89]=k;invoke(0x95f6);recall.push([...q.slice(0x1aa8,0x1aab)]);}
assert(recall.slice(1).every((p,i)=>p[1]!==recall[i][1]||p[2]!==recall[i][2]),'Recall must move on each game update');
fs.writeFileSync(path.join(O,'follower_validation.json'),JSON.stringify({passed:true,history,recall,scope:'Actual native Z80 routines after cold L4 startup; controlled follow and recall fixtures, not hardware'},null,2));console.log({history,recall});
