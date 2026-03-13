import { create } from 'zustand';

export type LLMProvider = 'openrouter' | 'openai' | 'deepseek';

interface LLMConfig {
  provider: LLMProvider;
  apiKey: string;
  model?: string; // optional override
}

interface SettingsState {
  llmConfig: LLMConfig;
  setLLMConfig: (config: Partial<LLMConfig>) => void;
  clearApiKey: () => void;
  hasApiKey: () => boolean;
}

const STORAGE_KEY = 'akg-settings';

/** Simple obfuscation — NOT encryption, just prevents casual plaintext scanning.
 *  Use btoa/atob for base64 encode/decode. */
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
      };
    }
  } catch { /* ignore */ }
  return { provider: 'openrouter', apiKey: '', model: '' };
}

function saveToStorage(config: LLMConfig) {
  try {
    // Store key obfuscated; never store plaintext 'apiKey' field
    const toSave = {
      provider: config.provider,
      apiKey_b64: obfuscate(config.apiKey),
      model: config.model || '',
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
}));

/** 构建 LLM 相关请求头 */
export function getLLMHeaders(): Record<string, string> {
  const { llmConfig } = useSettingsStore.getState();
  if (!llmConfig.apiKey) return {};
  return {
    'X-LLM-Provider': llmConfig.provider,
    'X-LLM-API-Key': llmConfig.apiKey,
    ...(llmConfig.model ? { 'X-LLM-Model': llmConfig.model } : {}),
  };
}

export const PROVIDER_INFO: Record<LLMProvider, { name: string; placeholder: string; hint: string }> = {
  openrouter: {
    name: 'OpenRouter',
    placeholder: 'sk-or-v1-...',
    hint: '支持所有主流模型，推荐。openrouter.ai 获取',
  },
  openai: {
    name: 'OpenAI',
    placeholder: 'sk-...',
    hint: 'GPT-4o / GPT-4o-mini。platform.openai.com 获取',
  },
  deepseek: {
    name: 'DeepSeek',
    placeholder: 'sk-...',
    hint: 'DeepSeek-V3 / Chat。platform.deepseek.com 获取',
  },
};