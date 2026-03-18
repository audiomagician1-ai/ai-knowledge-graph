import { create } from 'zustand';

export type LLMProvider = 'openrouter' | 'openai' | 'deepseek' | 'custom';

// ─── Local CORS Proxy ───
const PROXY_PORT = 9876;
const PROXY_BASE = `http://localhost:${PROXY_PORT}`;

interface LLMConfig {
  provider: LLMProvider;
  apiKey: string;
  model?: string;       // model name override
  baseUrl?: string;     // custom API base URL (for internal/proxy endpoints)
  useProxy?: boolean;   // true = route through local CORS proxy (for intranet URLs)
  /** @deprecated — migrated to useProxy */
  directMode?: boolean;
}

interface SettingsState {
  llmConfig: LLMConfig;
  setLLMConfig: (config: Partial<LLMConfig>) => void;
  clearApiKey: () => void;
  hasApiKey: () => boolean;
  /** True when user has their own API key configured → LLM calls go direct from browser */
  isDirectMode: () => boolean;
  /** True when using server-provided free LLM (no user key) */
  isUsingDefaultLLM: () => boolean;
}

const STORAGE_KEY = 'akg-settings';

/** Simple base64 obfuscation — NOT encryption. Only prevents casual shoulder-surfing in DevTools. */
function obfuscate(plain: string): string {
  if (!plain) return '';
  try { return btoa(encodeURIComponent(plain)); } catch { return plain; }
}

function deobfuscate(encoded: string): string {
  if (!encoded) return '';
  try { return decodeURIComponent(atob(encoded)); } catch { return encoded; }
}

function loadFromStorage(): LLMConfig {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      // Migrate: old directMode → useProxy
      const useProxy = parsed.useProxy ?? (parsed.directMode ? true : false);
      return {
        provider: parsed.provider || 'openrouter',
        apiKey: parsed.apiKey_b64 ? deobfuscate(parsed.apiKey_b64) : (parsed.apiKey || ''),
        model: parsed.model || '',
        baseUrl: parsed.baseUrl || '',
        useProxy,
      };
    }
  } catch { /* ignore */ }
  return { provider: 'openrouter', apiKey: '', model: '', baseUrl: '', useProxy: false };
}

function saveToStorage(config: LLMConfig) {
  try {
    const toSave = {
      provider: config.provider,
      apiKey_b64: obfuscate(config.apiKey),
      model: config.model || '',
      baseUrl: config.baseUrl || '',
      useProxy: config.useProxy ?? false,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
  } catch { /* ignore */ }
}

export const useSettingsStore = create<SettingsState>((set, get) => ({
  llmConfig: loadFromStorage(),

  setLLMConfig: (partial) => {
    const current = get().llmConfig;
    const updated = { ...current, ...partial };
    saveToStorage(updated);
    set({ llmConfig: updated });
  },

  clearApiKey: () => {
    const updated = { ...get().llmConfig, apiKey: '' };
    saveToStorage(updated);
    set({ llmConfig: updated });
  },

  hasApiKey: () => {
    return get().llmConfig.apiKey.length > 0;
  },

  isDirectMode: () => {
    const cfg = get().llmConfig;
    // Direct mode = call LLM from browser (vs. through backend API proxy)
    // Activated when user has API key AND a resolvable base URL exists
    // (providers have defaultBase, so user only needs a key for standard providers)
    const hasBase = !!(cfg.baseUrl || PROVIDER_INFO[cfg.provider]?.defaultBase);
    return !!(cfg.apiKey && hasBase);
  },

  isUsingDefaultLLM: () => {
    return !get().llmConfig.apiKey?.trim();
  },
}));

/** 构建 LLM 相关请求头 */
export function getLLMHeaders(): Record<string, string> {
  const { llmConfig } = useSettingsStore.getState();
  if (!llmConfig.apiKey) return {};
  const headers: Record<string, string> = {
    'X-LLM-Provider': llmConfig.provider,
    'X-LLM-API-Key': llmConfig.apiKey,
  };
  if (llmConfig.model) headers['X-LLM-Model'] = llmConfig.model;
  if (llmConfig.baseUrl) headers['X-LLM-Base-URL'] = llmConfig.baseUrl;
  return headers;
}

// ─── Proxy utilities ───

/**
 * Resolve the effective API base URL.
 * When useProxy is on, wraps the original URL through the local CORS proxy.
 */
export function resolveBaseUrl(baseUrl: string, useProxy: boolean): string {
  const raw = baseUrl.replace(/\/+$/, '');
  if (!useProxy) return raw;
  if (raw.startsWith(PROXY_BASE)) return raw;
  return `${PROXY_BASE}/proxy/${raw}`;
}

/** Probe whether the local CORS proxy is running (GET /health, 1.5s timeout) */
export async function probeProxy(): Promise<boolean> {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 1500);
    const res = await fetch(`${PROXY_BASE}/health`, { signal: ctrl.signal });
    clearTimeout(timer);
    if (!res.ok) return false;
    const data = await res.json();
    return data?.status === 'ok';
  } catch {
    return false;
  }
}

/**
 * Build the token-limit parameter for the request body.
 * OpenAI's newer models (o1, o3, chatgpt-5 series etc.)
 * require `max_completion_tokens` instead of `max_tokens`.
 */
function tokenLimitParam(model: string, tokens: number): Record<string, number> {
  const m = model.toLowerCase();
  if (/^(o[1-9]|chatgpt-)/.test(m) || /\/(o[1-9]|chatgpt-)/.test(m)) {
    return { max_completion_tokens: tokens };
  }
  return { max_tokens: tokens };
}

/** Try a direct fetch to the API to check if CORS is available.
 *  First tries GET /models (no token cost), falls back to POST /chat/completions with max_tokens: 1.
 *  Uses 15s timeout (generous for overseas APIs) + automatic 1 retry on timeout/network error. */
export async function probeCORS(
  baseUrl: string, apiKey: string, model: string,
): Promise<{ ok: boolean; status?: number; detail?: string }> {
  const base = baseUrl.replace(/\/+$/, '');
  const headers = { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` };

  // Attempt 0: Try GET /models (no token cost, quick CORS check)
  try {
    const ctrl0 = new AbortController();
    const timer0 = setTimeout(() => ctrl0.abort(), 8_000);
    const modelsRes = await fetch(`${base}/models`, { headers, signal: ctrl0.signal });
    clearTimeout(timer0);
    // Guard: some providers return 200 + HTML for wrong paths
    const mCT = modelsRes.headers.get('content-type') || '';
    if (modelsRes.ok && !mCT.includes('application/json')) {
      // Not a real API response — fall through to chat probe
    } else if (modelsRes.ok) {
      return { ok: true, status: modelsRes.status };
    }
    // If 404 or other error, fall through to chat probe
  } catch { /* timeout or CORS blocked — fall through */ }

  // Fallback: POST /chat/completions with max_tokens: 1 (minimal token cost)
  const url = `${base}/chat/completions`;
  const body = JSON.stringify({ model, messages: [{ role: 'user', content: 'hi' }], ...tokenLimitParam(model, 1) });

  const attempt = async (timeoutMs: number): Promise<{ ok: boolean; status?: number; detail?: string }> => {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const res = await fetch(url, { method: 'POST', headers, body, signal: ctrl.signal });
      clearTimeout(timer);
      // Guard: some providers return 200 + HTML for wrong paths
      const ct = res.headers.get('content-type') || '';
      if (res.ok && !ct.includes('application/json') && !ct.includes('text/event-stream')) {
        return { ok: false, status: res.status, detail: `HTTP ${res.status} but response is ${ct || 'unknown'} (expected JSON). Check your Base URL.` };
      }
      if (res.ok) return { ok: true, status: res.status };
      // Try to extract upstream error detail
      let detail = `HTTP ${res.status}`;
      try {
        const respBody = await res.text();
        const j = JSON.parse(respBody);
        if (j.error?.message) detail += `: ${j.error.message}`;
        else if (j.message) detail += `: ${j.message}`;
        else if (respBody.length < 200) detail += `: ${respBody}`;
      } catch { /* ignore parse errors */ }
      return { ok: false, status: res.status, detail };
    } catch (e) {
      clearTimeout(timer);
      throw e; // re-throw for retry logic
    }
  };

  // First attempt — 15s timeout
  try {
    return await attempt(15_000);
  } catch (e1) {
    // On timeout or network error, retry once (connection is likely warmed up now)
    try {
      return await attempt(10_000);
    } catch (e2) {
      return { ok: false, detail: e2 instanceof Error ? e2.message : 'Unknown error' };
    }
  }
}

/** Inline CORS proxy Node.js script source — downloaded by user */
export const PROXY_SCRIPT_SRC = `#!/usr/bin/env node
/**
 * AI 知识图谱 — LLM CORS 代理
 * 用法: node cors-proxy.cjs [端口]   默认端口 9876
 */
const http = require('http');
const https = require('https');
const { URL } = require('url');
const PORT = parseInt(process.argv[2] || '9876', 10);
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Max-Age': '86400',
  'Access-Control-Expose-Headers': '*',
};
http.createServer((req, res) => {
  if (req.method === 'OPTIONS') { res.writeHead(204, CORS); return res.end(); }
  if (req.url === '/health') {
    res.writeHead(200, { ...CORS, 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ status: 'ok', proxy: 'akg-cors', port: PORT }));
  }
  const m = req.url.match(/^\\/proxy\\/(https?:\\/\\/.+)$/);
  if (!m) { res.writeHead(400, { ...CORS, 'Content-Type': 'application/json' }); return res.end(JSON.stringify({ error: 'use /proxy/<url>' })); }
  const target = new URL(decodeURIComponent(m[1]));
  const chunks = [];
  req.on('data', c => chunks.push(c));
  req.on('end', () => {
    const body = Buffer.concat(chunks);
    const isStream = body.toString().includes('"stream":true') || body.toString().includes('"stream": true');
    const opts = {
      hostname: target.hostname, port: target.port || (target.protocol === 'https:' ? 443 : 80),
      path: target.pathname + target.search, method: req.method,
      headers: { 'Content-Type': req.headers['content-type'] || 'application/json', 'Content-Length': body.length },
    };
    if (req.headers.authorization) opts.headers['Authorization'] = req.headers.authorization;
    const transport = target.protocol === 'https:' ? https : http;
    transport.request(opts, (pRes) => {
      const h = { ...CORS };
      if (isStream) { h['Content-Type'] = 'text/event-stream'; h['Cache-Control'] = 'no-cache'; }
      else { h['Content-Type'] = pRes.headers['content-type'] || 'application/json'; }
      res.writeHead(pRes.statusCode || 200, h);
      pRes.pipe(res);
    }).on('error', (e) => {
      res.writeHead(502, { ...CORS, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: e.message }));
    }).end(body);
    console.log('[' + new Date().toISOString() + '] ' + req.method + ' -> ' + target.href + (isStream ? ' (stream)' : ''));
  });
}).listen(PORT, () => {
  console.log('\\n  CORS proxy running on http://localhost:' + PORT + '/proxy/<target-url>\\n');
});
`;

/** BAT launcher source (legacy — requires cors-proxy.cjs alongside) */
export const PROXY_BAT_SRC = '@echo off\r\nwhere node >nul 2>&1 || (echo [ERROR] Node.js not found. Install from https://nodejs.org && pause && exit /b)\r\necho Starting CORS proxy on port 9876...\r\nnode "%~dp0cors-proxy.cjs"\r\npause\r\n';

/**
 * Generate a self-contained .bat that embeds the CORS proxy JS as base64.
 * User downloads ONE file, double-clicks, done.
 *
 * Architecture: The bat writes a tiny Node decode-and-run script inline,
 * passes the base64 payload via a temp file (avoids CMD line-length and
 * quoting issues entirely), then exec's node on the decoded .cjs.
 *
 * IMPORTANT — CMD safety rules applied:
 *  - NO `for /f` (parenthesis + quote hell causes flash-exit)
 *  - NO `||` compound operators (unreliable in multi-line blocks)
 *  - Only simple `if errorlevel`, `set`, `echo`, `node`, `goto`, `call`
 *  - All user-visible error paths end with `pause` before `exit`
 */
export function generateSelfContainedBat(): string {
  const proxyJs = PROXY_SCRIPT_SRC;
  // btoa() only handles Latin1 — use TextEncoder for Unicode-safe base64
  const bytes = new TextEncoder().encode(proxyJs);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  const b64 = btoa(binary);

  const bat = [
    '@echo off',
    'chcp 65001 >nul 2>&1',
    'title AI Knowledge Graph - CORS Proxy',
    'echo.',
    '',
    'REM --- Check Node.js ---',
    'node --version >nul 2>&1',
    'if errorlevel 1 goto nonode',
    '',
    'REM --- Write base64 payload to temp file ---',
    `echo ${b64}> "%TEMP%\\akg-proxy.b64"`,
    '',
    'REM --- Decode and launch via node ---',
    'echo   Starting CORS proxy...',
    'echo.',
    'echo   ==========================================',
    'echo     AI Knowledge Graph - LLM CORS Proxy',
    'echo     http://localhost:9876/proxy/',
    'echo   ==========================================',
    'echo.',
    '',
    `node -e "var f=require('fs'),b=f.readFileSync(process.env.TEMP+'/akg-proxy.b64','utf8').trim();f.writeFileSync(process.env.TEMP+'/akg-cors-proxy.cjs',Buffer.from(b,'base64'));require(process.env.TEMP+'/akg-cors-proxy.cjs')" 9876`,
    '',
    'echo.',
    'echo   Proxy stopped.',
    'pause',
    'goto end',
    '',
    ':nonode',
    'echo.',
    'echo   [ERROR] Node.js is not installed or not in PATH.',
    'echo   Download from: https://nodejs.org',
    'echo.',
    'pause',
    '',
    ':end',
  ];
  return bat.join('\r\n');
}

/** Download a text blob as a file */
export function downloadBlob(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  // Delay revoke to ensure browser has time to start the download
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}

/** Validate model ID format for the given provider.
 *  Returns null if valid, or an error message string if invalid. */
export function validateModelId(provider: LLMProvider, model: string): string | null {
  if (!model) return null; // empty = use default, always valid
  if (provider === 'openrouter' && !model.includes('/')) {
    return 'OpenRouter 模型名需包含提供商前缀，格式: org/model（如 openai/gpt-4o, stepfun/step-3.5-flash）';
  }
  return null;
}

/** Get the provider-appropriate default model name */
export function getDefaultModel(provider: LLMProvider): string {
  switch (provider) {
    case 'openrouter': return 'openai/gpt-4o-mini';
    case 'deepseek': return 'deepseek-chat';
    default: return 'gpt-4o-mini';
  }
}

export const PROVIDER_INFO: Record<LLMProvider, { name: string; placeholder: string; hint: string; defaultBase: string; modelHint: string }> = {
  openrouter: {
    name: 'OpenRouter',
    placeholder: 'sk-or-v1-...',
    hint: '多模型聚合路由，支持 GPT-4o / Claude / Gemini 等',
    defaultBase: 'https://openrouter.ai/api/v1',
    modelHint: '格式: org/model（如 openai/gpt-4o、stepfun/step-3.5-flash）',
  },
  openai: {
    name: 'OpenAI',
    placeholder: 'sk-...',
    hint: 'GPT-4o / GPT-4o-mini / o1 系列',
    defaultBase: 'https://api.openai.com/v1',
    modelHint: '',
  },
  deepseek: {
    name: 'DeepSeek',
    placeholder: 'sk-...',
    hint: 'DeepSeek-V3 / DeepSeek-R1 系列',
    defaultBase: 'https://api.deepseek.com/v1',
    modelHint: '',
  },
  custom: {
    name: '自定义',
    placeholder: 'your-api-key',
    hint: '任意 OpenAI 兼容 API (内网、代理等)',
    defaultBase: '',
    modelHint: '',
  },
};