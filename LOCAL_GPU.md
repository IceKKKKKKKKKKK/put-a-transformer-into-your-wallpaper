# Fully local webpage and GPU inference

This mode serves the webpage from **http://127.0.0.1:8765/** and runs Polo Club's original GPT-2 ONNX model with **ONNX Runtime CUDA**. The visualization still receives all 720 attention tensors and the next-token logits. This is a local transport adaptation, not a different model or newly trained model.

> its a legendary incredible work

Credit: [Transformer Explainer / Polo Club](https://github.com/poloclub/transformer-explainer). Please retain [CREDIT.md](CREDIT.md), [CITATION.bib](CITATION.bib), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Install once

Prerequisites: Windows 11, a CUDA-capable NVIDIA GPU with a working CUDA 12-compatible driver, Python **3.11 or 3.12**, Node.js **22 or newer**, Git, and Lively Wallpaper with WebView2. The verified machine uses an RTX 4090. Other GPUs are not yet tested. Allow several GB of downloads and at least 10 GB of free disk space for the source checkout, dependencies, and model.

From a local PowerShell in this repository:

```powershell
./scripts/Install-LocalGpu.ps1 -EnableStartup
```

If Python is not on PATH, pass `-Python` with the full path to a Python 3.11/3.12 executable. The installer creates an isolated `.venv`; it does not replace system PyTorch, install a system CUDA toolkit, change the NVIDIA driver, or restart Windows.

Then import `dist/Transformer-Explainer-black.zip` or `dist/Transformer-Explainer-white.zip` through Lively's Add Wallpaper flow. The ZIPs are small presentation wrappers: run the local installer first. See [AGENTS.md](AGENTS.md) for display selection, input settings, centering, and verification.

With WebView2, use Lively's **Mouse** input mode first and click the prompt before typing. Lively's extra **Keyboard** forwarding can duplicate keys when the wallpaper already receives them directly; Mouse mode is its documented workaround. Verify this on the actual desktop.

`-EnableStartup` creates a current-user Startup shortcut named **Transformer Explainer Local GPU**. Enable Lively's own startup setting as well. The wallpaper waits for the local service if Lively starts first. Sign-in recovery still needs testing on each computer; installation does not restart Windows to test it.

## Everyday controls

```powershell
./scripts/Start-LocalGpu.ps1
./scripts/Stop-LocalGpu.ps1
```

Start is safe to run again when the verified service is already running. Stop releases its GPU resources; the wallpaper cannot generate again until the service resumes. To disable automatic startup, remove only the **Transformer Explainer Local GPU** shortcut from your Windows Startup folder. Keep the repository at its installed location or recreate the shortcut after moving it.

The page displays **Local GPU · your GPU name** when ready. The health endpoint is `http://127.0.0.1:8765/api/health`. If startup fails, inspect `.runtime/server.stderr.log`. A port conflict is reported instead of stopping an unrelated application. A CUDA initialization failure stops startup instead of silently falling back to CPU-only inference.

## What stays local

After installation, the webpage, JavaScript, styles, fonts, GPT-2 tokenizer, and 626 MiB model file are all on disk. The runtime has no download step. Prompts become token IDs in the local page and travel only to the local service; neither prompts nor token IDs are logged. Analytics and the automatic YouTube embed are removed. Reference links such as the paper, GitHub, and YouTube still need internet if you choose to open them.

The service binds only to `127.0.0.1`. It checks the Host and request Origin, allows no cross-origin API access, and serves a Content Security Policy that restricts page connections and assets to the local origin. It is not intended to be exposed to a LAN or the internet.

GPU inference does not mean every task runs on the GPU. Matrix multiplications, normalization, attention Softmax, and GELU run through CUDA. A few shape operations run on CPU. Tokenization, sampling, layout, and animation stay in the webpage. Lively pausing the page stops its generation requests, but the separate GPU service keeps the model resident until stopped.

## Reproducibility and checks

- Upstream source: `poloclub/transformer-explainer`, commit `bfe50afba10b9b560b84143ee1107d977defa74f`.
- Original model SHA-256: `ccf64e934094054603c5b7bd98191f0fd2ea0315a81e9e0d8104070f64413119`.
- Tokenizer: `Xenova/gpt2`, revision `bf2c7f02e0b826c60d03af341171bde20893da66` (tokenizer/config files only).
- ONNX Runtime GPU 1.23.2; CUDA/cuDNN DLLs installed inside `.venv` from the NVIDIA pip packages. Model loading verifies its checksum.
- The frontend uses a committed npm lockfile. Vite 6.4.3 resolves the upstream Vite 5 / Svelte plugin 6 peer mismatch; the adapter also fixes the Windows Sass import path.
- `local/prepare.py` applies the local transport, local assets, loading/error status, and an input-subscription fix so generation uses the current prompt. The original visualization and sampling implementation remain upstream.
- Every service start profiles a harmless warm-up and requires actual CUDA MatMul events. Aggregate evidence is saved to `.runtime/cuda-verification.json`; profiling then stops.

On the RTX 4090 setup, three test inputs compared all **721 outputs** against the same ONNX model on CPU. Top-token predictions matched; the largest absolute float32 difference was approximately **0.00047**. This checks numerical consistency, not language-model quality. Short warm inference calls were measured in tens of milliseconds; those timings exclude page transport and animation and are not a general benchmark.

The [resource charts in the README](README.md#resource-usage) describe the earlier browser CPU/WASM version. They do **not** measure this CUDA service; its combined CPU/RAM/VRAM usage needs a separate benchmark.

The UI keeps the upstream 12-word limit; the service additionally accepts at most 128 GPT-2 tokens per request. One inference runs at a time. Both black and white wrappers use the same local endpoint and model.
