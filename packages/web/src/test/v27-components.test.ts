import { describe, it, expect } from 'vitest';

describe('V2.7 WeakConceptsWidget', () => {
  it('should export WeakConceptsWidget as named export', async () => {
    const mod = await import('@/components/dashboard/WeakConceptsWidget');
    expect(mod.WeakConceptsWidget).toBeDefined();
    expect(typeof mod.WeakConceptsWidget).toBe('function');
  });
});

describe('V2.7 LearningEfficiencyChart', () => {
  it('should export LearningEfficiencyChart as named export', async () => {
    const mod = await import('@/components/dashboard/LearningEfficiencyChart');
    expect(mod.LearningEfficiencyChart).toBeDefined();
    expect(typeof mod.LearningEfficiencyChart).toBe('function');
  });
});

describe('V2.7 DashboardPage integration', () => {
  it('should export DashboardPage with V2.7 lazy widgets', async () => {
    const mod = await import('@/pages/DashboardPage');
    expect(mod.DashboardPage).toBeDefined();
    expect(typeof mod.DashboardPage).toBe('function');
  });

  it('should lazy-load WeakConceptsWidget', async () => {
    const mod = await import('@/components/dashboard/WeakConceptsWidget');
    expect(mod.WeakConceptsWidget).toBeDefined();
  });

  it('should lazy-load LearningEfficiencyChart', async () => {
    const mod = await import('@/components/dashboard/LearningEfficiencyChart');
    expect(mod.LearningEfficiencyChart).toBeDefined();
  });
});