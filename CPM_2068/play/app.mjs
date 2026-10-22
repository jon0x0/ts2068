import * as api from './tsrun/machine.js';
import {initKeyboard,handleKeyDown,handleKeyUp,handleBlur} from './tsrun/keyboard.js';
import {attachOliger,decodeMedia,decodeTapSet,encodeTapSet,storedZip} from './oliger.mjs';
const $=id=>document.getElementById(id),keys=new Uint8Array(8).fill(255);
const machine=api.createMachine(keys,new Uint8Array(2).fill(255));
const keyboard=initKeyboard($('keyboard'),keys),screen=$('screen'),ctx=screen.getContext('2d'),frame=ctx.createImageData(640,240);
let device,config,busy=false,clock=0,pendingFrames;
const matrix=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'];
function paint(){for(let i=0;i<machine.pixels.length;i++){const c=machine.pixels[i],bright=c&8?51:0,at=i*4;frame.data[at]=(c&2?204:0)+bright;frame.data[at+1]=(c&4?204:0)+bright;frame.data[at+2]=(c&1?204:0)+bright;frame.data[at+3]=255;}ctx.putImageData(frame,0,0);}
function status(){if(device)$('status').textContent=`A: ${config.disk} · ${device.raw.length/1024}KB · ${device.dirty?'unsaved changes — download DSK':'disk loaded'}`;}
function tick(now){if(!clock)clock=now;if(now-clock>100)clock=now-100;const count=Math.min(6,Math.floor((now-clock)/16.64));if(count){clock+=count*16.64;for(let i=0;i<count;i++){api.runFrame(machine);if(pendingFrames&&!--pendingFrames.left){const resolve=pendingFrames.resolve;pendingFrames=null;resolve();}}paint();status();}requestAnimationFrame(tick);}
function reset(){handleBlur(keyboard);device.reset();api.resetMachine(machine);clock=0;screen.focus({preventScroll:true});}
screen.addEventListener('keydown',e=>{if(!busy)handleKeyDown(keyboard,e);});
screen.addEventListener('keyup',e=>handleKeyUp(keyboard,e));
window.addEventListener('blur',()=>handleBlur(keyboard));
const emulatedFrames=left=>new Promise(resolve=>{pendingFrames={left,resolve};});
async function command(text){
 if(busy)return;
 const chars=(text.toUpperCase()+'\r').split('');
 // Validate before sending any part of a command.
 if(chars.some(c=>!matrix.some(row=>row.includes(c))&&!'.=:'.includes(c)))throw Error('Command box supports letters, digits, spaces, period, equals and colon. Use the screen keyboard for other symbols.');
 busy=true;$('send').disabled=true;handleBlur(keyboard);
 try{for(let c of chars){keys.fill(255);if('.=:'.includes(c)){keys[7]&=~2;c={'.':'M','=':'L',':':'Z'}[c];}for(let r=0;r<8;r++){const bit=matrix[r].indexOf(c);if(bit>=0){keys[r]&=~(1<<bit);break;}}await emulatedFrames(4);keys.fill(255);await emulatedFrames(4);}}
 finally{keys.fill(255);busy=false;$('send').disabled=false;screen.focus({preventScroll:true});}
}
$('commands').addEventListener('submit',e=>{e.preventDefault();command($('command').value).catch(error=>alert(error.message));});
for(const button of document.querySelectorAll('[data-command]'))button.onclick=()=>command(button.dataset.command).catch(error=>alert(error.message));
$('reset').onclick=()=>{if(!busy)reset();};
function download(format){const data=format==='zip'?storedZip(encodeTapSet(device.raw)):format==='tap'?device.exportTap():device.exportDsk(),blob=new Blob([data],{type:'application/octet-stream'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=config.disk.replace(/\.(dsk|tap)$/i,'')+'-saved.'+format;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('save').onclick=()=>download('dsk');
$('save-tap').onclick=()=>download('tap');
$('save-chunks').onclick=()=>download('zip');
$('disk-file').onchange=async()=>{const files=[...$('disk-file').files];if(!files.length)return;try{if(busy)throw Error('Wait for the command to finish.');const inputs=await Promise.all(files.map(async file=>({name:file.name,data:await file.arrayBuffer()}))),media=inputs.length===1?decodeMedia(inputs[0].data):decodeTapSet(inputs);if(media.sides!==device.sides)throw Error('Disk size must match this cartridge. Restart the launcher with its matching cartridge to change size.');if(device.dirty&&!confirm('The current disk has unsaved changes. Open another disk anyway?'))return;device.detach();device=attachOliger(machine,media);config.disk=inputs.length===1?files[0].name:'CPMRAM.TAP';reset();status();}catch(error){alert(error.message);}finally{$('disk-file').value='';}};
window.addEventListener('beforeunload',e=>{if(device?.dirty){e.preventDefault();e.returnValue='';}});
try{
 const fetchBytes=async url=>{const response=await fetch(url);if(!response.ok)throw Error(`Cannot load ${url}: ${response.status}`);return new Uint8Array(await response.arrayBuffer());};
 const response=await fetch('./config.json');if(!response.ok)throw Error('Cannot load emulator configuration.');
 config=await response.json();
 if(config.media){const size=new URLSearchParams(location.search).get('size')||'320';if(!config.media[size])throw Error('Choose size=160 or size=320.');Object.assign(config,config.media[size]);}
 const [home,ex,disk,cartridge]=await Promise.all([config.rom0||'./tsrun/roms/ts2068-0.rom',config.rom1||'./tsrun/roms/ts2068-1.rom',config.diskUrl||'./media/disk.dsk',config.cartridgeUrl||'./media/cpm.dck'].map(fetchBytes));
 for(const error of [api.setHomeRom(machine,home),api.setExRom(machine,ex),api.insertDock(machine,cartridge)])if(error)throw Error(error);
 device=attachOliger(machine,disk);
 for(const button of document.querySelectorAll('button,input[type=file]'))button.disabled=false;
 if(config.games===false)for(const button of document.querySelectorAll('[data-command="PLANET"],[data-command="ZORK1"]'))button.hidden=true;
 status();reset();requestAnimationFrame(tick);
}catch(error){$('status').textContent=error.message;console.error(error);}
