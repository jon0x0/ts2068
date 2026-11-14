"""r61: approved walkers and a responsive, selectable cold loader."""
from pathlib import Path
import sys,json,subprocess,re,struct,shutil
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import build_boss_motion_r60 as game
from boss_motion_assets_r60 import pack,unpack
from build_rocket_fix import code
OUT=ROOT/'build/fullgame/startup_r61';BASE=ROOT/'build/fullgame/boss_motion_r60'
def asm(name,text):
 text=text.replace('build/fullgame/startup_r61/',OUT.relative_to(ROOT).as_posix()+'/');p=OUT/(name+'.asm');p.write_text(text);r=subprocess.run([str(ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],cwd=ROOT,capture_output=True,text=True);p.with_suffix('.log').write_text(r.stdout+r.stderr);assert r.returncode==0 and 'warning:'not in (r.stdout+r.stderr).lower(),r.stdout+r.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy

def make_ui():
 font=(ROOT/'assets/fullgame_preloader_font.bin').read_bytes();im=np.zeros((192,256),np.uint8)
 def text(s,x,y,scale=1):
  for c in s:
   rows=font[(ord(c)-32)*8:(ord(c)-31)*8]
   for yy,b in enumerate(rows):
    for xx in range(8):
     if b&(128>>xx):im[y+yy*scale:y+(yy+1)*scale,x+xx*scale:x+(xx+1)*scale]=7
   x+=8*scale
 logo=Image.open(ROOT/'build/graphics/title_alignment/aligned_best.png').convert('RGB').crop((4,101,247,142)).resize((248,42),Image.Resampling.NEAREST);rgb=np.asarray(logo);mask=rgb.max(2)>50;im[11:53,4:252][mask]=5
 text('1-8 SELECT LEVEL',64,80);text('LEVEL 1',72,96,2);text('LOADING',72,128,2);text('000 OF 070...',24,152,2)
 data=bytearray(6912);attrs=np.full((24,32),7,np.uint8)
 for cy in range(1,7):
  for cx in range(32):
   if cy==6:attrs[cy,cx]=1
   elif cy<=2:attrs[cy,cx]=7
   else:attrs[cy,cx]=5
 attrs[12:14,:]=5;attrs[19:21,:]=6
 for y in range(192):
  at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2);data[at:at+32]=np.packbits(im[y]!=0).tobytes()
 data[6144:]=attrs.tobytes();packed=pack(data);assert unpack(packed)==data;(OUT/'loading_ui.lz').write_bytes(packed);(OUT/'loading_logo_attrs.bin').write_bytes(attrs[1:7].tobytes())
 digits=bytearray()
 for c in '0123456789':
  rows=font[(ord(c)-32)*8:(ord(c)-31)*8];pix=np.repeat(np.repeat(np.unpackbits(np.frombuffer(rows,dtype=np.uint8)).reshape(8,8),2,0),2,1);digits.extend(np.packbits(pix,axis=1).tobytes())
 (OUT/'loading_digits.bin').write_bytes(digits);print('UI packed',len(packed))

def main():
 OUT.mkdir(parents=True,exist_ok=True);game.OUT=OUT;game.ART_OVERRIDES={i:ROOT/f'build/graphics/small_walker_highlights/blue_{i}.npy'for i in range(21,26)};game.main();make_ui()
 # Native popup has a second entry at FDAA (C496 calls it directly).
 # All popup entry points must leave the HOME bytes used by the loader.
 for name in ['boot']+[f'level{n:02d}'for n in range(1,9)]:
  p=OUT/f'{name}_region.bin';b=bytearray(p.read_bytes());assert b[0xa496:0xa499]==bytes.fromhex('cd aa fd');b[0xa496:0xa499]=bytes.fromhex('cd 0d 00');p.write_bytes(b)
 manifest=json.loads((OUT/'generic_manifest.json').read_text());sources={r['level']:r for r in manifest}
 for n in range(1,9):
  p=OUT/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());entry=sources[n]['cache_symbols']['install_motion']if n!=5 else 0xDDDC;mapping=0x49 if n!=5 else 0x59
  b[0xd4:0xdb]=bytes([0x3e,mapping,0xd3,0xf4,0xc3,entry&255,entry>>8]);p.write_bytes(b)
  (OUT/'RTYPE'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
  fragments=[b[page*8192+sub*1024:page*8192+(sub+1)*1024]for page in [0,1,4,5,6,7]for sub in range(8)]
  (OUT/'RTYPE'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',v,k)for k,v in enumerate(fragments)))
 boot=(OUT/'boot_region.bin').read_bytes();workspace=boot[0x3400:0x3fe0];assert len(unpack(workspace))==8192
 common=bytearray(boot[0x4000:0x8000]);assert common[0x65f:0x662]==bytes.fromhex('cd a3 1f');assert common[0x656:0x659]==bytes(3);common[0x656:0x659]=bytes.fromhex('cd db 00');core=bytes(common)+workspace.ljust(3072,b'\0')+boot[0x3000:0x33b0].ljust(1024,b'\0')+boot[0xa000:0xa4ae].ljust(2048,b'\0');assert len(core)==22528
 (OUT/'RTYPE/RTCORE.TAP').write_bytes(b''.join(code(f'RTCORE{k:02X}',core[k*1024:(k+1)*1024],k)for k in range(22)))
 # Keep the proved runtime transport/tails and replace only the cold entry.
 text=(ROOT/'build/fullgame/transition_fix_r36/demand_loader.asm').read_text();text=text.replace('boot_entry:\n','boot_entry:\n        JP early_start\n',1)
 text=text.replace('        LD (BOOT_FLAG),A','        LD (BOOT_FLAG),A\n        LD (START_ACTIVE),A',1)
 text=text.replace('cache_loaded:\n','cache_loaded:\n        XOR A\n        LD (START_ACTIVE),A\n',1)
 a=text.index('draw_loading:');z=text.index('bad_header:',a);text=text[:a]+'draw_loading:\n        JP runtime_loading_ui\ndraw_progress:\n        JP runtime_progress_ui\n'+text[z:]
 a=text.index('video_settle:');z=text.index('hex_string:',a)
 text=text[:a]+'video_settle:\n        PUSH BC\n        PUSH DE\n        LD D,32\n        LD A,(SLOW_REPLY)\n        OR A\n        JR Z,settle_group\n        LD D,0\nsettle_group:\n        LD A,D\n        AND 7\n        JR NZ,settle_inner\n        LD A,127\n        LD (RX_TICKS),A\n        CALL startup_rx_hook\nsettle_inner:\n        LD B,0\nsettle_byte:\n        NOP\n        NOP\n        NOP\n        DJNZ settle_byte\n        DEC D\n        JR NZ,settle_group\n        POP DE\n        POP BC\n        RET\n'+text[z:]
 for label in ['title_text','load_text','page_text']:
  assert text.count(label)==1
  text=re.sub(r'^'+label+r': DB[^\n]*\n','',text,flags=re.M)
 text=text.replace('LD DE,$4884','LD DE,$50A2').replace('LD DE,$48C4','LD DE,$50C2')
 text=text.replace('font: INCBIN', (ROOT/'src/responsive_startup.asm').read_text()+'\nfont: INCBIN',1)
 transport=(ROOT/'third_party/fullgame_tspico/ram512_transport.inc').read_text().replace('tpi_rx:\n','tpi_rx:\n        CALL startup_rx_hook\n',1)
 text=text.replace('        INCLUDE "third_party/fullgame_tspico/ram512_transport.inc"',transport)
 loader,sy=asm('demand_loader',text)
 from build_preload_helpers_r61 import build as build_preload
 hot,hs,driver_bytes,restore_bytes=build_preload(OUT,asm,len(loader),sy['preload_entry']);home_hot,home_hs,_,_=build_preload(OUT,asm,len(loader),sy['preload_entry'],home=True)
 dispatcher,_=asm('hotkey_dispatch','        ORG $00DB\n        PUSH AF\n        DI\n        LD A,3\n        OUT ($F4),A\n        CALL $3A00\n        LD A,9\n        OUT ($F4),A\n        EI\n        POP AF\n        RET\n        ASSERT $ <= $00F7\n')
 home_dispatcher,_=asm('hotkey_home_dispatch',f'        ORG $00DB\n        PUSH AF\n        DI\n        LD A,$21\n        OUT ($F4),A\n        LD HL,$A000\n        LD DE,$7B00\n        LD BC,{len(home_hot)}\n        LDIR\n        CALL $7B00\n        LD A,9\n        OUT ($F4),A\n        EI\n        POP AF\n        RET\n        ASSERT $ <= $00F7\n')
 worker_defs={**sy,'PRELOAD_DRIVER_BYTES':driver_bytes,'PRELOAD_DRIVER_STATE':hs['preload_driver.state'],'RESTORE_BYTES':restore_bytes}
 worker,_=asm('preload_worker',''.join(f'{k} EQU ${v:04X}\n'for k,v in worker_defs.items()if '.'not in k)+(ROOT/'src/preload_worker_r61.asm').read_text())
 (OUT/'RTYPE/RTPRELD.TAP').write_bytes(code('RTPRELOAD',worker.ljust(8192,b'\0'),0x8000))
 oldsy=dict((k,int(v,16))for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(BASE/'demand_loader.sym').read_text(),re.I));oldlen=oldsy['program_end']-0x6000
 pattern=bytes.fromhex('21 00 40 11 00 60 01')+oldlen.to_bytes(2,'little')+bytes.fromhex('ed b0')
 for n in range(1,9):
  p=OUT/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());
  if n==5:
   assert len(home_hot)<=0x400;b[0xa000:0xa000+len(home_hot)]=home_hot;b[0xdb:0xdb+len(home_dispatcher)]=home_dispatcher
  else:
   assert not any(b[0x3a00:0x3fe0]);b[0x3a00:0x3a00+len(hot)]=hot;b[0xdb:0xdb+len(dispatcher)]=dispatcher
  at=b.find(pattern,0xa30,0xbc0);assert at>=0;b[at+7:at+9]=len(loader).to_bytes(2,'little');p.write_bytes(b)
  (OUT/'RTYPE'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
  (OUT/'RTYPE'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[page*8192+sub*1024:page*8192+(sub+1)*1024],k)for k,(page,sub)in enumerate((p,s)for p in [0,1,4,5,6,7]for s in range(8))))
 bootstrap,_=asm('disk_bootstrap',f'        ORG $8000\n        DI\n        LD SP,$FFF0\n        XOR A\n        OUT ($F4),A\n        LD HL,resident\n        LD DE,$6000\n        LD BC,{len(loader)}\n        LDIR\n        JP ${sy["boot_entry"]:04X}\nresident:\n')
 launcher=bootstrap+loader;(OUT/'launcher.bin').write_bytes(launcher)
 from build_cached_disk import block
 kw=lambda n:bytes([n])+b' ';val=lambda n:kw(176)+f'"{n}"'.encode();line=lambda n,b:struct.pack('>H',n)+struct.pack('<H',len(b)+1)+b+b'\r'
 program=b''.join(line(n,b)for n,b in [(10,kw(253)+val(32767)),(20,kw(239)+b'"" '+kw(175)),(30,kw(242)+val(60)),(40,kw(249)+kw(192)+val(32768)),(50,kw(226))]);header=bytes([0])+b'RTYPE DISK'+struct.pack('<HHH',len(program),10,len(program));(OUT/'RTYPE/RTFULL.TAP').write_bytes(block(0,header)+block(255,program)+code('RTYPE LOAD',launcher,32768))
 print('Loader',len(loader),'entry',hex(sy['early_start']))
if __name__=='__main__':main()
