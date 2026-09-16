"""Apply small, repeatable adapters to a pinned upstream checkout.

Read pristine files with git show rather than resetting a user's working tree.
This script only writes the explicitly listed files in our .runtime checkout.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_COMMIT = 'bfe50afba10b9b560b84143ee1107d977defa74f'
UP = ROOT / '.runtime/upstream'


def original(name):
    return subprocess.check_output(['git', '-C', str(UP), 'show', f'{UPSTREAM_COMMIT}:{name}']).decode()


def save(name, text):
    (UP / name).write_text(text, encoding='utf-8')


page = original('src/routes/+page.svelte')
page = page.replace("import * as ort from 'onnxruntime-web';", "import { connectLocal, localError, localStatus, localDevice } from '~/utils/local-client';")
page = page.replace("import { fetchAndMergeChunks } from '~/utils/fetchChunks';", '')
page = page.replace("import { AutoTokenizer }", "import { AutoTokenizer, env }")
start = page.index('\tort.env.wasm.wasmPaths')
end = page.index('\t// Subscribe inputs', start)
page = page[:start] + '''
  let active = false;
  env.allowRemoteModels = false;
  env.localModelPath = `${base}/tokenizer/`;
  env.useBrowserCache = false;

  onMount(() => {
    let unsubscribe = () => {};
    let cancelled = false;
    (async () => {
      try {
        const tokenizer = await AutoTokenizer.from_pretrained('gpt2');
        await connectLocal();
        if (cancelled) return;
        modelSession.set(true);
        isFetchingModel.set(false);
        active = true;
        unsubscribe = subscribeInputs(tokenizer);
      } catch (error) {
        localError.set(error instanceof Error ? error.message : String(error));
      }
    })();
    return () => { cancelled = true; unsubscribe(); };
  });

''' + page[end:]
# Svelte 5 may update the auto-subscribed value after this explicit subscriber.
# Use the callback value so generation never lags one prompt behind the input.
page = page.replace('const runModelOrCache = () => {', 'const runModelOrCache = (input: string) => {')
page = page.replace('input: $inputText.trim(),', 'input: input.trim(),')
page = page.replace('runModelOrCache();', 'runModelOrCache(value);')
page = page.replace('</script>', '''</script>

<div class="local-status" role="status">
  {#if $localError}
    <span role="alert">{$localError} Restart the local GPU service, then <button on:click={() => location.reload()}>reload</button>.</span>
  {:else}
    <span class="local-model">{$localStatus}</span>
    {#if $localDevice}<span class="local-device">{$localDevice}</span>{/if}
  {/if}
</div>
''', 1)
page = page.replace('<style lang="scss">', '''<style lang="scss">
  .local-status { position:fixed; bottom:20px; right:112px; z-index:9999; display:flex; flex-direction:column; gap:4px; max-width:calc(100vw - 136px); font:18px/1.4 Arial,sans-serif; text-align:right; background:white; color:#333; padding:6px 10px; border-radius:4px; }
  .local-model { font-size:22px; font-weight:600; }
  .local-device { font-size:18px; }
  .local-status button { text-decoration:underline; }
''', 1)
save('src/routes/+page.svelte', page)

data = original('src/utils/data.ts')
data = data.replace("import * as ort from 'onnxruntime-web';", "import { inferLocal, localError } from './local-client';")
start = data.index("\t\t// Convert token_ids to tensor")
end = data.index('\n\t\t// Extract the logits', start)
data = data[:start] + '\t\tconst results = await inferLocal(token_ids);\n' + data[end:]
data = data.replace('[...out.cpuData]', '[...out.data]')
# Reset the running indicator on failed transport, keep the error visible.
data = data.replace("console.error('Error during inference:', error.message);", "isModelRunning.set(false);\n\t\tlocalError.set(error instanceof Error ? error.message : String(error));")
# Catch at the input subscriber so rejected network promises do not disappear.
page = page.replace("sampling: $sampling\n\t\t\t});", "sampling: $sampling\n\t\t\t}).catch(() => {});")
save('src/routes/+page.svelte', page)
save('src/utils/data.ts', data)
shutil.copyfile(ROOT / 'local/client.ts', UP / 'src/utils/local-client.ts')

store = original('src/store/index.ts').replace("import * as ort from 'onnxruntime-web';", '')
store = store.replace('writable<ort.InferenceSession>()', 'writable<boolean>(false)')
store = store.replace('isTextbookOpen = writable<boolean>(true)', 'isTextbookOpen = writable<boolean>(false)')
save('src/store/index.ts', store)

form = original('src/components/InputForm.svelte')
form = form.replace('// $isModelRunning ||', '$isModelRunning ||')
form = form.replace('Try the examples while GPT-2 model is being downloaded (600MB)', 'Connecting to the local GPU service…')
save('src/components/InputForm.svelte', form)

# Desktop presentation: remove header branding/shortcuts, retain all attribution
# and paper links in the upstream article and the repository's credit files.
topbar = original('src/components/Topbar.svelte')
topbar, logo_count = re.subn(r'\s*<div class="logo[^\"]*" data-click="logo">.*?</div>', '', topbar, count=1, flags=re.S)
topbar, icons_count = re.subn(r'\s*<div class="icons[^\"]*">.*?</div>', '', topbar, count=1, flags=re.S)
if (logo_count, icons_count) != (1, 1):
    raise RuntimeError('Upstream header changed; review the local presentation patch.')
save('src/components/Topbar.svelte', topbar)

layout = original('src/routes/+layout.svelte')
layout = layout.replace("import GTM from '~/utils/gtm.svelte';", '').replace('<GTM />', '')
save('src/routes/+layout.svelte', layout)
katex = original('src/utils/Katex.svelte').replace("import katex from 'katex';", "import katex from 'katex';\nimport 'katex/dist/katex.min.css';")
katex = re.sub(r'<svelte:head>.*?</svelte:head>', '', katex, flags=re.S)
save('src/utils/Katex.svelte', katex)
html = original('src/app.html')
html = re.sub(r'\s*<link[^>]+https://fonts\.[^>]+>', '', html)
html = html.replace('%sveltekit.head%', "<style>@font-face{font-family:'Jersey 10';font-style:normal;font-weight:400;font-display:swap;src:url('%sveltekit.assets%/fonts/Jersey10-Regular.ttf') format('truetype')}</style>\n%sveltekit.head%")
save('src/app.html', html)
article = original('src/components/article/Article.svelte')
article = article.replace('Transformer Explainer features a live GPT-2 (small) model running directly in the browser.', 'The original Transformer Explainer runs GPT-2 (small) in the browser. This independent local wallpaper adaptation runs the same ONNX model on your NVIDIA GPU through a loopback-only service.')
article = article.replace('for seamless in-browser execution.', 'for inference. In this local adaptation, the webpage, tokenizer, and model are stored on your computer.')
article = re.sub(r'<iframe\s+src="https://www.youtube.com/embed/ECR4oAwocjs".*?</iframe>', '<a href="https://www.youtube.com/watch?v=ECR4oAwocjs" target="_blank" rel="noreferrer">Watch the original video on YouTube (internet required)</a>', article, flags=re.S)
save('src/components/article/Article.svelte', article)

# Keep huge model chunks outside Vite's static output; never serve weights to the browser.
config = original('svelte.config.js').replace('kit: {', "kit: {\n\t\tfiles: { assets: 'static-local' },")
save('svelte.config.js', config)
vite = original('vite.config.ts')
vite = "import { fileURLToPath } from 'node:url';\n" + vite
vite = vite.replace("`@import 'src/styles/variables.scss';`", "`@import '${fileURLToPath(new URL('./src/styles/variables.scss', import.meta.url)).replaceAll('\\\\', '/')}';`")
save('vite.config.ts', vite)
static = UP / 'static-local'
static.mkdir(exist_ok=True)
for path in (UP / 'static').iterdir():
    if path.name == 'model-v2': continue
    if path.is_dir(): shutil.copytree(path, static / path.name, dirs_exist_ok=True)
    else: shutil.copy2(path, static / path.name)
shutil.copytree(ROOT / '.runtime/tokenizer', static / 'tokenizer', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.cache'))
shutil.copytree(ROOT / '.runtime/fonts', static / 'fonts', dirs_exist_ok=True)

models = ROOT / '.runtime/models'
models.mkdir(exist_ok=True)
model = models / 'gpt2-explainer.onnx'
expected = 'ccf64e934094054603c5b7bd98191f0fd2ea0315a81e9e0d8104070f64413119'
if not model.exists():
    temp = model.with_suffix('.partial')
    with temp.open('wb') as dst:
        for i in range(63):
            with (UP / f'static/model-v2/gpt2.onnx.part{i}').open('rb') as src:
                shutil.copyfileobj(src, dst)
    temp.replace(model)
with model.open('rb') as f:
    if hashlib.file_digest(f, 'sha256').hexdigest() != expected:
        raise RuntimeError('Model checksum mismatch.')
print('Local frontend adapter and original ONNX model prepared.')
