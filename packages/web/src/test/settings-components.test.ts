import { describe, it, expect } from 'vitest';

describe('SettingsLLMConfig', () => {
  it('should export SettingsLLMConfig component', async () => {
    const mod = await import('@/components/settings/SettingsLLMConfig');
    expect(mod.SettingsLLMConfig).toBeDefined();
    expect(typeof mod.SettingsLLMConfig).toBe('function');
  });
});

describe('SettingsDataIO', () => {
  it('should export SettingsDataIO component', async () => {
    const mod = await import('@/components/settings/SettingsDataIO');
    expect(mod.SettingsDataIO).toBeDefined();
    expect(typeof mod.SettingsDataIO).toBe('function');
  });
});
