[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $repo 'dist'
$build = Join-Path $repo '.build'
$utf8 = New-Object System.Text.UTF8Encoding($false)
New-Item -ItemType Directory -Force -Path $dist, $build | Out-Null

foreach ($theme in @('black', 'white')) {
    $stage = Join-Path $build $theme
    New-Item -ItemType Directory -Force -Path $stage | Out-Null
    $html = [IO.File]::ReadAllText((Join-Path $repo 'src\index.html'))
    $html = $html.Replace('data-theme="black"', ('data-theme="' + $theme + '"'))
    [IO.File]::WriteAllText((Join-Path $stage 'index.html'), $html, $utf8)
    $info = [ordered]@{
        AppVersion = '2.2.1.0'
        Title = "Transformer Explainer - $theme"
        Desc = "Centered interactive wallpaper. Visualization and model by Polo Club's Transformer Explainer; independent Lively wrapper. See CREDIT.md."
        Author = 'Polo Club of Data Science (visualization); IceKKKKKKKKKKK (wallpaper wrapper)'
        Contact = 'https://github.com/IceKKKKKKKKKKK/transformer-explainer-wallpaper'
        Type = 1
        FileName = 'index.html'
        Arguments = ''
        IsAbsolutePath = $false
    }
    $themeIndex = 0
    if ($theme -eq 'white') { $themeIndex = 1 }
    $properties = [ordered]@{
        theme = [ordered]@{ type = 'dropdown'; value = $themeIndex; text = 'Theme'; items = @('Black', 'White') }
        frameHeight = [ordered]@{ type = 'slider'; value = 900; text = 'Webpage height (pixels)'; min = 700; max = 1440; step = 10 }
        verticalOffset = [ordered]@{ type = 'slider'; value = 0; text = 'Vertical adjustment (positive moves down)'; min = -200; max = 200; step = 10 }
    }
    [IO.File]::WriteAllText((Join-Path $stage 'LivelyInfo.json'), ($info | ConvertTo-Json -Depth 6), $utf8)
    [IO.File]::WriteAllText((Join-Path $stage 'LivelyProperties.json'), ($properties | ConvertTo-Json -Depth 6), $utf8)
    foreach ($name in @('LICENSE', 'CREDIT.md', 'CITATION.bib', 'THIRD_PARTY_NOTICES.md')) {
        Copy-Item -LiteralPath (Join-Path $repo $name) -Destination (Join-Path $stage $name) -Force
    }
    # Explicit allowlist: never package a user's Lively settings, cache, or logs.
    $files = @('index.html', 'LivelyInfo.json', 'LivelyProperties.json', 'LICENSE', 'CREDIT.md', 'CITATION.bib', 'THIRD_PARTY_NOTICES.md') |
        ForEach-Object { Join-Path $stage $_ }
    $zip = Join-Path $dist "Transformer-Explainer-$theme.zip"
    Compress-Archive -LiteralPath $files -DestinationPath $zip -Force
    Write-Output $zip
}
