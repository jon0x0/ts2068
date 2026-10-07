const frame=document.querySelector('#emulator');
const api=()=>frame.contentWindow.sinistar;
let ready=false,direction=255,firing=false,touchEnabled=true;
const send=()=>{if(ready)api().contacts(direction & (firing?0x7f:255));};
const release=()=>{direction=255;firing=false;bombId=null;padId=null;fireId=null;clearTimeout(fireRelease);document.querySelector('#knob').style.transform='';if(ready)api().release();};
const config=await (await fetch(new URL('./cartridge-controls.json',import.meta.url))).json();
for(const action of config.actions){
  const button=document.createElement('button');button.textContent=action.label;button.id=action.id;button.disabled=true;
  button.addEventListener('click',()=>api()?.press(action.code));
  document.getElementById(action.placement).append(button);
}
window.addEventListener('message',event=>{
  if(event.origin!==location.origin||event.source!==frame.contentWindow)return;
  if(event.data.type==='sinistar-ready'){ready=true;document.querySelectorAll('button').forEach(b=>b.disabled=false);document.querySelector('#status').textContent='';}
  if(event.data.type==='sinistar-error')document.querySelector('#status').textContent=event.data.message;
  if(event.data.type==='sinistar-state'){const s=event.data.message;
    for(const [id,on] of [['fast',s.fast],['bounce',s.bounce],['pause',s.paused]])document.getElementById(id).setAttribute('aria-pressed',String(on));
    document.querySelector('#pause').textContent=s.paused?'Resume':'Pause';
    for(const id of ['fast','bounce','start','restart'])document.getElementById(id).disabled=s.paused;
    document.querySelector('main').classList.toggle('paused',s.paused);
document.querySelector('#status').textContent=`${s.attract?'Attract mode — press Fire or Enter to start':s.lives?'Lives '+s.lives:'Press Fire or Enter to start'} · Bombs ${s.bombs} · Game sound ${s.muted?'OFF (S)':'ON'} · Fast mode ${s.fast?'ON':'OFF'} · Bounce ${s.bounce?'ON':'OFF'}`;}
});
const pad=document.querySelector('#pad'),fire=document.querySelector('#fire');
let padId=null,fireId=null,bombId=null,fireRelease=null;
function move(event){const r=pad.getBoundingClientRect(),x=(event.clientX-r.left-r.width/2)/(r.width/2),y=(event.clientY-r.top-r.height/2)/(r.height/2);direction=Math.hypot(x,y)<(config.touchPad?.deadZone ?? .45)?255:[0xf7,0xf5,0xfd,0xf9,0xfb,0xfa,0xfe,0xf6][(Math.round(Math.atan2(y,x)/(Math.PI/4))+8)%8];const length=Math.max(1,Math.hypot(x,y));document.querySelector('#knob').style.transform=`translate(${x/length*r.width*.24}px,${y/length*r.height*.24}px)`;send();}
pad.addEventListener('pointerdown',e=>{if(!ready||!touchEnabled||padId!==null)return;e.preventDefault();padId=e.pointerId;pad.setPointerCapture(padId);move(e);});
pad.addEventListener('pointermove',e=>{if(e.pointerId===padId)move(e);});
fire.addEventListener('pointerdown',e=>{if(!ready||!touchEnabled||fireId!==null)return;e.preventDefault();clearTimeout(fireRelease);fireId=e.pointerId;fire.setPointerCapture(fireId);firing=true;send();});
const bomb=document.querySelector('#bomb');
const bombKey={code:'KeyB',repeat:false,preventDefault(){}};
bomb.addEventListener('pointerdown',e=>{if(!ready||!touchEnabled||bombId!==null)return;e.preventDefault();bombId=e.pointerId;bomb.setPointerCapture(bombId);api().key(bombKey,true);});
for(const name of ['pointerup','pointercancel','lostpointercapture']){
 pad.addEventListener(name,e=>{if(e.pointerId===padId){padId=null;direction=255;document.querySelector('#knob').style.transform='';send();}});
 fire.addEventListener(name,e=>{if(e.pointerId===fireId){fireId=null;fireRelease=setTimeout(()=>{firing=false;send();},80);}});
 bomb.addEventListener(name,e=>{if(e.pointerId===bombId){bombId=null;api().key(bombKey,false);}});
}
for(const name of ['blur','pagehide'])window.addEventListener(name,release);
document.addEventListener('visibilitychange',()=>{if(document.hidden)release();});
window.addEventListener('resize',release);
document.addEventListener('fullscreenchange',release);
document.querySelector('#fullscreen').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.querySelector('main').requestFullscreen();}catch{document.querySelector('#status').textContent='Fullscreen is unavailable in this browser.';}});

const gameKeys=new Set(['KeyQ','KeyA','KeyO','KeyP','Space','Enter','KeyB','KeyR','KeyS','KeyC','KeyF']);
window.addEventListener('keydown',e=>{if(ready&&!e.ctrlKey&&!e.altKey&&!e.metaKey&&gameKeys.has(e.code)&&!(['Space','Enter'].includes(e.code)&&e.target.closest?.('button,a')))api().key(e,true);});
window.addEventListener('keyup',e=>{if(ready&&gameKeys.has(e.code))api().key(e,false);});

// Cartridge-owned touch switch; keyboard and physical gamepads remain active.
const touchToggle=document.createElement('button');
touchToggle.id='touch-toggle';touchToggle.innerHTML='Virtual<br>DPad';
touchToggle.title='Show or hide the on-screen D-pad and Fire button';
touchToggle.setAttribute('aria-label','On-screen touch controls');
touchToggle.setAttribute('aria-pressed','true');
document.querySelector('#fullscreen').after(touchToggle);
touchToggle.addEventListener('click',()=>{
  touchEnabled=!touchEnabled;
  // Drop touch contacts only; do not interrupt held physical keyboard keys.
  direction=255;firing=false;
  clearTimeout(fireRelease);if(bombId!==null&&ready)api().key(bombKey,false);bombId=null;
  document.querySelector('#knob').style.transform='';
  const oldPad=padId,oldFire=fireId;padId=null;fireId=null;
  if(oldPad!==null&&pad.hasPointerCapture(oldPad))pad.releasePointerCapture(oldPad);
  if(oldFire!==null&&fire.hasPointerCapture(oldFire))fire.releasePointerCapture(oldFire);
  if(ready)api().contacts(255);
  document.querySelector('main').classList.toggle('touch-off',!touchEnabled);
  touchToggle.setAttribute('aria-pressed',String(touchEnabled));
});

const crtToggle=document.createElement('button');
crtToggle.id='crt-toggle';crtToggle.textContent='CRT';crtToggle.disabled=!ready;
crtToggle.title='Enable or disable CRT scanlines';
crtToggle.setAttribute('aria-pressed','false');
document.querySelector('header').append(crtToggle);
let crtEnabled=false;
crtToggle.addEventListener('click',()=>{
  crtEnabled=!crtEnabled;api().setCrt(crtEnabled);
  crtToggle.setAttribute('aria-pressed',String(crtEnabled));
});

const fullscreenToggle=document.querySelector('#fullscreen');
fullscreenToggle.setAttribute('aria-pressed',String(!!document.fullscreenElement));
document.addEventListener('fullscreenchange',()=>fullscreenToggle.setAttribute('aria-pressed',String(!!document.fullscreenElement)));

// Mute only the output; keep emulation and the audio queue running normally.
const soundToggle=document.createElement('button');
soundToggle.id='sound-toggle';soundToggle.textContent='Audio On';soundToggle.disabled=!ready;
soundToggle.title='Mute browser output; the native S key controls game sound separately';
soundToggle.setAttribute('aria-pressed','true');
document.querySelector('header').append(soundToggle);
let soundEnabled=true;
soundToggle.addEventListener('click',()=>{
  soundEnabled=!soundEnabled;api().setSound(soundEnabled);
  soundToggle.textContent=soundEnabled?'Audio On':'Audio Off';
  soundToggle.setAttribute('aria-pressed',String(soundEnabled));
});

// Session options stay away from the active thumb controls.
for(const [id,label,code,on] of [['fast','Fast mode','KeyF',false],['bounce','Bounce','KeyC',true],['pause','Pause',null,false]]){
  const button=document.createElement('button');button.id=id;button.textContent=label;
  button.disabled=!ready;button.setAttribute('aria-pressed',String(on));
  button.addEventListener('click',()=>{
    if(code)api().press(code);
    else {release();api().setPaused(button.getAttribute('aria-pressed')!=='true');}
  });
  document.querySelector('#session-actions').append(button);
}
