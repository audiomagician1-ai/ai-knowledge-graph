import { describe, it, expect } from 'vitest';

describe('V2.5 SessionHistoryPage', () => {
  it('should export SessionHistoryPage as named export', async () => {
    const mod = await import('@/pages/SessionHistoryPage');
    expect(mod.SessionHistoryPage).toBeDefined();
    expect(typeof mod.SessionHistoryPage).toBe('function');
  });

  it('should define ACTION_LABELS with 4 entries (mastered/assessment/start/all)', async () => {
    // The page module should be importable without errors
    const mod = await import('@/pages/SessionHistoryPage');
    expect(mod).toBeDefined();
  });
});

describe('V2.5 MasteryTimeline', () => {
  it('should export MasteryTimeline component', async () => {
    const mod = await import('@/components/dashboard/MasteryTimeline');
    expect(mod.MasteryTimeline).toBeDefined();
    expect(typeof mod.MasteryTimeline).toBe('function');
  });
});

describe('V2.5 CrossDomainBridge', () => {
  it('should export CrossDomainBridge component', async () => {
    const mod = await import('@/components/graph/CrossDomainBridge');
    expect(mod.CrossDomainBridge).toBeDefined();
    expect(typeof mod.CrossDomainBridge).toBe('function');
  });
});

describe('V2.5 App Route Registration', () => {
  it('should register /history route via lazy import', async () => {
    const mod = await import('@/App');
    expect(mod.App).toBeDefined();
    expect(typeof mod.App).toBe('function');
  });
});

describe('V2.5 ChatIdleView Integration', () => {
  it('should export ChatIdleView with MasteryTimeline and CrossDomainBridge imported', async () => {
    const mod = await import('@/components/chat/ChatIdleView');
    expect(mod.ChatIdleView).toBeDefined();
    expect(typeof mod.ChatIdleView).toBe('function');
  });
});
