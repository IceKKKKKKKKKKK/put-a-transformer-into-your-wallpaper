[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$url = 'http://127.0.0.1:8765/api/health'
try { $health = Invoke-RestMethod $url -TimeoutSec 3 } catch { $health = $null }
if ($health.ready -and $health.service -eq 'transformer-explainer-local' -and $health.cuda_matmul_verified) {
    Write-Output ('Already running on ' + $health.device)
    return
}
if (Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 8765 is occupied. Inspect the existing process; do not kill an unrelated service.'
}
$python = Join-Path $repo '.venv\Scripts\python.exe'
$server = Join-Path $repo 'local\server.py'
if (-not (Test-Path -LiteralPath (Join-Path $repo '.runtime\site\index.html'))) { throw 'Run Install-LocalGpu.ps1 first.' }
$process = Start-Process -FilePath $python -ArgumentList ('"' + $server + '"') -WorkingDirectory $repo -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $repo '.runtime\server.stdout.log') -RedirectStandardError (Join-Path $repo '.runtime\server.stderr.log')
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    Start-Sleep -Seconds 1
    try { $health = Invoke-RestMethod $url -TimeoutSec 2 } catch { $health = $null }
    if ($health.ready -and $health.cuda_matmul_verified) {
        Write-Output ('Ready: ' + $health.device + ' at http://127.0.0.1:8765/')
        return
    }
    if ($process.HasExited) { throw 'GPU service exited. See .runtime/server.stderr.log.' }
}
throw 'GPU startup timed out. See .runtime/server.stderr.log.'
