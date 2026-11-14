from pathlib import Path
import sys,json,shutil,subprocess,re
R=Path.cwd();sys.path.insert(0,'scripts');from build_rocket_fix import code
B=R/'build/fullgame/l7_all_choices_r140';O=R/'build/fullgame/respawn_pickups_r141';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']and not any(k in p.name for k in['validation','summary','release_manifest']):shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
src=' ORG $01C8\nboss_pickups:\n CALL $8BAE\n PUSH HL\n JR spawn_pickups\nmain_input:\n PUSH HL\n LD BC,$7FFE\n LD A,($7A84)\n CP 73\n JR C,pickups_done\n LD A,($7ABE)\n CP 2\n JR NC,pickups_done\n LD A,($7AC1)\n LD HL,$7AC5\n OR (HL)\n JR NZ,pickups_done\nspawn_pickups:\n LD HL,$0002\n LD ($7AC1),HL\n LD ($7AC5),HL\n LD HL,$0A0C\n LD ($7AC3),HL\n LD L,$0E\n LD ($7AC7),HL\npickups_done:\n POP HL\n RET\n ASSERT $ <= $0200\n'
p=O/'respawn_pickups';p.with_suffix('.asm').write_text(src);exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';q=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr;helper=p.with_suffix('.bin').read_bytes();sy={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
b=bytearray((B/'level04_region.bin').read_bytes());b[0x1c8:0x200]=helper+bytes([255])*(56-len(helper));assert b[0x1fa3:0x1fa6]==bytes.fromhex('01fe7f');b[0x1fa3:0x1fa6]=bytes([0xcd])+sy['main_input'].to_bytes(2,'little');(O/'level04_region.bin').write_bytes(b)
for name in['LEVEL04.TAP','START04.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[k*8192+t*1024:k*8192+(t+1)*1024]for k in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
(O/'respawn_contract.json').write_text(json.dumps(dict(symbols=sy,helper_bytes=len(helper),pickup_positions=[[12,10],[14,10]],type=2,requires_collection=True,boss_gate=0x7a84,boss_checkpoint_column=73,input_hook=0x1fa3,respawn_policy='Replenish from boss-return checkpoint column73 onward, Force power below2, both pickup slots empty; no common RAM patch'),indent=2))
s=(R/'scripts/boss_motion_fixture_r140.mjs').read_text().replace('l7_all_choices_r140','respawn_pickups_r141');(R/'scripts/boss_motion_fixture_r141.mjs').write_text(s);print(sy,len(helper))

fc=json.loads((O/'follower_contract.json').read_text());fc.update(boss_shortcut_only=False,pickup_helper=[0x1c8,0x1c8+len(helper)],respawn_checkpoint_column=73,pickup_slots_preserved=True);(O/'follower_contract.json').write_text(json.dumps(fc,indent=2))
for name in['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R140',b'R141'))
p=O/'rtype/rt.tap';data=p.read_bytes();out=bytearray();at=0
while at<len(data):
 n=int.from_bytes(data[at:at+2],'little');q=bytearray(data[at+2:at+2+n]).replace(b'R140',b'R141');q[-1]=0
 for v in q[:-1]:q[-1]^=v
 out+=len(q).to_bytes(2,'little')+q;at+=n+2
p.write_bytes(out)
