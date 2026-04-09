/**
 * V3.7 Sprint FE Tests — LearningProfileWidget + DomainOverviewBatchWidget
 */
import { describe, it, expect } from 'vitest';

describe('V3.7 Dashboard Widgets', () => {
  it('LearningProfileWidget exports correctly', async () => {
    const mod = await import('../components/dashboard/LearningProfileWidget');
    expect(mod.LearningProfileWidget).toBeDefined();
    expect(typeof mod.LearningProfileWidget).toBe('function');
  });

  it('DomainOverviewBatchWidget exports correctly', async () => {
    const mod = await import('../components/dashboard/DomainOverviewBatchWidget');
    expect(mod.DomainOverviewBatchWidget).toBeDefined();
    expect(typeof mod.DomainOverviewBatchWidget).toBe('function');
  });

  it('DashboardWidgetGrid includes V3.7 new widgets', async () => {
    const src = await import('../components/dashboard/DashboardWidgetGrid?raw');
    expect(src.default).toContain('LearningProfileWidget');
    expect(src.default).toContain('DomainOverviewBatchWidget');
  });

  it('LearningProfileWidget has no required props', async () => {
    const mod = await import('../components/dashboard/LearningProfileWidget');
    expect(mod.LearningProfileWidget.length).toBe(0);
  });

  it('DomainOverviewBatchWidget has no required props', async () => {
    const mod = await import('../components/dashboard/DomainOverviewBatchWidget');
    expect(mod.DomainOverviewBatchWidget.length).toBe(0);
  });
});
