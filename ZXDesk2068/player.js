const frame=document.getElementById('emulator');
const status=document.getElementById('mode-status');
const normal=document.getElementById('normal'),hires=document.getElementById('hires');
const restart=document.getElementById('restart'),hold=document.getElementById('hold-click');
let mode=null,ready=false;
const held=new Set();
let latched=false;
function send(type,code){
  if(!ready)return;
  frame.contentWindow.dispatchEvent(new KeyboardEvent(type,{code,bubbles:true,cancelable:true}));
}
function releaseAll(){
  for(const code of held)send('keyup',code);
  held.clear();send('keyup','Space');send('keyup','ShiftLeft');send('keyup','ControlLeft');
  latched=false;hold.setAttribute('aria-pressed','false');
}
function start(which){
  releaseAll();ready=false;mode=which;
  normal.setAttribute('aria-pressed',String(which==='normal'));
  hires.setAttribute('aria-pressed',String(which==='hires'));
  const url=new URL('tsrun/index.html',location.href);
  url.searchParams.set('url',new URL(`downloads/${which==='hires'?'zxdesk2068-512':'zxdesk2068'}.tap`,location.href).href);
  url.searchParams.set('crt','0');url.searchParams.set('auto','1');url.searchParams.set('turbo','1');url.searchParams.set('muted','1');
  frame.hidden=false;document.getElementById('placeholder').hidden=true;
  document.getElementById('placeholder').style.display='none';
  document.getElementById('standalone').href=`?mode=${which}#try`;
  status.textContent=`Loading ${which==='hires'?'512 × 192':'256 × 192'} in TSRun. Please allow the tape to finish.`;
  frame.src=url.href;restart.disabled=false;
  history.replaceState(null,'',`?mode=${which}#try`);
}
normal.addEventListener('click',()=>start('normal'));hires.addEventListener('click',()=>start('hires'));
restart.addEventListener('click',()=>{if(mode)start(mode)});
frame.addEventListener('load',()=>{
  ready=true;
  const target=frame.contentWindow;
  const arrows={ArrowUp:'KeyQ',ArrowDown:'KeyA',ArrowLeft:'KeyO',ArrowRight:'KeyP'};
  for(const type of ['keydown','keyup'])target.addEventListener(type,event=>{
    const code=arrows[event.code];
    if(!code)return;
    // Capture before TSRun maps arrows to Spectrum cursor keys. Synthetic
    // modifier events stay in the emulator; no browser shortcut is pressed.
    event.preventDefault();event.stopImmediatePropagation();
    if(type==='keydown'){
      held.add(code);updateModifiers();send('keydown',code);
    }else{
      held.delete(code);send('keyup',code);updateModifiers();
    }
  },true);
  target.addEventListener('blur',releaseAll);
  status.textContent=`${mode==='hires'?'512 × 192':'256 × 192'} selected. TSRun loads the tape automatically; click inside its screen to use the keyboard.`;});
function updateModifiers(){
  const moving=[...held].some(k=>k!=='Space');
  send(moving?'keydown':'keyup','ShiftLeft');send(moving?'keydown':'keyup','ControlLeft');
}
for(const button of document.querySelectorAll('[data-key]')){
  const code=button.dataset.key;
  button.addEventListener('pointerdown',event=>{
    if(!ready)return;event.preventDefault();button.setPointerCapture(event.pointerId);
    held.add(code);updateModifiers();send('keydown',code);
  });
  function up(){held.delete(code);if(code!=='Space'||!latched)send('keyup',code);updateModifiers()}
  button.addEventListener('pointerup',up);button.addEventListener('pointercancel',up);button.addEventListener('lostpointercapture',up);
  button.addEventListener('keydown',event=>{if(!ready||!['Enter','Space'].includes(event.code))return;event.preventDefault();held.add(code);updateModifiers();send('keydown',code)});
  button.addEventListener('keyup',event=>{if(!['Enter','Space'].includes(event.code))return;event.preventDefault();up()});
}
hold.addEventListener('click',()=>{if(!ready)return;latched=!latched;hold.setAttribute('aria-pressed',String(latched));send(latched?'keydown':'keyup','Space')});
window.addEventListener('blur',releaseAll);document.addEventListener('visibilitychange',()=>{if(document.hidden)releaseAll()});
const initial=new URLSearchParams(location.search).get('mode');
if(initial==='normal'||initial==='hires')start(initial);
