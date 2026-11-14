from pathlib import Path
import json,sys,hashlib,subprocess,functools,zipfile,re
import numpy as np
R=Path.cwd();O=R/'build/fullgame/reviewed_r72';B=R/'build/fullgame/l2_rpc_r67';sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
layouts=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'];holds=set(json.loads((R/'src/art_review_holds.json').read_text())['entries']);assert holds=={'L2_003','L2_004','L2_005','L2_006','L3_040'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes():return {str(p.relative_to(O)):sha(p)for p in list(O.glob('*_region.bin'))+[O/'launcher.bin']+list((O/'rtype').glob('*.tap'))}
frozen=hashes();q=subprocess.run(['python','scripts/build_reviewed_r72.py'],capture_output=True,text=True);(O/'rebuild.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr;assert frozen==hashes(),'Non-deterministic primary build'
(O/'final_primary_hashes.json').write_text(json.dumps(frozen,indent=2))
checks=json.loads((O/'r72_checks.json').read_text());assert len(checks)==9 and all(r['passed']for r in checks)
backup_checks=json.loads((O/'r72_backup_checks.json').read_text());assert len(backup_checks)==3 and all(r['passed']for r in backup_checks)
boss=[json.loads((O/f'boss_level{n}.json').read_text())for n in range(1,9)];assert all(r['passed']for r in boss)
for n in[5,7]:assert (O/f'level{n:02d}_region.bin').read_bytes()==(B/f'level{n:02d}_region.bin').read_bytes()
for f in['launcher.bin','boot_region.bin','rtype/RTCORE.TAP','rtype/rt.tap']:assert (O/f).read_bytes()==(B/f).read_bytes(),f
# Decode native held frames independently, including their palette rows.
def native_pixels(b,n,i):
 m=bytes(0xc000)+b[0xa000:0xe000];at=layouts[n-1]['enemy_descriptors_start']+(i-1)*4;w,h=m[at:at+2];p=int.from_bytes(m[at+2:at+4],'little');out=[]
 for _ in range(w*h):
  tag=m[p];p+=1
  if tag==54:out.extend([0]*64);continue
  for y in range(8):
   a=b[0x2000+(tag&127)*8+y];bank=8 if a&64 else 0
   for x in range(8):out.append(((a&7)if m[p+y]&(128>>x)else(a>>3)&7)+bank)
  p+=8
 return w,h,bytes(out)
held_proofs=[]
for n,ids in[(1,[16,17,18,19]),(3,[40,41])]:
 before=(B/f'level{n:02d}_region.bin').read_bytes();after=(O/f'level{n:02d}_region.bin').read_bytes()
 for i in ids:assert native_pixels(before,n,i)==native_pixels(after,n,i);held_proofs.append(f'L{n}_{i:03d}')
a=(B/'level02_region.bin').read_bytes();b=(O/'level02_region.bin').read_bytes();assert a[0x2400:0x3285]==b[0x2400:0x3285];assert a[0xe350:0xe37c]==b[0xe350:0xe37c]
for i in range(41,45):assert native_pixels(a,2,i)==native_pixels(b,2,i),'L2 mouth changed'
held_proofs+=['L2_003','L2_004','L2_005','L2_006','L7_051']
assert sha(B/'RType_TS2068_r67.zip')=='f35144c6c728f6485fb3fcb658dd26b2a6fa3a4f737d531ba4d4eeb69b94a716'
def tape(p):
 raw=p.read_bytes();out=[];at=0
 while at<len(raw):
  size=int.from_bytes(raw[at:at+2],'little');v=raw[at+2:at+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;out.append(v);at+=size+2
 assert at==len(raw);return out
for p in (O/'rtype').glob('*.tap'):tape(p)
for n in range(1,9):
 raw=(O/f'level{n:02d}_region.bin').read_bytes();assert b''.join(v[1:-1]for v in tape(O/f'rtype/LEVEL{n:02d}.TAP')[1::2])==raw;assert b''.join(v[1:-1]for v in tape(O/f'rtype/START{n:02d}.TAP')[1::2])==b''.join(raw[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
preset=json.loads((R/'src/rpc_default_settings.json').read_text());assert preset['settings']=={'brightness':49,'contrast':65,'saturation':78,'gamma':1.13}
oldtime=json.loads((R/'build/diagnostics/l2_r67_perf/r67/timing.json').read_text())['tstates'];newtime=json.loads((R/'build/diagnostics/l2_r67_perf/r72/timing.json').read_text())['tstates'];cost=(newtime/oldtime-1)*100
readme='''R-Type TS2068 r72 - reviewed artwork, current-size disk game

Reset and replace the complete rtype folder. Run lowercase rt.tap.
Keep the supplied files together; subfolders under /TAP remain supported.
This is the expanded512KB disk package. Existing stock64KB target is unchanged.

47reviewed source choices are incorporated at CURRENT r67 dimensions. No D-size
enlargements, new strip pitches or actor movement/hitbox coordinates are added.
L1body/head details; L2organic body; L3selected ship strips; L4bosses; L6heads;
L8boss are updated. Existing L6return-pose alias13 follows selected pose10.

EVALUATION HOLDS: L2_003/004/005/006 andL3_040 retain their r67 appearance.
Earlier review flags (L1snake16..19,L3_041,L7_051) and unreviewed assets also stay.
L5 andL7 complete level files are byte-identicalr67.

Packing limits: shared palette rows approximate some native cells. L3strips
retain their existing transparent CELL layout so new graphics cannot overlap
neighbouring features; isolated proposed pixels outside that layout are masked.
L4uses normal-intensity pairs because its existing fine-shift palette synthesizer
operates on the normal bank. Compiled L6/L8phase0 retains selected colours.
L2mouth colours are preserved exactly while palette IDs are reassigned.

Loader protocol, controls, audio, AI and movement are unchanged; asset bindings are updated. L4uses a retired immutable source
area of its three updated compiled bosses for one preload packet. Cache rows
stay at their previous targets. L6/L8 packed restart backups are relocated
with their asset packets and restore the exact previous native source bytes. Runtime code and visibility/clipping paths stay.
The legacy debug module still prints R38; report this package as r72.

Checks: all8boss checkpoints (L7needs700updates toreachboss), ordinaryL3
2000updates andL6poses, repeated cold/cached4/6/4/2/4/8/4/1 and6/8/6/8/4/6/8/1 jumps, pause,
keyboard definitions, L4/L6death/respawn, activeL2/L6LoadAll/title, Force andrapidfire.
All held-source/cache checks, deterministic30product rebuild, tapechecksum/
reconstruction andZIPintegrity checks pass. Hardware confirmation is pending.
Known L3hardware glitches are not claimed fixed by these artwork changes.

Controlled160update L2boss CPUcost isabout1.7percent above r67. This measures
world-loop CPUtime, not hardwareFPS or all-level performance.

Future conversion default derived from37reviewed families across6levels:
Brightness49 / Contrast65 / Saturation78 / Gamma1.13, actual RPC SierraLite.
Levels are weighted equally so the30L3families do not dominate. Explicit holds
and unreviewed choices are excluded. This default is for future work; individual
settings in this build are retained. src/rpc_default_settings.json records it.

Select1-8 at title or use Lthen number inplay. B-release-B previews theboss.
L at title or Shift-L during play loadsall, then returns to title. Initial
Shift-L queuesLoadAll. Keys remain user-defined; both joystick sockets active.
P pauses (Shift-P whenP is a defined game key); P resumes. Music toggle retained.
'''
(O/'rtype/README.txt').write_text(readme,encoding='utf-8');(R/'docs/r72_readme.txt').write_text(readme,encoding='utf-8')
zp=O/'RType_TS2068_r72.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED)as z:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file()and p.name!='RTBOOT.TAP':
   info=zipfile.ZipInfo('rtype/'+p.name,date_time=(2026,11,6,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes())
with zipfile.ZipFile(zp)as z:assert z.testzip()is None;assert 'rtype/rt.tap'in z.namelist()
report={'version':72,'sha256':sha(zp),'bytes':zp.stat().st_size,'reviewed_source_choices':47,'held_appearance_proofs':held_proofs,'explicit_hold_policy':sorted(holds),'unchanged_levels':[5,7],'unchanged_boot_launcher_core':True,'primary_products_rebuilt_identically':len(frozen),'all_tapes_valid':True,'checks':checks,'restart_backup_checks':backup_checks,'boss_checks':boss,'L2_world_CPU_percent_vs_r67':cost,'future_default':preset,'hardware':'pending','stock64KB':'unchanged','known_L3_hardware_issue':'not claimed fixed','assets':json.loads((O/'native_art_report.json').read_text())};(O/'validation_summary.json').write_text(json.dumps(report,indent=2));print('READY',report['sha256'],report['bytes'],len(frozen),'products',cost)
