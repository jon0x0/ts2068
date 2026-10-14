// Crown integration; the bundled TSRun modules remain unmodified.
const base=new URL('./tsrun/',import.meta.url);
const frameMs=1000*58688/3528000;
async function resource(url,binary=false){const r=await fetch(url);if(!r.ok)throw Error(`${url}: HTTP ${r.status}`);return binary?new Uint8Array(await r.arrayBuffer()):r.text();}
async function boot(){
  const [cpu,video,sound,keys,pads]=await Promise.all(['machine.js','screen.js','sound.js','keyboard.js','joystick.js'].map(p=>import(new URL(p,base))));
  const matrix=new Uint8Array(8),joystick=new Uint8Array(2);
  const kbd=keys.initKeyboard(document.querySelector('#keyboard'),matrix);pads.initJoysticks(joystick);
  const machine=cpu.createMachine(matrix,joystick);
  const [home,exrom,cart,vert,frag]=await Promise.all([resource(new URL('roms/ts2068-0.rom',base),true),resource(new URL('roms/ts2068-1.rom',base),true),resource('../TheCrown.dck',true),resource(new URL('screen.vert.glsl',base)),resource(new URL('screen.frag.glsl',base))]);
  machine.homeRom.set(home);machine.exRom.set(exrom);
  const err=cpu.insertDock(machine,cart);if(err)throw Error(err);cpu.resetMachine(machine);
  const gfx=await new Promise((resolve,reject)=>video.initScreen(document.querySelector('#screen'),{vert,frag},(err,v)=>err?reject(Error(err)):resolve(v)));
  video.setCrt(gfx,false);
  const sfx=await new Promise((resolve,reject)=>sound.initSound(1000/frameMs,(err,v)=>err?reject(Error(err)):resolve(v)));
  cpu.setSoundRate(machine,sfx.context.sampleRate);cpu.enableSound(machine,true);sound.setSoundStereo(sfx,false);
  let touch=255,last=0,carry=frameMs,muted=false;
  const event=code=>({code,repeat:false,preventDefault(){}});
  window.crown={
    introActive(){return machine.ram[0xFAC0]===1;},
    physicalKey(event,down){if(!muted)sound.resumeSound(sfx);(down?keys.handleKeyDown:keys.handleKeyUp)(kbd,event);},
    key(code,down){if(!muted)sound.resumeSound(sfx);(down?keys.handleKeyDown:keys.handleKeyUp)(kbd,event(code));},
    contacts(value){touch=value;if(!muted)sound.resumeSound(sfx);},
    release(){touch=255;keys.handleBlur(kbd);},
    reset(){this.release();sound.resetSound(sfx);cpu.resetMachine(machine);},
    audio(){muted=!muted;sfx.context[muted?'suspend':'resume']();return !muted;},
  };
  function frame(now){requestAnimationFrame(frame);pads.pollJoysticks(joystick);joystick[0]&=touch;
    if(!last)last=now;carry+=Math.min(80,now-last);last=now;
    for(let n=0;carry>=frameMs&&n<4;n++){cpu.runFrame(machine);carry-=frameMs;const chunk=cpu.takeAudio(machine);if(chunk.n>0&&sound.soundIsRunning(sfx))sound.pushSound(sfx,chunk);}
    video.drawScreen(gfx,machine.pixels);
  }
  function resize(){
    video.resizeScreen(gfx);
    if(document.querySelector('#player').matches(':fullscreen')){
      const slot=document.querySelector('.screen-slot'),canvas=document.querySelector('#screen');
      const scale=Math.min(slot.clientWidth/640,slot.clientHeight/480);
      canvas.style.width=`${640*scale}px`;canvas.style.height=`${480*scale}px`;
    }
  }
  window.addEventListener('resize',resize);
  window.addEventListener('crown-layout-change',()=>requestAnimationFrame(resize));
  document.addEventListener('fullscreenchange',()=>requestAnimationFrame(resize));
  resize();
  document.querySelector('#status').textContent='Ready · wait for PRESS ANY KEY, then press any key or tap a game button.';
  window.dispatchEvent(new Event('crown-ready'));requestAnimationFrame(frame);
}
boot().catch(e=>{document.querySelector('#status').textContent='TSRun could not start: '+e.message;console.error(e);});
