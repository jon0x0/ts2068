param(
    [string]$Fuse = 'C:\apps\emulation\Fuse-JLODiskEmulation\fuse-1.9.1-win32\fuse.exe',
    [string]$Disk = '',
    [string]$Cartridge = ''
)
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
if (-not $Disk) { $Disk = Join-Path $project 'build\oliger-cpm.dsk' }
$fusePath = (Resolve-Path -LiteralPath $Fuse).Path
$diskPath = (Resolve-Path -LiteralPath $Disk).Path
$romPath = Join-Path (Split-Path -Parent $fusePath) 'roms\safe265.rom'
if (-not (Test-Path -LiteralPath $romPath)) { throw "Missing JLO ROM: $romPath" }
$diskHeader = [IO.File]::ReadAllBytes($diskPath)
if (-not $Cartridge) {
    $profile = if ($diskHeader[49] -eq 2) { 'oliger320' } else { 'oliger' }
    $Cartridge = Join-Path $project "build\profiles\$profile\ts2068-cpm.dck"
}
$cartPath = (Resolve-Path -LiteralPath $Cartridge).Path
$driveType = if ($diskHeader[49] -eq 2) { '"Double-sided 40 track"' } else { '"Single-sided 40 track"' }
$arguments = @('--machine', 'ts2068', '--jlo', '--rom-jlo', ('"'+$romPath+'"'),
    '--drive-jlo1-type', $driveType, '--disk-try-merge', 'Never',
    '--dock', ('"'+$cartPath+'"'))
$hasDiskOption = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($fusePath)).Contains('jlo0disk')
if ($hasDiskOption) {
    $arguments += @('--jlo0disk', ('"'+$diskPath+'"'))
} else {
    Write-Host 'In Fuse: Media > Disk > JLO > Drive A: (or Drive 0:) > Insert...'
    Write-Host "Select: $diskPath"
    Write-Host 'Then press Enter in the emulated CP/M screen to retry boot.'
}
Write-Host 'To preserve CP/M changes, use the JLO drive menu Save/Save As before exiting.'
Start-Process -FilePath $fusePath -ArgumentList $arguments -WorkingDirectory (Split-Path -Parent $fusePath) -WindowStyle Normal
