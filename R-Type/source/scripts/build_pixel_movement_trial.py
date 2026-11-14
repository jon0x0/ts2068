"""Browser movement proof and reusable ECM phase assets; not a native game patch."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from build_graphics import PALETTE,fit_pairs,quantize,unpack
from build_true_black import normal
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/diagnostics/pixel_movement_trial'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    mem=bytes(16384)+(ROOT/'build/native/snapshot.bin').read_bytes()
    colours=json.loads((ROOT/'build/fullgame/level01/compiled_ship.json').read_text())['rows']
    phases={};stream=bytearray()
    for pose in [2,3,4]:
        pointer=int.from_bytes(mem[0xbc67+(pose-1)*4+2:0xbc67+(pose-1)*4+4],'little')
        rgb=np.zeros((8,24,3),np.uint8)
        for cx in range(3):
            p=pointer+cx*9;bits=np.unpackbits(np.frombuffer(mem[p+1:p+9],dtype=np.uint8)).reshape(8,8)
            attrs=np.array([normal(v)for v in colours[cx]['colours']],np.uint8)
            indices=np.where(bits,(attrs&7)[:,None],((attrs>>3)&7)[:,None])+np.where(attrs&64,8,0)[:,None]
            rgb[:,cx*8:cx*8+8]=PALETTE[indices]
        phases[pose]=[]
        for phase in range(8):
            pixels=np.zeros((8,32,3),np.uint8);pixels[:,phase:phase+24]=rgb;mask=pixels.max(2)!=0
            pairs=fit_pairs(pixels.astype(float));edge=fit_pairs(pixels.astype(float),black=True)
            holes=(~mask).reshape(8,4,8).any(2);pairs[holes]=edge[holes]
            bits,attrs,_=quantize(Image.fromarray(pixels),pairs=pairs,dither='sierra');bits[~mask]=0
            attrs=np.array([[normal(int(a))for a in row]for row in attrs],np.uint8)
            indices=np.where(bits,np.repeat(attrs&7,8,axis=1),np.repeat((attrs>>3)&7,8,axis=1))+np.repeat(np.where(attrs&64,8,0),8,axis=1)
            assert not indices[~mask].any()
            rendered=PALETTE[indices].astype(np.uint8)
            for y in range(8):
                for x in range(0,32,8):assert len(set(map(tuple,rendered[y,x:x+8])))<=2
            stream+=np.packbits(bits,axis=1).tobytes()+attrs.tobytes()+np.packbits(mask,axis=1).tobytes()
            phases[pose].append(dict(rgb=rendered.tolist(),mask=mask.astype(int).tolist()))
    assert len(stream)==2304
    (OUT/'ship_phases.bin').write_bytes(stream)
    snapshot=(ROOT/'build/fullgame/boss_preview_r42/boss_level1.home.bin').read_bytes();scene=np.asarray(unpack(snapshot[0x4000:0x5800],snapshot[0x6000:0x7800]))
    background=np.zeros((192,256,3),np.uint8);background[144:]=scene[144:]
    data=dict(phases=phases,background=background.tolist())
    template='''<!doctype html><meta charset="utf-8"><title>R-Type one-pixel movement proof</title>
<style>body{background:#151515;color:#eee;font:17px system-ui;max-width:1050px;margin:24px auto}canvas{width:768px;max-width:100%;image-rendering:pixelated;background:black;border:1px solid #555}button{font:inherit;padding:8px;margin:6px}p{line-height:1.4}</style>
<h1>One-pixel ship movement trial</h1><p><strong>Separate browser prototype—not the full game or a cartridge.</strong> Actual ship poses and captured terrain, with legal precomputed ECM phases. Arrow keys move; P/Space fires on release (hold to charge). Click the screen first. Keyboard events are queued between updates. Shots originate at the displayed ship position; collision follows its pixel silhouette.</p>
<button id="mode">Mode: 1 pixel / 50 updates per second</button><button id="reset">Reset</button><span id="state"></span><br><canvas id="screen" width="256" height="192" tabindex="0"></canvas>
<p>The alternate mode uses 8-pixel steps at equal nominal travel speed to compare the feel. It is not a measured emulation of r43. Browser performance does not predict TS2068 performance. No enemy AI, weapon upgrades, stage progression or native joystick hardware is implemented here.</p>
<script>const assets=DATA;
const c=document.getElementById('screen'),ctx=c.getContext('2d'),base=new ImageData(256,192),state=document.getElementById('state');
for(let y=0;y<192;y++)for(let x=0;x<256;x++){let i=(y*256+x)*4;base.data.set([...assets.background[y][x],255],i)}
let x=40,y=80,pose=3,legacy=false,keys=new Set(),events=[],shots=[],charge=0,held=false,hits=0,moves=0,acc=0,last=performance.now();
function reset(){x=40;y=80;shots=[];events=[];charge=0;held=false;keys.clear();hits=0;moves=0;acc=0}
c.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Space','KeyP'].includes(e.code)){e.preventDefault();if(!keys.has(e.code))events.push([e.code,true]);keys.add(e.code)}});
c.addEventListener('keyup',e=>{if(keys.has(e.code))events.push([e.code,false]);keys.delete(e.code);e.preventDefault()});c.addEventListener('blur',()=>{keys.clear();events=[];held=false;charge=0});
function shipAt(xx,yy,p){return assets.phases[p][xx&7]}
function collision(xx,yy,p){let phase=shipAt(xx,yy,p),left=xx-(xx&7);for(let sy=0;sy<8;sy++)for(let sx=0;sx<32;sx++)if(phase.mask[sy][sx]){let px=left+sx,py=yy+sy;if(py>=144&&py<168&&px>=0&&px<256&&assets.background[py][px].some(v=>v))return true}return false}
function tick(){for(let [key,down]of events.splice(0)){if(key==='KeyP'||key==='Space'){if(down&&!held){held=true;charge=0}else if(!down&&held){shots.push({x:x+24,y:y+4,power:charge>=12?3:1});held=false;charge=0}}}if(held)charge++;
 let dx=(keys.has('ArrowRight')?1:0)-(keys.has('ArrowLeft')?1:0),dy=(keys.has('ArrowDown')?1:0)-(keys.has('ArrowUp')?1:0);pose=dy<0?2:dy>0?4:3;let amount=legacy?8:1;
 // Sweep intermediate pixels even in coarse mode, avoiding tunnelling through terrain.
 for(let n=0;n<amount;n++){let nx=Math.max(8,Math.min(224,x+dx));if(!collision(nx,y,pose))x=nx;else if(dx)hits++;let ny=Math.max(0,Math.min(152,y+dy));if(!collision(x,ny,pose))y=ny;else if(dy)hits++}if(dx||dy)moves++;
 for(let s of shots)s.x+=legacy?32:4;shots=shots.filter(s=>s.x<256)}
function render(){ctx.putImageData(base,0,0);let phase=shipAt(x,y,pose),left=x-(x&7);for(let sy=0;sy<8;sy++)for(let sx=0;sx<32;sx++){let rgb=phase.rgb[sy][sx];if(rgb.some(v=>v)){ctx.fillStyle=`rgb(${rgb})`;ctx.fillRect(left+sx,y+sy,1,1)}}ctx.fillStyle='#ffff00';for(let s of shots)ctx.fillRect(s.x,s.y,4,s.power);state.textContent=`Position ${x}, ${y} · phase ${x&7} · charge ${charge} · blocked ${hits}`}
function frame(now){acc+=Math.min(100,now-last);last=now;let dt=legacy?160:20;while(acc>=dt){tick();acc-=dt}render();requestAnimationFrame(frame)}
document.getElementById('mode').onclick=()=>{legacy=!legacy;acc=0;document.getElementById('mode').textContent=legacy?'Mode: 8-pixel comparison / equal travel speed':'Mode: 1 pixel / 50 updates per second';c.focus()};document.getElementById('reset').onclick=()=>{reset();c.focus()};requestAnimationFrame(frame);c.focus();
</script>'''
    (OUT/'index.html').write_text(template.replace('DATA',json.dumps(data,separators=(',',':'))),encoding='utf-8')
    (OUT/'manifest.json').write_text(json.dumps(dict(status='Interactive browser proof only, not a native gameplay modification',poses=3,horizontal_phases=8,phase_cache_bytes=len(stream),legal_ecm_checks=24*8*4,native_performance_measured=False),indent=2));print(OUT/'index.html')
if __name__=='__main__':main()
