/**
 * settings.ts store tests
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useSettingsStore, PROVIDER_INFO, resolveBaseUrl } from '@/lib/store/settings';

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
});
