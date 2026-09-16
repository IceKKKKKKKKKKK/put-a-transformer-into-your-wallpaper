[CmdletBinding()]
param([string]$Python = 'python', [switch]$EnableStartup)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo
foreach ($command in @('git', 'node', 'nvidia-smi', $Python)) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) { throw "Missing prerequisite: $command" }
}
& $Python -c 'import sys; assert (3,11) <= sys.version_info < (3,13)'
if ($LASTEXITCODE -ne 0) { throw 'Use Python 3.11 or 3.12.' }
$nodeVersion = & node --version
if ($LASTEXITCODE -ne 0 -or [int]($nodeVersion.TrimStart('v').Split('.')[0]) -lt 22) { throw 'Use Node.js 22 or newer.' }
& nvidia-smi --query-gpu=name --format=csv,noheader
if ($LASTEXITCODE -ne 0) { throw 'A working NVIDIA GPU driver is required.' }
New-Item -ItemType Directory -Force .runtime | Out-Null
$upstream = Join-Path $repo '.runtime\upstream'
$revision = 'bfe50afba10b9b560b84143ee1107d977defa74f'
if (-not (Test-Path -LiteralPath (Join-Path $upstream '.git'))) {
    & git init $upstream
    if ($LASTEXITCODE -ne 0) { throw 'git init failed.' }
    & git -C $upstream remote add origin https://github.com/poloclub/transformer-explainer.git
    & git -C $upstream fetch --depth 1 origin $revision
    if ($LASTEXITCODE -ne 0) { throw 'Upstream download failed.' }
    & git -C $upstream checkout --detach FETCH_HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Upstream checkout failed.' }
}
if ((& git -C $upstream rev-parse HEAD).Trim() -ne $revision) { throw 'Unexpected upstream revision; preserve it and inspect manually.' }
$venvPython = Join-Path $repo '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}
& $venvPython -m pip install -r local/requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'GPU dependencies failed to install.' }
& $venvPython local/fetch_assets.py
if ($LASTEXITCODE -ne 0) { throw 'Asset download failed.' }
Copy-Item local/frontend-package.json $upstream/package.json -Force
Copy-Item local/frontend-package-lock.json $upstream/package-lock.json -Force
$ErrorActionPreference = 'Continue' # Windows PowerShell 5 turns native stderr warnings into ErrorRecords.
& node .runtime/npm/package/bin/npm-cli.js --prefix $upstream ci --no-audit --no-fund *> .runtime/npm-install.log
$installExit = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
if ($installExit -ne 0) { Get-Content .runtime/npm-install.log -Tail 30; throw 'Frontend dependency installation failed.' }
& $venvPython local/prepare.py
if ($LASTEXITCODE -ne 0) { throw 'Frontend preparation failed.' }
$ErrorActionPreference = 'Continue'
& node .runtime/npm/package/bin/npm-cli.js --prefix $upstream run build *> .runtime/build.log
$buildExit = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
if ($buildExit -ne 0) { Get-Content .runtime/build.log -Tail 40; throw 'Frontend build failed.' }
New-Item -ItemType Directory -Force .runtime/site | Out-Null
Copy-Item -Path "$upstream/build/*" -Destination .runtime/site -Recurse -Force
& "$PSScriptRoot\Build-Packages.ps1"
& "$PSScriptRoot\Start-LocalGpu.ps1"
if ($EnableStartup) {
    $startup = [Environment]::GetFolderPath('Startup')
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut((Join-Path $startup 'Transformer Explainer Local GPU.lnk'))
    $shortcut.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
    $shortcut.Arguments = '-NoProfile -WindowStyle Hidden -File "' + (Join-Path $PSScriptRoot 'Start-LocalGpu.ps1') + '"'
    $shortcut.WorkingDirectory = $repo
    $shortcut.WindowStyle = 7
    $shortcut.Description = 'Start the local Transformer Explainer CUDA service at sign-in'
    $shortcut.Save()
}
Write-Output 'Local webpage and CUDA model are ready. Import the black or white ZIP into Lively.'
