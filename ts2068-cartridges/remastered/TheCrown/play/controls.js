const buttons=[...document.querySelectorAll('[data-key],[data-contact]')];
const pad=document.querySelector('#pad'),knob=document.querySelector('#knob');
let direction=255,fire=false,padId=null,ready=false;
const held=new Map(),timers=new Set();
const startupHeld=new Set(),physicalHeld=new Set();
let startupAt=0,startupRelease=null;
const api=()=>window.crown;
let touchEnabled=true;
document.querySelector('#touch-toggle').addEventListener('click',e=>{
  release();
  touchEnabled=!touchEnabled;
  document.querySelector('#player').classList.toggle('touch-off',!touchEnabled);
  document.querySelector('#keyboard-guide').hidden=touchEnabled;
  e.currentTarget.textContent=touchEnabled?'Touch controls: On':'Touch controls: Off';
  e.currentTarget.setAttribute('aria-pressed',String(touchEnabled));
  document.querySelector('#player').focus({preventScroll:true});
  window.dispatchEvent(new Event('crown-layout-change'));
});
buttons.forEach(b=>b.disabled=true);
window.addEventListener('crown-ready',()=>{ready=true;buttons.forEach(b=>b.disabled=false);});
function send(){if(ready)api().contacts(direction&(fire?127:255));}
function release(){for(const t of timers)clearTimeout(t);timers.clear();clearTimeout(startupRelease);startupRelease=null;startupHeld.clear();physicalHeld.clear();held.clear();padId=null;direction=255;fire=false;knob.style.transform='';buttons.forEach(b=>b.classList.remove('pressed'));if(ready)api().release();}
function down(b,id){if(!ready||held.has(b))return;const key=b.dataset.key;held.set(b,{id,time:performance.now(),minimum:api().introActive()?400:140});b.classList.add('pressed');if(b.id==='start')document.querySelector('#status').textContent='Keyboard, DPad and gamepad active · Help lists game commands.';if(key)api().key(key,true);else{fire=true;send();}}
function up(b,id){const h=held.get(b);if(!h||h.id!==id)return;const end=()=>{timers.delete(timer);if(held.get(b)!==h)return;held.delete(b);b.classList.remove('pressed');if(b.dataset.key)api().key(b.dataset.key,false);else{fire=false;send();}};const timer=setTimeout(end,Math.max(0,h.minimum-(performance.now()-h.time)));timers.add(timer);}
for(const b of buttons){
  b.addEventListener('pointerdown',e=>{if(e.button!==0)return;e.preventDefault();b.setPointerCapture(e.pointerId);down(b,e.pointerId);});
  b.addEventListener('pointerup',e=>up(b,e.pointerId));
  b.addEventListener('pointercancel',release);b.addEventListener('lostpointercapture',e=>up(b,e.pointerId));
  b.addEventListener('keydown',e=>{if(e.code==='Space'||e.code==='Enter'){e.preventDefault();e.stopPropagation();down(b,'keyboard');}});
  b.addEventListener('keyup',e=>{if(e.code==='Space'||e.code==='Enter'){e.preventDefault();e.stopPropagation();up(b,'keyboard');}});
  b.addEventListener('contextmenu',e=>e.preventDefault());
}
function move(e){const r=pad.getBoundingClientRect();let x=(e.clientX-r.left-r.width/2)/(r.width/2),y=(e.clientY-r.top-r.height/2)/(r.height/2);const len=Math.hypot(x,y);if(len>1){x/=len;y/=len;}const masks=[8,10,2,6,4,5,1,9];direction=len<.22?255:255^masks[(Math.round(Math.atan2(y,x)/(Math.PI/4))+8)%8];knob.style.transform=`translate(${x*r.width*.28}px,${y*r.height*.28}px)`;send();}
pad.addEventListener('pointerdown',e=>{if(!ready||e.button!==0||padId!==null)return;e.preventDefault();padId=e.pointerId;pad.setPointerCapture(padId);move(e);});
pad.addEventListener('pointermove',e=>{if(e.pointerId===padId)move(e);});
for(const name of ['pointerup','pointercancel','lostpointercapture'])pad.addEventListener(name,e=>{if(e.pointerId===padId){padId=null;direction=255;knob.style.transform='';send();}});
pad.addEventListener('contextmenu',e=>e.preventDefault());
// Capture startup input before a focused Fullscreen/Touch button can consume
// Enter or Space. Translate every ordinary host key to a reliable startup
// pulse; gameplay uses TSRun's complete keyboard map rather than a whitelist.
window.addEventListener('keydown',e=>{
  if(!ready||e.ctrlKey||e.altKey||e.metaKey||e.code==='Escape')return;
  if(api().introActive()){
    e.preventDefault();e.stopImmediatePropagation();
    document.querySelector('#player').focus({preventScroll:true});
    if(e.repeat)return;
    clearTimeout(startupRelease);startupRelease=null;
    if(startupHeld.size===0){startupAt=performance.now();api().key('Space',true);}
    startupHeld.add(e.code);
    return;
  }
  if((e.code==='Space'||e.code==='Enter')&&e.target.closest?.('button,a'))return;
  physicalHeld.add(e.code);api().physicalKey(e,true);
},true);
window.addEventListener('keyup',e=>{
  if(startupHeld.delete(e.code)){
    e.preventDefault();e.stopImmediatePropagation();
    if(startupHeld.size===0)startupRelease=setTimeout(()=>{startupRelease=null;if(ready)api().key('Space',false);},Math.max(0,400-(performance.now()-startupAt)));
    return;
  }
  if(ready&&physicalHeld.delete(e.code))api().physicalKey(e,false);
},true);
for(const name of ['blur','pagehide','resize'])window.addEventListener(name,release);
document.addEventListener('visibilitychange',()=>{if(document.hidden)release();});
document.addEventListener('fullscreenchange',release);
document.querySelector('#reset').addEventListener('click',()=>{release();if(ready)api().reset();});
document.querySelector('#audio').addEventListener('click',e=>{if(!ready)return;const on=api().audio();e.currentTarget.textContent=on?'Audio on':'Audio off';e.currentTarget.setAttribute('aria-pressed',String(on));});
document.querySelector('#fullscreen').addEventListener('click',async()=>{release();try{if(document.fullscreenElement)await document.exitFullscreen();else await document.querySelector('#player').requestFullscreen();}catch{document.querySelector('#status').textContent='Fullscreen unavailable; rotate your phone for a wider view.';}});
