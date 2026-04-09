import { describe, it, expect } from 'vitest';

describe('LoginOAuthButtons', () => {
  it('should export LoginOAuthButtons component', async () => {
    const mod = await import('@/components/auth/LoginOAuthButtons');
    expect(mod.LoginOAuthButtons).toBeDefined();
    expect(typeof mod.LoginOAuthButtons).toBe('function');
  });
});

describe('ReviewFlashcard', () => {
  it('should export ReviewFlashcard component', async () => {
    const mod = await import('@/components/review/ReviewFlashcard');
    expect(mod.ReviewFlashcard).toBeDefined();
    expect(typeof mod.ReviewFlashcard).toBe('function');
  });

  it('should export RATINGS constant with 4 items', async () => {
    const mod = await import('@/components/review/ReviewFlashcard');
    expect(mod.RATINGS).toBeDefined();
    expect(mod.RATINGS).toHaveLength(4);
    expect(mod.RATINGS[0].label).toBe('\u5fd8\u4e86');
    expect(mod.RATINGS[3].label).toBe('\u7b80\u5355');
  });
});
