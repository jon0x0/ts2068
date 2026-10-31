import {bootCartridge,advance,releaseKeys,setKey,paintIndices,FRAME_MS,WIDTH,HEIGHT} from './player/emulator.js';

const $=id=>document.getElementById(id);
const canvas=$('screen'),ctx=canvas.getContext('2d',{alpha:false});
const native=document.createElement('canvas');native.width=WIDTH;native.height=HEIGHT;
const nativeCtx=native.getContext('2d',{alpha:false}),image=nativeCtx.createImageData(WIDTH,HEIGHT);
ctx.imageSmoothingEnabled=false;
let catalog=[],selected=null,chosen=null,machine=null,paused=false,request=0,lastTime=0,elapsed=0,loading=false;
const cache=new Map(),buttons=new Map(),releases=new Map();
let held=new Map();
function bytes(url){
  if(!cache.has(url)){const pending=fetch(url).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}: ${url}`);return r.arrayBuffer();}).catch(e=>{if(cache.get(url)===pending)cache.delete(url);throw e;});cache.set(url,pending);}
  return cache.get(url);
}
function paint(){if(!machine)return;canvas.dataset.frame=String(machine.flashFrame);paintIndices(machine.pixels,image.data);nativeCtx.putImageData(image,0,0);ctx.imageSmoothingEnabled=false;ctx.drawImage(native,0,0,WIDTH,HEIGHT,0,0,640,480);}
function clearHeld(){for(const timeout of releases.values())clearTimeout(timeout);releases.clear();held.clear();releaseKeys(machine);}
function pulse(code){if(!machine||loading)return;const target=machine;setKey(target,code,true);setTimeout(()=>setKey(target,code,false),120);canvas.focus({preventScroll:true});}
function route(){const id=decodeURIComponent(location.hash.slice(1));const demo=catalog.find(d=>d.id===id)||catalog[0];const variant=new URL(location.href).searchParams.get('variant');select(demo,variant);}
function navigate(index){if(!catalog.length)return;const d=catalog[(index+catalog.length)%catalog.length];const u=new URL(location.href);u.hash=d.id;u.searchParams.delete('variant');history.pushState(null,'',u);select(d);}
function describe(d,v){
  for(const [id,value] of Object.entries({'demo-title':d.title,category:d.group,subtitle:d.subtitle,what:d.what,how:d.how,look:d.look,controls:d.controls}))$(id).textContent=value;
  $('experimental').hidden=!d.experimental;$('manual-controls').hidden=!d.manual;
  $('native-space').hidden=!d.space;$('native-space').textContent=d.space||'Compare ECM';
  $('variant').replaceChildren(...d.variants.map(x=>{const option=document.createElement('option');option.value=x.id;option.textContent=x.title;return option;}));$('variant').value=v.id;
  $('cartridge-download').href=v.cartridge;$('cartridge-download').download=v.cartridge.split('/').pop();
  $('demo-source').href=`https://github.com/jon0x0/ts2068/tree/main/demos/SCLD/${d.source}`;
  $('technical').href=d.technical;
  const link=new URL(location.href);link.hash=d.id;if(v.id===d.variants[0].id)link.searchParams.delete('variant');else link.searchParams.set('variant',v.id);$('permalink').href=link.href;
  const tapes=v.taps.map(x=>{const a=document.createElement('a');a.href=x.url;a.download=x.name;a.textContent=x.name;return a;});
  $('tapes').replaceChildren(...tapes);
  for(const [id,button] of buttons){button.setAttribute('aria-current',String(id===d.id));}
  document.title=`${d.title} · SCLD Display Lab`;
}
async function select(d,variantId){
  const token=++request;clearHeld();selected=d;chosen=d.variants.find(v=>v.id===variantId)||d.variants[0];const v=chosen;
  loading=true;$('error').hidden=true;$('status').textContent=`Loading ${d.title}…`;describe(d,v);
  try{
    const data=await bytes(v.cartridge);
    if(token!==request)return;
    const next=bootCartridge(data);
    advance(next,2);machine=next;paused=false;loading=false;elapsed=0;lastTime=0;paint();
    $('pause').textContent='Pause';$('pause').setAttribute('aria-pressed','false');$('status').textContent=d.title;
    // Useful, non-invasive diagnostics for repeatable browser checks.
    canvas.dataset.demo=d.id;canvas.dataset.variant=v.id;canvas.dataset.crt='off';
  }catch(error){
    if(token!==request)return;
    machine=null;loading=false;ctx.fillStyle='#000';ctx.fillRect(0,0,640,480);$('status').textContent='Cartridge unavailable';$('error-detail').textContent=error.message;$('error').hidden=false;
  }
}
function loop(now){
  if(!lastTime)lastTime=now;
  if(machine&&!paused&&!loading&&!document.hidden){elapsed+=Math.min(100,now-lastTime);let count=0;while(elapsed>=FRAME_MS&&count<6){advance(machine);elapsed-=FRAME_MS;count++;}if(count)paint();}
  lastTime=now;requestAnimationFrame(loop);
}
function buildList(){
  let group=null;
  for(const [i,d] of catalog.entries()){
    if(d.group!==group){group=d.group;const heading=document.createElement('h3');heading.className='group-title';heading.textContent=group;$('demo-list').append(heading);}
    const button=document.createElement('button');button.className='demo-button';button.type='button';button.dataset.demo=d.id;button.setAttribute('aria-current','false');
    const img=document.createElement('img');img.src=d.preview;img.alt='';img.width=56;img.height=42;img.loading='lazy';
    const copy=document.createElement('span'),title=document.createElement('span'),sub=document.createElement('span');title.className='demo-label';title.textContent=d.title;sub.className='demo-sub';sub.textContent=d.variants.length>1?`${d.variants.length} variants`:(d.experimental?'Attribute timing':'Native mode switching');copy.append(title,sub);button.append(img,copy);button.addEventListener('click',()=>navigate(i));$('demo-list').append(button);buttons.set(d.id,button);
  }
  $('count').textContent=String(catalog.length);
}
$('previous').addEventListener('click',()=>navigate(catalog.indexOf(selected)-1));$('next').addEventListener('click',()=>navigate(catalog.indexOf(selected)+1));
$('pause').addEventListener('click',()=>{paused=!paused;elapsed=0;lastTime=0;clearHeld();$('pause').textContent=paused?'Resume':'Pause';$('pause').setAttribute('aria-pressed',String(paused));});
$('restart').addEventListener('click',()=>{if(selected&&chosen)select(selected,chosen.id);});
$('retry').addEventListener('click',()=>{if(selected&&chosen){cache.delete(chosen.cartridge);select(selected,chosen.id);}else init();});
$('variant').addEventListener('change',()=>{const id=$('variant').value,u=new URL(location.href);u.hash=selected.id;u.searchParams.set('variant',id);history.pushState(null,'',u);select(selected,id);});
$('native-space').addEventListener('click',()=>pulse('Space'));
document.querySelectorAll('[data-native]').forEach(b=>b.addEventListener('click',()=>pulse(b.dataset.native)));
canvas.addEventListener('click',()=>canvas.focus({preventScroll:true}));
$('fullscreen').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await $('screen-shell').requestFullscreen();}catch{ $('status').textContent='Fullscreen is unavailable in this browser.'; }});
window.addEventListener('hashchange',route);window.addEventListener('popstate',route);
window.addEventListener('keydown',event=>{
  if(event.ctrlKey||event.metaKey||event.altKey||event.target.closest?.('input,textarea,select,button,a,summary,[contenteditable]'))return;
  if(event.code==='ArrowLeft'||event.code==='ArrowRight'){event.preventDefault();if(!event.repeat&&catalog.length)navigate(catalog.indexOf(selected)+(event.code==='ArrowRight'?1:-1));return;}
  if(!machine||loading)return;
  if(setKey(machine,event.code,true)){event.preventDefault();clearTimeout(releases.get(event.code));releases.delete(event.code);if(!held.has(event.code))held.set(event.code,performance.now());}
});
window.addEventListener('keyup',event=>{
  if(!machine||!held.has(event.code))return;event.preventDefault();const target=machine;
  const delay=Math.max(0,80-(performance.now()-held.get(event.code)));releases.set(event.code,setTimeout(()=>{setKey(target,event.code,false);held.delete(event.code);releases.delete(event.code);},delay));
});
window.addEventListener('blur',clearHeld);document.addEventListener('visibilitychange',()=>{clearHeld();elapsed=0;lastTime=0;});
async function init(){
  try{const response=await fetch('catalog.json');if(!response.ok)throw new Error(`Catalog HTTP ${response.status}`);const data=await response.json();catalog=data.families;if(!Array.isArray(catalog)||!catalog.length)throw new Error('Empty catalog');buildList();route();
    // Small cartridges are cached once. Selecting one never reloads the page
    // or downloads a second emulator; only the machine is replaced.
    const prefetch=()=>Promise.allSettled(catalog.flatMap(d=>d.variants.map(v=>bytes(v.cartridge))));
    if('requestIdleCallback'in window)requestIdleCallback(prefetch,{timeout:1500});else setTimeout(prefetch,500);
  }catch(error){$('status').textContent='Experiment list unavailable';$('error-detail').textContent=error.message;$('error').hidden=false;}
}
init();requestAnimationFrame(loop);
