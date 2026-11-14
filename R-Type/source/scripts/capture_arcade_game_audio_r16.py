from pathlib import Path
import subprocess,json
r=Path(__file__).resolve().parents[1];o=r/'build/audio/arcade';o.mkdir(exist_ok=True)
lua='''local m=manager.machine
local n=0
local function key(text,value)
 for _,port in pairs(m.ioport.ports) do for _,field in pairs(port.fields) do
  if field.name==text then field:set_value(value);print("KEY "..text.." "..value) end
 end end
end
tap=m.devices[":maincpu"].spaces["io"]:install_write_tap(0,1,"soundcommands",function(offset,data,mask) print("EVENT "..n.." "..(data&255)) end)
sub=emu.add_machine_frame_notifier(function()
 n=n+1
 if n==1 then for _,port in pairs(m.ioport.ports) do for _,field in pairs(port.fields) do print("INPUT "..field.name) end end end
 if n==720 then key("Coin 1",1) end
 if n==730 then key("Coin 1",0) end
 if n==780 then key("1 Player Start",1) end
 if n==790 then key("1 Player Start",0) end
 if n>=1100 and n<=1600 and n%10==0 then key("P1 Button 1",1);key("P1 Button 2",1) end
 if n>=1100 and n<=1600 and n%10==5 then key("P1 Button 1",0);key("P1 Button 2",0) end
end)
'''
(o/'gameplay.lua').write_text(lua)
cmd=[r'C:/apps/games/MAME/mame.exe','rtype','-noreadconfig','-rompath',str(r/'arcade')+';'+str(r/'build/mame_archival_standins_ff'),'-video','none','-sound','none','-wavwrite',str(o/'gameplay.wav'),'-nothrottle','-skip_gameinfo','-seconds_to_run','40','-autoboot_delay','0','-autoboot_script',str(o/'gameplay.lua'),'-cfg_directory',str(o),'-nvram_directory',str(o)]
p=subprocess.run(cmd,cwd=r,capture_output=True,text=True,timeout=110);(o/'gameplay.log').write_text(p.stdout+p.stderr);print(p.returncode,p.stdout[-800:],p.stderr[-500:])
