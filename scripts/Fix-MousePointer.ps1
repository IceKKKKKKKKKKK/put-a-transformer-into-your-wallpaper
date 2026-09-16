[CmdletBinding(DefaultParameterSetName = 'Apply')]
param(
    [Parameter(ParameterSetName = 'Check')][switch]$CheckOnly,
    [Parameter(ParameterSetName = 'Restore')][switch]$Restore
)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'This workaround is for Windows only.' }

# WebView2 can leave the pointer hidden after typing. Change the documented
# Windows preference instead of injecting a cursor or altering input forwarding.
# https://github.com/MicrosoftEdge/WebView2Feedback/issues/5708
if (-not ('TransformerWallpaper.PointerPreference' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
namespace TransformerWallpaper {
    public static class PointerPreference {
        [DllImport("user32.dll", EntryPoint = "SystemParametersInfoW", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool Read(uint action, uint param, out int value, uint flags);
        [DllImport("user32.dll", EntryPoint = "SystemParametersInfoW", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool Write(uint action, uint param, IntPtr value, uint flags);
    }
}
'@
}

function Get-HidePointerWhileTyping {
    $value = 0
    if (-not [TransformerWallpaper.PointerPreference]::Read(0x1020, 0, [ref]$value, 0)) {
        throw [ComponentModel.Win32Exception]::new([Runtime.InteropServices.Marshal]::GetLastWin32Error())
    }
    return [bool]$value
}

$before = Get-HidePointerWhileTyping
if ($CheckOnly) {
    [pscustomobject]@{ HidePointerWhileTyping = $before }
    return
}

$backupDirectory = Join-Path $env:LOCALAPPDATA 'TransformerExplainerWallpaper'
$backupPath = Join-Path $backupDirectory 'pointer-preference.json'
$desired = $false
if ($Restore) {
    if (-not (Test-Path -LiteralPath $backupPath)) { throw 'No saved pointer preference exists.' }
    $backup = Get-Content -LiteralPath $backupPath -Raw | ConvertFrom-Json
    if ($backup.Version -ne 1 -or $backup.HidePointerWhileTyping -isnot [bool]) {
        throw 'The saved pointer preference is invalid; no setting was changed.'
    }
    $desired = $backup.HidePointerWhileTyping
} elseif (-not (Test-Path -LiteralPath $backupPath)) {
    New-Item -ItemType Directory -Path $backupDirectory -Force | Out-Null
    [ordered]@{ Version = 1; HidePointerWhileTyping = $before } |
        ConvertTo-Json | Set-Content -LiteralPath $backupPath -Encoding UTF8
}

if ($before -ne $desired) {
    # SPI_SETMOUSEVANISH; persist for this user and notify running applications.
    if (-not [TransformerWallpaper.PointerPreference]::Write(0x1021, 0, [IntPtr]([int]$desired), 3)) {
        throw [ComponentModel.Win32Exception]::new([Runtime.InteropServices.Marshal]::GetLastWin32Error())
    }
}
$after = Get-HidePointerWhileTyping
if ($after -ne $desired) { throw 'Windows did not retain the requested pointer preference.' }
[pscustomobject]@{
    PreviousHidePointerWhileTyping = $before
    HidePointerWhileTyping = $after
    Changed = ($before -ne $after)
    Scope = 'Current Windows user; all applications'
    Backup = $backupPath
}
