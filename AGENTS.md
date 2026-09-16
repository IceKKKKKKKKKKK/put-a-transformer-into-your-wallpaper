# Install this wallpaper on the user's Windows computer

This repository contains a small presentation wrapper for the original remote Transformer Explainer, not a fork of its visualization or model. Read README.md and CREDIT.md. Preserve the attribution and exact phrase `its a legendary incredible work` in public descriptions. Never imply authorship of the upstream work.

## Scope and prerequisites

- Work on the target Windows host with local shell/file access. Windows GUI automation is needed for fully automatic Lively import and settings. Do not imply that a cloud checkout can change the user's desktop.
- Use the user's chosen theme (`black` or `white`) and Windows display number. If either is missing, ask only for that choice while inspecting prerequisites. Do not assume a display number is a Lively monitor index.
- Read applicable computer-use instructions before GUI work. Do not change Codex security settings or bypass a permission prompt to make this work. If GUI access is unavailable, prepare the ZIP and ask the user to perform the exact import step, then continue checks.
- Preserve other applications, wallpapers, display resolution, scaling, orientation, and primary-display selection. Never restart Windows automatically. Do not clear model caches.

## Install and apply

1. Inspect Windows version, `winget`, installed Lively and WebView2, and the current screen arrangement. Record the current Lively assignments/settings locally outside this repo. Identify the intended screen by its displayed Windows number and geometry, then compare against Lively's monitor selector. Ask the user to identify the screen if the mapping cannot be verified.
2. If Lively is absent, install its official package with `winget install --id rocksdanister.LivelyWallpaper --exact --source winget`. Respect any interactive installer prompt. Use the official WebView2 dependency if needed. Do not reinstall or upgrade a working installation unnecessarily. An existing Store installation may have different paths from a standalone installation.
3. Use the matching `dist/Transformer-Explainer-black.zip` or `dist/Transformer-Explainer-white.zip`. Rebuild with `powershell -File scripts/Build-Packages.ps1` only if the source changed or the packages are absent. ZIP contents must be at the archive root, with a relative `index.html` in `LivelyInfo.json`.
4. Open Lively's official **Add Wallpaper -> Choose a file** flow and select the ZIP. Complete the import. A bare external folder passed to `setwp` is not an import and may do nothing. Do not write Lively's internal library database to simulate an import.
5. Select the verified target screen and apply the imported wallpaper with **Per Screen** arrangement. If the user already uses a Span or Duplicate arrangement, explain the impact and resolve that conflict before replacing it. Keep all other per-screen assignments intact.
6. Set the web player to **WebView2**, enable disk cache, and enable **Keyboard** input (which includes mouse). Explain that Lively hides desktop icons globally in Keyboard mode; if that conflicts with the user's preferences, offer mouse-only input. Enable pointer movement forwarding if that control is available. Enable Start with Windows, pause on fullscreen apps, and continue with ordinary focused windows.
7. Close the upstream tutorial overlay. Wait until model loading finishes and Generate is enabled. First load may fetch roughly 600 MB; do not mistake slow model initialization for a failed installation.
8. Center the visualization. Default iframe height is 900 px and offset is 0. Use **Customize Wallpaper** to adjust `frameHeight` and `verticalOffset` to the actual screen; positive offset moves down. Check the diagram itself, not only the surrounding page. `theme` is a dropdown: 0 = Black, 1 = White.

## Supported CLI after import

Find the actual Lively executable and configured library path; do not hard-code the original author's user profile or wallpaper folder. Inspect the installed `LivelyInfo.json` to identify the exact imported title and index file. Once registered, these official commands can help:

```powershell
& $livelyExe setwp --file $registeredWallpaperDirectory --monitor $verifiedLivelyIndex
& $livelyExe setprop --monitor $verifiedLivelyIndex --property 'theme=0'
& $livelyExe seekwp --monitor $verifiedLivelyIndex --value 0
```

Use `theme=1` for white. Run only with discovered paths and verified indices. See the official [CLI documentation](https://github.com/rocksdanister/lively/wiki/Command-Line-Controls), [web player documentation](https://github.com/rocksdanister/lively/wiki/Web-Player), and [package format](https://github.com/rocksdanister/lively/wiki/Lively-Wallpaper-File).

## Verify before reporting success

- Inspect the actual target desktop: correct screen, chosen theme, centered diagram, and taskbar still available. A screenshot of a separate browser is not proof of desktop installation.
- On the desktop itself, click the prompt, enter a harmless test such as `The cat sat on the`, and click Generate. Confirm changed output, working hover/click controls, and no duplicate typed characters. Explore one Attention/QKV or MLP control and a sampling control.
- Keep configuration evidence separate from behavior evidence. If the tool cannot target the wallpaper window, ask the user to try the interaction; do not claim an input test passed from a screenshot or an enabled setting.
- Verify the previous assignments and Windows screen geometry are unchanged on every other monitor. Check startup is enabled; do not claim boot recovery was tested without an actual observation. An optional Lively-only restart can check app recovery, but it interrupts every active Lively wallpaper, so preserve them all and avoid doing it needlessly.
- Screenshot commands may stall while a wallpaper is paused behind a fullscreen app. Return to the desktop/resume normally, then retry; do not delete caches or leave fullscreen pausing disabled.
- Report the target screen, theme, installed location, successful checks, and any remaining user verification briefly. Keep machine-specific evidence out of commits and publications.

## Development and publication

Edit the wrapper in `src/index.html`; run `scripts/Build-Packages.ps1` to refresh both ZIPs. Check both archives: valid metadata, relative `index.html`, correct default theme/dropdown value, and attribution files. Keep black and white behavior identical apart from presentation.

Only publish repository files and reviewed demonstration media. Do not commit logs, model caches, credentials, personal paths, baseline settings, or unrelated workspace files. A recording must show real interaction and identify the actual environment; do not present a browser preview as a desktop interaction test. Preserve the taskbar when requested, and inspect the recording for unrelated private windows or notifications before upload.
