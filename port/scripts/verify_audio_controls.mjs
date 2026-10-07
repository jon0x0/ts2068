import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const adapter=fs.readFileSync(path.join(root,'mining-web/emulator/adapter.js'),'utf8');
const events=[];
const sandbox={window:{focus(){}},canvas:{focus(){}},started:false,sfx:{},kbd:{},machine:{},
 sound:{resumeSound(){},resetSound(){}},cpu:{resetMachine(){}},
 keys:{handleKeyDown:(k,e)=>events.push(['down',e.code]),handleKeyUp:(k,e)=>events.push(['up',e.code]),handleBlur(){}},setTimeout:fn=>fn()};
vm.createContext(sandbox);
vm.runInContext(adapter.slice(adapter.indexOf('  window.audioLab={'),adapter.indexOf("  window.addEventListener('keydown'")),sandbox);
const api=sandbox.window.audioLab;
api.toggleSound();assert.equal(sandbox.started,true);assert.equal(events.length,0,'first click activates browser audio');
api.toggleSound();assert.deepEqual(events,[['down','KeyS'],['up','KeyS']],'button sends native S');
events.length=0;
api.keyDown({code:'KeyS',repeat:true,preventDefault(){}});assert.equal(events.length,0);
api.keyDown({code:'KeyS',repeat:false,preventDefault(){}});api.keyUp({code:'KeyS'});
assert.deepEqual(events,[['down','KeyS'],['up','KeyS']]);
const nodes={emulator:{contentWindow:{audioLab:api}},restart:{},sound:{setAttribute(k,v){this[k]=v;}},stats:{}};
const handlers={};const outer={document:{getElementById:id=>nodes[id]},location:{origin:'http://test'},window:{addEventListener:(n,fn)=>handlers[n]=fn}};
vm.createContext(outer);
const html=fs.readFileSync(path.join(root,'mining-web/index.html'),'utf8');vm.runInContext(html.split('<script>')[1].split('</script>')[0],outer);
for(const enabled of [true,false]){
 handlers.message({origin:'http://test',source:nodes.emulator.contentWindow,data:{type:'mining-state',message:{soundStarted:true,soundEnabled:enabled}}});
 assert.equal(nodes.sound.textContent,`Sound: ${enabled?'ON':'OFF'} (S)`);assert.equal(nodes.sound['aria-pressed'],String(enabled));
}
events.length=0;handlers.keydown({code:'KeyS',repeat:false,preventDefault(){}});handlers.keyup({code:'KeyS',preventDefault(){}});
assert.deepEqual(events,[['down','KeyS'],['up','KeyS']],'outer page forwards S');
const report={dck_sha256:createHash('sha256').update(fs.readFileSync(path.join(root,'build/sinistar-mining.dck'))).digest('hex'),buttonActivatesBrowserAudio:true,buttonSendsNativeToggle:true,keyboardForwarding:true,repeatIgnored:true,buttonReflectsNativeState:true};
fs.writeFileSync(path.join(root,'build/frontend-audio-controls-verification.json'),JSON.stringify(report,null,2));console.log(report);
