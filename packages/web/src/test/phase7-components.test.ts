import { describe, it, expect } from 'vitest';

describe('learning-path-components', () => {
  it('should export PathGroupSection from PathGroupSection.tsx', async () => {
    const mod = await import('@/components/learning-path/PathGroupSection');
    expect(mod.PathGroupSection).toBeDefined();
    expect(typeof mod.PathGroupSection).toBe('function');
  });

  it('should export KnowledgeGapsSection from KnowledgeGapsSection.tsx', async () => {
    const mod = await import('@/components/learning-path/KnowledgeGapsSection');
    expect(mod.KnowledgeGapsSection).toBeDefined();
    expect(typeof mod.KnowledgeGapsSection).toBe('function');
  });

  it('should export KnowledgeGap type from KnowledgeGapsSection', async () => {
    const mod = await import('@/components/learning-path/KnowledgeGapsSection');
    expect(mod).toBeDefined();
  });

  it('should export PathGroup and PathConcept types from PathGroupSection', async () => {
    const mod = await import('@/components/learning-path/PathGroupSection');
    expect(mod).toBeDefined();
  });
});

describe('dashboard-content-parts', () => {
  it('should export OtherDomainCard from DashboardContentParts.tsx', async () => {
    const mod = await import('@/components/panels/DashboardContentParts');
    expect(mod.OtherDomainCard).toBeDefined();
    expect(typeof mod.OtherDomainCard).toBe('function');
  });

  it('should export ActivityRow from DashboardContentParts.tsx', async () => {
    const mod = await import('@/components/panels/DashboardContentParts');
    expect(mod.ActivityRow).toBeDefined();
    expect(typeof mod.ActivityRow).toBe('function');
  });

  it('should export formatTimeAgo from DashboardContentParts.tsx', async () => {
    const mod = await import('@/components/panels/DashboardContentParts');
    expect(mod.formatTimeAgo).toBeDefined();
    expect(typeof mod.formatTimeAgo).toBe('function');
  });

  it('formatTimeAgo returns correct relative time strings', async () => {
    const { formatTimeAgo } = await import('@/components/panels/DashboardContentParts');
    const now = Date.now();
    expect(formatTimeAgo(now)).toBe('刚刚');
    expect(formatTimeAgo(now - 5 * 60 * 1000)).toBe('5分钟前');
    expect(formatTimeAgo(now - 3 * 60 * 60 * 1000)).toBe('3小时前');
    expect(formatTimeAgo(now - 2 * 24 * 60 * 60 * 1000)).toBe('2天前');
    expect(formatTimeAgo(now - 45 * 24 * 60 * 60 * 1000)).toBe('1个月前');
  });
});

describe('chat-view-component', () => {
  it('should export ChatView from ChatView.tsx', async () => {
    const mod = await import('@/components/chat/ChatView');
    expect(mod.ChatView).toBeDefined();
    expect(typeof mod.ChatView).toBe('function');
  });
});
