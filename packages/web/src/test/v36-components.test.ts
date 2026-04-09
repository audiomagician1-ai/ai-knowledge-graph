/**
 * V3.6 Sprint FE Tests — FSRSInsightsWidget + GoalRecommendWidget + DashboardWidgetGrid
 */
import { describe, it, expect } from 'vitest';

describe('V3.6 Dashboard Widgets', () => {
  it('FSRSInsightsWidget exports correctly', async () => {
    const mod = await import('../components/dashboard/FSRSInsightsWidget');
    expect(mod.FSRSInsightsWidget).toBeDefined();
    expect(typeof mod.FSRSInsightsWidget).toBe('function');
  });

  it('GoalRecommendWidget exports correctly', async () => {
    const mod = await import('../components/dashboard/GoalRecommendWidget');
    expect(mod.GoalRecommendWidget).toBeDefined();
    expect(typeof mod.GoalRecommendWidget).toBe('function');
  });

  it('DashboardWidgetGrid includes V3.6 new widgets', async () => {
    const src = await import('../components/dashboard/DashboardWidgetGrid?raw');
    expect(src.default).toContain('FSRSInsightsWidget');
    expect(src.default).toContain('GoalRecommendWidget');
  });

  it('FSRSInsightsWidget has no required props', async () => {
    const mod = await import('../components/dashboard/FSRSInsightsWidget');
    expect(mod.FSRSInsightsWidget.length).toBe(0);
  });

  it('GoalRecommendWidget has no required props', async () => {
    const mod = await import('../components/dashboard/GoalRecommendWidget');
    expect(mod.GoalRecommendWidget.length).toBe(0);
  });
});
