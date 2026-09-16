# Third-party notices

The local installer downloads a pinned copy of Transformer Explainer and its original ONNX model, applies a local inference transport adapter, and serves the webpage on the user's computer. Demonstration media depict the upstream visualization. Its MIT license is reproduced below; the wrapper and adapter's separate license is in LICENSE.

The installer also downloads GPT-2 tokenizer files from [Xenova/gpt2](https://huggingface.co/Xenova/gpt2), and the Jersey 10 font from [Google Fonts](https://github.com/google/fonts/tree/main/ofl/jersey10) (SIL Open Font License 1.1). The font's OFL.txt is retained with the locally served font. JavaScript dependencies, KaTeX fonts, ONNX Runtime, and NVIDIA runtime libraries retain their own license files in the local installation; they are not included in the wallpaper ZIPs. Exact asset revisions and checksums are recorded in `local/fetch_assets.py`.

Source: https://github.com/poloclub/transformer-explainer/blob/main/LICENSE

## Transformer Explainer

MIT License

Copyright (c) 2022 Polo Club of Data Science

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
