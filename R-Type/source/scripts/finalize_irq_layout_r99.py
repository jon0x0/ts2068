from pathlib import Path
import json,hashlib,zipfile,functools,re
R=Path.cwd();O=R/'build/fullgame/irq_layout_r99';B=R/'build/fullgame/l5_bank_guard_r93'
for name in ['boss_level5.json','l5_repeat_jumps.json','all_vector_validation.json','pause_L5.json']:assert json.loads((O/name).read_text())['passed'],name
fire=json.loads((O/'unmodified_fire_validation.json').read_text());assert len(fire)==3 and all(r['passed']for r in fire)
startup=json.loads((O/'startup_selected_validation.json').read_text());assert len(startup)==2 and all(r['boot']>=0 and r['region']==r['level']-1 and r['titles']>0 for r in startup)
hashes={}
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();a=(B/f'level{n:02d}_region.bin').read_bytes().replace(b'R38 DEBUG',b'R99 DEBUG');assert len(b)==65536
 if n==5:
  allowed=set(range(0x8f00,0x9000))|set(range(0x8b30,0x8ba0))|set(range(0x9ea0,0x9fdb));assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(a,b)))
  assert a[0x8b30:0x8ba0]==bytes([255])*112
  assert b[0x8f00:0x9000]==bytes([0x5b])*256
  assert b[0x8b70:0x8ba0]==a[0x8f10:0x8f40]
  assert b[0x8bf0:0x8c00]==a[0x8bf0:0x8c00]
  for lo,hi in [(0,0x2000),(0x2000,0x8000),(0xa000,0x10000)]:assert b[lo:hi]==a[lo:hi]
  assert b[0xd8:0xdb]==bytes.fromhex('c3dcdd') and b.find(bytes.fromhex('c3dcdd'),0xdc0,0xdde)>=0
 else:assert b==a
 hashes[str(n)]=hashlib.sha256(b).hexdigest()
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
for name in ['RTCORE.TAP','RTPRELD.TAP']:assert (O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
for name in ['launcher.bin','demand_loader.bin']:assert (O/name).read_bytes()==(B/name).read_bytes().replace(b'PREPARING GAME  ',b'R99 PREPARING   ')
t=(O/'rtype/rt.tap').read_bytes();p=0
while p<len(t):
 size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;p+=size+2
report=dict(passed=True,base='r93',l5_experiments_r94_to_r98_removed=True,graphics_and_gameplay_code_unchanged=True,ui_key=0x8b30,ui_font=0x8b70,vector_page=[0x8f00,0x8fff],vector_entries=256,old_invalid_entries=99,interrupt_return_probes=[0,255],hardware_vector_not_measured=True,hardware_reboot_cause_unconfirmed=True,startup=startup,unmodified_fire=fire,region_sha256=hashes)
(O/'validation_summary.json').write_text(json.dumps(report,indent=2))
readme='''R-Type TS2068 r99 - restore pre-experiment L5 code, repair interrupt layout

Replace complete rtype folder, RESET, launch rtype/rt.tap.
Confirm R99 PREPARING. Artwork, movement and dimensions are retained.

R94-R98 boss experiments are removed. Drawing, cache, copy and interrupt
execution return to r93, with its original matching cold/runtime gateways.
R93 includes the confirmed r92 asset-bank overwrite repair. This does NOT
claim r93 was the last hardware-confirmed good release; that is unknown.

L5's 8F00..8FFF temporary IM2 table contained pause glyphs and key-definition
code at8F10..8F71:99 vector entries pointed away from5B5B. The emulator used
only the FF entry. UI code/font move to verified unused compositor padding
8B30/8B70, below scratch8BF0 and above live variables8B21. The vector page
is now entirely5B. Existing9000 temporary endpoint setup/restore retained.
UI is reassembled from source that exactly reproduces the earlier UI.

All256 table entries checked with live9000endpoint. Actual handler-return
probes at00/FF preserve bank/SP/I. These are injected vector tests; hardware
interrupt vector has NOT been measured. This layout defect is corrected,
but has NOT been established as the hardware freeze/reboot cause.

Unmodified L1 and early-selected L5 startup/title pass. L5 start/rapid fire
at three timings passes without game-over bypass, hundreds of updates.
EarlyL5/doubleB160updates and12bossjumps pass (game-over bypass in stress).
Pause restores exact screen/audio; both joystick sockets64combinations pass.
TAP checksums/reconstruction, code/asset scope andZIPCRC pass.
No hardware reboot reproduced in emulation. Hardware confirmation pending.
Stock64KB cartridge unchanged. Keep all release files together.
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r99.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','validation_summary.json','all_vector_validation.json']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)
