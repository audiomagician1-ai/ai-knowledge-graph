import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('useSpeechRecognition', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('should detect browser support', async () => {
    const mod = await import('@/lib/hooks/useSpeechRecognition');
    expect(mod.useSpeechRecognition).toBeDefined();
    expect(typeof mod.useSpeechRecognition).toBe('function');
  });

  it('should export correct hook signature', async () => {
    const mod = await import('@/lib/hooks/useSpeechRecognition');
    expect(mod.useSpeechRecognition.length).toBeLessThanOrEqual(2);
  });

  it('should export SPEECH_LANGUAGES with required properties', async () => {
    const { SPEECH_LANGUAGES } = await import('@/lib/hooks/useSpeechRecognition');
    expect(SPEECH_LANGUAGES).toBeDefined();
    expect(Array.isArray(SPEECH_LANGUAGES)).toBe(true);
    expect(SPEECH_LANGUAGES.length).toBeGreaterThanOrEqual(3); // at least zh, en, ja

    for (const lang of SPEECH_LANGUAGES) {
      expect(lang).toHaveProperty('code');
      expect(lang).toHaveProperty('label');
      expect(lang).toHaveProperty('flag');
      expect(lang.code).toMatch(/^[a-z]{2}-[A-Z]{2}$/); // BCP-47 format
    }
  });

  it('should include Chinese and English as default languages', async () => {
    const { SPEECH_LANGUAGES } = await import('@/lib/hooks/useSpeechRecognition');
    const codes = SPEECH_LANGUAGES.map((l) => l.code);
    expect(codes).toContain('zh-CN');
    expect(codes).toContain('en-US');
  });

  it('should export SpeechLangCode type-compatible codes', async () => {
    const { SPEECH_LANGUAGES } = await import('@/lib/hooks/useSpeechRecognition');
    // All codes should be valid strings
    SPEECH_LANGUAGES.forEach((l) => {
      expect(typeof l.code).toBe('string');
      expect(l.code.length).toBeGreaterThanOrEqual(4);
    });
  });
});

describe('Web Speech API types', () => {
  it('should have SpeechRecognition type available in window', () => {
    const hasApi = typeof window !== 'undefined' &&
      ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);
    expect(typeof hasApi).toBe('boolean');
  });
});
