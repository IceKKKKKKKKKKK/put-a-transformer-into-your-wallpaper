# Install this wallpaper on the user's Windows computer

This repository contains a presentation wrapper and local CUDA transport adapter for the original Transformer Explainer. Read README.md, LOCAL_GPU.md, and CREDIT.md. The visualization and ONNX model remain the work of the upstream team; local integration patches are in local/prepare.py. Preserve the attribution and exact phrase `its a legendary incredible work` in public descriptions. Never imply authorship of the upstream work.

## Scope and prerequisites

- Work on the target Windows host with local shell/file access. Windows GUI automation is needed for fully automatic Lively import and settings. Do not imply that a cloud checkout can change the user's desktop.
- Use the user's chosen theme (`black` or `white`) and Windows display number. If either is missing, ask only for that choice while inspecting prerequisites. Do not assume a display number is a Lively monitor index.
- Read applicable computer-use instructions before GUI work. Do not change Codex security settings or bypass a permission prompt to make this work. If GUI access is unavailable, prepare the ZIP and ask the user to perform the exact import step, then continue checks.
- Preserve other applications, wallpapers, display resolution, scaling, orientation, and primary-display selection. Never restart Windows automatically. Do not clear model caches.

## Install and apply

1. Inspect Windows version, `winget`, installed Lively and WebView2, and the current screen arrangement. Record the current Lively assignments/settings locally outside this repo. Identify the intended screen by its displayed Windows number and geometry, then compare against Lively's monitor selector. Ask the user to identify the screen if the mapping cannot be verified.
2. If Lively is absent, install its official package with `winget install --id rocksdanister.LivelyWallpaper --exact --source winget`. Respect any interactive installer prompt. Use the official WebView2 dependency if needed. Do not reinstall or upgrade a working installation unnecessarily. An existing Store installation may have different paths from a standalone installation.
3. Verify Python 3.11/3.12, Node.js 22+, Git, and a working CUDA-capable NVIDIA GPU/driver. Run `scripts/Install-LocalGpu.ps1 -EnableStartup`; use an explicit Python executable if needed. Do not silently switch to CPU-only inference or change GPU drivers. Require `/api/health` to report CUDA readiness and verified CUDA MatMul. Then use the matching `dist/Transformer-Explainer-black.zip` or `dist/Transformer-Explainer-white.zip`. Rebuild with `powershell -File scripts/Build-Packages.ps1` only if the source changed or the packages are absent. ZIP contents must be at the archive root, with a relative `index.html` in `LivelyInfo.json`.
4. Open Lively's official **Add Wallpaper -> Choose a file** flow and select the ZIP. Complete the import. A bare external folder passed to `setwp` is not an import and may do nothing. Do not write Lively's internal library database to simulate an import.
5. Select the verified target screen and apply the imported wallpaper with **Per Screen** arrangement. If the user already uses a Span or Duplicate arrangement, explain the impact and resolve that conflict before replacing it. Keep all other per-screen assignments intact.
6. Set the web player to **WebView2** and enable disk cache. Start with **Mouse** input mode and test direct typing after focusing the webpage. Lively documents duplicate keystrokes when Keyboard forwarding and direct wallpaper focus both receive the same key; Mouse mode is the official workaround. Only try Keyboard forwarding if focus/loading are correct but direct typing fails, and test for duplicates before keeping it. Keyboard mode hides desktop icons globally; preserve the user's existing icon visibility if changing modes. Enable pointer movement forwarding if available. Enable Start with Windows, pause on fullscreen apps, and continue with ordinary focused windows.
7. The local adapter starts with the tutorial closed. Wait until the **Model** and **Inference · CUDA** status appears and Generate is enabled on the actual desktop. The webpage, tokenizer, fonts, and model must be local; no remote model loading is expected after setup. The upstream app disables prompt editing during inference, while a diagram block is expanded, or while a weight popover is open. If the local service is unavailable, run `scripts/Start-LocalGpu.ps1`, inspect `.runtime/server.stderr.log`, and reapply only the target wallpaper if necessary. Preview uses a separate browser profile and is not proof that the installed instance works.
8. Center the visualization. Default iframe height is 900 px and offset is 0. Use **Customize Wallpaper** to adjust `frameHeight` and `verticalOffset` to the actual screen; positive offset moves down. Check the diagram itself, not only the surrounding page. `theme` is a dropdown: 0 = Black, 1 = White.
9. If the user reports the mouse pointer disappearing after clicking the prompt or typing, inspect `scripts/Fix-MousePointer.ps1 -CheckOnly`. WebView2 has a reported interaction with Windows' **Hide pointer while typing** option. Explain that disabling it affects the current Windows user across applications, then use the helper within the user's requested repair scope. It backs up the old value and supports `-Restore`. Keep Mouse input mode and the user's cursor theme unchanged, and verify behavior on the actual desktop. Do not apply this setting to every installation without the symptom.

## Supported CLI after import

Find the actual Lively executable and configured library path; do not hard-code the original author's user profile or wallpaper folder. Inspect the installed `LivelyInfo.json` to identify the exact imported title and index file. Once registered, these official commands can help:

```powershell
& $livelyExe setwp --file $registeredWallpaperDirectory --monitor $verifiedLivelyIndex
& $livelyExe setprop --monitor $verifiedLivelyIndex --property 'theme=0'
```

For a stuck WebView2 wallpaper, close and reapply the registered project on only the target screen. Lively 2.2.1.0's WebView2 reload-message handler does nothing, so do not rely on `seekwp --value 0` as a successful reload for that version. Wait for the close to finish before reapplying.

```powershell
& $livelyExe closewp --monitor $verifiedLivelyIndex
# Verify the target wallpaper has closed before continuing.
& $livelyExe setwp --file $registeredWallpaperDirectory --monitor $verifiedLivelyIndex
```

Use `theme=1` for white. Run only with discovered paths and verified indices. See the official [CLI documentation](https://github.com/rocksdanister/lively/wiki/Command-Line-Controls), [web player documentation](https://github.com/rocksdanister/lively/wiki/Web-Player), and [package format](https://github.com/rocksdanister/lively/wiki/Lively-Wallpaper-File).

## Verify before reporting success

- Inspect the actual target desktop: correct screen, chosen theme, centered diagram, and taskbar still available. A screenshot of a separate browser is not proof of desktop installation.
- On the desktop itself, click the prompt, enter a harmless test such as `The cat sat on the`, and click Generate. Confirm changed output, working hover/click controls, and no duplicate typed characters. Explore one Attention/QKV or MLP control and a sampling control.
- Keep configuration evidence separate from behavior evidence. If the tool cannot target the wallpaper window, ask the user to try the interaction; do not claim an input test passed from a screenshot or an enabled setting.
- Verify the previous assignments and Windows screen geometry are unchanged on every other monitor. Check both Lively startup and the current-user **Transformer Explainer Local GPU** Startup shortcut; do not claim boot recovery was tested without an actual observation. An optional Lively-only restart can check app recovery, but it interrupts every active Lively wallpaper, so preserve them all and avoid doing it needlessly.
- Screenshot commands may stall while a wallpaper is paused behind a fullscreen app. Return to the desktop/resume normally, then retry; do not delete caches or leave fullscreen pausing disabled.
- Report the target screen, theme, installed location, successful checks, and any remaining user verification briefly. Keep machine-specific evidence out of commits and publications.

## Development and publication

Keep `.runtime` and `.venv` out of git. Preserve the pinned model checksum, original credit, local-only runtime asset policy, and verified GPU requirement. The existing resource chart measures the old browser CPU version and must not be presented as a CUDA benchmark.

Edit the wrapper in `src/index.html`; run `scripts/Build-Packages.ps1` to refresh both ZIPs. Check both archives: valid metadata, relative `index.html`, correct default theme/dropdown value, and attribution files. Keep black and white behavior identical apart from presentation.

Only publish repository files and reviewed demonstration media. Do not commit logs, model caches, credentials, personal paths, baseline settings, or unrelated workspace files. A recording must show real interaction and identify the actual environment; do not present a browser preview as a desktop interaction test. Preserve the taskbar when requested, and inspect the recording for unrelated private windows or notifications before upload.
