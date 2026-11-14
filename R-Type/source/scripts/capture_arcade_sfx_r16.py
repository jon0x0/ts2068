from pathlib import Path
import subprocess,json
r=Path(__file__).resolve().parents[1];o=r/'build/audio/arcade';o.mkdir(exist_ok=True)
lua='''local m=manager.machine
local n=0
local ids={53,38,43,48,49,50,52,54,55,56,57,58,80,99}
sub=emu.add_machine_frame_notifier(function()
 n=n+1
 if n==300 then
  local cpu=m.devices[":maincpu"]
  local pc=cpu.state["PC"].value
  cpu.spaces["program"]:write_direct_u8(pc,0xEB)
  cpu.spaces["program"]:write_direct_u8(pc+1,0xFE)
  cpu.state["PSW"].value=cpu.state["PSW"].value&(~0x200)
 end
 for i,id in ipairs(ids) do
  local f=360+(i-1)*180
  if n==f-2 then m.devices[":maincpu"].spaces["io"]:write_u8(0,0) end
  if n==f then m.devices[":maincpu"].spaces["io"]:write_u8(0,id);print("SOUND "..id.." FRAME "..n) end
 end
end)
'''
(o/'isolated.lua').write_text(lua)
cmd=[r'C:/apps/games/MAME/mame.exe','rtype','-noreadconfig','-rompath',str(r/'arcade')+';'+str(r/'build/mame_archival_standins_ff'),'-video','none','-sound','none','-wavwrite',str(o/'isolated.wav'),'-nothrottle','-skip_gameinfo','-seconds_to_run','52','-autoboot_delay','0','-autoboot_script',str(o/'isolated.lua'),'-cfg_directory',str(o),'-nvram_directory',str(o)]
p=subprocess.run(cmd,cwd=r,capture_output=True,text=True,timeout=110);(o/'isolated.log').write_text(p.stdout+p.stderr);print(p.returncode,p.stdout[-800:],p.stderr[-500:])
