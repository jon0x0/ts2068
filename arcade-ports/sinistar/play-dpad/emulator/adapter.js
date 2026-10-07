// Sinistar cartridge personalization integration around TSRun's live public modules.
// Upstream: https://github.com/josef-jelinek/TSRun
const upstream=new URL('../tsrun/', import.meta.url).href;
const frameMs=1000*58688/3528000;
function notify(type,message){window.parent.postMessage({type,message},location.origin);}
async function resource(path,binary=false){
  const response=await fetch(path);
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
    resource('../assets/sinistar.dck',true),
    resource(upstream+'screen.vert.glsl'),resource(upstream+'screen.frag.glsl')]);
  if(rom0.length!==16384||rom1.length!==8192)throw new Error('Unexpected TS2068 system ROM sizes.');
  machine.homeRom.set(rom0);machine.exRom.set(rom1);
  const cartError=cpu.insertDock(machine,cartridge);
  if(cartError)throw new Error(cartError);
  cpu.resetMachine(machine);
  let gfx=null;
  await new Promise((resolve,reject)=>video.initScreen(canvas,{vert,frag},(err,value)=>{
    if(err||!value){reject(new Error(err||'WebGL2 unavailable'));notify('sinistar-error',err);return;}
    gfx=value;video.setCrt(gfx,false);resolve();
  }));
  const sfx=await new Promise((resolve,reject)=>sound.initSound(1000/frameMs,(err,value)=>{
    if(err||!value)reject(new Error(err||'Web Audio unavailable'));else resolve(value);
  }));
  const output=sfx.context.createGain();
  sfx.node.disconnect();sfx.node.connect(output);output.connect(sfx.context.destination);
  cpu.setSoundRate(machine,sfx.context.sampleRate);cpu.enableSound(machine,true);sound.setSoundStereo(sfx,false);
  let last=0,carry=frameMs,started=false,touch=255,lastState='',paused=false,soundEnabled=true;
  const held=new Map(),releases=new Map();
  function step(){
    cpu.runFrame(machine);
    const chunk=cpu.takeAudio(machine);
    if(chunk.n>0&&(sound.soundIsRunning(sfx)||sound.soundWantsFrame(sfx)))sound.pushSound(sfx,chunk);
  }
  function frame(now){
    requestAnimationFrame(frame);
    pads.pollJoysticks(joystick);
    // Sinistar uses native joystick 1 and fire bit 7.
    joystick[0]&=touch;
    if(!last)last=now;
    carry+=Math.min(80,now-last);last=now;
    let ran=0;
    if(paused)carry=0;
    while(!paused&&carry>=frameMs&&ran<4){step();carry-=frameMs;ran++;}
    if(!paused&&started&&sound.soundIsRunning(sfx)&&sound.soundWantsFrame(sfx)&&ran<4){step();carry=Math.max(carry,0)-frameMs;}
    video.drawScreen(gfx,machine.pixels);
    const state={paused,lives:machine.ram[0x7838],bombs:machine.ram[0x7826],attract:!!machine.ram[0x5e7b],muted:!!machine.ram[0x5e6e],fast:!!machine.ram[0x5bb1],bounce:!machine.ram[0x5c2b]};
    const encoded=JSON.stringify(state);if(encoded!==lastState){lastState=encoded;notify('sinistar-state',state);}
  }
  window.sinistar={
    setSound(on){soundEnabled=on;output.gain.value=on&&!paused?1:0;this.start();},
    setPaused(on){
      paused=on;this.release();carry=0;last=0;sound.resetSound(sfx);
      output.gain.value=soundEnabled&&!paused?1:0;
      if(!paused)this.start();
    },
    setCrt(on){video.setCrt(gfx,on);},
    key(event,down){
      event.preventDefault();if(paused)return;this.start();
      if(down){clearTimeout(releases.get(event.code));releases.delete(event.code);if(!held.has(event.code))held.set(event.code,performance.now());keys.handleKeyDown(kbd,event);}
      else {const delay=Math.max(0,80-(performance.now()-(held.get(event.code)??0)));releases.set(event.code,setTimeout(()=>{keys.handleKeyUp(kbd,event);held.delete(event.code);releases.delete(event.code);},delay));}
    },
    contacts(value){if(paused)return;touch=value;this.start();},
    release(){touch=255;for(const timer of releases.values())clearTimeout(timer);releases.clear();held.clear();keys.handleBlur(kbd);},
    start(){started=true;sound.resumeSound(sfx);return true;},
    press(code){
      if(paused)return;this.start();const event={code,preventDefault(){},repeat:false};
      keys.handleKeyDown(kbd,event);setTimeout(()=>keys.handleKeyUp(kbd,event),120);
    },
    reset(){this.release();sound.resetSound(sfx);cpu.resetMachine(machine);},
  };
  const gameKeys=new Set(['KeyQ','KeyA','KeyO','KeyP','Space','Enter','KeyB','KeyR','KeyS','KeyC','KeyF']);
  window.addEventListener('keydown',event=>{if(gameKeys.has(event.code)&&!event.ctrlKey&&!event.altKey&&!event.metaKey)window.sinistar.key(event,true);});
  window.addEventListener('keyup',event=>{if(gameKeys.has(event.code))window.sinistar.key(event,false);});
  window.addEventListener('blur',()=>window.sinistar.release());
  window.addEventListener('pointerdown',()=>window.sinistar.start());
  window.addEventListener('resize',()=>video.resizeScreen(gfx));
  requestAnimationFrame(frame);
  notify('sinistar-ready');
}
boot().catch(error=>{
  console.error(error);
  const message='TSRun could not start. '+error.message;
  document.getElementById('error').hidden=false;document.getElementById('error').textContent=message;
  notify('sinistar-error',message);
});
