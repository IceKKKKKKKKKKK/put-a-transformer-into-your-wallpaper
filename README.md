# Transformer Explainer Wallpaper

Use [Transformer Explainer](https://poloclub.github.io/transformer-explainer/) as an interactive Windows 11 desktop wallpaper, centered on your screen, with **black and white themes**.

All visualization and model credit belongs to the original **[Transformer Explainer team / Polo Club](https://github.com/poloclub/transformer-explainer)**.

> its a legendary incredible work

This independent project provides only the Lively wrapper, centering, themes, and installation guide. It does not claim authorship of Transformer Explainer and is not an official affiliated project. See [CITATION.bib](CITATION.bib) for the original paper and [CREDIT.md](CREDIT.md) for full attribution.

## Install with Codex

You need Windows 11 and **Codex running locally on that computer with terminal and Windows UI access**. Copy either prompt below. Replace "Windows display 1" with your preferred screen.

**Black theme:**

```text
Clone https://github.com/IceKKKKKKKKKKK/transformer-explainer-wallpaper and read AGENTS.md. Complete the Lively installation and setup, then apply the black Transformer Explainer wallpaper to Windows display 1. Verify the display mapping, preserve the other screens, enable mouse and keyboard interaction, caching, and startup, and test typing and generation on the actual desktop. Do not restart Windows automatically.
```

**White theme:**

```text
Clone https://github.com/IceKKKKKKKKKKK/transformer-explainer-wallpaper and read AGENTS.md. Complete the Lively installation and setup, then apply the white Transformer Explainer wallpaper to Windows display 1. Verify the display mapping, preserve the other screens, enable mouse and keyboard interaction, caching, and startup, and test typing and generation on the actual desktop. Do not restart Windows automatically.
```

Without desktop control, Codex can prepare the files, but you will need to help with ZIP import and the final interaction check. A cloud Codex session cannot directly configure another computer's Windows desktop.

## Manual installation

1. Install the official [Lively Wallpaper](https://www.rocksdanister.com/lively/).
2. Download the [black ZIP](https://github.com/IceKKKKKKKKKKK/transformer-explainer-wallpaper/raw/refs/heads/main/dist/Transformer-Explainer-black.zip) or [white ZIP](https://github.com/IceKKKKKKKKKKK/transformer-explainer-wallpaper/raw/refs/heads/main/dist/Transformer-Explainer-white.zip). In Lively, use **Add Wallpaper → Choose a file** to import the ZIP.
3. Select your screen, use **Per Screen**, and choose **WebView2** as the web player. Enable mouse/keyboard input and disk caching in Settings. Wait for the model to load, type a prompt, and click **Generate**.

Use **Customize Wallpaper** to switch the theme or adjust the webpage height and vertical offset. The default frame is 900 px high and centered on a 2560 × 1440 display; adjust it for your own screen.

- Black uses CSS inversion with hue compensation, so colors differ slightly from the original. White preserves the upstream appearance.
- Lively's **Keyboard** input mode includes mouse support but hides Windows desktop icons globally. To keep your icons, use mouse-only mode and enter text in a separate browser window.
- The first load downloads a large model (approximately 600 MB) and requires internet access. The wallpaper continues to depend on the original website. No model weights or persistent local server are bundled.
- Configure startup, fullscreen pausing, and continued playback behind ordinary windows in Lively Settings.

## Development

Edit `src/index.html`, then run `powershell -File scripts/Build-Packages.ps1` to build both importable ZIPs. The repository contains no personal display configuration, caches, or model weights.

Wallpaper wrapper: MIT. Upstream attribution and license: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Installation details follow [Lively's documentation](https://github.com/rocksdanister/lively/wiki).
