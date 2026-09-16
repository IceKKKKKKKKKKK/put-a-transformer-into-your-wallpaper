"""Loopback-only CUDA inference for Polo Club's original GPT-2 explainer model.

No model training or replacement: all 720 attention tensors and next-token logits
come from the original ONNX graph. Prompts and token IDs are never logged.
"""
from __future__ import annotations

import asyncio
from collections import Counter
from contextlib import asynccontextmanager
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import time

import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
import uvicorn

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.runtime'
PORT = 8765
MODEL_SHA256 = 'ccf64e934094054603c5b7bd98191f0fd2ea0315a81e9e0d8104070f64413119'
OUTPUTS = ['linear_output'] + [
    f'block_{layer}_attn_head_{head}_{stage}'
    for layer in range(12) for head in range(12)
    for stage in ('attn', 'attn_scaled', 'attn_masked', 'attn_softmax', 'attn_dropout')
]
state: dict = {'ready': False, 'requests': 0, 'last_inference_ms': None}
session: ort.InferenceSession | None = None
busy = asyncio.Lock()


def load_model():
    global session
    model = RUNTIME / 'models/gpt2-explainer.onnx'
    with model.open('rb') as f:
        if hashlib.file_digest(f, 'sha256').hexdigest() != MODEL_SHA256:
            raise RuntimeError('Model checksum mismatch. Run the local installer again.')
    ort.preload_dlls(directory='')
    if 'CUDAExecutionProvider' not in ort.get_available_providers():
        raise RuntimeError('CUDA is unavailable. No CPU-only fallback is permitted.')
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.log_severity_level = 3
    options.enable_profiling = True
    options.profile_file_prefix = str(RUNTIME / 'startup-cuda')
    session = ort.InferenceSession(str(model), sess_options=options, providers=[
        ('CUDAExecutionProvider', {'device_id': 0, 'use_tf32': 0}), 'CPUExecutionProvider'
    ])
    session.disable_fallback()
    if session.get_providers()[0] != 'CUDAExecutionProvider':
        raise RuntimeError('CUDA initialization failed; refusing CPU-only inference.')
    session.run(OUTPUTS, {'input': np.array([[464, 3797, 3332, 319, 262]], dtype=np.int64)})
    profile_path = Path(session.end_profiling())
    events = json.loads(profile_path.read_text())
    counts = Counter((e['args']['provider'], e['args'].get('op_name', ''))
                     for e in events if 'provider' in e.get('args', {}))
    if not counts[('CUDAExecutionProvider', 'MatMul')]:
        raise RuntimeError('Startup profiling did not verify CUDA matrix multiplication.')
    # Keep aggregate evidence only, not an unbounded stream of profiles.
    evidence = {'model_sha256': MODEL_SHA256, 'providers': session.get_providers(),
                'operators': [{'provider': p, 'op': op, 'count': n}
                              for (p, op), n in sorted(counts.items())]}
    (RUNTIME / 'cuda-verification.json').write_text(json.dumps(evidence, indent=2))
    profile_path.unlink()
    device = 'NVIDIA CUDA device 0'
    try:
        device = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader', '--id=0'],
            text=True, timeout=5, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        ).strip()
    except (OSError, subprocess.SubprocessError):
        pass
    state.update(ready=True, service='transformer-explainer-local', device=device,
                 provider='CUDAExecutionProvider', cuda_matmul_verified=True,
                 model='Polo Club Transformer Explainer GPT-2',
                 model_display='GPT-2 small (124M)', model_sha256=MODEL_SHA256)


@asynccontextmanager
async def lifespan(app):
    await asyncio.to_thread(load_model)
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware('http')
async def local_only(request: Request, call_next):
    if request.headers.get('host') != f'127.0.0.1:{PORT}':
        return Response('Use the 127.0.0.1 local address.', status_code=403)
    if request.method not in ('GET', 'HEAD'):
        origin = request.headers.get('origin')
        if origin and origin != f'http://127.0.0.1:{PORT}':
            return Response('Cross-origin requests are not allowed.', status_code=403)
    response = await call_next(request)
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; "
        "frame-src 'self'; worker-src 'self' blob:; object-src 'none'; base-uri 'self'"
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response


@app.get('/api/health')
async def health():
    return state


@app.get('/api/ready.png')
async def ready_image():
    return FileResponse(RUNTIME / 'site/favicon.png', media_type='image/png')


def infer(ids: list[int]) -> bytes:
    started = time.perf_counter()
    results = session.run(OUTPUTS, {'input': np.array([ids], dtype=np.int64)})
    inference_ms = round((time.perf_counter() - started) * 1000, 2)
    # A small JSON manifest followed by aligned float32 buffers preserves -inf
    # masking values exactly, without lossy JSON null substitutions.
    manifest, buffers, offset = [], [], 0
    for name, value in zip(OUTPUTS, results):
        value = np.ascontiguousarray(value, dtype='<f4')
        raw = value.tobytes()
        manifest.append({'name': name, 'dims': list(value.shape),
                         'offset': offset, 'length': value.size})
        buffers.append(raw)
        offset += len(raw)
    header = json.dumps({'tensors': manifest, 'inference_ms': inference_ms},
                        separators=(',', ':')).encode()
    padding = b' ' * (-(4 + len(header)) % 4)
    state.update(requests=state['requests'] + 1, last_inference_ms=inference_ms,
                 last_token_count=len(ids))
    return struct.pack('<I', len(header)) + header + padding + b''.join(buffers)


@app.post('/api/infer')
async def run(request: Request):
    if request.headers.get('content-type', '').split(';')[0] != 'application/json':
        raise HTTPException(415, 'Expected application/json.')
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 4096:
            raise HTTPException(413, 'Prompt is too large.')
    try:
        obj = json.loads(body)
    except (ValueError, UnicodeError):
        raise HTTPException(400, 'Invalid JSON.')
    ids = obj.get('token_ids') if isinstance(obj, dict) else None
    if not isinstance(ids, list) or not 1 <= len(ids) <= 128 or any(
        type(x) is not int or not 0 <= x < 50257 for x in ids
    ):
        raise HTTPException(422, 'Use 1 to 128 valid GPT-2 token IDs.')
    if busy.locked():
        raise HTTPException(429, 'A generation is already running. Please try again.')
    async with busy:
        packed = await asyncio.to_thread(infer, ids)
    return Response(packed, media_type='application/octet-stream')


@app.get('/')
async def home():
    return FileResponse(ROOT / 'src/index.html')


app.mount('/transformer-explainer', StaticFiles(directory=RUNTIME / 'site', html=True))

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=PORT, access_log=False)
