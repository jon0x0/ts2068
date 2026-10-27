param([string]$Port = 'COM14')
$ErrorActionPreference = 'Stop'
$helper = Join-Path $PSScriptRoot 'pico_debug.py'
$queueRoot = Join-Path $PSScriptRoot 'build/serial-debug'
foreach ($folder in @('pending', 'running')) {
    $folderPath = Join-Path $queueRoot $folder
    if ((Test-Path -LiteralPath $folderPath) -and
        @(Get-ChildItem -LiteralPath $folderPath -Filter '*.json').Count) {
        throw "Existing $folder jobs need inspection before starting another SD session."
    }
}
$files = @('personality128.py', 'personality128_stock.py', 'fs128_legacy.py',
           'personality128_fs.py', 'fs128_image.py')
for ($index = 0; $index -lt $files.Count; $index++) {
    $description = "$($index + 1)/6 Definitions only. KEEP TS RESET RELEASED."
    & python $helper queue load --file $files[$index] --description $description
    if ($LASTEXITCODE -ne 0) { throw 'Could not queue definitions.' }
}
& python $helper queue fs128-basic-run --description '6/6 HOLD TS RESET, Enter, RELEASE AT ARMED. Service stays running; then use 128 BASIC on Timex.'
if ($LASTEXITCODE -ne 0) { throw 'Could not queue SD service.' }
& python $helper serve --port $Port --timeout 180 --interrupt
exit $LASTEXITCODE
