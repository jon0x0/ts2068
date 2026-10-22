param([string]$Fuse = 'C:\apps\emulation\Fuse-JLODiskEmulation\fuse-1.9.1-win32\fuse.exe')
$project = Split-Path -Parent $PSScriptRoot
& (Join-Path $PSScriptRoot 'run_oliger.ps1') -Fuse $Fuse -Cartridge (Join-Path $project 'build\infocom-cpm.dck') -Disk (Join-Path $project 'build\infocom-cpm.dsk')
Write-Host 'At A>, type PLANET, ZORK1, HI, or SUBMIT DEMO.'
