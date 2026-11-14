"""Build real per-level disk loading from the preserved r32 gameplay image."""
from pathlib import Path
import subprocess,json,struct,hashlib,sys,zipfile,re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_true_black import change
def block(flag,payload):
 c=flag
 for v in payload:c^=v
 return struct.pack('<H',len(payload)+2)+bytes([flag])+payload+bytes([c])
def code(name,data,address):
 return block(0,bytes([3])+name.encode().ljust(10,b' ')+struct.pack('<HHH',len(data),address,0x8000))+block(255,data)
def main():
 out=ROOT/'build/fullgame/per_level_r33';out.mkdir(parents=True,exist_ok=True);folder=out/'RTYPE';folder.mkdir(exist_ok=True)
 asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
 def assemble(name,text):
  p=out/(name+'.asm');p.write_text(text);r=subprocess.run([str(asm),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],cwd=ROOT,capture_output=True,text=True);p.with_suffix('.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
  return p.with_suffix('.bin').read_bytes()
 old=(ROOT/'src/fullgame_preloader.asm').read_text()
 checksum=old[old.index('checksum_address:'):old.index('page_registers:')]
 transport=old[old.index('select_region:'):old.index('video_settle:')]
 transport=transport.replace('LD (REQUEST),A','LD (REQUEST),A\n        PUSH AF\n        LD A,7\n        LD (LOAD_OP),A\n        POP AF',1)
 text=(ROOT/'src/demand_loader_head.asm').read_text()+'\n'+checksum+'\n'+transport+'\n'+old[old.index('video_settle:'):old.index('bad_header:')]
 tail=(ROOT/'src/fullgame_transition_tail.asm').read_text();tail=tail[tail.index('        LD A,8'):];tail=tail.replace('        LD HL,$8100\n        LD DE,$A000\n        LD BC,DRIVER_LENGTH\n        LDIR\n','')
 text+='\nfinish_tail:\n        DISP $5E00\n'+tail+'\n        ENT\nfinish_tail_end:\nfont: INCBIN "assets/fullgame_preloader_font.bin"\n        INCLUDE "third_party/fullgame_tspico/ram512_transport.inc"\n        INCLUDE "third_party/fullgame_tspico/ram512b_files.inc"\nprogram_end:\n        ASSERT $ < $7800\n'
 loader=assemble('demand_loader',text)
 symbols={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9A-Fa-f]+)',(out/'demand_loader.sym').read_text())}
 original=(ROOT/'src/fullgame_gateway.asm').read_text()
 suffix=original[original.index('select_region:'):];suffix=suffix.replace('DB $42,0,$FF,1,0,0,0,11,0,0','DB $42,0,$FF,1,0,14,0,11,0,0')
 prefix=f'''        ORG $A000
        DI
        LD A,($719C)
        INC A
        CP '9'
        JR C,demand_level_ok
        LD A,'1'
demand_level_ok:
        LD ($719C),A
        LD ($FDA4),A
        LD E,0
        LD A,8
        CALL $F88C
        LD A,9
        CALL $F88C
        LD A,10
        CALL $F88C
        XOR A
        OUT ($F4),A
        LD A,8
        OUT ($F4),A
        LD HL,$6000
        LD DE,$4000
        LD BC,$2000
        LDIR
        XOR A
        OUT ($F4),A
        CALL select_region
        JP C,load_error
        LD A,1
        OUT ($F4),A
        LD HL,0
        LD DE,$6000
        LD BC,{len(loader)}
        LDIR
        XOR A
        OUT ($F4),A
        LD HL,demand_restore
        LD DE,$5E00
        LD BC,demand_restore_end-demand_restore
        LDIR
        JP $5E00
demand_restore:
        DISP $5E00
        LD HL,$8100
        LD DE,$A000
        LD BC,DRIVER_LENGTH
        LDIR
        JP $6000
        ENT
demand_restore_end:
'''
 gateway=assemble('demand_gateway','DRIVER_LENGTH EQU 0\n'+prefix+suffix);assert len(gateway)<=400,len(gateway)
 gateway=assemble('demand_gateway',f'DRIVER_LENGTH EQU {len(gateway)}\n'+prefix+suffix)
 entry=assemble('demand_entry',f'DRIVER_LENGTH EQU {len(gateway)}\n'+(ROOT/'src/fullgame_transition_entry.asm').read_text())
 source=(ROOT/'build/fullgame/restart_r32/RType_TS2068_restart_r32.ram512').read_bytes()
 regions=[bytearray(source[n*65536:(n+1)*65536])for n in range(8)]
 boot=bytearray(regions[0])
 runtime=change((ROOT/'build/fullgame/level01/runtime_region.bin').read_bytes(),1,True)
 for bank in (1,2,3):regions[0][bank*8192:(bank+1)*8192]=runtime[bank*8192:(bank+1)*8192]
 for region in [boot]+regions:
  region[0xa08:0xa08+len(entry)]=entry;region[0xa30:0xa30+len(gateway)]=gateway
 def stream(name,region):
  data=b''.join(code(f'RTPAGE{page:02X}',region[page*8192:(page+1)*8192],page)for page in range(8));(folder/name).write_bytes(data);return dict(file=name,sha256=hashlib.sha256(region).hexdigest(),bytes=len(region))
 records=[stream('RTBOOT.TAP',boot)]+[stream(f'LEVEL{n:02d}.TAP',region)for n,region in enumerate(regions,1)]
 (out/'boot_region.bin').write_bytes(boot)
 for n,region in enumerate(regions,1):(out/f'level{n:02d}_region.bin').write_bytes(region)
 # BASIC loads the code at8000; a short HOME trampoline relocates it to6000.
 bootstrap=assemble('disk_bootstrap',f'''        ORG $8000
        DI
        LD SP,$FFF0
        XOR A
        OUT ($F4),A
        LD HL,resident
        LD DE,$6000
        LD BC,{len(loader)}
        LDIR
        JP ${symbols['boot_entry']:04X}
resident:
''')
 player=bootstrap+loader
 kw=lambda n:bytes([n])+b' '
 val=lambda n:kw(176)+f'"{n}"'.encode()
 def line(n,b):return struct.pack('>H',n)+struct.pack('<H',len(b)+1)+b+b'\r'
 program=b''.join(line(n,b)for n,b in[(10,kw(253)+val(32767)),(20,kw(239)+b'"" '+kw(175)),(30,kw(242)+val(60)),(40,kw(249)+kw(192)+val(32768)),(50,kw(226))])
 header=bytes([0])+b'RTYPE DISK'+struct.pack('<HHH',len(program),10,len(program));launch=block(0,header)+block(255,program)+code('RTYPE LOAD',player,32768);(folder/'RTFULL.TAP').write_bytes(launch);(out/'launcher.bin').write_bytes(player)
 readme='R-Type per-level disk game\n\nPut this RTYPE folder anywhere under TAP, including nested subdirectories. Open that folder and load RTFULL.TAP. Keep RTBOOT.TAP and LEVEL01.TAP..LEVEL08.TAP beside the launcher. No command changes directory.\nStartup loads level1 only. Title keys1-8 select a starting level; release then Fire or keyboard0. Other levels load when needed, with LOADING LEVEL n and local page00..07. M toggles music. Transfers are verified before the level is used.\nUses the original shared-FIFO disk protocol and expansion RAM. No firmware changes. Physical validation pending. On error the screen shows ERROR, STEP and PAGE; keep those details.\nThis build performs foreground demand loading; idle-title prefetch is not implemented. The level3 hardware respawn-corruption report remains open.\n'
 (folder/'README.txt').write_text(readme)
 with zipfile.ZipFile(out/'RType_TS2068_per_level_r33.zip','w',zipfile.ZIP_DEFLATED)as z:
  for p in sorted(folder.iterdir()):z.write(p,'RTYPE/'+p.name)
 manifest=dict(status='Per-level runtime candidate; validation pending',loader_bytes=len(loader),gateway_bytes=len(gateway),startup_pages=8,current_region=0,resident_backup_region=7,relative_directory=True,idle_prefetch=False,levels=records)
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(manifest)
if __name__=='__main__':main()

