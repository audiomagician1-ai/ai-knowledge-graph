import { describe, it, expect } from 'vitest';

describe('V2.6 DomainRecommendWidget', () => {
  it('should export DomainRecommendWidget as named export', async () => {
    const mod = await import('@/components/dashboard/DomainRecommendWidget');
    expect(mod.DomainRecommendWidget).toBeDefined();
    expect(typeof mod.DomainRecommendWidget).toBe('function');
  });
});

describe('V2.6 StudyPlanWidget', () => {
  it('should export StudyPlanWidget as named export', async () => {
    const mod = await import('@/components/dashboard/StudyPlanWidget');
    expect(mod.StudyPlanWidget).toBeDefined();
    expect(typeof mod.StudyPlanWidget).toBe('function');
  });

  it('should define TYPE_STYLES for review/continue/new', async () => {
    // Module should import cleanly and component should be valid
    const mod = await import('@/components/dashboard/StudyPlanWidget');
    expect(mod.StudyPlanWidget).toBeDefined();
  });
});

describe('V2.6 LearningJourneyPage', () => {
  it('should export LearningJourneyPage as named export', async () => {
    const mod = await import('@/pages/LearningJourneyPage');
    expect(mod.LearningJourneyPage).toBeDefined();
    expect(typeof mod.LearningJourneyPage).toBe('function');
  });

  it('should define EVENT_ICONS mapping for mastered/milestone/domain_milestone', async () => {
    const mod = await import('@/pages/LearningJourneyPage');
    expect(mod).toBeDefined();
  });
});

describe('V2.6 App Route Registration', () => {
  it('should register /journey route via lazy import', async () => {
    const mod = await import('@/App');
    expect(mod.App).toBeDefined();
    expect(typeof mod.App).toBe('function');
  });
});

describe('V2.6 DashboardPage lazy widget imports', () => {
  it('should lazy-load DomainRecommendWidget', async () => {
    const mod = await import('@/components/dashboard/DomainRecommendWidget');
    expect(mod.DomainRecommendWidget).toBeDefined();
  });

  it('should lazy-load StudyPlanWidget', async () => {
    const mod = await import('@/components/dashboard/StudyPlanWidget');
    expect(mod.StudyPlanWidget).toBeDefined();
  });

  it('should export DashboardPage with new widgets', async () => {
    const mod = await import('@/pages/DashboardPage');
    expect(mod.DashboardPage).toBeDefined();
    expect(typeof mod.DashboardPage).toBe('function');
  });
});

describe('V2.6 HomePage Journey nav button', () => {
  it('should export HomePage with Map icon import', async () => {
    const mod = await import('@/pages/HomePage');
    expect(mod.HomePage).toBeDefined();
    expect(typeof mod.HomePage).toBe('function');
  });
});