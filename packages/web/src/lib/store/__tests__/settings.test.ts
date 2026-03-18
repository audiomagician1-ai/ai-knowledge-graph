/**
 * settings.ts store tests
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useSettingsStore, PROVIDER_INFO, resolveBaseUrl, validateModelId, getDefaultModel, generateSelfContainedBat, PROXY_SCRIPT_SRC } from '@/lib/store/settings';

const storage: Record<string, string> = {};
vi.stubGlobal('localStorage', {
  getItem: (key: string) => storage[key] ?? null,
  setItem: (key: string, value: string) => { storage[key] = value; },
  removeItem: (key: string) => { delete storage[key]; },
  clear: () => { Object.keys(storage).forEach(k => delete storage[k]); },
});

function resetStore() {
  localStorage.clear();
  useSettingsStore.setState({
    llmConfig: { provider: 'openrouter', apiKey: '', model: '', baseUrl: '', useProxy: false },
  });
}

describe('useSettingsStore', () => {
  beforeEach(() => {
    resetStore();
  });

  it('should default to openrouter provider', () => {
    const { llmConfig } = useSettingsStore.getState();
    expect(llmConfig.provider).toBe('openrouter');
  });

  it('should update config and persist to localStorage', () => {
    useSettingsStore.getState().setLLMConfig({ provider: 'deepseek', apiKey: 'test-key' });
    const { llmConfig } = useSettingsStore.getState();
    expect(llmConfig.provider).toBe('deepseek');
    expect(llmConfig.apiKey).toBe('test-key');
    // Check persistence
    const saved = JSON.parse(localStorage.getItem('akg-settings') || '{}');
    expect(saved.provider).toBe('deepseek');
    expect(saved.apiKey_b64).toBeTruthy(); // obfuscated
  });

  it('should clear API key', () => {
    useSettingsStore.getState().setLLMConfig({ apiKey: 'my-key' });
    useSettingsStore.getState().clearApiKey();
    expect(useSettingsStore.getState().llmConfig.apiKey).toBe('');
  });

  it('hasApiKey should reflect current state', () => {
    expect(useSettingsStore.getState().hasApiKey()).toBe(false);
    useSettingsStore.getState().setLLMConfig({ apiKey: 'k' });
    expect(useSettingsStore.getState().hasApiKey()).toBe(true);
  });

  it('isDirectMode should be true when apiKey is set and provider has defaultBase', () => {
    expect(useSettingsStore.getState().isDirectMode()).toBe(false);
    useSettingsStore.getState().setLLMConfig({ apiKey: 'sk-test', provider: 'openrouter' });
    expect(useSettingsStore.getState().isDirectMode()).toBe(true);
  });

  it('isDirectMode should be true for custom provider with baseUrl', () => {
    useSettingsStore.getState().setLLMConfig({ apiKey: 'sk-test', provider: 'custom', baseUrl: 'https://my-api.com/v1' });
    expect(useSettingsStore.getState().isDirectMode()).toBe(true);
  });

  it('isDirectMode should be false for custom provider without baseUrl', () => {
    useSettingsStore.getState().setLLMConfig({ apiKey: 'sk-test', provider: 'custom', baseUrl: '' });
    expect(useSettingsStore.getState().isDirectMode()).toBe(false);
  });
});

describe('resolveBaseUrl', () => {
  it('should return raw URL when useProxy is false', () => {
    expect(resolveBaseUrl('https://api.openai.com/v1', false)).toBe('https://api.openai.com/v1');
  });

  it('should strip trailing slashes', () => {
    expect(resolveBaseUrl('https://api.openai.com/v1/', false)).toBe('https://api.openai.com/v1');
  });

  it('should wrap URL through proxy when useProxy is true', () => {
    const result = resolveBaseUrl('https://my-internal-api.com/v1', true);
    expect(result).toBe('http://localhost:9876/proxy/https://my-internal-api.com/v1');
  });

  it('should not double-wrap if already proxied', () => {
    const result = resolveBaseUrl('http://localhost:9876/proxy/https://api.com/v1', true);
    expect(result).toBe('http://localhost:9876/proxy/https://api.com/v1');
  });
});

describe('PROVIDER_INFO', () => {
  it('should have defaultBase for standard providers', () => {
    expect(PROVIDER_INFO.openrouter.defaultBase).toBeTruthy();
    expect(PROVIDER_INFO.openai.defaultBase).toBeTruthy();
    expect(PROVIDER_INFO.deepseek.defaultBase).toBeTruthy();
  });

  it('should have empty defaultBase for custom provider', () => {
    expect(PROVIDER_INFO.custom.defaultBase).toBe('');
  });

  it('should have modelHint for openrouter', () => {
    expect(PROVIDER_INFO.openrouter.modelHint).toContain('org/model');
  });
});

describe('validateModelId', () => {
  it('should return null for empty model (uses default)', () => {
    expect(validateModelId('openrouter', '')).toBeNull();
  });

  it('should return null for valid openrouter model with org/ prefix', () => {
    expect(validateModelId('openrouter', 'openai/gpt-4o')).toBeNull();
    expect(validateModelId('openrouter', 'stepfun/step-3.5-flash')).toBeNull();
    expect(validateModelId('openrouter', 'anthropic/claude-3.5-sonnet')).toBeNull();
  });

  it('should return warning for openrouter model missing org/ prefix', () => {
    const warn = validateModelId('openrouter', 'gpt-4o');
    expect(warn).toBeTruthy();
    expect(warn).toContain('org/model');
  });

  it('should return warning for openrouter model "step-3.5-flash" without org prefix', () => {
    const warn = validateModelId('openrouter', 'step-3.5-flash');
    expect(warn).toBeTruthy();
  });

  it('should return null for non-openrouter providers regardless of format', () => {
    expect(validateModelId('openai', 'gpt-4o')).toBeNull();
    expect(validateModelId('deepseek', 'deepseek-chat')).toBeNull();
    expect(validateModelId('custom', 'my-model')).toBeNull();
  });
});

describe('getDefaultModel', () => {
  it('should return openai/gpt-4o-mini for openrouter', () => {
    expect(getDefaultModel('openrouter')).toBe('openai/gpt-4o-mini');
  });

  it('should return deepseek-chat for deepseek', () => {
    expect(getDefaultModel('deepseek')).toBe('deepseek-chat');
  });

  it('should return gpt-4o-mini for openai', () => {
    expect(getDefaultModel('openai')).toBe('gpt-4o-mini');
  });
});

describe('generateSelfContainedBat', () => {
  it('should return a string containing @echo off header', () => {
    const bat = generateSelfContainedBat();
    expect(bat).toContain('@echo off');
  });

  it('should contain base64-encoded proxy script payload', () => {
    const bat = generateSelfContainedBat();
    // The bat should contain an echo line with base64 payload
    expect(bat).toContain('akg-proxy.b64');
  });

  it('should handle Unicode characters in PROXY_SCRIPT_SRC without throwing', () => {
    // PROXY_SCRIPT_SRC contains Chinese: "AI 知识图谱 — LLM CORS 代理"
    expect(PROXY_SCRIPT_SRC).toContain('知识图谱');
    // generateSelfContainedBat should NOT throw InvalidCharacterError
    expect(() => generateSelfContainedBat()).not.toThrow();
  });

  it('should produce valid base64 that decodes back to original script', () => {
    const bat = generateSelfContainedBat();
    // Extract base64 payload from the bat file: echo <base64>> "%TEMP%\akg-proxy.b64"
    const match = bat.match(/^echo (.+)> "%TEMP%\\akg-proxy\.b64"/m);
    expect(match).toBeTruthy();
    const b64 = match![1];
    // Decode: base64 → binary string → Uint8Array → TextDecoder → original
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    const decoded = new TextDecoder().decode(bytes);
    expect(decoded).toBe(PROXY_SCRIPT_SRC);
  });
});
