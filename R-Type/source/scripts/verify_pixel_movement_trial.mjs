import fs from'node:fs';import vm from'node:vm';import assert from'node:assert/strict';
const out=new URL('../build/diagnostics/pixel_movement_trial/',import.meta.url),html=fs.readFileSync(new URL('index.html',out),'utf8'),code=html.match(/<script>([\s\S]*)<\/script>/)[1];
const handlers={},elements={screen:{getContext:()=>({putImageData(){},fillRect(){}}),addEventListener:(name,fn)=>handlers[name]=fn,focus(){}},mode:{},reset:{},state:{}};
const context=vm.createContext({document:{getElementById:id=>elements[id]},ImageData:class{constructor(w,h){this.data=new Uint8ClampedArray(w*h*4)}},performance:{now:()=>0},requestAnimationFrame(){}});vm.runInContext(code,context);
const run=s=>vm.runInContext(s,context);function key(code,down){handlers[down?'keydown':'keyup']({code,preventDefault(){}})}
run('reset()');key('ArrowRight',true);run('tick()');assert.equal(run('x'),41);assert.equal(run('x&7'),1);key('ArrowRight',false);
key('ArrowUp',true);run('tick()');assert.equal(run('y'),79);key('ArrowUp',false);
run('reset()');key('KeyP',true);key('KeyP',false);run('tick()');assert.equal(run('shots.length'),1,'Queued short tap lost');assert.equal(run('shots[0].y'),84);
run('reset()');key('KeyP',true);run('for(let i=0;i<15;i++)tick()');key('KeyP',false);run('tick()');assert.equal(run('shots[0].power'),3,'Charge lost');
run('reset()');key('ArrowLeft',true);run('for(let i=0;i<100;i++)tick()');assert.equal(run('x'),8);key('ArrowLeft',false);
run('reset();legacy=true');key('ArrowRight',true);run('tick()');assert.equal(run('x'),48);key('ArrowRight',false);
run('reset();legacy=false');key('ArrowDown',true);run('for(let i=0;i<150;i++)tick()');assert(run('y')<=152);assert(!run('collision(x,y,pose)'));key('ArrowDown',false);
run('render()');const report={passed:true,checks:['one-pixel X/Y','phase selection','queued short fire release','charged shot','left clamp','coarse comparison','swept terrain collision','render execution'],scope:'Headless browser-prototype logic, not a native Z80 movement integration'};fs.writeFileSync(new URL('validation.json',out),JSON.stringify(report,null,2));console.log(report);
