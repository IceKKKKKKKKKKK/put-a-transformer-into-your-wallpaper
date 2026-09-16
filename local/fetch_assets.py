"""Download pinned public assets once. Runtime inference has no network dependency."""
import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.runtime'
TOKENIZER = 'https://huggingface.co/Xenova/gpt2/resolve/bf2c7f02e0b826c60d03af341171bde20893da66/'
FONT = 'https://raw.githubusercontent.com/google/fonts/1ac2012c34919f5fa2675aacf723fa98edb30b5f/ofl/jersey10/'
ASSETS = [
    ('tokenizer/gpt2/config.json', TOKENIZER + 'config.json', 'c9e2a8cc16fced63fa05e353a330ec236bf52d16f01d27c18ee50f39849a39a5'),
    ('tokenizer/gpt2/tokenizer_config.json', TOKENIZER + 'tokenizer_config.json', '551e26ec611d8d0c8edc3ef72e518a38418cb71f40de1347dd486a595e1557d7'),
    ('tokenizer/gpt2/tokenizer.json', TOKENIZER + 'tokenizer.json', 'cda20b8ca044949aa07ac4078420c80d1a57139d5f9f33700e46fb2d891e7c66'),
    ('fonts/Jersey10-Regular.ttf', FONT + 'Jersey10-Regular.ttf', 'db9cbd091617048a145d249daa2b815fe7083be6ab66ac26626e21a4e01c3e82'),
    ('fonts/OFL.txt', FONT + 'OFL.txt', '436d5836064cec796c7ddde6fb4faeabdb6f2f17443a24a30d0c38b75d13f922'),
]
for name, url, expected in ASSETS:
    dest = RUNTIME / name
    if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() == expected:
        continue
    with urllib.request.urlopen(url, timeout=90) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != expected:
        raise RuntimeError(f'Asset checksum mismatch: {name}')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print('Downloaded', name)

# Codex's bundled Node may not expose npm. Use a project-local, integrity-checked npm.
npm = RUNTIME / 'npm'
if not (npm / 'package/bin/npm-cli.js').exists():
    with urllib.request.urlopen('https://registry.npmjs.org/npm/10.9.4', timeout=30) as response:
        dist = json.load(response)['dist']
    with urllib.request.urlopen(dist['tarball'], timeout=90) as response:
        data = response.read()
    digest = 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode()
    if digest != dist['integrity']:
        raise RuntimeError('npm tarball integrity mismatch.')
    npm.mkdir(exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        archive.extractall(npm, filter='data')
print('Pinned tokenizer, local font, and npm are ready.')
