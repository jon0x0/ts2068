"""Reproduce r6 title palette oscillation and verify r7 avoids menu repaints."""
from pathlib import Path
import subprocess,re,json
ROOT=Path(__file__).resolve().parents[1]
def run(name,lines):
 out=ROOT/'build/diagnostics/r7_title';out.mkdir(parents=True,exist_ok=True);program='\n'.join(lines);(out/(name+'.commands')).write_text(program)
 si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
 p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(ROOT/f'build/ecm_native/RType_level1_ECM_TSPico_RAM_{name}.dck'),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=25,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
 (out/(name+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 return [int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)]
def main():
 r6=(ROOT/'build/ecm_native/RType_level1_ECM_TSPico_RAM_r6.bin').read_bytes()
 signature=bytes.fromhex('21 00 58 11 00 60 01 00 03 cd');positions=[i for i in range(8192) if r6.startswith(signature,i) and r6[i+12]==0xcd];assert len(positions)==1
 a=positions[0];mirror=int.from_bytes(r6[a+10:a+12],'little');title=int.from_bytes(r6[a+13:a+15],'little');after=a+15
 # y106,x=3 contains logo pixels; use actual recoloured byte where legacy differs.
 data=(ROOT/'build/ecm_native/title_chroma_attributes.rle').read_bytes();attrs=b''.join(bytes([data[i+1]])*data[i] for i in range(0,len(data),2))
 sample=next((i,v) for i,v in enumerate(attrs) if v==0x45);y=100+sample[0]//30;x=1+sample[0]%30;addr=0x6000+((y&192)<<5)+((y&7)<<8)+((y&56)<<2)+x
 lines=['set $n 0',f'breakpoint {mirror} if spectrum:frames >= 2800 && spectrum:frames < 3000 && z80:bc == 768 && $n < 3',f'breakpoint {title} if spectrum:frames >= 2800 && $n < 3',f'breakpoint {after} if spectrum:frames >= 2800 && $n < 3',f'breakpoint {mirror} if $n == 3','breakpoint time 100 if spectrum:frames == 3200']
 for i in (1,2,3):
  lines += [f'commands {i}',f'print {i}',f'print [{addr}]']
  if i==3:lines+=['set $n $n+1']
  lines+=['continue','end']
 lines += ['commands 4','exit','end','commands 5','exit 1','end']
 v=run('r6',lines);events=list(zip(v[::2],v[1::2]));before=[value for stage,value in events if stage==2];after_values=[value for stage,value in events if stage==3];assert len(before)==len(after_values)==3 and all(a!=b for a,b in zip(before,after_values)),events
 sym=(ROOT/'build/ecm_native/renderer.sym').read_text();mirror7=int(re.search(r'mirror_attributes: EQU 0x([0-9a-fA-F]+)',sym).group(1),16)
 lines=['set $n 0','set $mirrors 0','breakpoint 0x1a00 if spectrum:frames >= 2800 && spectrum:frames < 3000',f'breakpoint {mirror7} if spectrum:frames >= 2800 && spectrum:frames < 3000','breakpoint time 100 if spectrum:frames == 3000','commands 1','set $n $n+1','continue','end','commands 2','set $mirrors $mirrors+1','continue','end','commands 3','print $n','print $mirrors','out 244 11','print [0x3ff0]','exit','end']
 w=run('r8',lines);assert len(w)==3 and w[0]>0 and w[1:]==[0,0],w
 result=dict(r6_attribute_address=hex(addr),r6_before_after_recolour=list(zip(before,after_values)),r6_tagged_events=events,r8_menu_input_calls=w[0],r8_menu_plane_repaints=w[1],r8_video_mode=w[2]);(ROOT/'build/diagnostics/r7_title/validation.json').write_text(json.dumps(result,indent=2));print(result)
if __name__=='__main__':main()
