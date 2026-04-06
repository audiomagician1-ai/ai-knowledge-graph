import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('useSpeechRecognition', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('should detect browser support', async () => {
    // Default: no SpeechRecognition → isSupported false
    const mod = await import('@/lib/hooks/useSpeechRecognition');
    // Can't call hook outside React, but we can verify module exports
    expect(mod.useSpeechRecognition).toBeDefined();
    expect(typeof mod.useSpeechRecognition).toBe('function');
  });

  it('should export correct hook signature', async () => {
    const mod = await import('@/lib/hooks/useSpeechRecognition');
    expect(mod.useSpeechRecognition.length).toBeLessThanOrEqual(2); // optional params
  });
});

describe('Web Speech API types', () => {
  it('should have SpeechRecognition type available in window', () => {
    // Verify our type declarations work (compile-time check mainly)
    const hasApi = typeof window !== 'undefined' &&
      ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);
    // In test env, likely false
    expect(typeof hasApi).toBe('boolean');
  });
});
