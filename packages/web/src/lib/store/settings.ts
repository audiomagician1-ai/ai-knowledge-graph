import { create } from 'zustand';

export type LLMProvider = 'openrouter' | 'openai' | 'deepseek' | 'custom';

interface LLMConfig {
  provider: LLMProvider;
  apiKey: string;
  model?: string;       // model name override
  baseUrl?: string;     // custom API base URL (for internal/proxy endpoints)
  directMode?: boolean; // true = browser calls LLM directly (for intranet keys)
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
      return {
        provider: parsed.provider || 'openrouter',
        apiKey: parsed.apiKey_b64 ? deobfuscate(parsed.apiKey_b64) : (parsed.apiKey || ''),
        model: parsed.model || '',
        baseUrl: parsed.baseUrl || '',
        directMode: parsed.directMode ?? false,
      };
    }
  } catch { /* ignore */ }
  return { provider: 'openrouter', apiKey: '', model: '', baseUrl: '', directMode: false };
}

function saveToStorage(config: LLMConfig) {
  try {
    const toSave = {
      provider: config.provider,
      apiKey_b64: obfuscate(config.apiKey),
      model: config.model || '',
      baseUrl: config.baseUrl || '',
      directMode: config.directMode ?? false,
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
    return !!(cfg.directMode && cfg.apiKey && cfg.baseUrl);
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