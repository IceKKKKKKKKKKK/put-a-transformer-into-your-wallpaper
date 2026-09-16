# Transformer Explainer Wallpaper

把 [Transformer Explainer](https://poloclub.github.io/transformer-explainer/) 变成 Windows 11 的可交互桌面壁纸，主体居中，提供 **黑色 / 白色** 两种选择。

All visualization and model credit belongs to the original **[Transformer Explainer team / Polo Club](https://github.com/poloclub/transformer-explainer)**.

> its a legendary incredible work

本项目仅提供 Lively 壁纸外框、居中布局、配色与安装指引。不是 Transformer Explainer 的作者，也不是官方关联项目。论文引用见 [CITATION.bib](CITATION.bib)，完整致谢见 [CREDIT.md](CREDIT.md)。

## 交给 Codex 安装

需要 Windows 11，以及**运行在这台电脑上、可访问终端和 Windows 界面的 Codex**。让 Codex 克隆本仓库并读取 [AGENTS.md](AGENTS.md)，复制下面任意一段即可；将“显示器 1”换成你要使用的屏幕。

**黑色：**

```text
请克隆 https://github.com/IceKKKKKKKKKKK/transformer-explainer-wallpaper，读取仓库 AGENTS.md，完成整套 Lively 安装和配置，把黑色 Transformer Explainer 壁纸应用到 Windows 显示器 1。核对屏幕映射，保留其他屏幕设置，启用鼠标和键盘交互、缓存及开机启动，并验证真实桌面输入和生成。不要自动重启 Windows。
```

**白色：**

```text
请克隆 https://github.com/IceKKKKKKKKKKK/transformer-explainer-wallpaper，读取仓库 AGENTS.md，完成整套 Lively 安装和配置，把白色 Transformer Explainer 壁纸应用到 Windows 显示器 1。核对屏幕映射，保留其他屏幕设置，启用鼠标和键盘交互、缓存及开机启动，并验证真实桌面输入和生成。不要自动重启 Windows。
```

Codex 没有桌面控制能力时，仍能准备文件；ZIP 导入和最终交互检查需要你配合。云端 Codex 无法直接设置另一台 Windows 电脑的桌面。

## 也可以直接安装

1. 安装官方 [Lively Wallpaper](https://www.rocksdanister.com/lively/)。
2. 下载 [黑色 ZIP](https://github.com/IceKKKKKKKKKKK/transformer-explainer-wallpaper/raw/refs/heads/main/dist/Transformer-Explainer-black.zip) 或 [白色 ZIP](https://github.com/IceKKKKKKKKKKK/transformer-explainer-wallpaper/raw/refs/heads/main/dist/Transformer-Explainer-white.zip)，在 Lively 里选择 **Add Wallpaper → Choose a file** 导入 ZIP。
3. 选择目标屏幕，使用 **Per Screen**；网页引擎选 **WebView2**。在设置中开启鼠标/键盘输入与磁盘缓存，等待模型加载后输入文字并点 **Generate**。

在 **Customize Wallpaper** 中可随时切换 Theme，调整网页高度与上下位置。默认高度 900 px，在 2560 × 1440 屏幕上居中显示；其他屏幕可自行微调。

- 黑色通过 CSS 反色及色相补偿实现，颜色会与原站略有不同；白色保留原站配色。
- Lively 的 **Keyboard** 输入模式也支持鼠标，但会隐藏 Windows 桌面图标。这是全局行为；若需要保留图标，可使用鼠标模式并在浏览器里输入文字。
- 首次加载会下载较大的模型（约 600 MB），需要联网；后续仍依赖原站。没有打包模型，也不需要常驻本地服务器。
- 开机启动、全屏时暂停、普通窗口下继续播放，可在 Lively 设置中配置。

## 开发

修改 `src/index.html` 后运行 `powershell -File scripts/Build-Packages.ps1`，生成两份可直接导入的 ZIP。仓库不包含个人显示器配置、缓存或模型权重。

Wallpaper wrapper: MIT. Upstream attribution and license: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Installation details follow [Lively's documentation](https://github.com/rocksdanister/lively/wiki).
