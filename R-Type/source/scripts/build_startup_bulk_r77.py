from pathlib import Path
import sys,shutil,re,subprocess,numpy as np
R=Path.cwd();B=R/'build/fullgame/terrain_token_fix_r76';O=R/'build/fullgame/startup_bulk_r77';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import pack,unpack
from build_rocket_fix import code
sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/'demand_loader.sym').read_text(),re.I)}
def asm(name,text):
 p=O/(name+'.asm');p.write_text(text,encoding='utf-8');q=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr;return p.with_suffix('.bin').read_bytes()
b=bytearray((B/'demand_loader.bin').read_bytes());a=sy['loading_screen']-0x6000;z=sy['loading_digits']-0x6000;ui=bytearray(unpack(b[a:z]));font=(R/'assets/fullgame_preloader_font.bin').read_bytes()
def off(y):return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
def text(s,x,y):
 for i,c in enumerate(s):
  for dy,v in enumerate(font[(ord(c)-32)*8:(ord(c)-31)*8]):ui[off(y+dy)+x//8+i]=v
for x,c in zip([136,152,168],'070'):text(c,x,152)
for x,c in zip([24,40,56],'000'):text(c,x,152)
text('1',168,96);packed=pack(ui);origin=sy["loading_digits"]+80
# The cold extension sits after the compressed UI terminator, before digits.
# It loads the existing worker without entering the game or snapshotting it.
loadertext=(B/'demand_loader.asm').read_text(encoding='utf-8-sig');mount=loadertext[loadertext.index('        LD HL,preload_name\n',loadertext.index('preload_entry:')):loadertext.index('preload_name:')]
prepare=sy['prepare_message'];address=sy['startup_actual_address'];pat=bytes.fromhex('2100c0');pos=b.find(pat,address-0x6000,address-0x6000+55);assert pos>=0;bufferhigh=0x6000+pos+2
stub=f'''        ORG ${origin:04X}
cold_bulk:
        LD A,($D623)
        OR A
        JR Z,cold_return
        LD A,$E0
        LD (${bufferhigh:04X}),A
'''+mount+f'''cold_bulk_return:
        LD A,$C0
        LD (${bufferhigh:04X}),A
cold_return:
        LD HL,${prepare:04X}
        RET
queued_progress:
        CALL startup_poll
        LD A,($D623)
        OR A
        RET Z
        LD HL,406
        LD DE,$5071
        JP startup_number
'''
head=''.join(f'{k} EQU ${v:04X}\n'for k,v in sy.items()if '.'not in k and k not in ['cold_bulk','cold_return','cold_bulk_return']);blob=asm('cold_bulk_extension',head+stub);assert len(packed)<=z-a and len(blob)<=240,(len(packed),len(blob),z-a)
ss=(O/'cold_bulk_extension.sym').read_text();ret=int(re.search(r'cold_bulk_return: EQU 0x([0-9a-f]+)',ss,re.I)[1],16)
b[a:z]=packed.ljust(z-a,b'\0');b[z:z+80]=b''.join(font[(ord(c)-32)*8:(ord(c)-31)*8]for c in '0123456789');b[z+80:z+80+len(blob)]=blob;pat=bytes([0x21])+prepare.to_bytes(2,'little');i=b.find(pat,sy['start_verify']-0x6000,sy['startup_verify_error']-0x6000);assert i>=0;b[i:i+3]=bytes([0xcd])+origin.to_bytes(2,'little')
# Preserve the complete validity mask when the cold handover enters the title.
x=bytes.fromhex('21')+sy['cache_masks'].to_bytes(2,'little')+bytes.fromhex('197e');i=b.find(x,sy['start_verify']-0x6000,sy['startup_verify_error']-0x6000);assert i>=0;b[i:i+5]=bytes([0x3a])+sy['VALID'].to_bytes(2,'little')+bytes(2)
# Single-level startup must also mark its completed level valid before handover.
# Worker will do this only in cold bulk mode; normal path uses original mask.
# extension handles both paths by setting VALID to existing | target mask.
# (implemented in worker for bulk, and a separate unchanged cold mask fallback below)
# Replace mask load with a helper expression is unnecessary: VALID is set when
# initial target reaches verified state in the extension. See compact stub below.
(O/'demand_loader.bin').write_bytes(b)
# Build worker with an independent cold entry and return, retaining normal hot path.
w=(B/'preload_worker.asm').read_text(encoding='utf-8-sig');w=w.replace('worker_entry:\n','worker_entry:\n        LD A,(START_ACTIVE)\n        CP 1\n        JP Z,cold_worker_entry\n',1);w=w.replace('        XOR A\n        LD (worker_level),A','worker_count_init:\n        XOR A\n        LD (worker_level),A',1);w=w.replace('        XOR A\n        LD (START_ACTIVE),A','        LD A,(worker_cold)\n        OR A\n        JP NZ,cold_worker_done\n        XOR A\n        LD (START_ACTIVE),A',1)
extra=f'''cold_worker_entry:
        LD A,1
        LD (worker_cold),A
        LD A,(RUN_LEVEL)
        LD (worker_cold_level),A
        CALL target_mask
        LD (VALID),A
        JP worker_count_init
cold_worker_done:
        LD A,(worker_cold_level)
        LD (RUN_LEVEL),A
        LD (DESIRED),A
        SUB '1'
        LD (TARGET),A
        CALL select_region
        JP C,fatal
        XOR A
        LD ($D623),A
        LD A,1
        LD (START_ACTIVE),A
        JP ${ret:04X}
worker_cold: DB 0
worker_cold_level: DB 0
'''
w=w.replace('worker_state: DS 9,0',extra+'worker_state: DS 9,0');w=w.replace('PRELOADING ALL  ','OTHER LEVELS   ');w=w.replace('        LD (worker_total),HL\n','        LD (worker_total),HL\n        LD A,(worker_cold)\n        OR A\n        JR Z,worker_total_ready\n        LD DE,70\n        ADD HL,DE\n        LD (worker_total),HL\n        LD HL,70\n        LD (worker_done),HL\nworker_total_ready:\n',1);worker=asm('preload_worker',w);assert len(worker)<=8192;(O/'rtype/RTPRELD.TAP').write_bytes(code('RTPRELOAD',worker.ljust(8192,b'\0'),0x8000))
# Normal startup VALID still needs the original target-only mask; if no bulk,
# load it from cache_masks. Cold bulk returns VALID=FF. Add this to extension.
# Revert mask patch; instead patch cold valid immediate in worker at cold return
# using the existing cold_start_image field after its mask load occurs is unsafe.
# Use target mask load original, then worker marks all valid in the cold image
# via a compact loader instruction choosing VALID when nonzero.
# Simpler: extension sets a two-byte pointer to VALID? finalize below.
# Keep normal path working by setting VALID in extension before queue check.
stub=stub.replace('cold_bulk:\n', 'cold_bulk:\n        CALL target_mask\n        LD HL,VALID\n        OR (HL)\n        LD (HL),A\n')
blob=asm('cold_bulk_extension',head+stub);ss=(O/'cold_bulk_extension.sym').read_text();newqp=int(re.search(r'queued_progress: EQU 0x([0-9a-f]+)',ss,re.I)[1],16);at=sy['startup_progress']-0x6000;b[at:at+3]=bytes([0xcd])+newqp.to_bytes(2,'little');newret=int(re.search(r'cold_bulk_return: EQU 0x([0-9a-f]+)',ss,re.I)[1],16);assert len(packed)<=z-a and len(blob)<=240,(len(packed),len(blob));b[a:z]=packed.ljust(z-a,b'\0');b[z:z+80]=b''.join(font[(ord(c)-32)*8:(ord(c)-31)*8]for c in '0123456789');b[z+80:z+80+len(blob)]=blob;w=w.replace(f'JP ${ret:04X}',f'JP ${newret:04X}');worker=asm('preload_worker',w);(O/'rtype/RTPRELD.TAP').write_bytes(code('RTPRELOAD',worker.ljust(8192,b'\0'),0x8000));digit=asm('small_digit',f'        ORG ${sy["startup_digit"]:04X}\n        LD L,A\n        LD H,0\n        ADD HL,HL\n        ADD HL,HL\n        ADD HL,HL\n        LD BC,${sy["loading_digits"]:04X}\n        ADD HL,BC\n        LD B,8\nrow:    LD A,(HL)\n        INC HL\n        LD (DE),A\n        INC D\n        DJNZ row\n        RET\n');at=sy['startup_digit']-0x6000;b[at:at+len(digit)]=digit;(O/'demand_loader.bin').write_bytes(b)
launch=bytearray((B/'launcher.bin').read_bytes());launch[-len(b):]=b;(O/'launcher.bin').write_bytes(launch);old=(B/'rtype/rt.tap').read_bytes();pos=0
for _ in range(2):pos+=2+int.from_bytes(old[pos:pos+2],'little')
(O/'rtype/rt.tap').write_bytes(old[:pos]+code('RTYPE LOAD',launch,32768));print('UI',len(packed),'extension',len(blob),'worker',len(worker),'loader',len(b))
s=(R/'scripts/boss_motion_fixture_r76.mjs').read_text(encoding='utf-8-sig').replace('terrain_token_fix_r76','startup_bulk_r77');(R/'scripts/boss_motion_fixture_r77.mjs').write_text(s,encoding='utf-8')
for name,oldver in [('verify_startup_queue',66),('verify_preload_title',76),('verify_boss_game',76)]:
 s=(R/f'scripts/{name}_r{oldver}.mjs').read_text(encoding='utf-8-sig').replace(f'boss_motion_fixture_r{oldver}','boss_motion_fixture_r77');(R/f'scripts/{name}_r77.mjs').write_text(s,encoding='utf-8')
