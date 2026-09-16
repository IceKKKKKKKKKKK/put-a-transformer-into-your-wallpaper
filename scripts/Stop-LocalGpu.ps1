[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$serverArgument = '"' + (Join-Path $repo 'local\server.py') + '"'
# Match this exact service entry point, never all Python processes or a recycled PID.
$targets = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object {
    $_.CommandLine -and $_.CommandLine.EndsWith($serverArgument, [StringComparison]::OrdinalIgnoreCase)
})
foreach ($target in $targets) { Stop-Process -Id $target.ProcessId -ErrorAction SilentlyContinue }
Write-Output 'Local GPU service stopped. Lively remains installed; run Start-LocalGpu.ps1 to resume.'
