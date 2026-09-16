// Transport adapter only. Visualization, tokenizer, and sampling remain upstream.
import { writable } from 'svelte/store';

export const localError = writable('');
export const localStatus = writable('Connecting to local GPU…');
export const localDevice = writable('');

export async function connectLocal() {
  const response = await fetch('/api/health', { signal: AbortSignal.timeout(10000) });
  if (!response.ok) throw new Error('Local GPU service is unavailable.');
  const health = await response.json();
  if (!health.ready || !health.cuda_matmul_verified) throw new Error('CUDA is not ready.');
  localStatus.set(`Model · ${health.model_display || health.model}`);
  localDevice.set(`Inference · CUDA · ${health.device}`);
  localError.set('');
  return true;
}

export async function inferLocal(token_ids: number[]) {
  const response = await fetch('/api/infer', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token_ids }), signal: AbortSignal.timeout(30000)
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Local inference failed (${response.status}).`);
  }
  const buffer = await response.arrayBuffer();
  const size = new DataView(buffer).getUint32(0, true);
  const header = JSON.parse(new TextDecoder().decode(new Uint8Array(buffer, 4, size)));
  const start = Math.ceil((4 + size) / 4) * 4;
  const tensors: Record<string, { dims: number[]; data: Float32Array }> = {};
  for (const t of header.tensors) {
    tensors[t.name] = { dims: t.dims, data: new Float32Array(buffer, start + t.offset, t.length) };
  }
  localError.set('');
  return tensors;
}
