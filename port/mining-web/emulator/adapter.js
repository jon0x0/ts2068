// Audio Lab integration around TSRun's live public modules.
// Upstream: https://github.com/josef-jelinek/TSRun
const upstream='/tsrun/';
const frameMs=1000*58688/3528000;
function notify(type,message){window.parent.postMessage({type,message},location.origin);}
async function resource(path,binary=false){
  const response=await fetch(path,{cache:'no-store'});
  if(!response.ok)throw new Error(`Could not load ${path}: HTTP ${response.status}`);
  return binary?new Uint8Array(await response.arrayBuffer()):response.text();
}
async function boot(){
  const [cpu,video,sound,keys,pads]=await Promise.all(
    ['machine.js','screen.js','sound.js','keyboard.js','joystick.js'].map(path=>import(upstream+path)));
  const canvas=document.getElementById('screen');
  const matrix=new Uint8Array(8),joystick=new Uint8Array(2);
  const kbd=keys.initKeyboard(document.getElementById('keyboard'),matrix);
  pads.initJoysticks(joystick);
  const machine=cpu.createMachine(matrix,joystick);
  const [rom0,rom1,cartridge,vert,frag]=await Promise.all([
    resource(upstream+'roms/ts2068-0.rom',true),resource(upstream+'roms/ts2068-1.rom',true),
    resource('../../build/sinistar-mining.dck',true),
    resource(upstream+'screen.vert.glsl'),resource(upstream+'screen.frag.glsl')]);
  if(rom0.length!==16384||rom1.length!==8192)throw new Error('Unexpected TS2068 system ROM sizes.');
  machine.homeRom.set(rom0);machine.exRom.set(rom1);
  const cartError=cpu.insertDock(machine,cartridge);
  if(cartError)throw new Error(cartError);
  cpu.resetMachine(machine);
  let gfx=null;
  await new Promise((resolve,reject)=>video.initScreen(canvas,{vert,frag},(err,value)=>{
    if(err||!value){reject(new Error(err||'WebGL2 unavailable'));notify('audio-lab-error',err);return;}
    gfx=value;video.setCrt(gfx,false);resolve();
  }));
  const sfx=await new Promise((resolve,reject)=>sound.initSound(3528000/58688,(err,value)=>{
    if(err||!value)reject(new Error(err||'Web Audio unavailable'));else resolve(value);
  }));
  cpu.setSoundRate(machine,sfx.context.sampleRate);cpu.enableSound(machine,true);sound.setSoundStereo(sfx,false);
  let last=0,carry=frameMs,started=false,lastState="";
  function step(){
    cpu.runFrame(machine);
    const chunk=cpu.takeAudio(machine);
    if(chunk.n>0&&(sound.soundIsRunning(sfx)||sound.soundWantsFrame(sfx)))sound.pushSound(sfx,chunk);
  }
  function frame(now){
    requestAnimationFrame(frame);
    pads.pollJoysticks(joystick);
    if(!last)last=now;
    carry+=Math.min(80,now-last);last=now;
    let ran=0;
    while(carry>=frameMs&&ran<4){step();carry-=frameMs;ran++;}
    if(started&&sound.soundIsRunning(sfx)&&sound.soundWantsFrame(sfx)&&ran<4){step();carry=Math.max(carry,0)-frameMs;}
    video.drawScreen(gfx,machine.pixels);
    const planetRecords=[...Array.from({length:8},(_,i)=>0x79b0+i*10),...Array.from({length:8},(_,i)=>0x7db0+i*10),0x58b4];
    const score=150*machine.ram[0x5c24]+200*machine.ram[0x783b]+500*Math.min(12,machine.ram[0x78ac])+(machine.ram[0x78ac]>=13?15000:0);
    const state={score,soundEnabled:started&&machine.ram[0x5e6e]===0,soundStarted:started,attract:machine.ram[0x5e7b]!==0,fastEnabled:machine.ram[0x5bb1]!==0,fastActive:machine.ram[0x5bb2]!==0,planetoids:Number(machine.ram[0x7810]!==0)+planetRecords.filter(a=>machine.ram[a+7]!==0).length,status:machine.ram[0x782f],lives:machine.ram[0x7838],protected:machine.ram[0x7839]>0,crystals:machine.ram[0x783b],bombHits:machine.ram[0x78ac],awakeDone:machine.ram[0x78c1],mouth:machine.ram[0x78bd],built:machine.ram[0x78bc],assembly:machine.ram[0x78b7],worker:machine.ram[0x78b3],mission:machine.ram[0x78b2],pickups:machine.ram[0x78b4],deliveries:machine.ram[0x78b5],hits:machine.ram[0x7827],collected:machine.ram[0x7826],released:machine.ram[0x782c],richter:machine.ram[0x7811],mass:machine.ram[0x7812],alive:machine.ram[0x7810],manual:machine.ram[0x78a4]};
    const encoded=JSON.stringify(state);if(encoded!==lastState){lastState=encoded;notify('mining-state',state);}

  }
  window.audioLab={
    start(){started=true;sound.resumeSound(sfx);window.focus();canvas.focus();return true;},
    toggleSound(){if(!started){this.start();return;}this.press("KeyS");},
    press(code){
      this.start();const event={code,preventDefault(){},repeat:false};
      keys.handleKeyDown(kbd,event);setTimeout(()=>keys.handleKeyUp(kbd,event),120);
    },
    keyDown(event){if(event.code==="KeyS"&&event.repeat){event.preventDefault();return;}if(event.code==="KeyS"&&!started){event.preventDefault();this.start();return;}this.start();keys.handleKeyDown(kbd,event);},
    keyUp(event){keys.handleKeyUp(kbd,event);},
    reset(){keys.handleBlur(kbd);sound.resetSound(sfx);cpu.resetMachine(machine);this.start();},
  };
  window.addEventListener('keydown',event=>window.audioLab.keyDown(event));
  window.addEventListener('keyup',event=>window.audioLab.keyUp(event));
  window.addEventListener('blur',()=>keys.handleBlur(kbd));
  window.addEventListener('pointerdown',()=>window.audioLab.start());
  window.addEventListener('resize',()=>video.resizeScreen(gfx));
  requestAnimationFrame(frame);
  notify('audio-lab-ready');
}
boot().catch(error=>{
  console.error(error);
  const message='TSRun could not start. '+error.message;
  document.getElementById('error').hidden=false;document.getElementById('error').textContent=message;
  notify('audio-lab-error',message);
});
