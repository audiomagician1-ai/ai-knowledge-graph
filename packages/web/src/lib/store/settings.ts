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
  isDirectMode: () => boolean;
}

const STORAGE_KEY = 'akg-settings';

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
    // Direct mode = use local proxy to call LLM from browser
    return !!(cfg.useProxy && cfg.apiKey && cfg.baseUrl);
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

/** Try a direct fetch to the API to check if CORS is available (3s timeout) */
export async function probeCORS(baseUrl: string, apiKey: string, model: string): Promise<boolean> {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 3000);
    const url = baseUrl.replace(/\/+$/, '') + '/chat/completions';
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({ model, messages: [{ role: 'user', content: 'hi' }], max_tokens: 1 }),
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    return res.ok;
  } catch {
    return false;
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

/** BAT launcher source */
export const PROXY_BAT_SRC = '@echo off\r\nwhere node >nul 2>&1 || (echo [ERROR] Node.js not found. Install from https://nodejs.org && pause && exit /b)\r\necho Starting CORS proxy on port 9876...\r\nnode "%~dp0cors-proxy.cjs"\r\npause\r\n';

/** Download a text blob as a file */
export function downloadBlob(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

export const PROVIDER_INFO: Record<LLMProvider, { name: string; placeholder: string; hint: string; defaultBase: string }> = {
  openrouter: {
    name: 'OpenRouter',
    placeholder: 'sk-or-v1-...',
    hint: '多模型聚合路由，支持 GPT-4o / Claude / Gemini 等',
    defaultBase: 'https://openrouter.ai/api/v1',
  },
  openai: {
    name: 'OpenAI',
    placeholder: 'sk-...',
    hint: 'GPT-4o / GPT-4o-mini / o1 系列',
    defaultBase: 'https://api.openai.com/v1',
  },
  deepseek: {
    name: 'DeepSeek',
    placeholder: 'sk-...',
    hint: 'DeepSeek-V3 / DeepSeek-R1 系列',
    defaultBase: 'https://api.deepseek.com/v1',
  },
  custom: {
    name: '自定义',
    placeholder: 'your-api-key',
    hint: '任意 OpenAI 兼容 API (内网、代理等)',
    defaultBase: '',
  },
};