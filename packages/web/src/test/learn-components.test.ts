import { describe, it, expect } from 'vitest';

describe('LearnHeader', () => {
  it('should export LearnHeader component', async () => {
    const mod = await import('@/components/learn/LearnHeader');
    expect(mod.LearnHeader).toBeDefined();
    expect(typeof mod.LearnHeader).toBe('function');
  });
});

describe('LearnMessageBubble', () => {
  it('should export LearnMessageBubble component', async () => {
    const mod = await import('@/components/learn/LearnMessageBubble');
    expect(mod.LearnMessageBubble).toBeDefined();
    expect(typeof mod.LearnMessageBubble).toBe('function');
  });
});

describe('LearnPostAssessment', () => {
  it('should export LearnPostAssessment component', async () => {
    const mod = await import('@/components/learn/LearnPostAssessment');
    expect(mod.LearnPostAssessment).toBeDefined();
    expect(typeof mod.LearnPostAssessment).toBe('function');
  });
});

describe('LearnGuideCard', () => {
  it('should export LearnGuideCard and LearnLoadingIndicator', async () => {
    const mod = await import('@/components/learn/LearnGuideCard');
    expect(mod.LearnGuideCard).toBeDefined();
    expect(mod.LearnLoadingIndicator).toBeDefined();
  });
});

describe('LearnInputArea', () => {
  it('should export LearnInputArea component', async () => {
    const mod = await import('@/components/learn/LearnInputArea');
    expect(mod.LearnInputArea).toBeDefined();
    expect(typeof mod.LearnInputArea).toBe('function');
  });
});
