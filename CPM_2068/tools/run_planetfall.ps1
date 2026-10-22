param([string]$Fuse = 'C:\apps\emulation\Fuse-JLODiskEmulation\fuse-1.9.1-win32\fuse.exe')
$project = Split-Path -Parent $PSScriptRoot
& (Join-Path $PSScriptRoot 'run_oliger.ps1') -Fuse $Fuse -Cartridge (Join-Path $project 'build\planetfall-cpm.dck') -Disk (Join-Path $project 'build\planetfall-cpm.dsk')
Write-Host 'At the CP/M A> prompt, type PLANET to play.'
