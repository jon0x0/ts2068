from pathlib import Path
import re,subprocess,json
R=Path.cwd();O=R/'build/fullgame/world_owner_r78';exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';s=(R/'src/game_pixel_overlay_fire_latest.asm').read_text();a=s.index('tick:\n');i=s.index('        CALL capture_fire',a);s=s[:i]+'''        LD HL,$7A98
        LD A,(HL)
        OR A
        JR Z,protection_done
        DEC (HL)
protection_done:
'''+s[i:];s=s.replace('        LD A,($5BC2)\n        OR A\n        RET Z\n        LD HL,$7A98\n        LD A,(HL)\n        OR A', '        LD A,($5BC2)\n        DEC A\n        RET NZ\n        LD HL,$7A98\n        CP (HL)',1);s=s.replace('        CP 2\n        JP C,inactive\n        CP 5\n        JP NC,inactive','        SUB 2\n        CP 3\n        JP NC,inactive',1);p=O/'overlay_protection.asm'
def assemble(text):
 p.write_text(text);q=subprocess.run([str(exe),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);return q.returncode==0,q.stdout+q.stderr
# Ignore final bound while selecting legal short branches; final assembly enforces it.
s=s.replace('        ASSERT $ <= $ED80','');accepted=[]
for line in list(dict.fromkeys(re.findall(r'^        JP (?:NZ,|Z,|NC,|C,)?[a-zA-Z_][\w.]*\s*$',s,re.M))):
 pos=s.find(line,s.index('X EQU'));
 if pos<0:continue
 trial=s[:pos]+s[pos:].replace(line,line.replace('JP ','JR '),1);ok,_=assemble(trial)
 if ok:s=trial;accepted.append(line.strip())
 if len(accepted)>=12:break
for line in list(dict.fromkeys(re.findall(r'^        JP (?:NZ,|Z,|NC,|C,)?[a-zA-Z_][\w.]*\s*$',s,re.M))):
 pos=s.find(line,s.index('X EQU'))
 if pos<0:continue
 trial=s[:pos]+s[pos:].replace(line,line.replace('JP ','JR '),1);ok,_=assemble(trial)
 if ok:s=trial;accepted.append(line.strip())
tails=[]
for match in list(re.finditer(r'        CALL ([^\n]+)\n        RET\n',s)):
 
 if ','in match.group(1).split(';')[0]:continue
 old=match.group(0);new='        JP '+match.group(1)+'\n';trial=s.replace(old,new,1);ok,_=assemble(trial)
 if ok:s=trial;tails.append(match.group(1))
print('shortened',accepted,'tailcalls',tails);ok,log=assemble(s+'\n        ASSERT $ <= $ED80\n');assert ok,log
(R/'src/game_pixel_overlay_r78.asm').write_text(s+'\n        ASSERT $ <= $ED80\n');(O/'short_branch_changes.json').write_text(json.dumps(accepted,indent=2));print('overlay bytes',p.with_suffix('.bin').stat().st_size,'branches',accepted)


