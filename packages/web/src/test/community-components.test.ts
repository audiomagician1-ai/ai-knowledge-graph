import { describe, it, expect } from 'vitest';

describe('SuggestionCard', () => {
  it('should export SuggestionCard, STATUS_META, TYPE_META', async () => {
    const mod = await import('@/components/community/SuggestionCard');
    expect(mod.SuggestionCard).toBeDefined();
    expect(mod.STATUS_META).toBeDefined();
    expect(mod.TYPE_META).toBeDefined();
    expect(mod.STATUS_META.pending.label).toBe('待审核');
    expect(mod.TYPE_META.concept.label).toBe('新概念');
    expect(mod.TYPE_META.link.label).toBe('新链接');
    expect(mod.TYPE_META.correction.label).toBe('纠错');
    expect(mod.TYPE_META.feedback.label).toBe('反馈');
  });
});

describe('SuggestionForm', () => {
  it('should export SuggestionForm component', async () => {
    const mod = await import('@/components/community/SuggestionForm');
    expect(mod.SuggestionForm).toBeDefined();
    expect(typeof mod.SuggestionForm).toBe('function');
  });
});
