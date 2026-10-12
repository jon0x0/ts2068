// Measure FE output envelopes and pitch from execution of the real RAM reporter.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const up=path.resolve('../TSRun'),api=await import(pathToFileURL(path.join(up,'machine.js')));
const cart=fs.readFileSync('build/diagnostic-v02.dck'),sym=Object.fromEntries([...fs.readFileSync('build/symbols.txt','utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);m.portF4=1;m.portFF=64;m.cpu.pc=sym.fault_draw_done;m.cpu.d=6;m.cpu.e=2;m.cpu.sp=0xbeef;m.cpu.iff1=false;
const read=m.bus.read,io=m.bus.ioWrite,stop={},tones=[],groups=[];let active=null,last=0,done=false;
m.bus.read=a=>{if(a===m.cpu.pc){assert.equal(m.cpu.sp,0xbeef);if(a===sym.pulse_group)groups.push(m.cpu.c);if(a===sym.report_next){done=true;throw stop;}}return read(a);};
m.bus.ioWrite=(p,v)=>{if((p&255)===254){if(v===23&&last===0){active={start:m.tstates,edges:[]};tones.push(active);}if(active&&v!==0&&active.edges.length<3)active.edges.push(m.tstates);if(v===0&&active){active.end=m.tstates;active=null;}last=v;}io(p,v);};
try{for(let frame=0;frame<2000;frame++)api.runFrame(m);}catch(e){if(e!==stop)throw e;}
assert.ok(done);assert.equal(tones.length,11);assert.deepEqual(groups,[2,1,6,5,4,3,2,1,2,1]);
const seconds=t=>t/api.cpuHz;
const durations=tones.map(t=>seconds(t.end-t.start)),gaps=tones.slice(1).map((t,i)=>seconds(t.start-tones[i].end));
assert.ok(durations[0]>1.15&&durations[0]<1.22);assert.ok(durations.slice(1).every(t=>t>.58&&t<.61));
assert.ok(gaps[0]>.88&&gaps[0]<.91);
assert.ok(gaps.slice(1).every((t,i)=>[1,7].includes(i)?t>1.28&&t<1.32:t>.40&&t<.42));
const pitches=tones.map(t=>api.cpuHz/(t.edges[2]-t.edges[0]));
assert.ok(pitches[0]>140&&pitches[0]<160);
assert.ok(pitches.slice(1).every(p=>p>420&&p<440&&p/pitches[0]>2.7),'clear sync/count pitch separation');
const record={image_sha256:createHash('sha256').update(cart).digest('hex'),result:'PASS',configuration:'TSRun FE output timestamps; U18/D5 report2/6/2; nominal3.528MHz',durations_seconds:durations,gaps_seconds:gaps,pitches_hz:tones.map(t=>api.cpuHz/(t.edges[2]-t.edges[0])),limitations:['Model instruction timing; actual speaker/output and clock require hardware observation']};
fs.writeFileSync('build/fault-timing-verification.json',JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify(record));
