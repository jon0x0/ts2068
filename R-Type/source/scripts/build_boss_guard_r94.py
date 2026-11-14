from pathlib import Path
import json,re,subprocess,sys,shutil
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
B=R/'build/fullgame/l5_bank_guard_r93';O=R/'build/fullgame/boss_guard_r94';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(x in p.name for x in ['.home.','failed','trace','scene_','jump_']):shutil.copy2(p,O/p.name)
def asm(name,s):
 p=O/(name+'.asm');p.write_text(s);v=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert v.returncode==0,v.stdout+v.stderr;return p.with_suffix('.bin').read_bytes()
sy=lambda name:{k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/(name+'.sym')).read_text(),re.I)}
cs=sy('cache');ms=sy('motion');hook=asm('boss_preview',(R/'src/boss_preview_r94.asm').read_text());assert len(hook)==84
helper=asm('l5_serial_guard',f''' ORG $DFC0
 CALL Z,${cs['init_cache']:04X}
 LD A,$5D
 OUT ($F4),A
 LD HL,irq_gate_source
 LD DE,$F89A
 LD BC,finish_source-irq_gate_source
 LDIR
 LD DE,$FA33
 LD C,helper_end-finish_source
 LDIR
 LD HL,$F89A
 LD ($FB01),HL
 RET
irq_gate_source:
 DISP $F89A
 LD A,($FD4B)
 CP 4
 JR Z,blocked
 LD A,($FBCA)
 AND $10
 JR Z,normal
blocked:
 POP HL ; discard FB03 and return straight to the IRQ caller
 LD HL,$7A8A
 RET
normal:
 JP $F930
 ASSERT $ == $F8B0
 ENT
finish_source:
 DISP $FA33
 LD HL,$FD4B
 DEC (HL)
 XOR A
 OUT ($FE),A
 JP $8B06
 ASSERT $ == $FA3D
 ENT
helper_end:
 ASSERT $ <= $E000
''');assert len(helper)==64,len(helper)
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());assert b.count(b'R38 DEBUG')==1;b=b.replace(b'R38 DEBUG',b'R94 DEBUG')
 if n==5:
  assert b[0x1ff7:0x1ffc]==bytes.fromhex('3e19d3f4c9');b[0x1fa3:0x1ff7]=hook
  q=b.find(b'\xcc'+cs['init_cache'].to_bytes(2,'little'),ms['warmup'],ms['restore_sources']);assert q>=0
  b[q:q+3]=bytes.fromhex('cdc0df');motion=bytearray((B/'motion.bin').read_bytes());motion[q-0xdc50:q-0xdc50+3]=bytes.fromhex('cdc0df');(O/'motion.bin').write_bytes(motion);b[0xdfc0:0xdfc0+len(helper)]=helper
  assert b[0x2400:0x3fe0]==(B/'level05_region.bin').read_bytes()[0x2400:0x3fe0]
 p.write_bytes(b)
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[page*8192+t*1024:page*8192+(t+1)*1024],k)for k,(page,t)in enumerate((page,t)for page in[0,1,4,5,6,7]for t in range(8))))
(O/'boss_guard.json').write_text(json.dumps(dict(guard_field='FD4B',active_value=4,finished_value=3,irq_gate=0xf89a,installer=0xdfc0,installer_bytes=len(helper),hook_bytes=len(hook),l5_trampoline_1ff7_preserved=True,l5_phase_payload_unchanged=True,policy='Music IRQ retained; gameplay callbacks skipped during checkpoint rebuild and raw L5 DOCK4 drawing'),indent=2))
for stem in ['boss_motion_fixture','verify_walker_game','verify_native_revisits','stress_l5_boss','repro_l4_l5_boss','audit_l5_init_irq']:
 p=R/f'scripts/{stem}_r93.mjs'
 if p.exists():
  s=p.read_text().replace('l5_bank_guard_r93','boss_guard_r94').replace('boss_motion_fixture_r93','boss_motion_fixture_r94');(R/f'scripts/{stem}_r94.mjs').write_text(s)
print('L5 guard installed;64byte tail;F89A..F8AF only;84byte hook preserves1FF7')
